"""
답변 수정 관련 스키마.

Stories: 5-2
FRs: FR25
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CorrectionRequest(BaseModel):
    """답변 수정 요청.

    AC2: 수정 모드에서 자연어 답변을 편집할 수 있다
    """

    corrected_answer: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="수정된 자연어 답변"
    )
    correction_reason: Optional[str] = Field(
        None,
        max_length=500,
        description="수정 사유"
    )


class CorrectionResponse(BaseModel):
    """수정 제출 응답.

    AC3: 수정된 답변이 원본과 함께 저장된다
    """

    success: bool = Field(..., description="성공 여부")
    correction_id: int = Field(..., description="수정 ID")
    message: str = Field(..., description="응답 메시지")


class CorrectionItem(BaseModel):
    """수정 이력 항목.

    AC4: 수정 이력이 관리된다
    """

    id: int = Field(..., description="수정 ID")
    admin_id: str = Field(..., description="수정 제출자 ID")
    original_answer: str = Field(..., description="원본 AI 응답")
    corrected_answer: str = Field(..., description="수정된 응답")
    correction_reason: Optional[str] = Field(None, description="수정 사유")
    is_training_data: bool = Field(..., description="학습 데이터 포함 여부")
    created_at: datetime = Field(..., description="생성 일시")


class CorrectionHistoryResponse(BaseModel):
    """수정 이력 응답.

    AC4: 수정 이력이 관리된다
    """

    query_id: str = Field(..., description="질의 ID")
    corrections: list[CorrectionItem] = Field(..., description="수정 이력 목록")
    total_count: int = Field(..., ge=0, description="전체 수정 건수")
