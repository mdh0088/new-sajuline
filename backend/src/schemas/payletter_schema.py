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
    # 문서상 필드(일부 수단에서는 누락될 수 있어 Optional 처리)
    code: Optional[str] = None
    message: Optional[str] = None

    user_id: Optional[str] = None
    user_name: Optional[str] = None
    order_no: Optional[str] = None
    service_name: Optional[str] = None
    product_name: Optional[str] = None
    custom_parameter: Optional[str] = None

    tid: Optional[str] = None
    cid: Optional[str] = None
    amount: Optional[int] = None
    taxfree_amount: Optional[int] = None
    tax_amount: Optional[int] = None
    pay_info: Optional[str] = None
    pgcode: Optional[str] = None
    billkey: Optional[str] = None

    domestic_flag: Optional[str] = None
    transaction_date: Optional[str] = None
    install_month: Optional[str] = None
    card_info: Optional[str] = None
    payhash: Optional[str] = None

    # 가상계좌
    account_no: Optional[str] = None
    account_name: Optional[str] = None
    account_holder: Optional[str] = None
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    issue_tid: Optional[str] = None
    expire_date: Optional[str] = None
    expire_time: Optional[str] = None

    # 현금영수증
    cash_receipt_code: Optional[str] = None
    cash_receipt_message: Optional[str] = None
    cash_receipt_type: Optional[str] = None
    cash_receipt_issue_type: Optional[str] = None
    cash_receipt_cid: Optional[str] = None
    cash_receipt_payer_sid: Optional[str] = None
    cash_receipt_deal_no: Optional[str] = None



