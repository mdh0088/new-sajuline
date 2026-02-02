"""
Rate Limiter 단위 테스트

AC 5 검증:
- 역할별 Rate Limiting (Super Admin: 60, Admin: 30, Viewer: 10)
- Redis 기반 sliding window 알고리즘
- Rate Limit 초과 시 429 에러
- Retry-After 헤더 포함
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from src.services.ai.security.rbac import AIRole
from src.services.ai.security.rate_limiter import (
    AIRateLimiter,
    ROLE_RATE_LIMITS,
    rate_limit_dependency,
)


class TestRoleRateLimits:
    """역할별 Rate Limit 상수 테스트"""

    def test_rate_limits_defined(self):
        """역할별 Rate Limit이 정의되어 있음"""
        assert ROLE_RATE_LIMITS[AIRole.SUPER_ADMIN] == 60
        assert ROLE_RATE_LIMITS[AIRole.ADMIN] == 30
        assert ROLE_RATE_LIMITS[AIRole.VIEWER] == 10


class TestAIRateLimiter:
    """AIRateLimiter 클래스 테스트"""

    @pytest.fixture
    def mock_redis(self):
        """Redis Mock 픽스처"""
        redis_mock = Mock()
        redis_mock.incr = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.ttl = AsyncMock()
        return redis_mock

    @pytest.fixture
    def rate_limiter(self, mock_redis):
        """Rate Limiter 픽스처"""
        return AIRateLimiter(mock_redis)

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, rate_limiter, mock_redis):
        """첫 요청은 항상 허용"""
        mock_redis.incr.return_value = 1

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.ADMIN
        )

        assert allowed is True
        assert retry_after is None
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_within_limit_allowed(self, rate_limiter, mock_redis):
        """Limit 이내 요청은 허용"""
        # Admin limit: 30
        mock_redis.incr.return_value = 25

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.ADMIN
        )

        assert allowed is True
        assert retry_after is None

    @pytest.mark.asyncio
    async def test_at_limit_allowed(self, rate_limiter, mock_redis):
        """Limit 정확히 도달 시 마지막 요청 허용"""
        # Admin limit: 30
        mock_redis.incr.return_value = 30

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.ADMIN
        )

        assert allowed is True
        assert retry_after is None

    @pytest.mark.asyncio
    async def test_exceed_limit_denied(self, rate_limiter, mock_redis):
        """Limit 초과 시 거부"""
        # Admin limit: 30
        mock_redis.incr.return_value = 31
        mock_redis.ttl.return_value = 45  # 45초 남음

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.ADMIN
        )

        assert allowed is False
        assert retry_after == 45
        mock_redis.ttl.assert_called_once()

    @pytest.mark.asyncio
    async def test_super_admin_higher_limit(self, rate_limiter, mock_redis):
        """Super Admin은 높은 limit"""
        # Super Admin limit: 60
        mock_redis.incr.return_value = 50

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.SUPER_ADMIN
        )

        assert allowed is True

    @pytest.mark.asyncio
    async def test_viewer_lower_limit(self, rate_limiter, mock_redis):
        """Viewer는 낮은 limit"""
        # Viewer limit: 10
        mock_redis.incr.return_value = 11
        mock_redis.ttl.return_value = 30

        allowed, retry_after = await rate_limiter.check_rate_limit(
            admin_id=1,
            role=AIRole.VIEWER
        )

        assert allowed is False
        assert retry_after == 30

    @pytest.mark.asyncio
    async def test_different_admins_independent(self, rate_limiter, mock_redis):
        """서로 다른 관리자는 독립적인 limit"""
        # Admin 1: 첫 요청
        mock_redis.incr.return_value = 1
        allowed1, _ = await rate_limiter.check_rate_limit(1, AIRole.ADMIN)

        # Admin 2: 첫 요청
        mock_redis.incr.return_value = 1
        allowed2, _ = await rate_limiter.check_rate_limit(2, AIRole.ADMIN)

        assert allowed1 is True
        assert allowed2 is True
        assert mock_redis.incr.call_count == 2


class TestRateLimitDependency:
    """rate_limit_dependency() 함수 테스트"""

    @pytest.mark.asyncio
    async def test_allowed_request(self):
        """허용된 요청"""
        mock_redis = Mock()
        mock_limiter = Mock(spec=AIRateLimiter)
        mock_limiter.check_rate_limit = AsyncMock(return_value=(True, None))

        permission = {
            "admin_id": 1,
            "role": AIRole.ADMIN,
            "allowed": True,
        }

        with patch('src.services.ai.security.rate_limiter.AIRateLimiter', return_value=mock_limiter):
            result = await rate_limit_dependency(permission, mock_redis)

        assert result is None  # 정상 통과

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Rate Limit 초과 시 429 에러"""
        mock_redis = Mock()
        mock_limiter = Mock(spec=AIRateLimiter)
        mock_limiter.check_rate_limit = AsyncMock(return_value=(False, 45))

        permission = {
            "admin_id": 1,
            "role": AIRole.ADMIN,
            "allowed": True,
        }

        with patch('src.services.ai.security.rate_limiter.AIRateLimiter', return_value=mock_limiter):
            with pytest.raises(HTTPException) as exc_info:
                await rate_limit_dependency(permission, mock_redis)

        assert exc_info.value.status_code == 429
        assert "요청 한도" in exc_info.value.detail
        # Retry-After 헤더 확인
        assert "Retry-After" in exc_info.value.headers
        assert exc_info.value.headers["Retry-After"] == "45"
