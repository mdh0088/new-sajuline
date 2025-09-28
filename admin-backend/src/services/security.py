"""
보안 의존성: 현재 사용자 파싱 (쿠키 기반)
"""
from fastapi import Request, HTTPException, status, Depends

from src.schemas.auth_schema import TokenPayload
from src.services.auth_service import AuthService
from src.services.deps import get_auth_service


async def get_current_user(request: Request, auth_service: AuthService = Depends(get_auth_service)) -> TokenPayload:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 토큰이 없습니다")
    payload = auth_service.verify_token(access_token)
    return TokenPayload(
        sub=payload["sub"],
        email=payload["email"],
        role=payload.get("role", "admin"),
        exp=payload["exp"],
        iat=payload["iat"],
        jti=payload["jti"],
        token_type=payload.get("token_type", "access"),
    )


