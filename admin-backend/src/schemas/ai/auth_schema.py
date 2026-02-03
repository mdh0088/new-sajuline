"""
AI 어시스턴트 인증 관련 스키마

Stories: 1-2
FRs: FR-012
"""

from pydantic import BaseModel, Field


class AuthErrorResponse(BaseModel):
    """인증 에러 응답 스키마"""

    detail: str = Field(..., description="에러 메시지")
    code: str = Field(..., description="에러 코드")


# 에러 코드 정의
AUTH_ERROR_CODES = {
    "AUTH_REQUIRED": "인증이 필요합니다",
    "INVALID_TOKEN": "유효하지 않은 토큰입니다",
    "SESSION_EXPIRED": "세션이 만료되었습니다. 다시 로그인해주세요",
    "TOKEN_DECODE_ERROR": "토큰을 해석할 수 없습니다",
}
