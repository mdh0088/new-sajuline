"""
포인트 상품(PointProduct) 모델 정의 - t_point_product 테이블
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Integer, DECIMAL, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class PointProduct(Base):
    """포인트 상품 테이블 (t_point_product)

    improved-schema.sql의 정의를 준수합니다.
    """

    __tablename__ = "t_point_product"

    # 기본키 및 식별자
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="상품 PK")
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="상품 코드")

    # 상품 기본 정보
    product_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="상품명")
    point_amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="포인트 수량")
    price: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False, comment="가격")
    bonus_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="보너스 포인트")
    discount_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False, default=0, comment="할인율")

    # 전시/상태/기간
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="노출 순서")
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="판매 시작일")
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="판매 종료일")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("uk_product_code", "product_code", unique=True),
        Index("idx_is_active_order", "is_active", "display_order"),
        Index("idx_valid_date", "valid_from", "valid_until"),
        {"comment": "포인트 상품"},
    )

    def __repr__(self) -> str:
        return f"<PointProduct(product_code={self.product_code}, name={self.product_name}, active={self.is_active})>"



