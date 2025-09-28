"""
권한 유틸리티: 역할 검증
"""
from fastapi import HTTPException, status
from src.schemas.auth_schema import TokenPayload


def verify_admin_role(current_user: TokenPayload) -> None:
    """관리자 권한 확인"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자만 접근할 수 있습니다")


def verify_counselor_role(current_user: TokenPayload) -> None:
    """상담사 권한 확인"""
    if current_user.role != "counselor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="상담사만 접근할 수 있습니다")


def verify_role(current_user: TokenPayload, required_role: str) -> None:
    if current_user.role != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{required_role}만 접근할 수 있습니다")


