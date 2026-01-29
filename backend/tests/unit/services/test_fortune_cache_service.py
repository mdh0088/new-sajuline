"""
운세 캐시 서비스 단위 테스트

Story 2.3 Task 6: FortuneCacheService 테스트 (AC: 6)
- Redis 캐시 조회/저장 테스트 (Mock Redis)
- DB 폴백 테스트
- TTL 계산 테스트
- Redis 장애 시 폴백 테스트
- 커버리지 85% 이상
"""
import pytest
from datetime import date
from unittest.mock import Mock, AsyncMock, patch

from src.services.fortune_cache_service import (
    FortuneCacheService,
    FORTUNE_TTL
)
from src.repositories.fortune_repository import FortuneRepository
from src.models.fortune_history_model import FortuneType, FortuneHistory
from src.schemas.fortune_schema import FortuneResponse, DayPillar


@pytest.fixture
def sample_fortune_response() -> FortuneResponse:
    """테스트용 운세 응답 데이터"""
    return FortuneResponse(
        target_date=date(2026, 1, 29),
        fortune_type="daily",
        day_pillar=DayPillar(stem="갑", branch="진"),
        overall="오늘은 좋은 기운이 감돕니다.",
        love="연인과 좋은 시간을 보내세요.",
        career="업무에서 성과를 낼 수 있습니다.",
        health="충분한 휴식이 필요합니다.",
        wealth="재물운이 좋습니다.",
        source="llm"
    )


@pytest.fixture
def sample_fortune_history(sample_fortune_response: FortuneResponse):
    """테스트용 FortuneHistory 모델"""
    history = Mock(spec=FortuneHistory)
    history.id = "test-history-id"
    history.user_id = "test-user-123"
    history.fortune_type = "daily"
    history.target_date = date(2026, 1, 29)
    history.content = sample_fortune_response.model_dump_json()
    history.ai_model = "gpt-4o-mini"
    history.prompt_version = "v1.0.0"
    return history


@pytest.fixture
def mock_redis_client():
    """모킹된 Redis 클라이언트"""
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.setex = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    return client


@pytest.fixture
def mock_fortune_repository():
    """모킹된 운세 리포지토리"""
    repo = AsyncMock(spec=FortuneRepository)
    repo.get_fortune_by_user_date = AsyncMock(return_value=None)
    repo.create_fortune_history = AsyncMock()
    return repo


@pytest.fixture
def cache_service(mock_redis_client, mock_fortune_repository):
    """FortuneCacheService 인스턴스"""
    return FortuneCacheService(mock_redis_client, mock_fortune_repository)


@pytest.mark.unit
class TestGetCachedFortune:
    """get_cached_fortune() 메서드 테스트"""

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_redis_cache_hit(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository,
        sample_fortune_response: FortuneResponse
    ):
        """AC2: Redis 캐시 히트 시 DB 조회 없이 반환"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.get.return_value = sample_fortune_response.model_dump_json()

        # When
        result, status = await cache_service.get_cached_fortune(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert status == "HIT"
        assert result is not None
        assert result.fortune_type == "daily"
        mock_redis_client.get.assert_called_once()
        mock_fortune_repository.get_fortune_by_user_date.assert_not_called()

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_db_fallback_on_redis_miss(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository,
        sample_fortune_history
    ):
        """AC3: Redis 미스 시 DB 폴백"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.get.return_value = None
        mock_fortune_repository.get_fortune_by_user_date.return_value = sample_fortune_history

        # When
        result, status = await cache_service.get_cached_fortune(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert status == "DB_HIT"
        assert result is not None
        mock_fortune_repository.get_fortune_by_user_date.assert_called_once()
        # Redis 재설정 시도
        mock_redis_client.setex.assert_called_once()

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_redis_failure_db_fallback(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository,
        sample_fortune_history
    ):
        """AC4: Redis 장애 시 DB 폴백으로 정상 응답"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.get.side_effect = Exception("Redis connection failed")
        mock_fortune_repository.get_fortune_by_user_date.return_value = sample_fortune_history

        # When
        result, status = await cache_service.get_cached_fortune(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert status == "DB_HIT"
        assert result is not None
        mock_log.warning.assert_called()  # Redis 실패 로그

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_cache_miss(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository
    ):
        """캐시 미스 시 None과 MISS 반환"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.get.return_value = None
        mock_fortune_repository.get_fortune_by_user_date.return_value = None

        # When
        result, status = await cache_service.get_cached_fortune(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is None
        assert status == "MISS"


@pytest.mark.unit
class TestSetFortuneCache:
    """set_fortune_cache() 메서드 테스트"""

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_cache_set_success(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository,
        sample_fortune_response: FortuneResponse
    ):
        """AC1: Redis + DB 동시 저장 성공"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log

        # When
        result = await cache_service.set_fortune_cache(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29),
            fortune_data=sample_fortune_response,
            ai_model="gpt-4o-mini",
            prompt_version="v1.0.0"
        )

        # Then
        assert result is True
        mock_fortune_repository.create_fortune_history.assert_called_once()
        mock_redis_client.setex.assert_called_once()

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_cache_set_redis_failure_continues(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client,
        mock_fortune_repository,
        sample_fortune_response: FortuneResponse
    ):
        """Redis 저장 실패해도 DB 저장 성공 시 True 반환"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.setex.side_effect = Exception("Redis error")

        # When
        result = await cache_service.set_fortune_cache(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29),
            fortune_data=sample_fortune_response
        )

        # Then
        assert result is True
        mock_fortune_repository.create_fortune_history.assert_called_once()


@pytest.mark.unit
class TestTTLCalculation:
    """TTL 계산 테스트"""

    def test_daily_ttl(self, cache_service: FortuneCacheService):
        """AC5: 일운 TTL 24시간"""
        ttl = cache_service._get_ttl(FortuneType.DAILY)
        assert ttl == 86400  # 24 * 60 * 60

    def test_weekly_ttl(self, cache_service: FortuneCacheService):
        """AC5: 주운 TTL 7일"""
        ttl = cache_service._get_ttl(FortuneType.WEEKLY)
        assert ttl == 604800  # 7 * 24 * 60 * 60

    def test_monthly_ttl(self, cache_service: FortuneCacheService):
        """AC5: 월운 TTL 30일"""
        ttl = cache_service._get_ttl(FortuneType.MONTHLY)
        assert ttl == 2592000  # 30 * 24 * 60 * 60

    def test_yearly_ttl(self, cache_service: FortuneCacheService):
        """AC5: 연운 TTL 365일"""
        ttl = cache_service._get_ttl(FortuneType.YEARLY)
        assert ttl == 31536000  # 365 * 24 * 60 * 60

    def test_ttl_constants(self):
        """TTL 상수 확인"""
        assert FORTUNE_TTL[FortuneType.DAILY] == 86400
        assert FORTUNE_TTL[FortuneType.WEEKLY] == 604800
        assert FORTUNE_TTL[FortuneType.MONTHLY] == 2592000
        assert FORTUNE_TTL[FortuneType.YEARLY] == 31536000


@pytest.mark.unit
class TestCacheKeyGeneration:
    """캐시 키 생성 테스트"""

    def test_daily_cache_key(self, cache_service: FortuneCacheService):
        """일운 캐시 키 형식"""
        key = cache_service._build_cache_key(
            user_id="user123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )
        assert key == "fortune:daily:user123:2026-01-29"

    def test_weekly_cache_key(self, cache_service: FortuneCacheService):
        """주운 캐시 키 형식"""
        key = cache_service._build_cache_key(
            user_id="user123",
            fortune_type=FortuneType.WEEKLY,
            target_date=date(2026, 1, 29)
        )
        assert key == "fortune:weekly:user123:2026-W04"

    def test_monthly_cache_key(self, cache_service: FortuneCacheService):
        """월운 캐시 키 형식"""
        key = cache_service._build_cache_key(
            user_id="user123",
            fortune_type=FortuneType.MONTHLY,
            target_date=date(2026, 1, 29)
        )
        assert key == "fortune:monthly:user123:2026-01"

    def test_yearly_cache_key(self, cache_service: FortuneCacheService):
        """연운 캐시 키 형식"""
        key = cache_service._build_cache_key(
            user_id="user123",
            fortune_type=FortuneType.YEARLY,
            target_date=date(2026, 1, 29)
        )
        assert key == "fortune:yearly:user123:2026"


@pytest.mark.unit
class TestDateKeyGeneration:
    """날짜 키 생성 테스트"""

    def test_daily_date_key(self, cache_service: FortuneCacheService):
        """일운 날짜 키: ISO 형식"""
        key = cache_service._get_date_key(FortuneType.DAILY, date(2026, 1, 29))
        assert key == "2026-01-29"

    def test_weekly_date_key(self, cache_service: FortuneCacheService):
        """주운 날짜 키: YYYY-WNN 형식"""
        key = cache_service._get_date_key(FortuneType.WEEKLY, date(2026, 1, 29))
        # 2026-01-29는 2026년 4주차
        assert key.startswith("2026-W")

    def test_monthly_date_key(self, cache_service: FortuneCacheService):
        """월운 날짜 키: YYYY-MM 형식"""
        key = cache_service._get_date_key(FortuneType.MONTHLY, date(2026, 1, 29))
        assert key == "2026-01"

    def test_yearly_date_key(self, cache_service: FortuneCacheService):
        """연운 날짜 키: YYYY 형식"""
        key = cache_service._get_date_key(FortuneType.YEARLY, date(2026, 1, 29))
        assert key == "2026"


@pytest.mark.unit
class TestInvalidateCache:
    """캐시 무효화 테스트"""

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_invalidate_success(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client
    ):
        """캐시 무효화 성공"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.delete.return_value = 1

        # When
        result = await cache_service.invalidate_cache(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is True
        mock_redis_client.delete.assert_called_once()

    @patch('src.services.fortune_cache_service.get_logger_with_request_id')
    async def test_invalidate_failure(
        self,
        mock_logger,
        cache_service: FortuneCacheService,
        mock_redis_client
    ):
        """캐시 무효화 실패 (Redis 에러)"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.delete.side_effect = Exception("Redis error")

        # When
        result = await cache_service.invalidate_cache(
            user_id="test-user-123",
            fortune_type=FortuneType.DAILY,
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is False
        mock_log.warning.assert_called()


@pytest.mark.unit
class TestHistoryToResponse:
    """DB 이력 → 응답 스키마 변환 테스트"""

    def test_history_to_response(
        self,
        cache_service: FortuneCacheService,
        sample_fortune_history
    ):
        """FortuneHistory → FortuneResponse 변환"""
        # When
        response = cache_service._history_to_response(sample_fortune_history)

        # Then
        assert isinstance(response, FortuneResponse)
        assert response.fortune_type == "daily"
        assert response.overall == "오늘은 좋은 기운이 감돕니다."
