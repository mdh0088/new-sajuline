"""
캐시 매니저 단위 테스트.

Stories: STORY-6-2
FRs: FR30, NFR-P5, NFR-P6, NFR-I3
"""

import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import redis.asyncio as redis

from src.services.ai.utils.cache_manager import (
    AICacheManager,
    CacheConfig,
    CacheEntry,
    CacheStats,
)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock(spec=redis.Redis)
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock(return_value=True)
    mock.hincrby = AsyncMock(return_value=1)
    mock.hincrbyfloat = AsyncMock(return_value=1.0)
    mock.hgetall = AsyncMock(return_value={})
    mock.delete = AsyncMock(return_value=0)
    mock.scan_iter = AsyncMock(return_value=iter([]))
    mock.pipeline = MagicMock()
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def cache_config():
    """기본 캐시 설정"""
    return CacheConfig(
        query_ttl=300,
        schema_ttl=3600,
        stats_ttl=86400,
        prefix="ai_cache",
    )


@pytest.fixture
def cache_manager(mock_redis, cache_config):
    """캐시 매니저 인스턴스"""
    return AICacheManager(mock_redis, cache_config)


class TestAICacheManager:
    """AICacheManager 단위 테스트"""

    def test_init(self, cache_manager, cache_config):
        """초기화 테스트"""
        assert cache_manager.config == cache_config
        assert cache_manager._connected is True

    def test_generate_cache_key(self, cache_manager):
        """캐시 키 생성 테스트"""
        key = cache_manager._generate_cache_key(
            question="오늘 결제 금액은?",
            db_scope="mariadb",
            admin_role="admin",
        )

        # 키 형식 검증
        assert key.startswith("ai_cache:query:")
        assert len(key.split(":")[-1]) == 16  # 해시 길이

        # 동일 입력 → 동일 키
        key2 = cache_manager._generate_cache_key(
            question="오늘 결제 금액은?",
            db_scope="mariadb",
            admin_role="admin",
        )
        assert key == key2

        # 다른 입력 → 다른 키
        key3 = cache_manager._generate_cache_key(
            question="오늘 회원 수는?",
            db_scope="mariadb",
            admin_role="admin",
        )
        assert key != key3

    def test_generate_cache_key_normalization(self, cache_manager):
        """질문 정규화 테스트"""
        # 공백 정리
        key1 = cache_manager._generate_cache_key(
            "오늘  결제   금액은?", "mariadb", "admin"
        )
        key2 = cache_manager._generate_cache_key(
            "오늘 결제 금액은?", "mariadb", "admin"
        )
        assert key1 == key2

        # 대소문자 통일
        key3 = cache_manager._generate_cache_key(
            "TODAY Payment", "mariadb", "admin"
        )
        key4 = cache_manager._generate_cache_key(
            "today payment", "mariadb", "admin"
        )
        assert key3 == key4

    @pytest.mark.asyncio
    async def test_get_cached_response_hit(self, cache_manager, mock_redis):
        """캐시 히트 테스트"""
        # Mock 데이터 설정
        cached_data = {
            "response": {"answer": "100만원", "sql": "SELECT SUM(...)"},
            "created_at": "2024-01-01T00:00:00",
            "question": "오늘 결제 금액은?",
            "db_scope": "mariadb",
            "hit_count": 0,
        }
        mock_redis.get.return_value = json.dumps(cached_data, ensure_ascii=False)

        # 실행
        result = await cache_manager.get_cached_response(
            question="오늘 결제 금액은?",
            db_scope="mariadb",
            admin_role="admin",
        )

        # 검증
        assert result is not None
        assert result.from_cache is True
        assert result.data == cached_data["response"]
        assert result.created_at == "2024-01-01T00:00:00"
        assert result.hit_count == 1

        # Redis 호출 검증
        mock_redis.get.assert_called_once()
        mock_redis.hincrby.assert_called_once_with("ai_cache:stats", "hits", 1)

    @pytest.mark.asyncio
    async def test_get_cached_response_miss(self, cache_manager, mock_redis):
        """캐시 미스 테스트"""
        mock_redis.get.return_value = None

        result = await cache_manager.get_cached_response(
            question="오늘 결제 금액은?",
            db_scope="mariadb",
            admin_role="admin",
        )

        assert result is None
        mock_redis.hincrby.assert_called_once_with("ai_cache:stats", "misses", 1)

    @pytest.mark.asyncio
    async def test_get_cached_response_redis_error(self, cache_manager, mock_redis):
        """Redis 에러 시 동작 테스트"""
        mock_redis.get.side_effect = redis.RedisError("Connection failed")

        result = await cache_manager.get_cached_response(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        assert result is None
        assert cache_manager._connected is False

    @pytest.mark.asyncio
    async def test_set_cached_response(self, cache_manager, mock_redis):
        """응답 캐싱 테스트"""
        response = {"answer": "100만원", "sql": "SELECT SUM(...)"}

        result = await cache_manager.set_cached_response(
            question="오늘 결제 금액은?",
            db_scope="mariadb",
            admin_role="admin",
            response=response,
        )

        assert result is True
        mock_redis.setex.assert_called_once()

        # setex 호출 인자 검증
        call_args = mock_redis.setex.call_args
        key, ttl, value = call_args[0]
        assert key.startswith("ai_cache:query:")
        assert ttl == 300  # query_ttl

        cached_data = json.loads(value)
        assert cached_data["response"] == response
        assert cached_data["question"] == "오늘 결제 금액은?"

    @pytest.mark.asyncio
    async def test_set_cached_response_redis_error(self, cache_manager, mock_redis):
        """캐시 저장 실패 테스트"""
        mock_redis.setex.side_effect = redis.RedisError("Write failed")

        result = await cache_manager.set_cached_response(
            question="테스트",
            db_scope="mariadb",
            admin_role="admin",
            response={"answer": "test"},
        )

        assert result is False
        assert cache_manager._connected is False

    @pytest.mark.asyncio
    async def test_invalidate_by_pattern(self, cache_manager, mock_redis):
        """패턴 기반 무효화 테스트"""

        async def mock_scan_iter(**kwargs):
            keys = [
                b"ai_cache:query:abc123",
                b"ai_cache:query:def456",
            ]
            for key in keys:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete.return_value = 2

        deleted = await cache_manager.invalidate_by_pattern("query:")

        assert deleted == 2
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalidate_all(self, cache_manager, mock_redis):
        """전체 무효화 테스트"""

        async def mock_scan_iter(**kwargs):
            for key in [b"ai_cache:query:test1", b"ai_cache:query:test2"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete.return_value = 2

        deleted = await cache_manager.invalidate_all()

        assert deleted == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, cache_manager, mock_redis):
        """통계 조회 테스트"""
        mock_redis.hgetall.return_value = {
            b"hits": b"30",
            b"misses": b"70",
            b"avg_cached_time": b"50.5",
            b"avg_uncached_time": b"250.0",
        }

        stats = await cache_manager.get_stats()

        assert stats.total_requests == 100
        assert stats.cache_hits == 30
        assert stats.cache_misses == 70
        assert stats.hit_rate == 30.0
        assert stats.avg_response_time_cached == 50.5
        assert stats.avg_response_time_uncached == 250.0

    @pytest.mark.asyncio
    async def test_get_stats_zero_requests(self, cache_manager, mock_redis):
        """요청 0건 통계 테스트"""
        mock_redis.hgetall.return_value = {}

        stats = await cache_manager.get_stats()

        assert stats.total_requests == 0
        assert stats.hit_rate == 0.0

    @pytest.mark.asyncio
    async def test_record_response_time(self, cache_manager, mock_redis):
        """응답 시간 기록 테스트"""
        # Pipeline mock 설정
        pipeline_mock = AsyncMock()
        pipeline_mock.hincrbyfloat = AsyncMock()
        pipeline_mock.hincrby = AsyncMock()
        pipeline_mock.execute = AsyncMock()
        pipeline_mock.__aenter__ = AsyncMock(return_value=pipeline_mock)
        pipeline_mock.__aexit__ = AsyncMock(return_value=None)
        mock_redis.pipeline.return_value = pipeline_mock

        # 캐시된 응답 시간 기록
        await cache_manager.record_response_time(
            response_time_ms=50.5, from_cache=True
        )

        # Pipeline 호출 확인
        pipeline_mock.hincrbyfloat.assert_called()
        pipeline_mock.hincrby.assert_called()
        pipeline_mock.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self, cache_manager, mock_redis):
        """헬스체크 성공 테스트"""
        mock_redis.ping.return_value = True

        result = await cache_manager.health_check()

        assert result is True
        assert cache_manager._connected is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, cache_manager, mock_redis):
        """헬스체크 실패 테스트"""
        mock_redis.ping.side_effect = redis.RedisError("Connection lost")

        result = await cache_manager.health_check()

        assert result is False
        assert cache_manager._connected is False

    @pytest.mark.asyncio
    async def test_cache_disabled_on_connection_failure(
        self, cache_manager, mock_redis
    ):
        """연결 실패 시 캐시 비활성화 테스트"""
        # 연결 실패
        cache_manager._connected = False

        # 캐시 조회는 None 반환
        result = await cache_manager.get_cached_response(
            "test", "mariadb", "admin"
        )
        assert result is None

        # Redis 호출 안 함
        mock_redis.get.assert_not_called()

        # 캐시 저장도 실패
        result = await cache_manager.set_cached_response(
            "test", "mariadb", "admin", {}
        )
        assert result is False
        mock_redis.setex.assert_not_called()


class TestCacheEntry:
    """CacheEntry 데이터클래스 테스트"""

    def test_cache_entry_creation(self):
        """CacheEntry 생성 테스트"""
        entry = CacheEntry(
            data={"answer": "test"},
            created_at="2024-01-01T00:00:00",
            hit_count=5,
            from_cache=True,
        )

        assert entry.data == {"answer": "test"}
        assert entry.created_at == "2024-01-01T00:00:00"
        assert entry.hit_count == 5
        assert entry.from_cache is True


class TestCacheStats:
    """CacheStats 데이터클래스 테스트"""

    def test_cache_stats_creation(self):
        """CacheStats 생성 테스트"""
        stats = CacheStats(
            total_requests=100,
            cache_hits=30,
            cache_misses=70,
            hit_rate=30.0,
            avg_response_time_cached=50.0,
            avg_response_time_uncached=250.0,
        )

        assert stats.total_requests == 100
        assert stats.cache_hits == 30
        assert stats.cache_misses == 70
        assert stats.hit_rate == 30.0
