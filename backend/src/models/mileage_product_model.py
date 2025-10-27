"""
마일리지 상품 모델 (t_mileage_product 테이블)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class MileageProduct(Base):
    """마일리지 상품 테이블"""

    __tablename__ = "t_mileage_product"

    # 기본키
    mileage_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="마일리지 상품 ID"
    )

    # 상품명
    m_product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="상품명"
    )

    # 상품 가격
    m_product_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="상품가격"
    )

    # 충전 포인트
    charge_point: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="충전 포인트"
    )

    # 상품 이미지
    m_product_img: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="상품 이미지 경로"
    )

    # 이미지 URL
    image_url: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="이미지 URL"
    )

    # 노출 기간
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="상품 노출 시작일"
    )

    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="상품 노출 종료일"
    )

    # 노출 순번
    ord: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="노출 순번"
    )

    # 태그
    tags: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        comment="태그"
    )

    # 상품 설명
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="상품설명"
    )

    # 활성화 여부
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="사용유무"
    )

    # 생성일시
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="생성일시"
    )

    # 수정일시
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=func.current_timestamp(),
        comment="수정일시"
    )

    def __repr__(self) -> str:
        return f"<MileageProduct(mileage_id={self.mileage_id}, m_product_name={self.m_product_name})>"
