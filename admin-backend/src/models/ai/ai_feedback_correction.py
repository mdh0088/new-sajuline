"""
AI 피드백 수정 모델.

사용자가 제출한 AI 응답 수정 데이터를 저장하고,
향후 AI 모델 학습에 활용합니다.

Stories: 5-2
FRs: FR25
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class AIFeedbackCorrection(Base):
    """AI 피드백 수정 테이블 (t_ai_feedback_correction).

    AC3: 수정된 답변이 원본과 함께 저장
    AC4: 수정 이력이 관리
    AC5: 수정된 답변이 향후 학습 데이터로 표시
    """
    __tablename__ = "t_ai_feedback_correction"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="수정 ID"
    )
    admin_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("t_admin.admin_id"),
        nullable=False,
        index=True,
        comment="수정 제출자 ID"
    )
    query_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="질의 ID (t_ai_query_history.query_id)"
    )
    original_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="원본 AI 응답"
    )
    corrected_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="수정된 응답"
    )
    correction_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="수정 사유"
    )
    is_training_data: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="학습 데이터 포함 여부"
    )
    reviewed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="검토 완료 여부"
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("t_admin.admin_id"),
        nullable=True,
        comment="검토자 ID"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="검토 일시"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        index=True,
        comment="생성 일시"
    )

    def __repr__(self) -> str:
        return (
            f"<AIFeedbackCorrection(id={self.id}, "
            f"query_id={self.query_id}, "
            f"reviewed={self.reviewed})>"
        )
