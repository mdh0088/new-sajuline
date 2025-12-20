"""
대시보드 API

- 수익 통계: 일별/월별/연별 결제 수익 조회
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.payment_repository import PaymentRepository
from src.services.payment_service import PaymentService
from src.schemas.payment_schema import RevenueStatParams


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_payment_service(
    db: AsyncSession = Depends(get_db_maria),
) -> PaymentService:
    return PaymentService(PaymentRepository(db), mssql=None)


@router.get("/test")
async def test_dashboard():
    """대시보드 테스트 엔드포인트"""
    return {"message": "Dashboard API is working"}


@router.get("/revenue/stats", response_model=APIResponse, summary="수익 통계 조회")
async def get_revenue_stats(
    stat_type: str = Query("daily", description="통계 타입: daily|monthly|yearly"),
    year: Optional[int] = Query(None, description="조회 연도 (미지정시 현재 연도)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="조회 월 (일별 통계시 사용, 미지정시 현재 월)"),
    service: PaymentService = Depends(_get_payment_service),
):
    """
    수익 통계 조회 API

    - stat_type: daily (일별), monthly (월별), yearly (연별)
    - year: 조회 연도 (미지정시 현재 연도)
    - month: 조회 월 (일별 통계시 필요, 미지정시 현재 월)

    응답:
    - items: 통계 데이터 목록 (label, total_amount, count)
    - total_revenue: 조회 기간 총 수익
    - total_count: 조회 기간 총 건수
    """
    params = RevenueStatParams(
        stat_type=stat_type,
        year=year,
        month=month,
    )
    data = await service.get_revenue_stats(params)
    return ok(data=data.model_dump(), message="수익 통계 조회 성공")
