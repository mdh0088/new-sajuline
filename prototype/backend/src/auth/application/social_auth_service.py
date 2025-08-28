"""
소셜 인증 애플리케이션 서비스

소셜 로그인 관련 유즈케이스 구현
"""
import random
from datetime import datetime, timedelta
from typing import Optional, List, TYPE_CHECKING

from ..domain.entities import (
    TokenType, TokenPair, UserInfo, AuthProvider,
    SocialUserInfo, SocialLoginResponse, SocialSignupRequest,
    KakaoOAuthConfig, NaverOAuthConfig
)
from ..domain.services import SocialAuthService
from ..domain.ports import AuthRepositoryPort
from .services import AuthApplicationService
from src.ars.domain.ports import ARSUserRepositoryPort
from ..infrastructure.repositories import (
    KakaoOAuthClient, NaverOAuthClient
)
from ...user.domain.ports import UserRepositoryPort
from ...common.services import TokenService
from ...common.config.settings import get_settings
from ...common.exceptions.custom import (
    ConflictException, AuthenticationException, ValidationException
)
from ...common.utils.sanitizer import Sanitizer

if TYPE_CHECKING:
    from ...user.domain.models import User


class SocialAuthApplicationService:
    """소셜 인증 애플리케이션 서비스"""
    
    def __init__(self, auth_repository: AuthRepositoryPort, user_repository: UserRepositoryPort, ars_repository: ARSUserRepositoryPort, auth_service: AuthApplicationService) -> None:
        self.auth_repository: AuthRepositoryPort = auth_repository
        self.user_repository: UserRepositoryPort = user_repository
        self.ars_repository: ARSUserRepositoryPort = ars_repository
        self.auth_service: AuthApplicationService = auth_service
        self.settings = get_settings()
        
        # TokenService 초기화
        self.token_service = TokenService(
            secret_key=self.settings.SECRET_KEY,
            algorithm="HS256",
            access_token_expire_minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    def _get_oauth_client(self, provider: str):
        """OAuth 클라이언트 팩토리"""
        # 디버깅: 설정값 확인
        print(f"[DEBUG] Provider: {provider}")
        print(f"[DEBUG] FRONTEND_URL: {self.settings.FRONTEND_URL}")
        print(f"[DEBUG] KAKAO_CLIENT_ID: {self.settings.KAKAO_CLIENT_ID}")
        print(f"[DEBUG] NAVER_CLIENT_ID: {self.settings.NAVER_CLIENT_ID}")
        print(f"[DEBUG] NAVER_CLIENT_SECRET: {self.settings.NAVER_CLIENT_SECRET}")
        
        if provider == AuthProvider.KAKAO:
            # 환경변수에서 카카오 설정 로드
            config = KakaoOAuthConfig(
                client_id=self.settings.KAKAO_CLIENT_ID,
                redirect_uri=f"{self.settings.FRONTEND_URL}/auth/social/kakao/callback",
                auth_url=self.settings.KAKAO_AUTH_URL,
                token_url=self.settings.KAKAO_TOKEN_URL,
                user_info_url=self.settings.KAKAO_USER_INFO_URL,
                logout_url=self.settings.KAKAO_LOGOUT_URL
            )
            print(f"[DEBUG] 카카오 OAuth Config - client_id: {config.client_id}, redirect_uri: {config.redirect_uri}")
            return KakaoOAuthClient(config)
        
        elif provider == AuthProvider.NAVER:
            # 환경변수에서 네이버 설정 로드
            config = NaverOAuthConfig(
                client_id=self.settings.NAVER_CLIENT_ID,
                client_secret=self.settings.NAVER_CLIENT_SECRET,
                redirect_uri=f"{self.settings.FRONTEND_URL}/auth/social/naver/callback",
                auth_url=self.settings.NAVER_AUTH_URL,
                token_url=self.settings.NAVER_TOKEN_URL,
                user_info_url=self.settings.NAVER_USER_INFO_URL
            )
            print(f"[DEBUG] 네이버 OAuth Config - client_id: {config.client_id}, redirect_uri: {config.redirect_uri}")
            return NaverOAuthClient(config)
        
        else:
            raise ValidationException(
                message=f"지원하지 않는 소셜 로그인 제공자입니다: {provider}",
                field="provider"
            )
    
    async def _generate_unique_placeholder_phone(self, seed: str) -> str:
        """
        MariaDB 제약을 만족하는 11자리 임시 전화번호 생성(010 + 8자리).
        기존 번호와 중복되지 않도록 최대 N회 재시도.
        """
        base = "010"

        def digits_from_seed(s: str) -> str:
            only_digits = ''.join(ch for ch in s if ch.isdigit())
            if len(only_digits) >= 8:
                return only_digits[-8:]
            rand_pad = f"{random.randint(0, 10**8 - 1):08d}"
            return (only_digits + rand_pad)[:8]

        suffix = digits_from_seed(seed)
        for _ in range(10):
            candidate = base + suffix
            exists = await self.user_repository.get_user_by_phone(candidate)
            if not exists:
                return candidate
            suffix = f"{random.randint(0, 10**8 - 1):08d}"
        raise ValidationException(message="임시 전화번호 생성 실패")
    
    async def _validate_social_user_uniqueness(self, user_id: str, email: str, phone: str, nickname: str) -> List[str]:
        """
        소셜 로그인 사용자 생성 전 종합 중복 검증
        Returns: 중복된 필드명 리스트
        """
        conflicts = []
        
        # 각 unique 필드별 중복 검사
        if await self.user_repository.get_user_by_id(user_id):
            conflicts.append("user_id")
        if await self.user_repository.get_user_by_email(email):
            conflicts.append("email") 
        if await self.user_repository.get_user_by_phone(phone):
            conflicts.append("phone")
        if await self.user_repository.get_user_by_nickname(nickname):
            conflicts.append("nickname")
            
        return conflicts
    
    async def _find_existing_social_user(self, provider: str, user_id: str, email: str) -> Optional['User']:
        """
        소셜 로그인 기존 사용자 조회 (다중 검색)
        """
        # 1차: user_id로 조회
        user = await self.user_repository.get_user_by_id(user_id)
        if user:
            print(f"[DEBUG] 기존 사용자 발견 (user_id): {user.user_id}")
            return user
        
        # 2차: email로 조회 (네이버 특화)
        if provider == AuthProvider.NAVER:
            user = await self.user_repository.get_user_by_email(email)
            if user and user.social_provider == AuthProvider.NAVER:
                print(f"[DEBUG] 기존 네이버 사용자 발견 (email): {user.user_id}")
                return user
        
        print(f"[DEBUG] 기존 사용자 없음: provider={provider}, user_id={user_id}, email={email}")
        return None
    
    async def _ensure_unique_nickname(self, nickname: str, max_len: int = 100) -> str:
        """
        닉네임 유니크 보장. 중복 시 -1, -2 ... 접미사로 보정.
        """
        # 닉네임 sanitization
        sanitized = Sanitizer.sanitize_html(nickname or "user")
        base = sanitized.strip()[:max_len]
        candidate = base or "user"
        idx = 1
        while await self.user_repository.get_user_by_nickname(candidate):
            suffix = f"-{idx}"
            candidate = (base[: max_len - len(suffix)] + suffix) if len(base) + len(suffix) > max_len else base + suffix
            idx += 1
            if idx > 100:
                raise ConflictException(message="닉네임이 모두 사용 중입니다.")
        return candidate
    
    async def _create_user_tokens(self, user_id: str, email: str) -> TokenPair:
        """사용자 토큰 생성 (공통 메서드)"""
        # Access Token 생성
        access_token = self.token_service.create_jwt_token(user_id, email, TokenType.ACCESS)
        
        # Refresh Token 생성
        refresh_token = self.token_service.create_jwt_token(user_id, email, TokenType.REFRESH)
        
        # Refresh Token 저장
        await self.auth_repository.store_refresh_token(
            user_id, refresh_token, 
            datetime.utcnow() + timedelta(days=self.token_service.refresh_token_expire_days)
        )
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.token_service.access_token_expire_minutes * 60
        )
    
    async def social_login_callback(
        self, 
        provider: str, 
        code: str, 
        state: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """소셜 로그인 OAuth 콜백 처리"""
        try:
            # OAuth 클라이언트 생성
            oauth_client = self._get_oauth_client(provider)
            
            # 1. Authorization code로 access token 획득
            if provider == AuthProvider.NAVER:
                token_data = await oauth_client.get_access_token(code, state)
            else:
                token_data = await oauth_client.get_access_token(code)
            
            access_token = token_data.get('access_token')
            if not access_token:
                raise AuthenticationException(
                    message="소셜 로그인 토큰 획득에 실패했습니다."
                )
            
            # 2. Access token으로 사용자 정보 조회
            social_user_info = await oauth_client.get_user_info(access_token)
            
            # 3. 카카오/네이버별 사용자 식별자 처리
            if provider == AuthProvider.KAKAO:
                # 카카오: 'kko' + 카카오 ID 패턴 (old-docs와 동일)
                user_id = f"kko{social_user_info.social_id}"
                user_email = social_user_info.email or f"kko{social_user_info.social_id}@kakao.local"  # 이메일이 없으면 임시 이메일
            elif provider == AuthProvider.NAVER:
                # 네이버: 이메일을 user_id로 사용 (old-docs와 동일)
                if not social_user_info.email:
                    raise ValidationException(
                        message="네이버 로그인에서 이메일 정보를 가져올 수 없습니다.",
                        field="email"
                    )
                user_id = social_user_info.email
                user_email = social_user_info.email
            else:
                raise ValidationException(
                    message=f"지원하지 않는 소셜 로그인 제공자입니다: {provider}",
                    field="provider"
                )
            
            # 4. 기존 회원 확인 (종합 검색)
            print(f"[DEBUG] 기존 사용자 조회 시도: provider={provider}, user_id={user_id}, email={user_email}")
            existing_user = await self._find_existing_social_user(provider, user_id, user_email)
            print(f"[DEBUG] existing_user 조회 결과: {existing_user}")
            
            if existing_user:
                # 기존 회원 → 로그인 처리
                tokens = await self._create_user_tokens(user_id, user_email)
                
                # 로그인 로그 기록
                # TODO: 로그인 로그 구현
                
                # 마지막 로그인 시간 업데이트  
                # TODO: update_last_login 메서드 구현 필요
                # await self.auth_repository.update_last_login(user_id)
                
                return SocialLoginResponse(
                    success=True,
                    message="소셜 로그인되었습니다.",
                    is_new_user=False,
                    tokens=tokens,
                    user=UserInfo(
                        id=user_id,
                        email=user_email,
                        name=existing_user.nickname,
                        is_active=existing_user.is_active,
                        email_verified=True,  # 소셜 로그인은 이메일 인증 완료로 간주
                        created_at=existing_user.created_at
                    )
                )
            else:
                # 신규 사용자 → 추가 정보 입력 필요
                print(f"[DEBUG] 신규 사용자 발견 - 추가 정보 입력 필요: provider={provider}, user_id={user_id}, email={user_email}")
                
                # 필요한 추가 정보 목록 (일반 회원가입과 동일한 정보 수집)
                missing_fields = []
                if not social_user_info.name and not social_user_info.nickname:
                    missing_fields.append('name')  # 닉네임
                missing_fields.append('phone')  # 전화번호 (항상 필요)
                missing_fields.append('gender')  # 성별 (항상 필요)
                missing_fields.extend(['agree_terms', 'agree_privacy', 'agree_marketing'])  # 약관 동의
                
                # 소셜 사용자 정보에 필요한 필드 추가
                enhanced_social_info = SocialUserInfo(
                    social_id=social_user_info.social_id,
                    email=user_email,
                    name=social_user_info.name,
                    nickname=social_user_info.nickname,
                    profile_image=social_user_info.profile_image,
                    provider=provider,
                    user_id=user_id  # 생성될 user_id 미리 포함
                )

                return SocialLoginResponse(
                    success=True,
                    message=f"{provider} 인증이 완료되었습니다. 회원가입을 위해 추가 정보를 입력해주세요.",
                    is_new_user=True,
                    requires_additional_info=True,
                    social_user_info=enhanced_social_info,
                    missing_fields=missing_fields
                )
                
        except Exception as e:
            # OAuth 클라이언트 정리
            if 'oauth_client' in locals():
                await oauth_client.close()
            
            if isinstance(e, (AuthenticationException, ValidationException, ConflictException)):
                raise e
            else:
                raise ValidationException(
                    message=f"소셜 로그인 처리 중 오류가 발생했습니다: {str(e)}"
                )
        finally:
            # OAuth 클라이언트 정리
            if 'oauth_client' in locals():
                await oauth_client.close()
    
    async def social_signup(
        self,
        social_signup_request: SocialSignupRequest,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """소셜 회원가입 처리 - signup 메서드로 일원화"""
        from ..domain.entities import SignupResponse
        try:
            # 1) 소셜별 user_id/email 구성
            if social_signup_request.provider == AuthProvider.KAKAO:
                user_id = f"kko{social_signup_request.social_id}"
                user_email = social_signup_request.email or f"kko{social_signup_request.social_id}@kakao.local"
            elif social_signup_request.provider == AuthProvider.NAVER:
                if not social_signup_request.email:
                    raise ValidationException(message="네이버 소셜 회원가입에서 이메일 정보가 필요합니다.", field="email")
                user_id = social_signup_request.email
                user_email = social_signup_request.email
            else:
                raise ValidationException(message=f"지원하지 않는 소셜 로그인 제공자입니다: {social_signup_request.provider}", field="provider")

            # 2) 공통 회원가입 DTO로 변환 후 AuthApplicationService.signup 재사용
            from ..domain.entities import SignupRequest
            signup_request = SignupRequest(
                user_id=user_id,
                email=user_email,
                password="SOCIAL_DUMMY_123!",  # Pydantic 최소 길이 통과용 더미 (is_social=True로 실제 저장은 비번 미사용)
                phone=social_signup_request.phone or "",
                name=social_signup_request.name,
                gender=social_signup_request.gender,
                agree_terms=social_signup_request.agree_terms,
                agree_privacy=social_signup_request.agree_privacy,
                agree_marketing=social_signup_request.agree_marketing,
            )

            # 주입된 AuthApplicationService 사용 (수동 생성 금지)
            return await self.auth_service.signup(
                signup_request,
                is_social=True,
                join_type_override=social_signup_request.provider.value.upper(),
                generate_tokens=True,
                email_verified_when_tokens=True,
            )
        except (AuthenticationException, ValidationException, ConflictException):
            raise
        except Exception as e:
            raise ValidationException(message=f"소셜 회원가입 처리 중 오류가 발생했습니다: {str(e)}")