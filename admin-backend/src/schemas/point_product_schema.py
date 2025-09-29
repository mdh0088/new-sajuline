"""
포인트 상품(PointProduct) Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class PointProductItem(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    point_amount: int
    price: float
    bonus_point: int
    discount_rate: float
    display_order: int
    is_active: bool
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PointProductListResponse(BaseModel):
    items: List[PointProductItem]
    total: int


class PointProductCreateRequest(BaseModel):
    product_name: str
    point_amount: int
    price: float
    bonus_point: float | int = Field(default=0)
    discount_rate: float | int = Field(default=0)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PointProductUpdateRequest(BaseModel):
    product_id: int = Field(..., description="수정 대상 PK")
    product_name: Optional[str] = None
    point_amount: Optional[int] = None
    price: Optional[float] = None
    bonus_point: Optional[float | int] = None
    discount_rate: Optional[float | int] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PointProductDeleteRequest(BaseModel):
    product_id: int


class PointProductDeleteResponse(BaseModel):
    product_id: int
    updated: bool


