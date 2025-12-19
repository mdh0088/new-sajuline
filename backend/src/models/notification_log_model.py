"""
Notification Log Model
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from zoneinfo import ZoneInfo

from sqlalchemy import (
    BigInteger, Integer, String, Text, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class RecipientType(str, Enum):
    """Recipient Type"""
    USER = "USER"
    COUNSELOR = "COUNSELOR"


class SendStatus(str, Enum):
    """Send Status"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class NotificationLog(Base):
    """Notification Log Table"""
    __tablename__ = "t_notification_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    recipient_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_notification_template.template_id"),
        nullable=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    send_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)
    provider_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(KST), nullable=False)
