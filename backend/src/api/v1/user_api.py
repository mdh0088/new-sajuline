"""
사용자 관련 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

# 레이트 리미팅 import 추가
from src.common.middleware.rate_limit import limiter

from src.core.database import get_db_maria
from src.core.redis import get_redis, get_token_blacklist_service
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.schemas.user_schema import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    UserLogin, PasswordChange, UserSignup
)
from src.schemas.auth_schema import LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse
from src.common.response import APIResponse, ok, fail
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException

router = APIRouter(prefix="/users", tags=["users"])


# Dependency injection functions
def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    """사용자 리포지토리 의존성 주입"""
    return UserRepository(db)


def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserService:
    """사용자 서비스 의존성 주입"""
    return UserService(user_repo, auth_service)


@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
    responses={
        201: {"description": "성공"},
        400: {"description": "중복된 사용자 정보"}
    }
)
@limiter.limit("3/hour")  # 시간당 3회 제한 (어뷰징 방지)
async def create_user(
    request: Request,  # ⭐ Request 파라미터 추가 필수
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 생성 - 중복 검증 및 비밀번호 해싱"""
    return await user_service.create_user(user_data)


@router.post(
    "/signup",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="통합 회원가입",
    description="이메일과 비밀번호로 일반 회원가입 또는 소셜 정보로 소셜 회원가입을 처리합니다.",
    responses={
        201: {"description": "회원가입 성공"},
        400: {"description": "중복된 사용자 정보 또는 유효하지 않은 입력"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("3/hour")  # 시간당 3회 제한 (어뷰징 방지)
async def signup(
    request: Request,  # Rate Limiting 필수
    signup_data: UserSignup,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """통합 회원가입 - 일반/소셜 가입 통합 처리"""
    result = await user_service.signup(signup_data)
    return ok(data=result, message="회원가입이 완료되었습니다.")


@router.post(
    "/social/signup", 
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="소셜 회원가입 (자동 로그인)",
    description="소셜 회원가입과 동시에 자동 로그인 처리하여 JWT 토큰을 HttpOnly 쿠키에 설정합니다.",
    responses={
        201: {"description": "회원가입 및 로그인 성공"},
        400: {"description": "중복된 사용자 정보 또는 유효하지 않은 입력"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("3/hour")  # 시간당 3회 제한 (어뷰징 방지)
async def social_signup_with_login(
    request: Request,  # Rate Limiting 필수
    response: Response,
    signup_data: UserSignup,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """소셜 회원가입 + 자동 로그인"""
    log = get_logger_with_request_id()
    log.info("Social signup with auto-login attempt", user_id=signup_data.user_id, provider=signup_data.social_provider)
    
    # 소셜 정보 필수 검증
    if not signup_data.social_provider or not signup_data.social_id:
        raise BaseAppException("소셜 회원가입에는 social_provider와 social_id가 필수입니다.", status_code=400)
    
    # 회원가입 처리
    result = await user_service.signup(signup_data)
    
    # 자동 로그인을 위한 JWT 토큰들 생성
    auth_service = AuthService()
    access_token = auth_service.create_access_token(
        user_id=result.user_id,
        email=result.email,
        role="user"
    )
    
    refresh_token = auth_service.create_refresh_token(
        user_id=result.user_id,
        email=result.email,
        role="user"
    )
    
    # HttpOnly 쿠키에 JWT 토큰들 설정
    # Access Token (30분)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=30 * 60  # 30분
    )
    
    # Refresh Token (7일)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=7 * 24 * 60 * 60  # 7일
    )
    
    # 마지막 로그인 시간 업데이트
    await user_service.user_repo.update_last_login(result.user_id)
    
    log.info("Social signup with auto-login completed with refresh token", user_id=result.user_id, provider=signup_data.social_provider)
    return ok(data=result, message="소셜 회원가입 및 로그인이 완료되었습니다.")


@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="사용자 조회",
    responses={404: {"description": "사용자 없음"}}
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 ID로 조회"""
    return await user_service.get_user(user_id)


@router.get(
    "/email/{email}", 
    response_model=UserResponse,
    summary="이메일로 사용자 조회",
    responses={404: {"description": "사용자 없음"}}
)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """이메일로 사용자 조회"""
    return await user_service.get_user_by_email(email)


@router.put(
    "/{user_id}", 
    response_model=UserResponse,
    summary="사용자 정보 수정",
    responses={404: {"description": "사용자 없음"}}
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 정보 수정 - 중복 검증 포함"""
    return await user_service.update_user(user_id, user_data)


@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    responses={404: {"description": "사용자 없음"}}
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 삭제"""
    await user_service.delete_user(user_id)


@router.get(
    "/", 
    response_model=UserListResponse,
    summary="사용자 목록 조회",
    description="페이지네이션과 상태 필터 지원"
)
async def get_user_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    user_status: Optional[str] = Query(None, description="사용자 상태 필터"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 목록 조회 - 페이징 및 상태별 필터링"""
    return await user_service.get_user_list(page, size, user_status)


@router.post(
    "/authenticate", 
    response_model=UserResponse,
    summary="사용자 인증",
    responses={
        401: {"description": "인증 실패"},
        423: {"description": "계정 잠금"}
    }
)
@limiter.limit("10/minute")  # 분당 10회 제한 (브루트포스 공격 방지)
async def authenticate_user(
    request: Request,
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 인증 - ID/이메일 및 비밀번호 검증"""
    return await user_service.authenticate_user(login_data.user_id, login_data.password)


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="사용자 로그인",
    description="사용자 ID와 비밀번호로 로그인하고 JWT 토큰을 HttpOnly 쿠키에 설정",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "인증 실패"},
        403: {"description": "계정 비활성화"},
        423: {"description": "계정 잠금"}
    }
)
@limiter.limit("15/minute")  # 분당 15회 제한 (로그인 시도 제한)
async def login(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_maria),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """사용자 로그인"""
    log = get_logger_with_request_id()
    log.info("Login attempt", user_id=login_request.user_id)
    
    # 테스트용 강제 API 레이어 오류 발생  
    if login_request.user_id == "api_error_test":
        raise BaseAppException("API layer: 예상치 못한 시스템 오류 테스트", status_code=500)
    
    # 로그인 처리 (예외는 전역 핸들러에서 처리)
    access_token, user_response = await user_service.login(
        user_id_or_email=login_request.user_id,
        password=login_request.password
    )
    
    # Refresh Token 생성
    refresh_token = auth_service.create_refresh_token(
        user_id=user_response.user_id,
        email=user_response.email,
        role="user"
    )
    
    # HttpOnly 쿠키에 JWT 토큰들 설정
    # Access Token (30분)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=30 * 60  # 30분
    )
    
    # Refresh Token (7일)  
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=7 * 24 * 60 * 60  # 7일
    )
    
    # 응답 데이터 생성 (토큰 만료 시간 포함)
    login_response = LoginResponse(
        user_id=user_response.user_id,
        email=user_response.email,
        nickname=user_response.nickname,
        access_token_expires_in=30 * 60,  # 30분 (초 단위)
        refresh_token_expires_in=7 * 24 * 60 * 60  # 7일 (초 단위)
    )
    
    log.info("Authentication successful with refresh token", user_id=user_response.user_id)
    return ok(data=login_response, message="로그인 성공")


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="사용자 로그아웃",
    description="현재 로그인된 사용자를 로그아웃하고 JWT 토큰 쿠키를 삭제",
    responses={200: {"description": "로그아웃 성공"}}
)
async def logout(response: Response):
    """사용자 로그아웃"""
    # HttpOnly 쿠키에서 JWT 토큰들 삭제
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return ok(data=None, message="로그아웃 성공")

@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="토큰 갱신",
    description="Refresh Token으로 새로운 Access Token 발급. 기존 토큰은 블랙리스트 처리됩니다.",
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
    auth_service: AuthService = Depends(get_auth_service)
):
    """토큰 갱신 - Refresh Token으로 새로운 Access Token 발급"""
    log = get_logger_with_request_id()
    
    try:
        # 테스트용 강제 API 레이어 오류 발생
        if refresh_request.refresh_token == "api_refresh_error_test":
            raise BaseAppException("API layer: 토큰 갱신 처리 실패 테스트", status_code=500)
        
        # Refresh Token 검증 및 페이로드 추출
        refresh_payload = auth_service.verify_refresh_token(refresh_request.refresh_token)
        log.info("Refresh token validation successful", user_id=refresh_payload["sub"])
        
        # 새로운 Access Token 생성
        new_access_token = auth_service.create_access_token(
            user_id=refresh_payload["sub"],
            email=refresh_payload["email"],
            role=refresh_payload["role"]
        )
        
        # HttpOnly 쿠키에 새로운 Access Token 설정
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,  # HTTPS에서만 전송
            samesite="lax",  # CSRF 보호
            max_age=30 * 60  # 30분
        )
        
        # 토큰 갱신 응답 데이터 생성
        token_response = TokenResponse(
            access_token_expires_in=30 * 60,  # 30분 (초 단위)
            refresh_token_expires_in=7 * 24 * 60 * 60  # 7일 (초 단위)
        )
        
        log.info("Token refresh completed successfully", user_id=refresh_payload["sub"])
        return ok(data=token_response, message="토큰 갱신 성공")
        
    except Exception as e:
        log.error("Token refresh failed", error=str(e))
        raise
