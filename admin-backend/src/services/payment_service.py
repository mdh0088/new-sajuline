"""
결제 서비스 (관리자 백엔드)
"""
from __future__ import annotations

from typing import List, Tuple
from datetime import datetime

from src.repositories.payment_repository import PaymentRepository
from src.schemas.payment_schema import (
    PaymentListParams,
    PaymentListResponse,
    PaymentWithUserItem,
    PaymentDetailResponse,
)


class PaymentService:
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo

    async def list_payments(self, params: PaymentListParams) -> PaymentListResponse:
        # 페이지/리밋 보정
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        # 날짜 파싱
        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        rows, total = await self.payment_repo.get_list_with_user(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            amount=params.amount,
            payment_method=params.payment_method or None,
            payment_status=params.payment_status or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items: List[PaymentWithUserItem] = []
        for payment, user in rows:
            # 모든 필드를 dict로 구성 (from_attributes 사용 없이 직접 매핑)
            payment_dict = {c.name: getattr(payment, c.name) for c in payment.__table__.columns}
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            items.append(PaymentWithUserItem(payment=payment_dict, user=user_dict))

        return PaymentListResponse(items=items, page=params.page, limit=params.limit, total=total)

    async def get_detail(self, payment_id: int) -> PaymentDetailResponse:
        row = await self.payment_repo.get_detail_with_user(payment_id)
        if not row:
            # 통일된 예외 클래스 파일 존재와 무관하게, FastAPI에서 404로 매핑되도록 ValueError 사용
            raise ValueError("결제를 찾을 수 없습니다")
        payment, user = row
        payment_dict = {c.name: getattr(payment, c.name) for c in payment.__table__.columns}
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return PaymentDetailResponse(payment=payment_dict, user=user_dict)


