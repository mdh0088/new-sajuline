"""
결제 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PaymentBase(BaseModel):
    """결제 기본 스키마"""
    order_no: str = Field(..., description="주문번호")
    user_id: str = Field(..., description="사용자 ID")
    product_id: Optional[int] = Field(None, description="상품 ID")
    payment_type: str = Field(..., description="결제 유형")
    amount: int = Field(..., description="결제 금액")
    point_amount: int = Field(default=0, description="충전 포인트")
    mileage_used: int = Field(default=0, description="사용 마일리지")
    payment_method: str = Field(..., description="결제 수단")


class PaymentCreate(PaymentBase):
    """결제 생성 요청 스키마"""
    payment_status: str = Field(default="PENDING", description="결제 상태")
    pg_tid: Optional[str] = Field(None, description="PG 거래번호")
    cid: str = Field(default="", description="cid")
    billkey: Optional[str] = Field(None, description="자동결제 재결제용 키")
    card_info: Optional[str] = Field(None, description="마스킹 카드번호")
    pay_info: str = Field(default="", description="결제정보")
    tax_amount: str = Field(default="0", description="세금")
    install_month: Optional[str] = Field(None, description="할부개월")
    pay_hash: Optional[str] = Field(None, description="결제 해시")
    taxfree_amount: Optional[str] = Field(None, description="비과세 금액")
    nonsettle_amount: Optional[str] = Field(None, description="미결제 금액")
    discount_amount: Optional[str] = Field(None, description="할인 금액")
    point_use_flag: Optional[str] = Field(None, description="포인트 사용 여부")
    disposable_cup_deposit: Optional[str] = Field(None, description="일회용컵 보증금")
    domestic_flag: str = Field(default="", description="도메스틱 플래그")
    paid_at: Optional[datetime] = Field(None, description="결제 완료 시간")
    code: Optional[str] = Field(None, description="결과 코드")
    result_message: Optional[str] = Field(None, description="결과 메시지")


class PaymentUpdate(BaseModel):
    """결제 수정 요청 스키마"""
    payment_status: Optional[str] = Field(None, description="결제 상태")
    pg_tid: Optional[str] = Field(None, description="PG 거래번호")
    paid_at: Optional[datetime] = Field(None, description="결제 완료 시간")
    code: Optional[str] = Field(None, description="성공코드")
    result_message: Optional[str] = Field(None, description="결과 메시지")
    cancel_amount: Optional[int] = Field(None, description="환불 금액")
    cancelled_at: Optional[datetime] = Field(None, description="취소 시간")


class PaymentResponse(PaymentBase):
    """결제 응답 스키마"""
    payment_id: int = Field(..., description="결제 ID")
    payment_status: str = Field(..., description="결제 상태")
    pg_tid: Optional[str] = Field(None, description="PG 거래번호")
    cid: str = Field(..., description="cid")
    billkey: Optional[str] = Field(None, description="자동결제 재결제용 키")
    card_info: Optional[str] = Field(None, description="마스킹 카드번호")
    pay_info: str = Field(..., description="결제정보")
    tax_amount: str = Field(..., description="세금")
    install_month: Optional[str] = Field(None, description="할부개월")
    pay_hash: Optional[str] = Field(None, description="결제 해시")
    taxfree_amount: Optional[str] = Field(None, description="비과세 금액")
    nonsettle_amount: Optional[str] = Field(None, description="미결제 금액")
    discount_amount: Optional[str] = Field(None, description="할인 금액")
    point_use_flag: Optional[str] = Field(None, description="포인트 사용 여부")
    disposable_cup_deposit: Optional[str] = Field(None, description="일회용컵 보증금")
    domestic_flag: str = Field(..., description="도메스틱 플래그")
    paid_at: Optional[datetime] = Field(None, description="결제 완료 시간")
    code: Optional[str] = Field(None, description="성공코드")
    result_message: Optional[str] = Field(None, description="결과 메시지")
    cancel_amount: Optional[int] = Field(None, description="환불 금액")
    cancelled_at: Optional[datetime] = Field(None, description="취소 시간")
    account_no: Optional[str] = Field(None, description="계좌번호")
    account_name: Optional[str] = Field(None, description="예금주명")
    account_holder: Optional[str] = Field(None, description="계좌 소유자")
    bank_code: Optional[str] = Field(None, description="은행 코드")
    bank_name: Optional[str] = Field(None, description="은행명")
    expire_date: Optional[str] = Field(None, description="만료일")
    expire_time: Optional[str] = Field(None, description="만료시간")
    issue_tid: Optional[str] = Field(None, description="발급 거래번호")
    cash_receipt_type: Optional[str] = Field(None, description="현금영수증 종류")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentSummary(BaseModel):
    """결제 요약 정보 (목록 조회용)"""
    payment_id: int = Field(..., description="결제 ID")
    order_no: str = Field(..., description="주문번호")
    payment_type: str = Field(..., description="결제 유형")
    amount: int = Field(..., description="결제 금액")
    point_amount: int = Field(..., description="충전 포인트")
    payment_method: str = Field(..., description="결제 수단")
    payment_status: str = Field(..., description="결제 상태")
    paid_at: Optional[datetime] = Field(None, description="결제 완료 시간")
    created_at: datetime = Field(..., description="생성일시")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    """결제 목록 응답 스키마"""
    payments: list[PaymentSummary] = Field(..., description="결제 목록")
    total: int = Field(..., description="전체 결제 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")