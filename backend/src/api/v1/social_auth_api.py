"""
소셜 로그인 API 엔드포인트 (Kakao, Naver OAuth 2.0)
"""
from typing import Union

from fastapi import APIRouter, Depends, Query, Response, Request
from src.common.middleware.rate_limit import limiter
from src.core.redis import get_redis
from src.core.dependencies import SocialAuthServiceDep
from src.schemas.auth_schema import (
    LoginResponse,
    SocialAuthURLResponse,
    SocialSignupRequired
)
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException, ValidationError

router = APIRouter(prefix="/auth/social", tags=["social-auth"])


@router.get(
    "/{provider}/url",
    response_model=APIResponse[SocialAuthURLResponse],
    summary="소셜 로그인 URL 생성",
    description="Kakao 또는 Naver OAuth 인증 페이지 URL을 생성합니다. Frontend는 이 URL로 사용자를 리다이렉트합니다.",
    responses={
        200: {"description": "OAuth URL 생성 성공"},
        400: {"description": "지원하지 않는 소셜 제공자"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한
async def get_social_auth_url(
    request: Request,
    provider: str,
    social_auth_service: SocialAuthServiceDep,
    redis_client = Depends(get_redis)
):
    """소셜 로그인 URL 생성

    **지원 Provider**: kakao, naver

    **플로우**:
    1. State 생성 (CSRF 방지용 랜덤 문자열)
    2. Redis에 state 저장 (10분 TTL)
    3. OAuth 인증 URL 생성 (state 포함)
    4. Frontend로 URL 반환

    **Frontend 사용법**:
    ```javascript
    const response = await fetch('/api/v1/auth/social/kakao/url');
    const { authorization_url } = response.data;
    window.location.href = authorization_url;  // 사용자를 Kakao 로그인 페이지로 이동
    ```
    """
    log = get_logger_with_request_id()
    log.info("Social auth URL requested", provider=provider)

    try:
        # OAuth URL 생성
        url_response = await social_auth_service.get_authorization_url(provider, redis_client)

        log.info("Social auth URL generated successfully", provider=provider)
        return ok(data=url_response, message=f"{provider.upper()} 로그인 URL 생성 성공")

    except ValidationError as e:
        log.warning("Invalid provider", provider=provider, error=str(e))
        raise
    except Exception as e:
        log.error("Failed to generate social auth URL", provider=provider, error=str(e))
        raise BaseAppException(f"소셜 로그인 URL 생성 실패: {str(e)}", status_code=500)


@router.get(
    "/{provider}/callback",
    response_model=APIResponse[Union[LoginResponse, SocialSignupRequired]],
    summary="소셜 로그인 콜백 처리",
    description="OAuth Provider가 redirect하는 callback을 처리합니다. 기존 사용자는 자동 로그인, 신규 사용자는 회원가입 필요 응답을 반환합니다.",
    responses={
        200: {"description": "로그인 성공 또는 회원가입 필요"},
        400: {"description": "유효하지 않은 인증 코드 또는 state"},
        401: {"description": "OAuth 인증 실패"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한
async def handle_social_callback(
    request: Request,
    response: Response,
    provider: str,
    social_auth_service: SocialAuthServiceDep,
    code: str = Query(..., description="OAuth 인증 코드"),
    state: str = Query(None, description="CSRF 방지용 state (Naver 필수)"),
    redis_client = Depends(get_redis)
):
    """소셜 로그인 콜백 처리

    **OAuth Provider가 호출** (사용자 인증 후 자동 redirect)

    **플로우**:
    1. State 검증 (Redis에서 확인, CSRF 방지)
    2. 인증 코드로 액세스 토큰 교환
    3. 액세스 토큰으로 사용자 정보 조회
    4. 기존 사용자 확인:
       - **존재**: JWT 발급 → HttpOnly 쿠키 설정 → 자동 로그인
       - **없음**: 회원가입 필요 응답 (social_id, email 포함)

    **응답 케이스**:
    - **LoginResponse**: 기존 사용자, JWT 쿠키 설정됨
    - **SocialSignupRequired**: 신규 사용자, Frontend는 `/api/v1/users/social/signup` 호출 필요
    """
    log = get_logger_with_request_id()
    log.info("Social callback received", provider=provider, has_state=bool(state))

    try:
        # OAuth 콜백 처리
        result = await social_auth_service.handle_callback(
            provider=provider,
            code=code,
            state=state,
            redis_client=redis_client,
            response=response
        )

        # 응답 타입에 따라 메시지 구분
        if isinstance(result, LoginResponse):
            log.info("Social login successful",
                    provider=provider,
                    user_id=result.user_id)
            return ok(data=result, message="소셜 로그인 성공")
        else:  # SocialSignupRequired
            log.info("Social signup required",
                    provider=provider,
                    social_id=result.social_id)
            return ok(data=result, message="회원가입이 필요합니다")

    except ValidationError as e:
        log.warning("Social callback validation failed",
                   provider=provider,
                   error=str(e))
        raise
    except Exception as e:
        log.error("Social callback processing failed",
                 provider=provider,
                 error=str(e))
        raise BaseAppException(f"소셜 로그인 처리 실패: {str(e)}", status_code=500)


# 참고: 소셜 회원가입 완료는 기존 user_api.py의 엔드포인트 사용
# POST /api/v1/users/social/signup
# - social_provider, social_id, email, 기타 정보 전달
# - UserService.signup() 호출 (이미 social_provider 지원)
# - JWT 발급 및 자동 로그인
