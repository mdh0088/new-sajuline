"""
인증 관련 스키마
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    user_id: str = Field(..., min_length=1, max_length=30, description="사용자 ID")
    password: str = Field(..., min_length=1, max_length=255, description="비밀번호")


class LoginData(BaseModel):
    """로그인 응답 데이터"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    nickname: str = Field(..., description="사용자 닉네임")


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    role: str = Field(..., description="사용자 역할")
    exp: int = Field(..., description="만료 시간")
    iat: int = Field(..., description="발급 시간")
    jti: str = Field(..., description="JWT ID")