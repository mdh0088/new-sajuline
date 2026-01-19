"""
Auth 도메인 엔티티 정의
인증, 인가, 토큰 관리 관련 엔티티
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenType(str, Enum):
    """토큰 타입"""
    ACCESS = "access"
    REFRESH = "refresh"


class AuthProvider(str, Enum):
    """인증 제공자"""
    LOCAL = "local"
    KAKAO = "kakao"
    NAVER = "naver"
    GOOGLE = "google"


class LoginRequest(BaseModel):
    """로그인 요청"""
    user_id: str = Field(..., min_length=4, max_length=20, description="사용자 ID")
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class SignupRequest(BaseModel):
    """회원가입 요청"""
    user_id: str = Field(..., min_length=4, max_length=20, description="사용자 ID")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., pattern=r'^01[0-9]{8,9}$', description="전화번호 (필수)")
    gender: Optional[str] = Field(None, pattern=r'^[MF]$', description="성별 (M/F)")
    agree_terms: bool = True
    agree_privacy: bool = True
    agree_marketing: bool = False


class TokenPair(BaseModel):
    """토큰 쌍"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """사용자 정보 (인증용)"""
    id: str
    email: str
    name: str
    is_active: bool
    email_verified: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """로그인 응답"""
    success: bool = True
    message: str = "로그인되었습니다."
    tokens: TokenPair
    user: UserInfo


class SignupResponse(BaseModel):
    """회원가입 응답"""
    success: bool = True
    message: str = "회원가입이 완료되었습니다."
    user: UserInfo
    tokens: Optional[TokenPair] = None  # 소셜 회원가입의 경우 토큰 포함


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """토큰 갱신 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """비밀번호 재설정 확인 요청"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class EmailVerificationRequest(BaseModel):
    """이메일 인증 요청"""
    token: str


class EmailCheckRequest(BaseModel):
    """이메일 중복 확인 요청"""
    email: EmailStr


class EmailCheckResponse(BaseModel):
    """이메일 중복 확인 응답"""
    email: str
    available: bool
    message: str


class PhoneCheckRequest(BaseModel):
    """전화번호 중복 확인 요청"""
    phone: str = Field(..., pattern=r'^01[0-9]{8,9}$', description="전화번호")


class PhoneCheckResponse(BaseModel):
    """전화번호 중복 확인 응답"""
    phone: str
    available: bool
    message: str


class NicknameCheckRequest(BaseModel):
    """닉네임 중복 확인 요청"""
    nickname: str = Field(..., min_length=2, max_length=50, description="닉네임")


class NicknameCheckResponse(BaseModel):
    """닉네임 중복 확인 응답"""
    nickname: str
    available: bool
    message: str


class SocialLoginRequest(BaseModel):
    """소셜 로그인 요청"""
    provider: AuthProvider
    access_token: str
    code: Optional[str] = None


class SocialCallbackRequest(BaseModel):
    """소셜 로그인 OAuth 콜백 요청"""
    provider: AuthProvider
    code: str
    state: Optional[str] = None  # 네이버용


class SocialUserInfo(BaseModel):
    """소셜 로그인 사용자 정보"""
    provider: AuthProvider
    social_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    user_id: Optional[str] = None  # 생성될 user_id (신규 사용자의 경우)
    raw_data: dict = {}  # 원본 소셜 플랫폼 데이터


class SocialSignupRequest(BaseModel):
    """소셜 회원가입 요청"""
    provider: AuthProvider
    social_id: str
    email: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=50)
    nickname: Optional[str] = Field(None, min_length=2, max_length=30)
    phone: str = Field(..., pattern=r'^01[0-9]{8,9}$', description="전화번호 (필수)")
    gender: Optional[str] = Field(None, pattern=r'^[MF]$', description="성별 (M/F)")
    agree_terms: bool = True
    agree_privacy: bool = True
    agree_marketing: bool = False



class SocialLoginResponse(BaseModel):
    """소셜 로그인 응답"""
    success: bool = True
    message: str = "로그인되었습니다."
    is_new_user: bool = False  # 신규 사용자 여부
    requires_additional_info: bool = False  # 추가 정보 입력 필요 여부
    tokens: Optional[TokenPair] = None  # 기존 사용자의 경우 토큰 포함
    user: Optional[UserInfo] = None  # 기존 사용자의 경우 사용자 정보 포함
    social_user_info: Optional[SocialUserInfo] = None  # 신규 사용자의 경우 소셜 정보 포함
    missing_fields: Optional[list[str]] = None  # 신규 사용자의 경우 부족한 필드 목록


class KakaoOAuthConfig(BaseModel):
    """카카오 OAuth 설정"""
    client_id: str
    redirect_uri: str
    auth_url: str
    token_url: str
    user_info_url: str
    logout_url: str


class NaverOAuthConfig(BaseModel):
    """네이버 OAuth 설정"""
    client_id: str
    client_secret: str
    redirect_uri: str
    auth_url: str
    token_url: str
    user_info_url: str


class LogoutRequest(BaseModel):
    """로그아웃 요청"""
    access_token: str
    refresh_token: Optional[str] = None


class LogoutResponse(BaseModel):
    """로그아웃 응답"""
    success: bool = True
    message: str = "로그아웃되었습니다."


class AuthenticatedUser(BaseModel):
    """인증된 사용자 정보"""
    user_id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    roles: list[str] = []
    permissions: list[str] = []


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str  # user_id
    email: str
    exp: datetime
    iat: datetime
    type: TokenType
    jti: Optional[str] = None  # JWT ID


class AuthSession(BaseModel):
    """인증 세션"""
    session_id: str
    user_id: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    last_accessed_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True 