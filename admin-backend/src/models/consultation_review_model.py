"""
상담 후기 모델 (t_consultation_review)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, SMALLINT, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ConsultationReview(Base):
    """상담 후기 테이블 (t_consultation_review)"""

    __tablename__ = "t_consultation_review"

    # 기본키
    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="후기 PK")

    # 세션 및 사용자 정보
    session_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, comment="상담 세션 ID")
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="작성자 ID")
    counselor_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="상담사 ID")

    # 후기 내용
    rating: Mapped[int] = mapped_column(SMALLINT, nullable=False, comment="평점 (1-5)")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="후기 내용")
    counselor_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="상담사 답변")
    review_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="리뷰 태그")

    # 상태 및 카운트
    is_best: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="베스트 후기")
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="공개 여부")
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="좋아요 수")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, comment="생성일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="수정일시")
    counselor_replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="상담사 답변일시")

    __table_args__ = (
        Index("uk_session_id", "session_id", unique=True),
        Index("idx_user_id", "user_id"),
        Index("idx_counselor_id", "counselor_id"),
        Index("idx_is_best_visible", "is_best", "is_visible"),
        Index("idx_created_at", "created_at"),
        {"comment": "상담 후기"},
    )

    def __repr__(self) -> str:
        return f"<ConsultationReview(id={self.review_id}, user={self.user_id}, counselor={self.counselor_id})>"