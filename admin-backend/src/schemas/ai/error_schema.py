"""
AI 에러 응답 스키마.

Stories: 2-1
FRs: FR-012 (입력 유효성 검사), FR-015 (에러 처리)
"""

from pydantic import BaseModel, Field
from typing import List


# AI 에러 코드 상수
class AIErrorCode:
    """AI BI 어시스턴트 에러 코드"""

    # 입력 유효성 검사 에러 (4xx)
    QUESTION_TOO_SHORT = "AIBI_QUESTION_TOO_SHORT"
    QUESTION_TOO_LONG = "AIBI_QUESTION_TOO_LONG"
    INVALID_INPUT = "AIBI_INVALID_INPUT"
    SQL_KEYWORD_DETECTED = "AIBI_SQL_KEYWORD_DETECTED"
    FORBIDDEN_PATTERN = "AIBI_FORBIDDEN_PATTERN"

    # 권한 에러 (4xx)
    UNAUTHORIZED = "AIBI_UNAUTHORIZED"
    FORBIDDEN = "AIBI_FORBIDDEN"
    RATE_LIMITED = "AIBI_RATE_LIMITED"

    # LLM 에러 (5xx)
    LLM_TIMEOUT = "AIBI_LLM_TIMEOUT"
    LLM_ERROR = "AIBI_LLM_ERROR"
    LLM_UNAVAILABLE = "AIBI_LLM_UNAVAILABLE"

    # 데이터베이스 에러 (5xx)
    DB_UNAVAILABLE = "AIBI_DB_UNAVAILABLE"
    DB_QUERY_ERROR = "AIBI_DB_QUERY_ERROR"
    DB_TIMEOUT = "AIBI_DB_TIMEOUT"

    # 시스템 에러 (5xx)
    INTERNAL_ERROR = "AIBI_INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "AIBI_SERVICE_UNAVAILABLE"


class AIErrorResponse(BaseModel):
    """AI 에러 응답 스키마"""

    success: bool = Field(default=False, description="항상 False")
    error_code: str = Field(description="에러 코드 (AIErrorCode)")
    message: str = Field(description="사용자에게 표시할 에러 메시지")
    suggestions: List[str] = Field(default_factory=list, description="해결 방법 제안")
    technical_details: str | None = Field(
        default=None, description="기술 상세 정보 (디버그 모드에서만)"
    )
