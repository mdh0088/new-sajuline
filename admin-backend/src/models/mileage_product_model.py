"""
마일리지 상품 모델 (t_mileage_product)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class MileageProduct(Base):
    """마일리지 상품 테이블 (t_mileage_product)"""

    __tablename__ = "t_mileage_product"

    # 기본키
    mileage_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="마일리지 상품 PK")

    # 상품 기본 정보
    m_product_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="상품명")
    m_product_value: Mapped[int] = mapped_column(Integer, nullable=False, comment="상품 가치")
    charge_point: Mapped[int] = mapped_column(Integer, nullable=False, comment="충전 포인트")

    # 이미지 정보
    m_product_img: Mapped[str] = mapped_column(String(255), nullable=False, comment="S3 저장 파일명")
    image_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="원본 파일명")

    # 유효 기간
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="판매 시작일")
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="판매 종료일")

    # 전시 순서 및 상태
    ord: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="노출 순서")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")

    # 상세 설명
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="상품 설명")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(KST), comment="생성일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(KST), comment="수정일시")

    __table_args__ = (
        Index("idx_is_active_ord", "is_active", "ord"),
        Index("idx_valid_date", "valid_from", "valid_until"),
        Index("idx_created_at", "created_at"),
        {"comment": "마일리지 상품"},
    )

    def __repr__(self) -> str:
        return f"<MileageProduct(id={self.mileage_id}, name={self.m_product_name}, active={self.is_active})>"