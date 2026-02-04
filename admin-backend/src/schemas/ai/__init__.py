"""
AI Assistant 스키마.

Stories: 1-2, 2-1
"""

from src.schemas.ai.auth_schema import AuthErrorResponse, AUTH_ERROR_CODES
from src.schemas.ai.query_schema import (
    AIQueryRequest,
    AIQueryResponse,
    AIQueryMetadata,
)
from src.schemas.ai.error_schema import AIErrorResponse, AIErrorCode
from src.schemas.ai.correction_schema import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionItem,
    CorrectionHistoryResponse,
)
from src.schemas.ai.feedback_schema import (
    AIFeedbackRequest,
    AIFeedbackResponse,
)

__all__ = [
    "AuthErrorResponse",
    "AUTH_ERROR_CODES",
    "AIQueryRequest",
    "AIQueryResponse",
    "AIQueryMetadata",
    "AIErrorResponse",
    "AIErrorCode",
    "CorrectionRequest",
    "CorrectionResponse",
    "CorrectionItem",
    "CorrectionHistoryResponse",
    "AIFeedbackRequest",
    "AIFeedbackResponse",
]
