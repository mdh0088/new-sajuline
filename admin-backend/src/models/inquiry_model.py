"""
1:1 문의 모델 (관리자 백엔드 / t_inquiry)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text, Integer, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Inquiry(Base):
    """1:1 문의 테이블 (t_inquiry)

    상담사 문의 목록/상세/수정/삭제 API에서 활용
    """

    __tablename__ = "t_inquiry"

    # 기본키
    inquiry_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="문의 ID",
    )

    # 문의자 정보
    inquirer_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="문의자 타입: USER, COUNSELOR, GUEST",
    )
    inquirer_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="문의자 ID",
    )
    counselor_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="문의 상담사 ID",
    )

    # 문의 내용
    category: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="문의 카테고리",
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="제목",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="내용",
    )

    # 처리 상태
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="읽음 상태",
    )

    # 답변 정보
    reply_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="관리자 답변",
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="답변 시간",
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="생성일시",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
        comment="수정일시",
    )

    __table_args__ = (
        Index("idx_inquiry_inquirer_type", "inquirer_type"),
        Index("idx_inquiry_inquirer_id", "inquirer_id"),
        Index("idx_inquiry_counselor_id", "counselor_id"),
        Index("idx_inquiry_is_read", "is_read"),
        Index("idx_inquiry_created_at", "created_at"),
        {"comment": "1:1 문의"},
    )

    def __repr__(self) -> str:
        return f"<Inquiry(inquiry_id={self.inquiry_id}, inquirer_type={self.inquirer_type}, title={self.title})>"



