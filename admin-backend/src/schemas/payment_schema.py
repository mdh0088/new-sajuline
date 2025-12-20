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


class PaymentCancelRequest(BaseModel):
    payment_id: int = Field(..., description="결제 ID")


class PaymentCancelResponse(BaseModel):
    success: bool = Field(..., description="취소 성공 여부")
    payment_id: int = Field(..., description="결제 ID")
    cancel_amount: int = Field(..., description="취소 금액")
    cancelled_at: datetime = Field(..., description="취소 시간")
    message: str = Field(..., description="결과 메시지")


# ===== 수익 통계 스키마 =====

class RevenueStatType(str):
    """수익 통계 타입"""
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RevenueStatParams(BaseModel):
    """수익 통계 요청 파라미터"""
    stat_type: str = Field(default="daily", description="통계 타입: daily|monthly|yearly")
    year: Optional[int] = Field(default=None, description="조회 연도 (미지정시 현재 연도)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="조회 월 (일별 통계시 사용, 미지정시 현재 월)")


class RevenueStatItem(BaseModel):
    """수익 통계 항목"""
    label: str = Field(..., description="라벨 (날짜/월/연도)")
    total_amount: int = Field(..., description="총 수익 금액")
    count: int = Field(..., description="결제 건수")


class RevenueStatResponse(BaseModel):
    """수익 통계 응답"""
    stat_type: str = Field(..., description="통계 타입")
    year: int = Field(..., description="조회 연도")
    month: Optional[int] = Field(None, description="조회 월 (일별 통계시)")
    items: List[RevenueStatItem] = Field(..., description="통계 데이터 목록")
    total_revenue: int = Field(..., description="조회 기간 총 수익")
    total_count: int = Field(..., description="조회 기간 총 건수")



