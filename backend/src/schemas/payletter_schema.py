"""
Payletter 연동 전용 스키마
"""
from typing import Optional
from pydantic import BaseModel, Field


class PaymentRequestPayload(BaseModel):
    product_id: int = Field(..., description="선택한 포인트 상품 ID")
    payment_method: str = Field("creditcard", description="결제 수단 표시용")


class PayletterRequestResponse(BaseModel):
    token: str | int
    online_url: Optional[str] = None
    mobile_url: Optional[str] = None


class PayletterCallbackBody(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    service_name: Optional[str] = None
    product_name: Optional[str] = None
    custom_parameter: Optional[str] = None
    tid: Optional[str] = None
    cid: Optional[str] = None
    amount: Optional[int] = None
    pay_info: Optional[str] = None
    pgcode: Optional[str] = None
    domestic_flag: Optional[str] = None
    billkey: Optional[str] = None
    transaction_date: Optional[str] = None
    card_info: Optional[str] = None
    payhash: Optional[str] = None
    install_month: Optional[str] = None



