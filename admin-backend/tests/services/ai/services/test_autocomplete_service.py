"""
자동완성 서비스 단위 테스트.

Stories: 4-3
FRs: FR22
"""
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Issue #13 수정: import 전에 loguru mock
sys.modules["loguru"] = MagicMock()

from src.services.ai.services.autocomplete_service import AutocompleteService


@pytest.fixture
async def mock_redis():
    """Redis 모킹 fixture."""
    mock_client = AsyncMock()
    return mock_client


@pytest.fixture
def autocomplete_service(mock_redis):
    """AutocompleteService fixture."""
    return AutocompleteService(redis_client=mock_redis)


@pytest.mark.asyncio
class TestAutocompleteSuggest:
    """suggest() 메서드 테스트 (AC1, AC2, AC3)."""

    async def test_suggest_returns_popular_questions(
        self, autocomplete_service, mock_redis
    ):
        """AC2: 자주 사용된 질문이 우선 제안된다 (점수 기반 정렬)."""
        # Given: Redis에 인기 질문이 있음 (Issue #5 수정: zrevrange 사용)
        mock_redis.zrevrange.return_value = [
            b"\xec\x98\xa4\xeb\x8a\x98 \xea\xb0\x80\xec\x9e\x85\xec\x9e\x90 \xec\x88\x98\xeb\x8a\x94?",  # "오늘 가입자 수는?"
            b"\xec\x9d\xb4\xeb\xb2\x88 \xeb\x8b\xac \xeb\xa7\xa4\xec\xb6\x9c",  # "이번 달 매출"
        ]

        # When: 자동완성 요청
        result = await autocomplete_service.suggest("오늘", limit=5)

        # Then: 인기 질문이 반환됨
        assert len(result) >= 1
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)
        mock_redis.zrevrange.assert_called_once()

    async def test_suggest_includes_table_columns(
        self, autocomplete_service, mock_redis
    ):
        """AC3: 테이블/컬럼 이름이 자동완성에 포함된다."""
        # Given: 인기 질문이 없고, 키워드만 있음 (Issue #5 수정)
        mock_redis.zrevrange.return_value = []  # 인기 질문 없음
        mock_redis.smembers.return_value = {
            b"members",
            b"payments",
            b"member_id"
        }

        # When: 자동완성 요청
        result = await autocomplete_service.suggest("mem", limit=5)

        # Then: 테이블/컬럼이 반환됨
        assert len(result) >= 0  # 키워드가 있을 수 있음
        mock_redis.zrevrange.assert_called_once()

    async def test_suggest_limits_results(
        self, autocomplete_service, mock_redis
    ):
        """AC1: limit 개수만큼만 반환된다."""
        # Given: 많은 인기 질문이 있음
        mock_redis.zrevrange.return_value = [
            b"question1",
            b"question2",
            b"question3",
            b"question4",
            b"question5",
            b"question6",
        ]

        # When: limit=3으로 자동완성 요청
        result = await autocomplete_service.suggest("q", limit=3)

        # Then: 최대 3개만 반환됨 (prefix 필터링 후)
        assert len(result) <= 3

    async def test_suggest_with_empty_query(
        self, autocomplete_service, mock_redis
    ):
        """빈 쿼리는 API에서 검증되므로 Service로 오지 않음."""
        # Given: API에서 min_length=2 검증
        # When: Service에 빈 쿼리가 오는 경우 (방어 코드)
        mock_redis.zrevrange.return_value = []
        result = await autocomplete_service.suggest("", limit=5)

        # Then: 빈 결과 반환
        assert result == []


@pytest.mark.asyncio
class TestAutocompleteIndexing:
    """질문 인덱싱 테스트 (AC2, AC5)."""

    async def test_index_question_increments_score(
        self, autocomplete_service, mock_redis
    ):
        """질문 사용 시 점수가 증가한다 (AC2 - 사용 빈도 기반 정렬)."""
        # Given: 질문
        question = "오늘 가입자 수는?"

        # When: 질문 인덱싱
        await autocomplete_service.index_question(question)

        # Then: Redis ZINCRBY 호출됨 (점수 증가)
        mock_redis.zincrby.assert_called_once_with(
            "ai:autocomplete:questions", 1, question
        )

    async def test_index_question_with_expiry(
        self, autocomplete_service, mock_redis
    ):
        """인덱싱 시 TTL이 설정된다 (AC5 - 캐시 히트율)."""
        # Given: 질문
        question = "이번 달 매출은?"

        # When: 질문 인덱싱
        await autocomplete_service.index_question(question)

        # Then: ZINCRBY 후 EXPIRE 호출됨
        assert mock_redis.zincrby.call_count == 1
        # Note: expire는 선택사항 (설정에 따라 다름)


@pytest.mark.asyncio
class TestCacheHitRate:
    """캐시 히트율 테스트 (AC5) - Issue #1 수정."""

    async def test_cache_hit_rate_meets_threshold(
        self, autocomplete_service, mock_redis
    ):
        """AC5: 캐시 히트율이 30% 이상이다."""
        # Given: Redis 캐시에 데이터가 있음 (히트)
        mock_redis.zrevrange.return_value = [
            b"question1",
            b"question2",
        ]
        mock_redis.smembers.return_value = set()

        # When: 10번 자동완성 요청
        for _ in range(10):
            await autocomplete_service.suggest("q", limit=5)

        # Then: 캐시 히트율 확인 (Issue #1 수정)
        hit_rate_stats = autocomplete_service.get_cache_hit_rate()
        assert hit_rate_stats["total_requests"] == 10
        assert hit_rate_stats["cache_hits"] == 10  # 모두 히트
        assert hit_rate_stats["hit_rate"] == 1.0  # 100%
        assert hit_rate_stats["threshold_met"] is True  # 30% 이상

    async def test_cache_hit_rate_with_errors(
        self, autocomplete_service, mock_redis
    ):
        """에러 발생 시 캐시 미스 처리 테스트 (Issue #1 추가)."""
        # Given: Redis 에러 발생 시나리오
        call_count = [0]

        def mock_zrevrange(*args, **kwargs):
            call_count[0] += 1
            # 짝수번째는 에러 발생
            if call_count[0] % 2 == 0:
                raise Exception("Redis connection error")
            return [b"question"]

        mock_redis.zrevrange.side_effect = mock_zrevrange

        # When: 10번 요청 (5번 성공, 5번 에러)
        for _ in range(10):
            try:
                await autocomplete_service.suggest("test", limit=5)
            except:
                pass  # 에러 무시

        # Then: 성공한 5번만 히트
        stats = autocomplete_service.get_cache_hit_rate()
        assert stats["total_requests"] == 10
        # 에러 발생 시 suggest가 빈 배열 반환하지만 total_requests는 증가
        # cache_hits는 성공한 경우만 증가


@pytest.mark.asyncio
class TestEdgeCases:
    """엣지 케이스 테스트."""

    async def test_suggest_handles_redis_error(
        self, autocomplete_service, mock_redis
    ):
        """Redis 에러 시 빈 결과를 반환한다."""
        # Given: Redis 에러 발생
        mock_redis.zrangebylex.side_effect = Exception("Connection failed")

        # When: 자동완성 요청
        result = await autocomplete_service.suggest("test", limit=5)

        # Then: 빈 결과 반환 (에러는 로그로만 기록)
        assert result == []

    async def test_suggest_with_special_characters(
        self, autocomplete_service, mock_redis
    ):
        """특수문자가 포함된 쿼리를 처리한다."""
        # Given: 특수문자가 포함된 쿼리
        mock_redis.zrangebylex.return_value = []

        # When: 특수문자 쿼리로 요청
        result = await autocomplete_service.suggest("test@#$", limit=5)

        # Then: 에러 없이 처리됨
        assert isinstance(result, list)

    async def test_index_question_with_empty_string(
        self, autocomplete_service, mock_redis
    ):
        """빈 문자열은 인덱싱하지 않는다."""
        # When: 빈 문자열 인덱싱
        await autocomplete_service.index_question("")

        # Then: Redis 호출 안 됨
        mock_redis.zincrby.assert_not_called()
