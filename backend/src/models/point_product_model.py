"""
포인트 상품 모델 (t_point_product 테이블)
"""
from typing import Optional

from sqlalchemy import String, Integer, Index
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

    # 포인트 수량 (참고용)
    point_amount: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="포인트 수량"
    )

    __table_args__ = (
        Index('idx_point_product_name', 'product_name'),
        {"comment": "포인트 상품"}
    )

    def __repr__(self) -> str:
        return f"<PointProduct(product_id={self.product_id}, product_name={self.product_name})>"



