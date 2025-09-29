"""
결제 관리 API (관리자 백엔드)

- 결제 목록 조회: t_payment JOIN t_user, 다양한 필터, created_at DESC, 페이징
- 결제 상세 조회: payment_id로 t_payment JOIN t_user 단건 조회
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, APIResponseBuilder, ok
from src.core.database import get_db as get_db_maria
from src.repositories.payment_repository import PaymentRepository
from src.services.payment_service import PaymentService
from src.schemas.payment_schema import PaymentListParams


router = APIRouter(prefix="/payments", tags=["payments"])


def _get_payment_service(db: AsyncSession = Depends(get_db_maria)) -> PaymentService:
    return PaymentService(PaymentRepository(db))


@router.get("/list", response_model=APIResponse, summary="결제 목록 조회")
async def list_payments(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|user_id|nickname|email|phone"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    amount: Optional[int] = Query(None, description="결제 금액"),
    payment_method: Optional[str] = Query(None, description="결제 수단"),
    payment_status: Optional[str] = Query(None, description="결제 상태: SUCCESS|HOLD|FAIL 등"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    service: PaymentService = Depends(_get_payment_service),
):
    params = PaymentListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        amount=amount,
        payment_method=payment_method,
        payment_status=payment_status,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    data = await service.list_payments(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in data.items],
        page=data.page,
        limit=data.limit,
        total=data.total,
        message="결제 목록 조회 성공",
    )


@router.get("/detail", response_model=APIResponse, summary="결제 상세 조회")
async def get_payment_detail(
    payment_id: int = Query(..., description="결제 ID"),
    service: PaymentService = Depends(_get_payment_service),
):
    data = await service.get_detail(payment_id)
    return ok(data=data.model_dump(), message="결제 상세 조회 성공")


