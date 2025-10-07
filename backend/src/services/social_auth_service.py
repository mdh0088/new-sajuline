"""
소셜 로그인 인증 서비스 (Kakao, Naver OAuth 2.0)

기존 Login/Refresh API와 동일한 JWT 토큰 패턴 사용:
- AuthService.create_access_token() / create_refresh_token()
- HttpOnly 쿠키 설정 (secure=settings.is_production)
- Redis: OAuth state 검증 (CSRF 방지) - 기존 블랙리스트와 독립적
"""
from typing import Dict, Optional, Union
from datetime import datetime, timedelta, timezone

from fastapi import Response

from src.common.utils.oauth_clients import (
    KakaoOAuthClient,
    NaverOAuthClient,
    generate_oauth_state
)
from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from src.schemas.auth_schema import (
    LoginResponse,
    SocialAuthURLResponse,
    SocialUserInfo,
    SocialSignupRequired
)
from src.exceptions.custom_exceptions import ValidationError
from src.common.logging import get_logger_with_request_id
from src.config.settings import settings

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))


class SocialAuthService:
    """소셜 로그인 인증 서비스

    OAuth 2.0 Authorization Code Flow:
    1. get_authorization_url(): Frontend에서 호출, OAuth URL 생성
    2. handle_callback(): OAuth Provider가 redirect, 토큰 교환 및 사용자 조회
       - 기존 사용자: 자동 로그인 (JWT 발급, 기존 login API와 동일)
       - 신규 사용자: 회원가입 필요 응답
    3. 회원가입: 기존 user_api.py의 /users/social/signup 사용
    """

    def __init__(
        self,
        auth_service: AuthService,
        user_repository: UserRepository
    ):
        self.auth_service = auth_service
        self.user_repository = user_repository
        self.kakao_client = KakaoOAuthClient()
        self.naver_client = NaverOAuthClient()

    def _get_oauth_client(self, provider: str) -> Union[KakaoOAuthClient, NaverOAuthClient]:
        """Provider에 맞는 OAuth 클라이언트 반환

        Args:
            provider: 'kakao' or 'naver'

        Returns:
            KakaoOAuthClient or NaverOAuthClient

        Raises:
            ValidationError: 지원하지 않는 provider
        """
        if provider.lower() == "kakao":
            return self.kakao_client
        elif provider.lower() == "naver":
            return self.naver_client
        else:
            raise ValidationError(f"지원하지 않는 소셜 제공자입니다: {provider}")

    async def get_authorization_url(
        self,
        provider: str,
        redis_client
    ) -> SocialAuthURLResponse:
        """OAuth 인증 URL 생성

        Args:
            provider: 소셜 제공자 ('kakao' or 'naver')
            redis_client: Redis 클라이언트 (state 저장용)

        Returns:
            SocialAuthURLResponse: OAuth URL과 state

        Raises:
            ValidationError: 지원하지 않는 provider
        """
        log = get_logger_with_request_id()

        # OAuth 클라이언트 선택
        oauth_client = self._get_oauth_client(provider)

        # State 생성 (CSRF 방지)
        state = generate_oauth_state()

        # Redis에 state 저장 (10분 TTL)
        # 키 형식: oauth_state:{provider}:{state}
        # 기존 blacklist:{jti}와 완전히 분리된 네임스페이스
        await redis_client.setex(
            f"oauth_state:{provider}:{state}",
            600,  # 10분
            "1"
        )

        # OAuth URL 생성
        authorization_url = oauth_client.get_authorization_url(state)

        log.info("OAuth authorization URL generated",
                provider=provider,
                state=state)

        return SocialAuthURLResponse(
            authorization_url=authorization_url,
            state=state
        )

    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: Optional[str],
        redis_client,
        response: Response
    ) -> Union[LoginResponse, SocialSignupRequired]:
        """OAuth Callback 처리

        플로우:
        1. State 검증 (CSRF 방지) - Redis에서 확인 후 삭제
        2. 인증 코드로 액세스 토큰 교환
        3. 액세스 토큰으로 사용자 정보 조회
        4. 기존 사용자 확인
           - 존재: JWT 발급하여 자동 로그인 (기존 login API와 동일 패턴)
           - 없음: 회원가입 필요 응답

        Args:
            provider: 소셜 제공자 ('kakao' or 'naver')
            code: OAuth 인증 코드
            state: CSRF 방지용 state (Naver 필수)
            redis_client: Redis 클라이언트
            response: FastAPI Response (JWT 쿠키 설정용)

        Returns:
            LoginResponse (기존 사용자) or SocialSignupRequired (신규 사용자)

        Raises:
            ValidationError: State 불일치, 토큰 교환 실패
        """
        log = get_logger_with_request_id()

        # 1. State 검증 (Naver는 필수)
        if provider.lower() == "naver" and not state:
            raise ValidationError("Naver OAuth는 state 파라미터가 필수입니다")

        if state:
            state_key = f"oauth_state:{provider}:{state}"
            stored_state = await redis_client.get(state_key)
            if not stored_state:
                log.warning("Invalid OAuth state", provider=provider, state=state)
                raise ValidationError("유효하지 않은 OAuth state입니다")

            # State 사용 후 삭제 (일회용)
            await redis_client.delete(state_key)

        # 2. OAuth 클라이언트 선택
        oauth_client = self._get_oauth_client(provider)

        # 3. 인증 코드로 액세스 토큰 교환
        if provider.lower() == "kakao":
            token_data = await oauth_client.get_access_token(code)
        else:  # naver
            token_data = await oauth_client.get_access_token(code, state)

        access_token = token_data.get("access_token")
        if not access_token:
            raise ValidationError("액세스 토큰을 받지 못했습니다")

        # 4. 액세스 토큰으로 사용자 정보 조회
        user_info_raw = await oauth_client.get_user_info(access_token)

        # 5. Provider별 사용자 정보 파싱
        social_user_info = self._parse_user_info(provider, user_info_raw)

        log.info("Social user info retrieved",
                provider=provider,
                social_id=social_user_info.social_id,
                email=social_user_info.email)

        # 6. 기존 사용자 확인
        existing_user = await self._find_existing_social_user(
            provider=provider,
            social_id=social_user_info.social_id
        )

        # 디버깅: 조회 결과 로그
        if existing_user:
            log.info("FOUND existing social user",
                    provider=provider,
                    social_id=social_user_info.social_id,
                    stored_user_id=existing_user.user_id)
        else:
            log.info("NOT FOUND existing social user",
                    provider=provider,
                    social_id=social_user_info.social_id,
                    expected_user_id=f"kko{social_user_info.social_id}" if provider.lower() == "kakao" else social_user_info.social_id)

        if existing_user:
            # 기존 사용자: 자동 로그인 (기존 login API와 동일한 JWT 발급)
            log.info("Existing social user found, auto-login",
                    user_id=existing_user.user_id)

            # JWT 토큰 생성 (기존 AuthService 사용)
            access_token_jwt = self.auth_service.create_access_token(
                user_id=existing_user.user_id,
                email=existing_user.email,
                role="user"
            )
            refresh_token_jwt = self.auth_service.create_refresh_token(
                user_id=existing_user.user_id,
                email=existing_user.email,
                role="user"
            )

            # HttpOnly 쿠키 설정 (auth_api.py 패턴 따름)
            # secure는 프로덕션에서만 True (개발환경 호환성)
            secure_cookie = settings.is_production

            # Access Token (30분)
            response.set_cookie(
                key="access_token",
                value=access_token_jwt,
                httponly=True,
                secure=secure_cookie,
                samesite="lax",
                max_age=settings.access_token_expire_minutes * 60
            )

            # Refresh Token (7일)
            response.set_cookie(
                key="refresh_token",
                value=refresh_token_jwt,
                httponly=True,
                secure=secure_cookie,
                samesite="lax",
                max_age=settings.refresh_token_expire_days * 24 * 60 * 60
            )

            return LoginResponse(
                user_id=existing_user.user_id,
                email=existing_user.email,
                nickname=existing_user.nickname,
                access_token_expires_in=settings.access_token_expire_minutes * 60,
                refresh_token_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60
            )

        else:
            # 신규 사용자: 회원가입 필요
            log.info("New social user, signup required",
                    provider=provider,
                    social_id=social_user_info.social_id)

            return SocialSignupRequired(
                requires_signup=True,
                provider=social_user_info.provider,
                social_id=social_user_info.social_id,
                email=social_user_info.email,
                name=social_user_info.name,
                profile_image=social_user_info.profile_image
            )

    def _parse_user_info(self, provider: str, raw_data: Dict) -> SocialUserInfo:
        """Provider별 사용자 정보 파싱

        Args:
            provider: 'kakao' or 'naver'
            raw_data: OAuth API 응답 데이터

        Returns:
            SocialUserInfo: 통일된 사용자 정보 형식
        """
        if provider.lower() == "kakao":
            # Kakao 응답 형식
            kakao_id = str(raw_data.get("id"))
            kakao_account = raw_data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})

            return SocialUserInfo(
                provider="kakao",
                social_id=kakao_id,
                email=kakao_account.get("email"),
                name=profile.get("nickname"),
                profile_image=profile.get("profile_image_url")
            )

        elif provider.lower() == "naver":
            # Naver 응답 형식
            response_data = raw_data.get("response", {})

            return SocialUserInfo(
                provider="naver",
                social_id=response_data.get("email"),  # Naver는 email을 social_id로 사용
                email=response_data.get("email"),
                name=response_data.get("name"),
                profile_image=response_data.get("profile_image")
            )

        else:
            raise ValidationError(f"지원하지 않는 소셜 제공자입니다: {provider}")

    async def _find_existing_social_user(
        self,
        provider: str,
        social_id: str
    ) -> Optional[any]:
        """소셜 계정으로 기존 사용자 조회

        Args:
            provider: 소셜 제공자 ('kakao' or 'naver')
            social_id: 소셜 고유 ID

        Returns:
            User 모델 or None
        """
        log = get_logger_with_request_id()

        try:
            # Provider별 user_id 형식 생성 (프로토타입 패턴 유지)
            if provider.lower() == "kakao":
                user_id = f"kko{social_id}"
            elif provider.lower() == "naver":
                user_id = social_id  # Naver는 email 그대로 사용
            else:
                return None

            # user_id로 사용자 조회
            existing_user = await self.user_repository.get_by_id(user_id)

            if existing_user:
                log.info("Existing social user found",
                        provider=provider,
                        user_id=user_id)
            else:
                log.info("No existing social user",
                        provider=provider,
                        user_id=user_id)

            return existing_user

        except Exception as e:
            log.error("Error finding existing social user",
                     provider=provider,
                     social_id=social_id,
                     expected_user_id=user_id,
                     error_type=type(e).__name__,
                     error=str(e),
                     exc_info=True)
            return None


# 의존성 함수
def get_social_auth_service(
    auth_service: AuthService,
    user_repository: UserRepository
) -> SocialAuthService:
    """SocialAuthService 의존성"""
    return SocialAuthService(auth_service, user_repository)
