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

__all__ = [
    "AuthErrorResponse",
    "AUTH_ERROR_CODES",
    "AIQueryRequest",
    "AIQueryResponse",
    "AIQueryMetadata",
    "AIErrorResponse",
    "AIErrorCode",
]
