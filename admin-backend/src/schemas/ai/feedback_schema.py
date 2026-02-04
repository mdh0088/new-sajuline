"""
AI 피드백 스키마.

Stories: 5-1
FRs: FR-024, FR-026
"""

from typing import Optional

from pydantic import BaseModel, Field


class AIFeedbackRequest(BaseModel):
    """피드백 제출 요청 스키마"""

    query_id: str = Field(
        ...,
        description="질의 응답 ID (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    rating: int = Field(..., ge=1, le=5, description="1-5점 별점 평가")
    comment: Optional[str] = Field(
        None, max_length=1000, description="선택적 텍스트 피드백"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query_id": "550e8400-e29b-41d4-a716-446655440000",
                    "rating": 4,
                    "comment": "결과는 정확했지만 응답이 조금 느렸어요",
                },
                {
                    "query_id": "550e8400-e29b-41d4-a716-446655440001",
                    "rating": 5,
                },
            ]
        }
    }


class AIFeedbackResponse(BaseModel):
    """피드백 제출 응답 스키마"""

    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"success": True, "message": "피드백이 제출되었습니다. 감사합니다!"}
            ]
        }
    }
