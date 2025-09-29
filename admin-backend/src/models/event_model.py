"""
이벤트/프로모션(Event) 모델 정의 - t_event 테이블
"""
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from src.core.database import Base


class Event(Base):
    """이벤트/프로모션 테이블 (t_event)

    improved-schema.sql 기준 구현.
    """

    __tablename__ = "t_event"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="이벤트 PK")
    event_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="이벤트 코드")

    event_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="이벤트명")
    event_type: Mapped[str] = mapped_column(String(30), nullable=False, comment="이벤트 타입")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="설명")
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="약관")
    banner_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="배너 이미지")

    reward_type: Mapped[str] = mapped_column(String(30), nullable=False, comment="보상 타입")
    reward_value: Mapped[int] = mapped_column(Integer, nullable=False, comment="보상 값")
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="최대 참여자수")
    current_participants: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="현재 참여자수")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="시작일")
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="종료일")

    # 컬럼명은 metadata 이지만, SQLAlchemy Base.metadata 충돌을 피하기 위해 속성명은 metadata_json으로 사용
    metadata_json: Mapped[Optional[Any]] = mapped_column("metadata", JSON, nullable=True, comment="추가 데이터")

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)


