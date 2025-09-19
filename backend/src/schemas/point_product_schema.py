"""
포인트 상품 Pydantic 스키마
"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PointProductResponse(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    point_amount: int = Field(..., description="충전 포인트")
    price: int = Field(..., description="판매 가격(원)")
    bonus_point: int = Field(..., description="보너스 포인트")
    discount_rate: int = Field(..., description="할인율(%)")
    display_order: int = Field(..., description="노출 순서")
    is_active: bool = Field(..., description="활성화 여부")
    
    model_config = ConfigDict(from_attributes=True)


class PointProductListResponse(BaseModel):
    items: list[PointProductResponse] = Field(..., description="상품 목록")
    total: int = Field(..., description="총 개수")



