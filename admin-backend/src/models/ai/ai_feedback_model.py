"""
AI 피드백 모델.

Stories: STORY-5-1, STORY-5-3
FRs: FR-027
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class AIFeedback(Base):
    """AI 피드백 테이블 (t_ai_feedback).

    사용자가 AI 응답에 대해 제출한 피드백을 저장합니다.
    """

    __tablename__ = "t_ai_feedback"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="피드백 ID"
    )
    query_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_ai_query_history.query_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="질의 ID (UUID)",
    )
    admin_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("t_admin.admin_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="관리자 ID",
    )
    rating: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="별점 (1-5)"
    )
    comment: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="피드백 코멘트"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        index=True,
        comment="생성 일시",
    )

    def __repr__(self) -> str:
        return (
            f"<AIFeedback(id={self.id}, "
            f"query_id={self.query_id}, "
            f"rating={self.rating})>"
        )
