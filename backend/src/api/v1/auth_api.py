"""
인증 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from src.common.middleware.rate_limit import limiter
from src.core.redis import get_redis
from src.schemas.auth_schema import RefreshTokenRequest, TokenResponse
from src.schemas.auth_schema import TokenPayload as TokenPayloadSchema
from src.services.auth_service import AuthService, get_current_user, TokenPayload as ServiceTokenPayload, KST
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException, AuthenticationError
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()

@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="토큰 갱신",
    description="Refresh Token으로 새로운 Access Token과 Refresh Token 발급. 기존 Refresh Token은 블랙리스트 처리됩니다 (Refresh Token Rotation).",
    responses={
        200: {"description": "토큰 갱신 성공"},
        401: {"description": "유효하지 않거나 만료된 Refresh Token"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("20/minute")  # 분당 20회 제한 (토큰 갱신 남용 방지)
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    redis_client = Depends(get_redis)
):
    """토큰 갱신 - Refresh Token Rotation으로 Access Token과 Refresh Token 모두 재발급"""
    log = get_logger_with_request_id()
    
    try:
        # 쿠키에서 기존 Refresh Token 추출 (블랙리스트용)
        old_refresh_token = request.cookies.get("refresh_token") or refresh_request.refresh_token
        if not old_refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 없습니다")
        
        # Refresh Token 검증 및 페이로드 추출
        refresh_payload = await auth_service.verify_refresh_token(old_refresh_token, redis_client)
        log.info("Refresh token validation successful", user_id=refresh_payload["sub"])
        
        # 새로운 Access Token 생성
        new_access_token = auth_service.create_access_token(
            user_id=refresh_payload["sub"],
            email=refresh_payload["email"],
            role=refresh_payload["role"]
        )
        
        # 새로운 Refresh Token 생성 (Refresh Token Rotation)
        new_refresh_token = auth_service.create_refresh_token(
            user_id=refresh_payload["sub"],
            email=refresh_payload["email"],
            role=refresh_payload["role"]
        )
        
        # 기존 Refresh Token 블랙리스트 처리 (보안)
        from datetime import datetime
        old_token_expires = datetime.fromtimestamp(refresh_payload["exp"], tz=KST)
        await auth_service.blacklist_token(
            jti=refresh_payload["jti"],
            expires_at=old_token_expires,
            redis_client=redis_client
        )
        
        # HttpOnly 쿠키에 새로운 Access Token 설정
        secure_cookie = settings.is_production
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=secure_cookie,  # 개발환경에서는 False로 전달
            samesite="lax",  # CSRF 보호
            max_age=30 * 60  # 30분
        )

        # HttpOnly 쿠키에 새로운 Refresh Token 설정
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=secure_cookie,  # 개발환경에서는 False로 전달
            samesite="lax",  # CSRF 보호
            max_age=7 * 24 * 60 * 60  # 7일
        )
        
        # 토큰 갱신 응답 데이터 생성
        token_response = TokenResponse(
            access_token_expires_in=30 * 60,  # 30분 (초 단위)
            refresh_token_expires_in=7 * 24 * 60 * 60  # 7일 (초 단위)
        )
        
        log.info("Token refresh completed successfully", user_id=refresh_payload["sub"])
        return ok(data=token_response, message="토큰 갱신 성공")
        
    except AuthenticationError as e:
        log.warning("Token refresh failed (auth)", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except BaseAppException as e:
        log.error("Token refresh failed (app)", error=str(e))
        raise HTTPException(status_code=getattr(e, "status_code", status.HTTP_400_BAD_REQUEST), detail=str(e))
    except Exception as e:
        log.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="토큰 갱신 중 서버 오류")


@router.get(
    "/me",
    response_model=APIResponse[TokenPayloadSchema],
    summary="현재 인증된 사용자 토큰 정보",
    description="HttpOnly Access Token에서 추출한 사용자 식별자와 역할 정보를 반환합니다.",
)
async def who_am_i(
    request: Request,
    current_user: ServiceTokenPayload = Depends(get_current_user)
):
    """현재 사용자 토큰 페이로드 반환"""
    payload = TokenPayloadSchema(
        sub=current_user.sub,
        email=current_user.email,
        role=current_user.role,
        exp=current_user.exp,
        iat=current_user.iat,
        jti=current_user.jti,
        token_type="access"
    )
    return ok(data=payload, message="현재 사용자 정보")