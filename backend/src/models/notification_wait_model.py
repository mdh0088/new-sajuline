"""
알림톡 발송 대기 모델 (t_notification_wait 테이블)
상담사 접속 알림을 설정한 사용자 목록 관리
"""
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class NotificationWait(Base):
    """알림톡 발송 대기 테이블"""

    __tablename__ = "t_notification_wait"

    # 기본키
    wait_idx: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="대기 ID"
    )

    # 사용자 ID
    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="유저 id"
    )

    # 상담사 ID
    counselor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="상담사 id"
    )

    # 발송 유무
    is_send: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="발송유무"
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="등록일"
    )

    # 인덱스 정의
    __table_args__ = (
        Index('t_notification_wait_user_id_IDX', 'user_id'),
        Index('t_notification_wait_counselor_id_IDX', 'counselor_id'),
        {'comment': '알림톡 발송 대기 리스트'}
    )

    def __repr__(self) -> str:
        return f"<NotificationWait(wait_idx={self.wait_idx}, user_id={self.user_id}, counselor_id={self.counselor_id}, is_send={self.is_send})>"
