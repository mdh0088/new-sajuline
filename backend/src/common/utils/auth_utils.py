"""
인증 관련 공통 유틸리티 함수
"""
from fastapi import HTTPException, status
from src.services.auth_service import TokenPayload


def verify_counselor_role(current_user: TokenPayload) -> None:
    """
    상담사 권한 확인
    
    Args:
        current_user: JWT 토큰에서 추출된 사용자 정보
        
    Raises:
        HTTPException: 상담사 권한이 없는 경우 403 에러 발생
    """
    if current_user.role != "counselor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="상담사만 접근할 수 있습니다"
        )


def verify_user_role(current_user: TokenPayload) -> None:
    """
    사용자 권한 확인
    
    Args:
        current_user: JWT 토큰에서 추출된 사용자 정보
        
    Raises:
        HTTPException: 사용자 권한이 없는 경우 403 에러 발생
    """
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="일반 사용자만 접근할 수 있습니다"
        )


def verify_role(current_user: TokenPayload, required_role: str) -> None:
    """
    특정 역할 권한 확인
    
    Args:
        current_user: JWT 토큰에서 추출된 사용자 정보
        required_role: 필요한 역할 (user, counselor)
        
    Raises:
        HTTPException: 필요한 권한이 없는 경우 403 에러 발생
    """
    if current_user.role != required_role:
        role_names = {
            "user": "일반 사용자",
            "counselor": "상담사"
        }
        role_name = role_names.get(required_role, required_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{role_name}만 접근할 수 있습니다"
        )