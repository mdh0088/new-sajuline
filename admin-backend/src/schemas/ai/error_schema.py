"""
AI 에러 응답 스키마.

Stories: 2-1, 4-2
FRs: FR-012 (입력 유효성 검사), FR-015 (에러 처리), FR20, FR21
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


# AI 에러 코드 상수
class AIErrorCode:
    """AI BI 어시스턴트 에러 코드"""

    # 입력 유효성 검사 에러 (4xx)
    QUESTION_TOO_SHORT = "AIBI_QUESTION_TOO_SHORT"
    QUESTION_TOO_LONG = "AIBI_QUESTION_TOO_LONG"
    INVALID_INPUT = "AIBI_INVALID_INPUT"
    INVALID_QUERY = "AIBI_INVALID_QUERY"  # Story 3-1: SQL 생성 실패
    SQL_KEYWORD_DETECTED = "AIBI_SQL_KEYWORD_DETECTED"
    FORBIDDEN_PATTERN = "AIBI_FORBIDDEN_PATTERN"

    # 권한 에러 (4xx)
    UNAUTHORIZED = "AIBI_UNAUTHORIZED"
    FORBIDDEN = "AIBI_FORBIDDEN"
    RATE_LIMITED = "AIBI_RATE_LIMITED"

    # Story 3-1: 보안 에러 (4xx)
    SECURITY_VIOLATION = "AIBI_SECURITY_VIOLATION"  # Layer 2 SQL 보안 위반

    # LLM 에러 (5xx)
    LLM_TIMEOUT = "AIBI_LLM_TIMEOUT"
    LLM_ERROR = "AIBI_LLM_ERROR"
    LLM_UNAVAILABLE = "AIBI_LLM_UNAVAILABLE"

    # 데이터베이스 에러 (5xx)
    DB_UNAVAILABLE = "AIBI_DB_UNAVAILABLE"
    DB_QUERY_ERROR = "AIBI_DB_QUERY_ERROR"
    DB_TIMEOUT = "AIBI_DB_TIMEOUT"
    DATABASE_ERROR = "AIBI_DATABASE_ERROR"  # 일반 데이터베이스 에러
    QUERY_EXECUTION_ERROR = "AIBI_QUERY_EXECUTION_ERROR"  # 쿼리 실행 실패

    # 시스템 에러 (5xx)
    INTERNAL_ERROR = "AIBI_INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "AIBI_SERVICE_UNAVAILABLE"


class AIErrorResponse(BaseModel):
    """AI 에러 응답 스키마 (Story 4-2: 사용자 친화적 에러)"""

    success: bool = Field(default=False, description="항상 False")
    error_code: str = Field(description="에러 코드 (AIErrorCode)")
    message: str = Field(description="사용자에게 표시할 에러 메시지")
    suggestions: List[str] = Field(default_factory=list, description="해결 방법 제안 (Story 4-2)")
    error_guide: Dict[str, Any] | None = Field(
        default=None, description="에러 유형별 안내 정보 (Story 4-2: AC5)"
    )
    technical_details: str | None = Field(
        default=None, description="기술 상세 정보 (디버그 모드에서만)"
    )
