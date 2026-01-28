"""
운세 이력(FortuneHistory) 모델

Story 2.1 Task 5: 운세 이력 테이블 (AC: 6)
- user_id, fortune_type, target_date, content, ai_model, prompt_version, created_at 컬럼 포함
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Date, Text, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class FortuneType(str, Enum):
    """운세 유형"""
    DAILY = "daily"  # 일일 운세
    WEEKLY = "weekly"  # 주간 운세
    MONTHLY = "monthly"  # 월간 운세
    YEARLY = "yearly"  # 연간 운세


class FortuneHistory(Base):
    """
    운세 이력 테이블

    사용자의 AI 운세 생성 이력을 저장합니다.
    """

    __tablename__ = "fortune_histories"

    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="운세 이력 ID (UUID)"
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="사용자 ID"
    )
    fortune_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="운세 유형 (daily, weekly, monthly, yearly)"
    )
    target_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="운세 대상 날짜"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="AI 생성 운세 내용"
    )
    ai_model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="사용된 AI 모델 (예: gpt-4o-mini)"
    )
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="프롬프트 버전 (예: v1.0.0)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        comment="생성일시"
    )

    __table_args__ = (
        Index("idx_user_type_date", "user_id", "fortune_type", "target_date"),
        {"comment": "AI 운세 생성 이력"}
    )

    def __repr__(self) -> str:
        return f"<FortuneHistory(id={self.id}, user_id={self.user_id}, type={self.fortune_type})>"
