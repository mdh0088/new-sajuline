"""
이벤트(Event) 모델 정의
"""
from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Boolean, CheckConstraint, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class EventType(str, Enum):
    """이벤트 타입"""
    SIGNUP = "SIGNUP"          # 회원가입 이벤트
    LOGIN = "LOGIN"            # 로그인 이벤트
    CONSULTATION = "CONSULTATION"  # 상담 이벤트
    POINT = "POINT"            # 포인트 이벤트
    PROMOTION = "PROMOTION"    # 프로모션 이벤트
    SEASONAL = "SEASONAL"      # 시즌 이벤트


class RewardType(str, Enum):
    """보상 타입"""
    POINT = "POINT"      # 포인트
    MILEAGE = "MILEAGE"  # 마일리지
    COUPON = "COUPON"    # 쿠폰


class Event(Base):
    """이벤트 테이블"""
    __tablename__ = "t_event"
    
    # 기본키
    event_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True, 
        comment="이벤트 ID"
    )
    
    # 기본 정보
    event_code: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        comment="이벤트 코드"
    )
    event_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="이벤트명"
    )
    event_type: Mapped[str] = mapped_column(
        String(30), 
        nullable=False, 
        comment="이벤트 타입: SIGNUP, LOGIN, CONSULTATION, POINT, PROMOTION, SEASONAL"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="설명"
    )
    terms: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="약관"
    )
    banner_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True, 
        comment="배너 이미지 URL"
    )
    
    # 보상 정보
    reward_type: Mapped[str] = mapped_column(
        String(30), 
        nullable=False, 
        comment="보상 타입: POINT, MILEAGE, COUPON"
    )
    reward_value: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        comment="보상 값"
    )
    
    # 참여 관련
    max_participants: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        comment="최대 참여자수"
    )
    current_participants: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0, 
        comment="현재 참여자수"
    )
    
    # 상태 및 기간
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=True, 
        comment="활성화 여부"
    )
    valid_from: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        comment="시작일"
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        comment="종료일"
    )
    
    # 추가 데이터
    event_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata",  # 실제 DB 컬럼명
        JSON, 
        nullable=True, 
        comment="추가 데이터 (JSON)"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        comment="생성 일시"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        onupdate=datetime.utcnow, 
        comment="수정 일시"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_type_active', 'event_type', 'is_active'),
        Index('idx_valid_date', 'valid_from', 'valid_until'),
        Index('idx_created_at', 'created_at'),
        CheckConstraint(
            "event_type IN ('SIGNUP','LOGIN','CONSULTATION','POINT','PROMOTION','SEASONAL')",
            name='chk_event_type'
        ),
        CheckConstraint(
            "reward_type IN ('POINT','MILEAGE','COUPON')",
            name='chk_reward_type'
        ),
        CheckConstraint(
            "valid_from < valid_until",
            name='chk_valid_date_range'
        ),
        CheckConstraint(
            "current_participants >= 0",
            name='chk_current_participants_positive'
        ),
        CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name='chk_max_participants_positive'
        ),
        {'comment': '이벤트'}
    )
    
    def __repr__(self) -> str:
        return f"<Event(event_id={self.event_id}, event_code={self.event_code}, event_name={self.event_name})>"