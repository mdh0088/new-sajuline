"""사용자 활동 로그 모델"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Text, DateTime, Index,
    CheckConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserActivityLog(Base):
    """사용자 활동 로그 테이블"""
    
    __tablename__ = "t_user_activity_log"
    
    # 기본키
    log_id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True,
        comment="로그 ID"
    )
    
    # 사용자 정보
    user_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="사용자 ID (익명 사용자는 NULL 가능)"
    )
    user_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="USER",
        comment="사용자 타입: USER, COUNSELOR, GUEST"
    )
    
    # 활동 정보
    activity_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="활동 타입"
    )
    activity_detail: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="활동 상세 (JSON 형태)"
    )
    
    # 접속 정보
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), 
        nullable=True,
        comment="IP 주소 (IPv6 지원)"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="User Agent"
    )
    device_type: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="기기 타입: DESKTOP, MOBILE, TABLET"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="생성일시"
    )
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_user_id_created', 'user_id', 'created_at'),
        Index('idx_activity_type', 'activity_type'),
        Index('idx_created_at', 'created_at'),
        CheckConstraint(
            "user_type IN ('USER', 'COUNSELOR', 'GUEST')",
            name='chk_user_type'
        ),
        CheckConstraint(
            "device_type IS NULL OR device_type IN ('DESKTOP', 'MOBILE', 'TABLET')",
            name='chk_device_type'
        ),
        CheckConstraint(
            "activity_detail IS NULL OR JSON_VALID(activity_detail)",
            name='chk_activity_detail_json'
        ),
        {'comment': '사용자 활동 로그'}
    )
    
    def __repr__(self) -> str:
        return f"<UserActivityLog(log_id={self.log_id}, user_id={self.user_id}, activity_type={self.activity_type})>"