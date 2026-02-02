"""
권한 유틸리티: 역할 검증 및 JWT 인증

Stories: 1-2
FRs: FR-012
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from src.schemas.auth_schema import TokenPayload
from src.schemas.ai.auth_schema import AUTH_ERROR_CODES
from src.models.admin_model import Admin
from src.config.settings import settings
from src.core.database import get_db
from src.services.ai.utils.auth_logger import log_ai_access


# HTTP Bearer 인증 스킴
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """
    현재 인증된 관리자 반환

    Authorization: Bearer {token} 헤더로 JWT 토큰 검증

    Args:
        credentials: HTTP Bearer 인증 정보
        db: 데이터베이스 세션

    Returns:
        Admin: 인증된 관리자 객체

    Raises:
        HTTPException(401): 인증 실패
    """
    token = credentials.credentials
    error_code = None
    error_detail = None

    try:
        # JWT 토큰 디코드
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        admin_id: str = payload.get("sub")

        if admin_id is None:
            error_code = "INVALID_TOKEN"
            error_detail = AUTH_ERROR_CODES[error_code]
            # 인증 실패 로깅
            await log_ai_access(
                admin_id="unknown",
                endpoint="auth",
                status="failure",
                error_code=error_code
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"detail": error_detail, "code": error_code},
            )

    except JWTError as e:
        # JWT 만료 또는 형식 오류
        error_str = str(e)
        if "expired" in error_str.lower():
            error_code = "SESSION_EXPIRED"
            error_detail = AUTH_ERROR_CODES[error_code]
        else:
            error_code = "INVALID_TOKEN"
            error_detail = AUTH_ERROR_CODES[error_code]

        # 인증 실패 로깅
        await log_ai_access(
            admin_id="unknown",
            endpoint="auth",
            status="failure",
            error_code=error_code
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": error_detail, "code": error_code},
        )

    # DB에서 관리자 조회
    result = await db.execute(
        select(Admin).where(Admin.admin_id == admin_id)
    )
    admin = result.scalar_one_or_none()

    if admin is None:
        error_code = "INVALID_TOKEN"
        error_detail = AUTH_ERROR_CODES[error_code]
        # 인증 실패 로깅
        await log_ai_access(
            admin_id=admin_id,
            endpoint="auth",
            status="failure",
            error_code=error_code
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": error_detail, "code": error_code},
        )

    # 활성 상태 확인
    if not admin.is_active:
        error_code = "INVALID_TOKEN"
        error_detail = "비활성화된 관리자입니다"
        # 인증 실패 로깅
        await log_ai_access(
            admin_id=admin_id,
            endpoint="auth",
            status="failure",
            error_code=error_code
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": error_detail, "code": error_code},
        )

    return admin


async def get_optional_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
    db: AsyncSession = Depends(get_db),
) -> Admin | None:
    """
    선택적 인증 - 토큰 없어도 허용

    Args:
        credentials: HTTP Bearer 인증 정보 (선택적)
        db: 데이터베이스 세션

    Returns:
        Admin | None: 인증된 관리자 객체 또는 None
    """
    if credentials is None:
        return None

    try:
        return await get_current_admin(credentials, db)
    except HTTPException:
        # 인증 실패 시 None 반환 (에러 발생 안 함)
        return None


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


