"""
인증 관련 스키마
"""
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    user_id: str = Field(..., min_length=1, max_length=30, description="사용자 ID")
    password: str = Field(..., min_length=1, max_length=255, description="비밀번호")


class LoginResponse(BaseModel):
    """로그인 응답 데이터"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    nickname: str = Field(..., description="사용자 닉네임")
    access_token_expires_in: int = Field(..., description="액세스 토큰 만료시간(초)")
    refresh_token_expires_in: int = Field(..., description="리프레시 토큰 만료시간(초)")


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: Optional[str] = Field(None, description="갱신용 토큰 (쿠키에서 자동 추출)")


class TokenResponse(BaseModel):
    """토큰 응답 데이터"""
    access_token_expires_in: int = Field(..., description="액세스 토큰 만료시간(초)")
    refresh_token_expires_in: int = Field(..., description="리프레시 토큰 만료시간(초)")


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    role: str = Field(..., description="사용자 역할")
    exp: int = Field(..., description="만료 시간")
    iat: int = Field(..., description="발급 시간")
    jti: str = Field(..., description="JWT ID")
    token_type: str = Field(default="access", description="토큰 타입 (access/refresh)")


# ==================== 소셜 로그인 관련 스키마 ====================

class SocialAuthURLResponse(BaseModel):
    """소셜 로그인 URL 응답"""
    authorization_url: str = Field(..., description="OAuth 인증 페이지 URL")
    state: str = Field(..., description="CSRF 방지용 state 파라미터")


class SocialCallbackRequest(BaseModel):
    """소셜 로그인 콜백 요청"""
    code: str = Field(..., description="OAuth 인증 코드")
    state: Optional[str] = Field(None, description="CSRF 방지용 state 파라미터 (Naver 필수)")


class SocialUserInfo(BaseModel):
    """소셜 로그인 사용자 정보"""
    provider: str = Field(..., description="소셜 제공자 (kakao/naver)")
    social_id: str = Field(..., description="소셜 고유 ID")
    email: Optional[str] = Field(None, description="이메일")
    name: Optional[str] = Field(None, description="이름")
    profile_image: Optional[str] = Field(None, description="프로필 이미지 URL")


class SocialSignupRequired(BaseModel):
    """소셜 회원가입 필요 응답"""
    requires_signup: bool = Field(default=True, description="회원가입 필요 여부")
    provider: str = Field(..., description="소셜 제공자 (kakao/naver)")
    social_id: str = Field(..., description="소셜 고유 ID")
    email: Optional[str] = Field(None, description="이메일")
    name: Optional[str] = Field(None, description="이름 (선택)")
    profile_image: Optional[str] = Field(None, description="프로필 이미지 URL (선택)")