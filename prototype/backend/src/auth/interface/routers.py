"""
Auth 인터페이스 라우터
인증 관련 API 엔드포인트
"""
# stdlib
from typing import Optional

# third-party
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# local
from ..domain.entities import (
    LoginRequest, LoginResponse, SignupRequest, SignupResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    EmailCheckRequest, EmailCheckResponse, PhoneCheckRequest, PhoneCheckResponse,
    LogoutRequest, LogoutResponse, AuthenticatedUser,
    SocialLoginResponse, SocialSignupRequest, NicknameCheckRequest, NicknameCheckResponse
)
from ..application import AuthApplicationService, SocialAuthApplicationService
from ..infrastructure.providers import get_auth_service as provide_auth_service, get_social_auth_service as provide_social_auth_service
from ...common.utils.client_info import get_client_ip, get_user_agent
from ...common.config.settings import get_settings
from ...common.response import APIResponse
from ...common.decorators.error_handler import handle_api_errors
from ...common.logging.config import set_user_id
from ...common.exceptions.custom import AuthUnauthorizedException, ValidationException

# module-level constants
ACCESS_TOKEN_MAX_AGE = 60 * 30       # 30분
REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # 7일

# FastAPI Router 설정
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["인증"],
    responses={
        400: {"description": "잘못된 요청"},
        401: {"description": "인증 실패"},
        422: {"description": "검증 오류"},
        500: {"description": "서버 오류"}
    }
)

# JWT Bearer 토큰 스킴
security = HTTPBearer()


async def get_auth_service(
    service: AuthApplicationService = Depends(provide_auth_service),
) -> AuthApplicationService:
    return service


async def get_social_auth_service(
    service: SocialAuthApplicationService = Depends(provide_social_auth_service),
) -> SocialAuthApplicationService:
    return service


async def get_current_user_dependency(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> AuthenticatedUser:
    """현재 사용자 의존성 주입"""
    if not credentials:
        raise AuthUnauthorizedException()
    
    user = await auth_service.get_current_user(credentials.credentials)
    try:
        request.state.user_id = user.user_id
        request.state.user_token = set_user_id(user.user_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "사용자 컨텍스트 설정 중 오류 발생: %s", e, exc_info=False
        )
    return user


@router.post(
    "/signup",
    response_model=APIResponse[SignupResponse],
    summary="회원가입",
    description="이메일과 비밀번호로 새 계정을 생성합니다.",
    responses={
        200: {"description": "회원가입 성공"},
        400: {"description": "이미 존재하는 이메일 또는 유효하지 않은 입력"},
    }
)
@handle_api_errors
async def signup(
    signup_request: SignupRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[SignupResponse]:
    """회원가입"""
    return await auth_service.signup(signup_request)


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "잘못된 인증 정보"},
        423: {"description": "계정 잠금"},
    }
)
@handle_api_errors
async def login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[LoginResponse]:
    """로그인"""
    # 클라이언트 정보 추출
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    result = await auth_service.login(login_request, client_ip, user_agent)
    
    # 리프레시 토큰을 HttpOnly 쿠키로 설정
    response.set_cookie(
        key="refresh_token",
        value=result.tokens.refresh_token,
        max_age=60 * 60 * 24 * 7,  # 7일
        httponly=True,
        secure=True,  # HTTPS에서만
        samesite="strict",
        path="/"  # 전체 도메인에서 사용
    )
    
    return result


@router.post(
    "/refresh",
    response_model=APIResponse[RefreshTokenResponse],
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "토큰 갱신 성공"},
        401: {"description": "유효하지 않은 리프레시 토큰"},
    }
)
@handle_api_errors
async def refresh_token(
    request: Request,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[RefreshTokenResponse]:
    """토큰 갱신"""
    # HttpOnly 쿠키에서 리프레시 토큰 추출
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AuthUnauthorizedException(message="리프레시 토큰이 필요합니다.")
    
    refresh_request = RefreshTokenRequest(refresh_token=refresh_token)
    return await auth_service.refresh_token(refresh_request)


@router.post(
    "/logout",
    response_model=APIResponse[LogoutResponse],
    summary="로그아웃",
    description="현재 세션을 종료하고 토큰을 무효화합니다.",
    responses={
        200: {"description": "로그아웃 성공"},
        401: {"description": "유효하지 않은 토큰"},
    }
)
@handle_api_errors
async def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[LogoutResponse]:
    """로그아웃"""
    # 액세스 토큰은 Authorization 헤더에서, 리프레시 토큰은 쿠키에서 추출
    access_token = credentials.credentials
    refresh_token = request.cookies.get("refresh_token")
    
    result = await auth_service.logout(access_token, refresh_token)
    
    # HttpOnly 쿠키 제거
    response.delete_cookie(
        key="refresh_token",
        path="/"
    )
    
    return result


@router.post(
    "/check-email",
    response_model=APIResponse[EmailCheckResponse],
    summary="이메일 중복 확인",
    description="회원가입 전에 이메일 사용 가능 여부를 확인합니다.",
    responses={
        200: {"description": "이메일 확인 완료"},
        400: {"description": "잘못된 이메일 형식"},
    }
)
@handle_api_errors
async def check_email(
    email_request: EmailCheckRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[EmailCheckResponse]:
    """이메일 중복 확인"""
    return await auth_service.check_email_availability(email_request.email)


@router.post(
    "/check-phone",
    response_model=APIResponse[PhoneCheckResponse],
    summary="전화번호 중복 확인",
    description="회원가입 전에 전화번호 사용 가능 여부를 확인합니다.",
    responses={
        200: {"description": "전화번호 확인 완료"},
        400: {"description": "잘못된 전화번호 형식"},
    }
)
@handle_api_errors
async def check_phone(
    phone_request: PhoneCheckRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[PhoneCheckResponse]:
    """전화번호 중복 확인"""
    return await auth_service.check_phone_availability(phone_request.phone)


@router.post(
    "/check-nickname",
    response_model=APIResponse[NicknameCheckResponse],
    summary="닉네임 중복 확인",
    description="회원가입 전에 닉네임 사용 가능 여부를 확인합니다.",
    responses={
        200: {"description": "닉네임 확인 완료"},
        400: {"description": "잘못된 닉네임 형식"},
    }
)
@handle_api_errors
async def check_nickname(
    nickname_request: NicknameCheckRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[NicknameCheckResponse]:
    """닉네임 중복 확인"""
    return await auth_service.check_nickname_availability(nickname_request.nickname)


@router.get(
    "/me",
    response_model=APIResponse[AuthenticatedUser],
    summary="현재 사용자 정보",
    description="현재 로그인된 사용자의 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        401: {"description": "인증되지 않은 사용자"},
    }
)
@handle_api_errors
async def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user_dependency)
) -> APIResponse[AuthenticatedUser]:
    """현재 사용자 정보 조회"""
    return APIResponse(success=True, data=current_user, error=None, meta=None)


@router.get(
    "/validate",
    summary="토큰 유효성 검증",
    description="JWT 토큰의 유효성을 검증합니다.",
    responses={
        200: {"description": "유효한 토큰"},
        401: {"description": "유효하지 않은 토큰"},
    }
)
@handle_api_errors
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> APIResponse[dict]:
    """토큰 유효성 검증"""
    if not credentials:
        raise AuthUnauthorizedException()
    
    user_id = await auth_service.validate_token(credentials.credentials)
    if not user_id:
        raise AuthUnauthorizedException(message="유효하지 않은 토큰입니다.")
    
    return APIResponse(success=True, data={"valid": True, "user_id": user_id}, error=None, meta=None)


@router.get(
    "/sentry-debug",
    summary="Sentry 테스트용 에러 트리거",
    include_in_schema=False,
)
@handle_api_errors
async def sentry_debug() -> APIResponse[dict]:
    _ = 1 / 0  # noqa: B018
    return APIResponse(success=True, data={"ok": True}, error=None, meta=None)


# ==================== 소셜 로그인 API ====================

@router.get(
    "/social/{provider}/url",
    summary="소셜 로그인 URL 생성",
    description="소셜 로그인을 위한 OAuth URL을 생성합니다.",
    response_model=APIResponse[dict]
)
@handle_api_errors
async def get_social_login_url(
    provider: str,
    request: Request
):
    """소셜 로그인 URL 생성"""
    settings = get_settings()
    
    if provider == "kakao":
        # 카카오 OAuth URL 생성
        client_id = settings.KAKAO_CLIENT_ID
        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/kakao/callback"
        auth_url = f"{settings.KAKAO_AUTH_URL}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        
        return APIResponse(success=True, data={"auth_url": auth_url, "provider": "kakao"}, error=None, meta=None)
    
    elif provider == "naver":
        # 네이버 OAuth URL 생성
        client_id = settings.NAVER_CLIENT_ID
        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/naver/callback"
        import uuid
        state = str(uuid.uuid4())
        auth_url = f"{settings.NAVER_AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state={state}"
        
        return APIResponse(success=True, data={"auth_url": auth_url, "provider": "naver", "state": state}, error=None, meta=None)
    
    else:
        raise ValidationException(message=f"지원하지 않는 소셜 로그인 제공자: {provider}", field="provider")


@router.get(
    "/social/{provider}/callback",
    summary="소셜 로그인 콜백 처리",
    description="소셜 로그인 콜백을 처리하고 사용자 정보를 반환합니다.",
    response_model=APIResponse[SocialLoginResponse]
)
@handle_api_errors
async def handle_social_callback(
    provider: str,
    request: Request,
    response: Response,
    code: str = Query(..., description="인증 코드"),
    state: Optional[str] = Query(None, description="상태 값 (naver용)"),
    social_auth_service: SocialAuthApplicationService = Depends(get_social_auth_service)
):
    """소셜 로그인 콜백 처리"""
    # IP 주소와 User-Agent 추출
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # 소셜 로그인 처리
    result = await social_auth_service.social_login_callback(
        provider=provider,
        code=code,
        state=state,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    # HttpOnly 쿠키로 토큰 설정 (선택사항)
    if result.tokens and response:
        response.set_cookie(
            key="access_token",
            value=result.tokens.access_token,
            httponly=True,
            secure=True,  # HTTPS에서만
            samesite="lax",
            max_age=ACCESS_TOKEN_MAX_AGE
        )
        
        if result.tokens.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=result.tokens.refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=REFRESH_TOKEN_MAX_AGE
            )
    
    return result


@router.post(
    "/social/signup",
    summary="소셜 회원가입",
    description="소셜 로그인 사용자의 추가 정보를 받아 회원가입을 완료합니다.",
    response_model=APIResponse[SignupResponse],
    status_code=status.HTTP_201_CREATED
)
@handle_api_errors
async def social_signup(
    signup_request: SocialSignupRequest,
    request: Request,
    response: Response,
    social_auth_service: SocialAuthApplicationService = Depends(get_social_auth_service)
):
    """소셜 회원가입"""
    # IP 주소와 User-Agent 추출
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # 소셜 회원가입 처리
    result = await social_auth_service.social_signup(
        signup_request,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    # HttpOnly 쿠키로 토큰 설정 (선택사항)
    if result.tokens and response:
        response.set_cookie(
            key="access_token",
            value=result.tokens.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=ACCESS_TOKEN_MAX_AGE
        )
        
        if result.tokens.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=result.tokens.refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=REFRESH_TOKEN_MAX_AGE
            )
    
    return result


@router.get(
    "/health",
    summary="Auth 서비스 상태 확인",
    description="Auth 서비스의 상태를 확인합니다.",
    include_in_schema=False  # Swagger 문서에서 숨김
)
@handle_api_errors
async def health_check() -> APIResponse[dict]:
    """Auth 서비스 헬스체크"""
    import datetime
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "auth",
            "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        error=None,
        meta=None,
    )


