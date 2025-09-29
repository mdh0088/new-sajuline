"""
관리자 백엔드 결제 스키마
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class PaymentListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search_type: str = Field(default="all", description="all|user_id|nickname|email|phone")
    search_name: Optional[str] = Field(default=None)
    amount: Optional[int] = Field(default=None)
    payment_method: Optional[str] = Field(default=None)
    payment_status: Optional[str] = Field(default=None)
    start_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")


class PaymentItem(BaseModel):
    # t_payment 주요 필드 요약 (응답 리스트용)
    payment_id: int
    order_no: str
    user_id: str
    amount: int
    payment_method: str
    payment_status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentWithUserItem(BaseModel):
    payment: Dict[str, Any] = Field(..., description="t_payment 모든 필드")
    user: Dict[str, Any] = Field(..., description="t_user 모든 필드")


class PaymentListResponse(BaseModel):
    items: List[PaymentWithUserItem]
    page: int
    limit: int
    total: int


class PaymentDetailResponse(BaseModel):
    payment: Dict[str, Any]
    user: Dict[str, Any]


