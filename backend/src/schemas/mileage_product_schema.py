"""
마일리지 상품 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MileageProductBase(BaseModel):
    """마일리지 상품 기본 스키마"""
    m_product_name: str = Field(..., description="상품명")
    m_product_value: int = Field(..., description="상품가격")
    charge_point: int = Field(..., description="충전 포인트")
    m_product_img: Optional[str] = Field(None, description="상품 이미지 경로")
    image_url: Optional[str] = Field(None, description="이미지 URL")
    valid_from: Optional[datetime] = Field(None, description="상품 노출 시작일")
    valid_until: Optional[datetime] = Field(None, description="상품 노출 종료일")
    ord: int = Field(..., description="노출 순번")
    tags: Optional[str] = Field(None, description="태그")
    description: Optional[str] = Field(None, description="상품설명")
    is_active: bool = Field(..., description="사용유무")


class MileageProductResponse(MileageProductBase):
    """마일리지 상품 응답 스키마"""
    mileage_id: int = Field(..., description="마일리지 상품 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    model_config = ConfigDict(from_attributes=True)


class MileagePurchaseRequest(BaseModel):
    """마일리지 상품 구매 요청 스키마"""
    mileage_id: int = Field(..., description="마일리지 상품 ID")


class MileageHistoryResponse(BaseModel):
    """마일리지 내역 응답 스키마"""
    transaction_id: int = Field(..., description="거래 ID")
    transaction_type: str = Field(..., description="거래 유형 (EARN: 적립, USE: 사용)")
    currency_type: str = Field(..., description="통화 유형 (MILEAGE)")
    amount: int = Field(..., description="거래 금액")
    balance_after: int = Field(..., description="거래 후 잔액")
    reference_type: Optional[str] = Field(None, description="참조 유형")
    reference_id: Optional[str] = Field(None, description="참조 ID")
    description: Optional[str] = Field(None, description="거래 설명")
    created_at: datetime = Field(..., description="거래 일시")

    model_config = ConfigDict(from_attributes=True)
