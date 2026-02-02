"""
RBAC 모듈 단위 테스트

AC 1-4 검증:
- Super Admin 전체 접근 권한
- Admin 제한된 접근 권한
- Viewer 최소 접근 권한
- 권한 없는 접근 시도 403 에러
"""
import pytest
from unittest.mock import Mock
from fastapi import HTTPException

from src.services.ai.security.rbac import (
    AIRole,
    get_admin_ai_role,
    check_ai_permission,
)
from src.models.admin_model import Admin


class TestAIRole:
    """AIRole Enum 테스트"""

    def test_role_values(self):
        """역할 값 확인"""
        assert AIRole.SUPER_ADMIN.value == "super_admin"
        assert AIRole.ADMIN.value == "admin"
        assert AIRole.VIEWER.value == "viewer"


class TestGetAdminAIRole:
    """get_admin_ai_role() 함수 테스트"""

    def test_super_admin_role(self):
        """Super Admin 역할 반환"""
        admin = Mock(spec=Admin)
        admin.role = "super_admin"

        role = get_admin_ai_role(admin)

        assert role == AIRole.SUPER_ADMIN

    def test_admin_role(self):
        """Admin 역할 반환"""
        admin = Mock(spec=Admin)
        admin.role = "admin"

        role = get_admin_ai_role(admin)

        assert role == AIRole.ADMIN

    def test_viewer_role(self):
        """Viewer 역할 반환"""
        admin = Mock(spec=Admin)
        admin.role = "viewer"

        role = get_admin_ai_role(admin)

        assert role == AIRole.VIEWER

    def test_default_to_viewer(self):
        """알 수 없는 역할은 Viewer로 기본값"""
        admin = Mock(spec=Admin)
        admin.role = "unknown_role"

        role = get_admin_ai_role(admin)

        assert role == AIRole.VIEWER


class TestCheckAIPermission:
    """check_ai_permission() 의존성 테스트"""

    @pytest.fixture
    def super_admin(self):
        """Super Admin 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 1
        admin.role = "super_admin"
        admin.username = "super_admin"
        return admin

    @pytest.fixture
    def normal_admin(self):
        """일반 Admin 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 2
        admin.role = "admin"
        admin.username = "admin_user"
        return admin

    @pytest.fixture
    def viewer(self):
        """Viewer 픽스처"""
        admin = Mock(spec=Admin)
        admin.id = 3
        admin.role = "viewer"
        admin.username = "viewer_user"
        return admin

    def test_super_admin_permission(self, super_admin):
        """Super Admin은 항상 권한 허용"""
        permission = check_ai_permission(super_admin)

        assert permission["admin_id"] == 1
        assert permission["role"] == AIRole.SUPER_ADMIN
        assert permission["allowed"] is True

    def test_admin_permission(self, normal_admin):
        """Admin 권한 확인"""
        permission = check_ai_permission(normal_admin)

        assert permission["admin_id"] == 2
        assert permission["role"] == AIRole.ADMIN
        assert permission["allowed"] is True

    def test_viewer_permission(self, viewer):
        """Viewer 권한 확인"""
        permission = check_ai_permission(viewer)

        assert permission["admin_id"] == 3
        assert permission["role"] == AIRole.VIEWER
        assert permission["allowed"] is True

    def test_unauthenticated_access(self):
        """인증되지 않은 접근 거부"""
        with pytest.raises(HTTPException) as exc_info:
            check_ai_permission(None)

        assert exc_info.value.status_code == 401
        assert "인증" in exc_info.value.detail

    def test_inactive_admin(self):
        """비활성화된 관리자 접근 거부"""
        admin = Mock(spec=Admin)
        admin.id = 4
        admin.role = "admin"
        admin.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            check_ai_permission(admin)

        assert exc_info.value.status_code == 403
        assert "비활성화" in exc_info.value.detail
