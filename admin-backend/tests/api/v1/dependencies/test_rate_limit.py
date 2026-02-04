"""
Rate Limit Dependency 테스트.

Stories: 3-4
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import HTTPException, Request
from src.api.v1.dependencies.rate_limit import rate_limit_dependency
from src.services.ai.audit.rate_limiter import RateLimitResult, AIRole


class TestRateLimitDependency:
    """Rate Limit Dependency 테스트"""

    @pytest.fixture
    def mock_admin(self):
        """Mock Admin 객체"""
        admin = Mock()
        admin.id = 100
        admin.role = "admin"
        return admin

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis 클라이언트"""
        return AsyncMock()

    @pytest.fixture
    def mock_request(self):
        """Mock Request 객체"""
        request = Mock(spec=Request)
        request.state = Mock()
        return request

    @pytest.mark.asyncio
    async def test_rate_limit_allowed(self, mock_request, mock_admin, mock_redis):
        """Rate limit 허용 - Admin 반환"""
        # Mock rate limit result (허용)
        with patch("src.api.v1.dependencies.rate_limit.AIRateLimiter") as MockLimiter:
            mock_limiter = MockLimiter.return_value
            mock_limiter.check_rate_limit = AsyncMock(return_value=RateLimitResult(
                allowed=True,
                current_count=10,
                limit=30,
                window_reset=60,
            ))

            result = await rate_limit_dependency(
                request=mock_request,
                current_admin=mock_admin,
                redis_client=mock_redis,
            )

            assert result == mock_admin
            # Rate limit 헤더가 request.state에 설정되었는지 확인
            assert hasattr(mock_request.state, "rate_limit_headers")
            headers = mock_request.state.rate_limit_headers
            assert headers["X-RateLimit-Limit"] == "30"
            assert headers["X-RateLimit-Remaining"] == "20"  # 30 - 10
            assert headers["X-RateLimit-Reset"] == "60"

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_raises_429(self, mock_request, mock_admin, mock_redis):
        """Rate limit 초과 - 429 에러 발생"""
        with patch("src.api.v1.dependencies.rate_limit.AIRateLimiter") as MockLimiter:
            mock_limiter = MockLimiter.return_value
            mock_limiter.check_rate_limit = AsyncMock(return_value=RateLimitResult(
                allowed=False,
                current_count=31,
                limit=30,
                retry_after=45,
                window_reset=45,
            ))

            with pytest.raises(HTTPException) as exc_info:
                await rate_limit_dependency(
                    request=mock_request,
                    current_admin=mock_admin,
                    redis_client=mock_redis,
                )

            # 429 상태 코드 확인
            assert exc_info.value.status_code == 429

            # 에러 메시지 확인
            detail = exc_info.value.detail
            assert "요청 한도를 초과했습니다" in detail["message"]
            assert detail["code"] == "AIBI_RATE_LIMITED"
            assert detail["retry_after"] == 45

            # 헤더 확인
            headers = exc_info.value.headers
            assert headers["Retry-After"] == "45"
            assert headers["X-RateLimit-Limit"] == "30"
            assert headers["X-RateLimit-Remaining"] == "0"
            assert headers["X-RateLimit-Reset"] == "45"

    @pytest.mark.asyncio
    async def test_rate_limit_logs_exceeded_event(self, mock_request, mock_admin, mock_redis):
        """Rate limit 초과 시 감사 로그 기록"""
        with patch("src.api.v1.dependencies.rate_limit.AIRateLimiter") as MockLimiter, \
             patch("src.api.v1.dependencies.rate_limit.AIAuditLogger") as MockLogger:
            mock_limiter = MockLimiter.return_value
            mock_limiter.check_rate_limit = AsyncMock(return_value=RateLimitResult(
                allowed=False,
                current_count=31,
                limit=30,
                retry_after=45,
                window_reset=45,
            ))
            MockLogger.log_rate_limit_exceeded = AsyncMock()

            try:
                await rate_limit_dependency(
                    request=mock_request,
                    current_admin=mock_admin,
                    redis_client=mock_redis,
                )
            except HTTPException:
                pass

            # log_rate_limit_exceeded 호출 확인
            MockLogger.log_rate_limit_exceeded.assert_called_once_with(
                admin_id=100,
                admin_role="admin",
                current_count=31,
                limit=30,
            )

    @pytest.mark.asyncio
    async def test_super_admin_higher_limit(self, mock_request, mock_redis):
        """Super Admin은 더 높은 제한 적용"""
        admin = Mock()
        admin.id = 1
        admin.role = "super_admin"

        with patch("src.api.v1.dependencies.rate_limit.AIRateLimiter") as MockLimiter, \
             patch("src.api.v1.dependencies.rate_limit.get_admin_ai_role") as mock_get_role:
            mock_get_role.return_value = AIRole.SUPER_ADMIN
            mock_limiter = MockLimiter.return_value
            mock_limiter.check_rate_limit = AsyncMock(return_value=RateLimitResult(
                allowed=True,
                current_count=50,
                limit=60,
                window_reset=60,
            ))

            result = await rate_limit_dependency(
                request=mock_request,
                current_admin=admin,
                redis_client=mock_redis,
            )

            assert result == admin
            # check_rate_limit이 SUPER_ADMIN 역할로 호출되었는지 확인
            mock_limiter.check_rate_limit.assert_called_once_with(
                1,
                AIRole.SUPER_ADMIN,
            )
