"""
RBAC 통합 테스트

AC 1-6 검증:
- Super Admin 전체 접근 테스트
- Admin 제한된 접근 테스트
- Viewer 최소 접근 테스트
- 403 에러 반환 테스트
- 429 Rate Limit 테스트
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from src.services.ai.security.rbac import AIRole, check_ai_permission
from src.services.ai.security.rate_limiter import rate_limit_dependency
from src.services.ai.config.table_permissions import can_access_table
from src.models.admin_model import Admin


class TestSuperAdminAccess:
    """Super Admin 전체 접근 테스트"""

    @pytest.fixture
    def super_admin(self):
        """Super Admin 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 1
        admin.role = "super_admin"
        admin.username = "super_admin"
        admin.is_active = True
        return admin

    def test_super_admin_all_permissions(self, super_admin):
        """Super Admin은 모든 권한을 가짐"""
        permission = check_ai_permission(super_admin)

        assert permission["admin_id"] == 1
        assert permission["role"] == AIRole.SUPER_ADMIN
        assert permission["allowed"] is True

    def test_super_admin_all_tables(self, super_admin):
        """Super Admin은 모든 테이블 접근 가능"""
        permission = check_ai_permission(super_admin)
        role = permission["role"]

        # 일반 테이블
        assert can_access_table(role, "t_payment")
        assert can_access_table(role, "t_user")

        # 민감 테이블
        assert can_access_table(role, "t_admin")
        assert can_access_table(role, "t_user_password")
        assert can_access_table(role, "t_payment_card")

        # 임의의 테이블
        assert can_access_table(role, "any_random_table")

    @pytest.mark.asyncio
    async def test_super_admin_high_rate_limit(self, super_admin):
        """Super Admin은 높은 Rate Limit (60/min)"""
        permission = check_ai_permission(super_admin)

        # Redis Mock
        mock_redis = Mock()
        mock_redis.incr = AsyncMock(return_value=50)  # 60 미만

        # Rate Limit 체크
        result = await rate_limit_dependency(permission, mock_redis)

        # 허용됨 (에러 없음)
        assert result is None


class TestAdminAccess:
    """Admin 제한된 접근 테스트"""

    @pytest.fixture
    def admin(self):
        """Admin 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 2
        admin.role = "admin"
        admin.username = "admin_user"
        admin.is_active = True
        return admin

    def test_admin_limited_permissions(self, admin):
        """Admin은 제한된 권한을 가짐"""
        permission = check_ai_permission(admin)

        assert permission["admin_id"] == 2
        assert permission["role"] == AIRole.ADMIN
        assert permission["allowed"] is True

    def test_admin_allowed_tables(self, admin):
        """Admin은 허용된 테이블만 접근 가능"""
        permission = check_ai_permission(admin)
        role = permission["role"]

        # 허용된 테이블
        assert can_access_table(role, "t_payment")
        assert can_access_table(role, "t_user")
        assert can_access_table(role, "t_counselor")
        assert can_access_table(role, "t_order")

    def test_admin_blocked_sensitive_tables(self, admin):
        """Admin은 민감 테이블 접근 불가"""
        permission = check_ai_permission(admin)
        role = permission["role"]

        # 민감 테이블 차단
        assert not can_access_table(role, "t_admin")
        assert not can_access_table(role, "t_user_password")
        assert not can_access_table(role, "t_payment_card")

    @pytest.mark.asyncio
    async def test_admin_medium_rate_limit(self, admin):
        """Admin은 중간 Rate Limit (30/min)"""
        permission = check_ai_permission(admin)

        # Redis Mock
        mock_redis = Mock()
        mock_redis.incr = AsyncMock(return_value=25)  # 30 미만

        # Rate Limit 체크
        result = await rate_limit_dependency(permission, mock_redis)

        # 허용됨
        assert result is None


class TestViewerAccess:
    """Viewer 최소 접근 테스트"""

    @pytest.fixture
    def viewer(self):
        """Viewer 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 3
        admin.role = "viewer"
        admin.username = "viewer_user"
        admin.is_active = True
        return admin

    def test_viewer_minimal_permissions(self, viewer):
        """Viewer는 최소 권한을 가짐"""
        permission = check_ai_permission(viewer)

        assert permission["admin_id"] == 3
        assert permission["role"] == AIRole.VIEWER
        assert permission["allowed"] is True

    def test_viewer_minimal_tables(self, viewer):
        """Viewer는 최소한의 테이블만 접근 가능"""
        permission = check_ai_permission(viewer)
        role = permission["role"]

        # 일부 테이블만 허용 (집계용)
        assert can_access_table(role, "t_payment")
        assert can_access_table(role, "t_order")

        # 대부분 테이블 차단
        assert not can_access_table(role, "t_user")
        assert not can_access_table(role, "t_counselor")

    def test_viewer_blocked_sensitive_tables(self, viewer):
        """Viewer는 민감 테이블 접근 불가"""
        permission = check_ai_permission(viewer)
        role = permission["role"]

        # 민감 테이블 차단
        assert not can_access_table(role, "t_admin")
        assert not can_access_table(role, "t_user_password")
        assert not can_access_table(role, "t_payment_card")

    @pytest.mark.asyncio
    async def test_viewer_low_rate_limit(self, viewer):
        """Viewer는 낮은 Rate Limit (10/min)"""
        permission = check_ai_permission(viewer)

        # Redis Mock
        mock_redis = Mock()
        mock_redis.incr = AsyncMock(return_value=8)  # 10 미만

        # Rate Limit 체크
        result = await rate_limit_dependency(permission, mock_redis)

        # 허용됨
        assert result is None


class Test403ErrorResponse:
    """403 에러 반환 테스트"""

    def test_unauthenticated_403(self):
        """미인증 사용자는 401 에러"""
        with pytest.raises(HTTPException) as exc_info:
            check_ai_permission(None)

        assert exc_info.value.status_code == 401

    def test_inactive_admin_403(self):
        """비활성화된 관리자는 403 에러"""
        admin = Mock(spec=Admin)
        admin.id = 4
        admin.role = "admin"
        admin.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            check_ai_permission(admin)

        assert exc_info.value.status_code == 403


class Test429RateLimitError:
    """429 Rate Limit 에러 테스트"""

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_429(self):
        """Rate Limit 초과 시 429 에러"""
        permission = {
            "admin_id": 1,
            "role": AIRole.ADMIN,
            "allowed": True,
        }

        # Redis Mock - Limit 초과
        mock_redis = Mock()
        mock_redis.incr = AsyncMock(return_value=31)  # Admin limit: 30
        mock_redis.ttl = AsyncMock(return_value=45)

        with patch('src.services.ai.security.rate_limiter.AIRateLimiter') as mock_limiter_class:
            mock_limiter = Mock()
            mock_limiter.check_rate_limit = AsyncMock(return_value=(False, 45))
            mock_limiter_class.return_value = mock_limiter

            with pytest.raises(HTTPException) as exc_info:
                await rate_limit_dependency(permission, mock_redis)

            assert exc_info.value.status_code == 429
            assert "Retry-After" in exc_info.value.headers
