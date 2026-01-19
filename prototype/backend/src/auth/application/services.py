"""
Auth 애플리케이션 서비스
인증과 관련된 유즈케이스 구현
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import random


from ..domain.entities import (
    LoginRequest, LoginResponse, SignupRequest, SignupResponse,
    RefreshTokenRequest, RefreshTokenResponse, TokenType, TokenPair, TokenPayload,
    UserInfo, AuthenticatedUser, LogoutRequest, LogoutResponse,
    EmailCheckRequest, EmailCheckResponse, PhoneCheckRequest, PhoneCheckResponse,
    NicknameCheckRequest, NicknameCheckResponse,
    SocialUserInfo, SocialLoginResponse, SocialSignupRequest,
    AuthProvider, KakaoOAuthConfig, NaverOAuthConfig
)
from ..domain.services import (
    PasswordService, AuthValidationService, AuthSessionService
)
from ...common.services import TokenService
from ..domain.ports import AuthRepositoryPort
from ..infrastructure.token_blacklist import token_blacklist_service
from ...user.domain.ports import UserRepositoryPort
from src.counselor.domain.ports import CounselorRepositoryPort
from src.ars.domain.ports import ARSUserRepositoryPort
from ...common.config.settings import get_settings
from ...common.exceptions.custom import (
    ConflictException, AuthenticationException, AccountLockedException,
    AccountInactiveException, ValidationException, NotFoundException
)
from ...common.utils.sanitizer import Sanitizer
import re
from ...common.logging.events import log_event

class AuthApplicationService:
    """인증 애플리케이션 서비스"""
    
    def __init__(
        self,
        auth_repository: AuthRepositoryPort,
        user_repository: UserRepositoryPort,
        ars_repository: ARSUserRepositoryPort,
        counselor_repository: CounselorRepositoryPort,
    ) -> None:
        self.auth_repository: AuthRepositoryPort = auth_repository
        self.user_repository: UserRepositoryPort = user_repository
        self.ars_repository: ARSUserRepositoryPort = ars_repository
        self.counselor_repository: CounselorRepositoryPort = counselor_repository
        self.password_service: PasswordService = PasswordService()
        self.settings = get_settings()
        
        # TokenService 초기화
        self.token_service = TokenService(
            secret_key=self.settings.SECRET_KEY,
            algorithm="HS256",
            access_token_expire_minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    async def _verify_jwt_token(self, token: str, expected_type: Optional[TokenType] = None) -> TokenPayload:
        """JWT 토큰 검증 (블랙리스트 확인 포함)"""
        # TokenService를 통한 기본 검증
        token_payload = self.token_service.verify_jwt_token(token, expected_type)
        
        # 블랙리스트 확인
        if await token_blacklist_service.is_token_blacklisted(token_payload.jti):
            raise AuthenticationException(message="로그아웃된 토큰입니다.")
        
        return token_payload

    async def signup(
        self,
        signup_request: SignupRequest,
        *,
        is_social: bool = False,
        join_type_override: Optional[str] = None,
        generate_tokens: bool = False,
        email_verified_when_tokens: bool = False,
    ) -> SignupResponse:
        """회원가입"""
        # 비밀번호 강도 검증 (소셜 가입은 비밀번호 검증/저장 제외)
        if not is_social:
            is_valid, errors = PasswordService.validate_password_strength(signup_request.password)
            if not is_valid:
                raise ValidationException(
                    message=f"비밀번호가 요구사항을 충족하지 않습니다: {', '.join(errors)}",
                    field="password"
                )
        
        # 필수 약관 동의 확인
        if not AuthValidationService.validate_terms_agreement(
            signup_request.agree_terms, signup_request.agree_privacy
        ):
            raise ValidationException(
                message="필수 약관에 동의해주세요.",
                field="terms"
            )
        
        # 사용자 ID 중복 확인
        if await self.user_repository.get_user_by_id(signup_request.user_id):
            raise ConflictException(
                message="이미 사용 중인 사용자 ID입니다.",
                details={"field": "user_id"}
            )
        
        # 이메일 중복 확인 (t_user.email + t_counselor.counselor_id 교차 검사)
        if await self.user_repository.get_user_by_email(signup_request.email):
            raise ConflictException(
                message="이미 사용 중인 이메일입니다.",
                details={"field": "email"}
            )
        # 상담사 ID가 이메일과 같은 경우도 중복으로 간주
        if await self.counselor_repository.get_counselor_by_id(signup_request.email):
            raise ConflictException(
                message="이미 사용 중인 이메일입니다.",
                details={"field": "email"}
            )
        
        # 전화번호 검증 (필수)
        if not AuthValidationService.validate_phone_format(signup_request.phone):
            raise ValidationException(
                message="올바른 전화번호 형식이 아닙니다.",
                field="phone"
            )
        
        # 전화번호 중복 확인 (필수)
        if await self.user_repository.get_user_by_phone(signup_request.phone):
            raise ConflictException(
                message="이미 사용 중인 전화번호입니다.",
                details={"field": "phone"}
            )
        
        # 닉네임 XSS 방어를 위한 sanitization
        sanitized_nickname = Sanitizer.sanitize_html(signup_request.name)
        
        # 닉네임 중복 확인 (t_user.nickname + t_counselor.nickname 교차 검사)
        if await self.user_repository.get_user_by_nickname(sanitized_nickname):
            raise ConflictException(
                message="이미 사용 중인 닉네임입니다.",
                details={"field": "nickname"}
            )
        if await self.counselor_repository.get_counselor_by_nickname(sanitized_nickname):
            raise ConflictException(
                message="이미 사용 중인 닉네임입니다.",
                details={"field": "nickname"}
            )
        
        # 비밀번호 해시 (소셜은 빈 해시 유지)
        password_hash = "" if is_social else self.password_service.hash_password(signup_request.password)

        # DB에 동시 저장 (MariaDB -> MSSQL 순, 실패 시 보상/롤백)
        try:
            # 1) MariaDB: flush만 수행 (커밋 지연)
            created_user = await self.user_repository.create_user_deferred_commit(
                user_id=signup_request.user_id,
                email=signup_request.email,
                password_hash=password_hash,
                phone=signup_request.phone,
                nickname=sanitized_nickname,
                join_type=(join_type_override or "COMMON"),
                gender=signup_request.gender,
                agree_marketing=signup_request.agree_marketing,
            )

            # 2) MSSQL INSERT (리포지토리로 위임)
            try:
                await self.ars_repository.create_tm60_user(
                    u_id=created_user.user_id,
                    u_tel=created_user.phone or "",
                    u_kname=created_user.nickname or created_user.user_id,
                    u_passwd="",
                )
            except Exception:
                # MSSQL 실패 시 MariaDB 롤백
                await self.user_repository.rollback()
                raise

            # 3) 두 DB 모두 성공한 경우에만 MariaDB 커밋
            await self.user_repository.commit()
        except ConflictException:
            raise
        
        # 응답 생성
        user_info = UserInfo(
            id=created_user.user_id,
            email=created_user.email,
            name=created_user.nickname,
            is_active=created_user.is_active,
            email_verified=(email_verified_when_tokens if generate_tokens else False),
            created_at=created_user.created_at
        )
        
        if generate_tokens:
            tokens = await self._create_user_tokens(created_user.user_id, created_user.email)
            return SignupResponse(user=user_info, tokens=tokens)
        
        return SignupResponse(user=user_info)


    async def login(self, login_request: LoginRequest, 
                   client_ip: Optional[str] = None,
                   user_agent: Optional[str] = None) -> LoginResponse:
        """로그인"""
        # 사용자 조회
        user = await self.user_repository.get_user_by_user_id(login_request.user_id)
        if not user:
            # 로그인 실패 이벤트 (사용자 미존재)
            log_event(
                "auth.login.fail",
                domain="app.auth",
                level="ERROR",
                user_id=login_request.user_id,
                error_code="USER_NOT_FOUND",
                reason="invalid_credentials",
                client_ip=client_ip,
            )
            raise AuthenticationException(message="사용자 ID 또는 비밀번호가 올바르지 않습니다.")
        
        # 계정 잠금 확인
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = (user.locked_until - datetime.utcnow()).seconds // 60
            raise AccountLockedException(
                message=f"로그인 시도 횟수 초과로 계정이 잠겼습니다. {remaining_time}분 후에 다시 시도해주세요.",
                locked_until=str(user.locked_until)
            )
        
        # 비밀번호 검증 (소셜 로그인 사용자는 password_hash가 빈 문자열)
        if user.password_hash and not self.password_service.verify_password(login_request.password, user.password_hash):
            # 로그인 실패 횟수 증가
            user.failed_login_count = (user.failed_login_count or 0) + 1
            
            # 5회 실패 시 계정 잠금 (10분간)
            if user.failed_login_count >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=10)
                await self.user_repository.update_user(user)
                raise AccountLockedException(
                    message="로그인 시도 횟수 초과로 계정이 잠겼습니다. 10분 후에 다시 시도해주세요.",
                    locked_until=str(user.locked_until)
                )
            
            await self.user_repository.update_user(user)
            log_event(
                "auth.login.fail",
                domain="app.auth",
                level="ERROR",
                user_id=user.user_id,
                error_code="INVALID_PASSWORD",
                reason="invalid_credentials",
                attempts=user.failed_login_count,
                client_ip=client_ip,
            )
            raise AuthenticationException(
                message=f"사용자 ID 또는 비밀번호가 올바르지 않습니다. (시도: {user.failed_login_count}/5)"
            )
        
        # 로그인 성공 - 실패 횟수 초기화
        if user.failed_login_count > 0 or user.locked_until:
            user.failed_login_count = 0
            user.locked_until = None
            await self.user_repository.update_user(user)
        
        # 계정 상태 확인
        if not user.is_active:
            log_event(
                "auth.login.fail",
                domain="app.auth",
                level="ERROR",
                user_id=user.user_id,
                error_code="ACCOUNT_INACTIVE",
                reason="account_inactive",
                client_ip=client_ip,
            )
            raise AccountInactiveException(
                message="비활성화된 계정입니다."
            )
        
        # 토큰 생성
        access_token = self.token_service.create_jwt_token(user.user_id, user.email, TokenType.ACCESS)
        refresh_token = self.token_service.create_jwt_token(user.user_id, user.email, TokenType.REFRESH)
        
        # 세션 정보 생성 및 저장
        device_info = AuthSessionService.extract_device_info(user_agent)
        session_info = AuthSessionService.create_session_info(
            user.user_id, device_info, client_ip, user_agent
        )
        await self.auth_repository.create_session(session_info)
        
        # 응답 생성
        tokens = TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_service.access_token_expire_minutes * 60
        )
        
        user_info = UserInfo(
            id=user.user_id,
            email=user.email,
            name=user.nickname,
            is_active=user.is_active,
            email_verified=True,  # 간단히 true로 설정
            created_at=user.created_at
        )
        
        # 로그인 성공 이벤트
        log_event(
            "auth.login.success",
            domain="app.auth",
            level="INFO",
            user_id=user.user_id,
            session_id=session_info.get("session_id"),
            channel="password",
            client_ip=client_ip,
        )
        return LoginResponse(tokens=tokens, user=user_info)

    async def refresh_token(self, refresh_request: RefreshTokenRequest) -> RefreshTokenResponse:
        """토큰 갱신"""
        # 리프레시 토큰 검증
        token_payload = await self._verify_jwt_token(refresh_request.refresh_token, TokenType.REFRESH)
        
        # 사용자 존재 확인
        user = await self.user_repository.get_user_by_id(token_payload.sub)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다.",
                resource="user"
            )
        
        # 계정 상태 확인
        if not user.is_active:
            raise AccountInactiveException(
                message="비활성화된 계정입니다."
            )
        
        # 새로운 액세스 토큰 생성
        new_access_token = self.token_service.create_jwt_token(user.user_id, user.email, TokenType.ACCESS)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=self.token_service.access_token_expire_minutes * 60
        )

    async def check_email_availability(self, email: str) -> EmailCheckResponse:
        """이메일 중복 확인"""
        # 이메일 형식 검증
        if not AuthValidationService.validate_email_format(email):
            raise ValidationException(
                message="올바른 이메일 형식이 아닙니다.",
                field="email"
            )
        
        # 중복 확인 (t_user.email + t_counselor.counselor_id 교차 검사)
        user = await self.user_repository.get_user_by_email(email)
        counselor = await self.counselor_repository.get_counselor_by_id(email)
        available = (user is None) and (counselor is None)
        
        return EmailCheckResponse(
            email=email,
            available=available,
            message="사용 가능한 이메일입니다." if available else "이미 사용 중인 이메일입니다."
        )

    async def check_phone_availability(self, phone: str) -> PhoneCheckResponse:
        """전화번호 중복 확인"""
        # 전화번호 형식 검증
        if not AuthValidationService.validate_phone_format(phone):
            raise ValidationException(
                message="올바른 전화번호 형식이 아닙니다.",
                field="phone"
            )
        
        # 중복 확인
        user = await self.user_repository.get_user_by_phone(phone)
        available = user is None
        
        return PhoneCheckResponse(
            phone=phone,
            available=available,
            message="사용 가능한 전화번호입니다." if available else "이미 사용 중인 전화번호입니다."
        )

    async def check_nickname_availability(self, nickname: str) -> NicknameCheckResponse:
        """닉네임 중복 확인"""
        # 닉네임 sanitization
        sanitized_nickname = Sanitizer.sanitize_html(nickname)
        
        # 닉네임 길이 검증
        if len(sanitized_nickname) < 2 or len(sanitized_nickname) > 50:
            raise ValidationException(
                message="닉네임은 2자 이상 50자 이하여야 합니다.",
                field="nickname"
            )
        
        # 중복 확인 (t_user.nickname + t_counselor.nickname 교차 검사)
        user = await self.user_repository.get_user_by_nickname(sanitized_nickname)
        counselor = await self.counselor_repository.get_counselor_by_nickname(sanitized_nickname)
        available = (user is None) and (counselor is None)
        
        return NicknameCheckResponse(
            nickname=sanitized_nickname,
            available=available,
            message="사용 가능한 닉네임입니다." if available else "이미 사용 중인 닉네임입니다."
        )

    

    async def logout(self, access_token: str, refresh_token: Optional[str] = None) -> LogoutResponse:
        """로그아웃"""
        # 토큰 검증
        token_payload = await self._verify_jwt_token(access_token, TokenType.ACCESS)
        
        # 세션 비활성화
        await self.auth_repository.deactivate_user_sessions(token_payload.sub)
        
        # JWT 블랙리스트에 추가
        await token_blacklist_service.blacklist_token(token_payload.jti, token_payload.exp)
        
        # 리프레시 토큰도 블랙리스트에 추가
        if refresh_token:
            try:
                refresh_payload = await self._verify_jwt_token(refresh_token, TokenType.REFRESH)
                await token_blacklist_service.blacklist_token(refresh_payload.jti, refresh_payload.exp)
            except AuthenticationException:
                # 리프레시 토큰이 유효하지 않아도 로그아웃은 성공
                pass
        
        return LogoutResponse()

    async def get_current_user(self, access_token: str) -> AuthenticatedUser:
        """현재 사용자 정보 조회"""
        # 토큰 검증
        token_payload = await self._verify_jwt_token(access_token, TokenType.ACCESS)
        
        # 사용자 조회
        user = await self.user_repository.get_user_by_id(token_payload.sub)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다.",
                resource="user"
            )
        
        # 계정 상태 확인
        if not user.is_active:
            raise AccountInactiveException(
                message="비활성화된 계정입니다."
            )
        
        return AuthenticatedUser(
            user_id=user.user_id,
            email=user.email,
            name=user.nickname,
            is_active=user.is_active,
            is_verified=False,  # TODO: 이메일 인증 구현
            roles=[],  # TODO: 역할 시스템 구현
            permissions=[]  # TODO: 권한 시스템 구현
        )

    async def validate_token(self, token: str) -> Optional[str]:
        """토큰 검증 및 사용자 ID 반환 (간편 버전)"""
        try:
            token_payload = await self._verify_jwt_token(token)
            return token_payload.sub
        except (AuthenticationException, ValidationException, ConflictException, NotFoundException, AccountLockedException, AccountInactiveException):
            return None




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