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
    access_token: str = Field(..., description="새 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료 시간(초)")


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    role: str = Field(..., description="사용자 역할")
    exp: int = Field(..., description="만료 시간")
    iat: int = Field(..., description="발급 시간")
    jti: str = Field(..., description="JWT ID")
    token_type: str = Field(default="access", description="토큰 타입 (access/refresh)")