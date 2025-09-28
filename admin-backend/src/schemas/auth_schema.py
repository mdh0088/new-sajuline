"""
인증 관련 스키마 (관리자 백엔드)
"""
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    user_id: str = Field(..., min_length=1, max_length=100, description="로그인 ID")
    password: str = Field(..., min_length=1, max_length=255, description="비밀번호")


class LoginResponse(BaseModel):
    """로그인 응답 데이터"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일")
    nickname: str = Field(..., description="표시명")
    access_token_expires_in: int = Field(..., description="액세스 토큰 만료시간(초)")
    refresh_token_expires_in: int = Field(..., description="리프레시 토큰 만료시간(초)")


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str = Field(..., description="주체 ID")
    email: str = Field(..., description="이메일")
    role: str = Field(..., description="역할 (admin|counselor)")
    exp: int = Field(..., description="만료 시간(Unix)")
    iat: int = Field(..., description="발급 시간(Unix)")
    jti: str = Field(..., description="JWT ID")
    token_type: str = Field(default="access", description="토큰 타입 (access|refresh)")


