"""
알림 로그 모델 (t_notification_log)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Index, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class NotificationLog(Base):
    __tablename__ = "t_notification_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="수신자 타입: USER, COUNSELOR")
    recipient_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="수신자 ID")
    channel: Mapped[str] = mapped_column(String(20), nullable=False, comment="발송 채널")
    template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="제목")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="내용")
    variables: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, comment="치환 변수")
    send_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", comment="발송 상태")
    provider_response: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, comment="제공자 응답")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="발송 시간")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="읽은 시간")
    failed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="실패 사유")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="재시도 횟수")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_recipient", "recipient_type", "recipient_id"),
        Index("idx_send_status", "send_status"),
        Index("idx_created_at", "created_at"),
        {"comment": "알림 발송 로그"},
    )






























