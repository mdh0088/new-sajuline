"""
역할 기반 접근 제어 (RBAC) 모듈

AI 어시스턴트 기능에 대한 역할별 권한 관리
"""

from enum import Enum
from typing import TypedDict

from fastapi import HTTPException, status

from src.models.admin_model import Admin


class AIRole(str, Enum):
    """AI 어시스턴트 역할"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"


# 역할별 Rate Limit (요청/분)
ROLE_RATE_LIMITS = {
    AIRole.SUPER_ADMIN: 60,
    AIRole.ADMIN: 30,
    AIRole.VIEWER: 10,
}


class AIPermission(TypedDict):
    """AI 권한 정보"""

    admin_id: int
    role: AIRole
    allowed: bool


def get_admin_ai_role(admin: Admin) -> AIRole:
    """
    관리자의 AI 역할 조회

    Args:
        admin: 관리자 모델

    Returns:
        AIRole: AI 역할 (알 수 없는 역할은 Viewer로 기본값)
    """
    role_mapping = {
        "super_admin": AIRole.SUPER_ADMIN,
        "admin": AIRole.ADMIN,
        "viewer": AIRole.VIEWER,
    }

    return role_mapping.get(admin.role, AIRole.VIEWER)


def check_ai_permission(admin: Admin | None) -> AIPermission:
    """
    AI 어시스턴트 접근 권한 확인

    FastAPI dependency로 사용

    Args:
        admin: 현재 인증된 관리자 (None이면 미인증)

    Returns:
        AIPermission: 권한 정보

    Raises:
        HTTPException: 인증되지 않았거나 비활성화된 경우
    """
    # 미인증 확인
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
        )

    # 비활성화된 관리자 확인
    if hasattr(admin, "is_active") and not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다",
        )

    # 역할 조회
    role = get_admin_ai_role(admin)

    return {
        "admin_id": admin.id,
        "role": role,
        "allowed": True,
    }
