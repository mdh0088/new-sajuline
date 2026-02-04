"""
Rate Limiter 단위 테스트.

Stories: 3-4
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from src.services.ai.audit.rate_limiter import (
    AIRateLimiter,
    RateLimitResult,
    RATE_LIMITS,
    AIRole,
)


class TestRateLimitResult:
    """RateLimitResult 데이터클래스 테스트"""

    def test_create_allowed_result(self):
        """허용된 요청 결과 생성"""
        result = RateLimitResult(
            allowed=True,
            current_count=5,
            limit=10,
            window_reset=60,
        )

        assert result.allowed is True
        assert result.current_count == 5
        assert result.limit == 10
        assert result.retry_after is None
        assert result.window_reset == 60

    def test_create_blocked_result(self):
        """차단된 요청 결과 생성"""
        result = RateLimitResult(
            allowed=False,
            current_count=11,
            limit=10,
            retry_after=30,
            window_reset=30,
        )

        assert result.allowed is False
        assert result.current_count == 11
        assert result.retry_after == 30


class TestAIRateLimiter:
    """AIRateLimiter 클래스 테스트"""

    @pytest.fixture
    def mock_redis(self):
        """Redis 클라이언트 모킹"""
        redis = AsyncMock()
        redis.incr = AsyncMock()
        redis.expire = AsyncMock()
        redis.ttl = AsyncMock()
        redis.get = AsyncMock()
        return redis

    @pytest.mark.asyncio
    async def test_rate_limits_constants(self):
        """역할별 Rate Limit 상수 정의 확인"""
        assert RATE_LIMITS[AIRole.SUPER_ADMIN] == 60
        assert RATE_LIMITS[AIRole.ADMIN] == 30
        assert RATE_LIMITS[AIRole.VIEWER] == 10

    @pytest.mark.asyncio
    async def test_check_rate_limit_first_request(self, mock_redis):
        """첫 요청 - 허용"""
        mock_redis.incr.return_value = 1
        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert result.allowed is True
        assert result.current_count == 1
        assert result.limit == 30
        assert result.retry_after is None
        assert result.window_reset == 60

        # 첫 요청이므로 expire 설정되어야 함
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_rate_limit_within_limit(self, mock_redis):
        """제한 내 요청 - 허용"""
        mock_redis.incr.return_value = 15  # 30 제한 중 15번째
        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert result.allowed is True
        assert result.current_count == 15
        assert result.limit == 30

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, mock_redis):
        """제한 초과 요청 - 차단"""
        mock_redis.incr.return_value = 31  # 30 제한 초과
        mock_redis.ttl.return_value = 45  # 45초 남음

        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert result.allowed is False
        assert result.current_count == 31
        assert result.limit == 30
        assert result.retry_after == 45
        assert result.window_reset == 45

    @pytest.mark.asyncio
    async def test_check_rate_limit_super_admin_higher_limit(self, mock_redis):
        """Super Admin은 더 높은 제한 적용"""
        mock_redis.incr.return_value = 45
        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.SUPER_ADMIN,
        )

        assert result.allowed is True
        assert result.limit == 60  # Super Admin 제한

    @pytest.mark.asyncio
    async def test_check_rate_limit_viewer_lower_limit(self, mock_redis):
        """Viewer는 낮은 제한 적용"""
        mock_redis.incr.return_value = 5
        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=200,
            role=AIRole.VIEWER,
        )

        assert result.allowed is True
        assert result.limit == 10  # Viewer 제한

    @pytest.mark.asyncio
    async def test_redis_key_format(self, mock_redis):
        """Redis 키 형식 확인"""
        mock_redis.incr.return_value = 1
        limiter = AIRateLimiter(mock_redis)

        with patch("src.services.ai.audit.rate_limiter.datetime") as mock_dt:
            mock_now = Mock()
            mock_now.strftime.return_value = "202602040100"
            mock_dt.now.return_value = mock_now

            await limiter.check_rate_limit(
                admin_id=123,
                role=AIRole.ADMIN,
            )

            # ai_ratelimit:{admin_id}:{minute} 형식
            mock_redis.incr.assert_called_once()
            call_args = mock_redis.incr.call_args[0][0]
            assert call_args == "ai_ratelimit:123:202602040100"

    @pytest.mark.asyncio
    async def test_get_usage_stats_no_usage(self, mock_redis):
        """사용량 통계 조회 - 사용 없음"""
        mock_redis.get.return_value = None
        limiter = AIRateLimiter(mock_redis)

        stats = await limiter.get_usage_stats(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert stats["current"] == 0
        assert stats["limit"] == 30
        assert stats["remaining"] == 30
        assert stats["reset_seconds"] == 60

    @pytest.mark.asyncio
    async def test_get_usage_stats_with_usage(self, mock_redis):
        """사용량 통계 조회 - 사용 중"""
        mock_redis.get.return_value = "12"
        limiter = AIRateLimiter(mock_redis)

        stats = await limiter.get_usage_stats(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert stats["current"] == 12
        assert stats["limit"] == 30
        assert stats["remaining"] == 18
        assert stats["reset_seconds"] == 60

    @pytest.mark.asyncio
    async def test_ttl_minimum_retry_after(self, mock_redis):
        """TTL이 0 또는 음수일 때 최소 1초 설정"""
        mock_redis.incr.return_value = 31
        mock_redis.ttl.return_value = 0  # TTL 만료 직전

        limiter = AIRateLimiter(mock_redis)

        result = await limiter.check_rate_limit(
            admin_id=100,
            role=AIRole.ADMIN,
        )

        assert result.retry_after == 1  # 최소값
