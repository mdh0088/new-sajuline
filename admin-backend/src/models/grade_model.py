"""
등급(Grade) 모델 정의 - t_grade 테이블
"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from sqlalchemy import (
    String,
    DateTime,
    Integer,
    Boolean,
    Text,
    Index,
    CheckConstraint,
    DECIMAL,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from src.core.database import Base


class Grade(Base):
    """등급 정의 테이블 (t_grade)

    프로젝트 전역 스키마(문서)의 t_grade 정의를 기준으로 작성.
    """

    __tablename__ = "t_grade"

    # 기본키
    grade_code: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        comment="등급 코드",
    )

    # 등급 기본 정보
    grade_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="등급명")
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, comment="등급 레벨")

    # 등급 조건 및 혜택
    min_purchase_amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="최소 구매 금액")
    point_earn_rate: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False, comment="포인트 적립률")
    discount_rate: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False, default=Decimal("0.00"), comment="할인율")
    benefits: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="추가 혜택 (JSON)")

    # 표시/설명
    grade_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="등급 이미지 URL")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="등급 설명")

    # 상태
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, comment="생성일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="수정일시")

    __table_args__ = (
        Index("uk_grade_level", "grade_level", unique=True),
        Index("idx_is_active", "is_active"),
        CheckConstraint("point_earn_rate >= 0 AND point_earn_rate <= 100", name="chk_point_earn_rate"),
        CheckConstraint("discount_rate >= 0 AND discount_rate <= 100", name="chk_discount_rate"),
        CheckConstraint("min_purchase_amount >= 0", name="chk_min_purchase_amount"),
        {"comment": "등급 정의"},
    )

    def __repr__(self) -> str:  # pragma: no cover - 단순 표현
        return f"<Grade(grade_code={self.grade_code}, grade_name={self.grade_name}, grade_level={self.grade_level})>"


