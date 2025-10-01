"""
마일리지 상품 스키마
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MileageProductItem(BaseModel):
    """마일리지 상품 응답 아이템"""

    mileage_id: int
    m_product_name: str
    m_product_value: int
    charge_point: int
    m_product_img: str
    image_url: str
    valid_from: datetime
    valid_until: datetime
    ord: int
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MileageProductListResponse(BaseModel):
    """마일리지 상품 목록 응답"""

    total: int
    items: list[MileageProductItem]


class MileageProductCreateRequest(BaseModel):
    """마일리지 상품 등록 요청"""

    m_product_name: str = Field(..., min_length=1, max_length=100, description="상품명")
    m_product_value: int = Field(..., gt=0, description="상품 가치")
    charge_point: int = Field(..., gt=0, description="충전 포인트")
    valid_from: datetime = Field(..., description="판매 시작일")
    valid_until: datetime = Field(..., description="판매 종료일")
    ord: int = Field(default=0, description="노출 순서")
    description: Optional[str] = Field(None, description="상품 설명")
    is_active: bool = Field(default=True, description="활성화 여부")


class MileageProductUpdateRequest(BaseModel):
    """마일리지 상품 수정 요청"""

    m_product_name: Optional[str] = Field(None, min_length=1, max_length=100, description="상품명")
    m_product_value: Optional[int] = Field(None, gt=0, description="상품 가치")
    charge_point: Optional[int] = Field(None, gt=0, description="충전 포인트")
    valid_from: Optional[datetime] = Field(None, description="판매 시작일")
    valid_until: Optional[datetime] = Field(None, description="판매 종료일")
    ord: Optional[int] = Field(None, description="노출 순서")
    description: Optional[str] = Field(None, description="상품 설명")
    is_active: Optional[bool] = Field(None, description="활성화 여부")


class MileageProductDeleteResponse(BaseModel):
    """마일리지 상품 삭제 응답"""

    message: str
    deleted_id: int