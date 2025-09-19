"""
포인트 상품 모델 (t_point_product 테이블)
"""
from typing import Optional

from sqlalchemy import String, Integer, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class PointProduct(Base):
    """포인트 상품 테이블"""

    __tablename__ = "t_point_product"

    # 기본키
    product_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="상품 ID"
    )

    # 상품명
    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="상품명"
    )

    # 포인트 수량
    point_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="포인트 수량"
    )

    # 판매 가격(원)
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="판매 가격(원)"
    )

    # 보너스 포인트
    bonus_point: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="보너스 포인트"
    )

    # 할인율(%)
    discount_rate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="할인율(%)"
    )

    # 노출 순서
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="노출 순서"
    )

    # 활성화 여부
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="활성화 여부"
    )

    __table_args__ = (
        Index('idx_point_product_name', 'product_name'),
        Index('idx_point_product_active', 'is_active'),
        Index('idx_point_product_display_order', 'display_order'),
        {"comment": "포인트 상품"}
    )

    def __repr__(self) -> str:
        return f"<PointProduct(product_id={self.product_id}, product_name={self.product_name})>"



