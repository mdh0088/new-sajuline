"""
이벤트 참여 로그(Event Participation Log) 모델 정의
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Integer, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class EventParticipationLog(Base):
    """이벤트 참여 로그 테이블"""
    __tablename__ = "t_event_participation_log"
    
    # 기본키
    log_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True, 
        comment="참여 로그 ID"
    )
    
    # 참조 필드 (외래키 제약조건 제거)
    event_id: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        comment="이벤트 ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="사용자 ID"
    )
    
    # 참여 데이터
    participation_data: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True, 
        comment="참여 데이터 (JSON)"
    )
    
    # 보상 정보
    reward_type: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True, 
        comment="보상 타입"
    )
    reward_value: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        comment="보상 값"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        comment="참여 일시"
    )
    
    # 관계 정의 (선택사항 - 필요시 활용)
    # event: Mapped["Event"] = relationship("Event", back_populates="participations")
    # user: Mapped["User"] = relationship("User", back_populates="event_participations")
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='uk_event_user'),
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_event_id', 'event_id'),
        {'comment': '이벤트 참여 로그'}
    )
    
    def __repr__(self) -> str:
        return f"<EventParticipationLog(log_id={self.log_id}, event_id={self.event_id}, user_id={self.user_id})>"