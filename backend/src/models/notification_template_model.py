"""
Notification Template Model
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, JSON
)
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class NotificationChannel(str, Enum):
    """Notification Channel Types"""
    KAKAO = "KAKAO"
    SMS = "SMS"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class NotificationTemplate(Base):
    """Notification Template Table"""
    __tablename__ = "t_notification_template"

    template_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    content_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    button_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(KST), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=lambda: datetime.now(KST), nullable=True)
