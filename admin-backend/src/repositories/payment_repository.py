"""
결제 Repository (관리자 백엔드)
"""
from __future__ import annotations

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import aliased

from src.models.payment_model import Payment
from src.models.user_model import User


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list_with_user(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        amount: Optional[int],
        payment_method: Optional[str],
        payment_status: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Tuple[Payment, User]], int]:
        """
        결제 목록 + 사용자 조인 조회
        - t_payment.user_id = t_user.user_id JOIN
        - created_at DESC 정렬
        - 다양한 필터 처리
        """

        conditions = []

        # 기본 조인
        stmt = select(Payment, User).join(User, Payment.user_id == User.user_id)
        count_stmt = select(func.count()).select_from(select(Payment.payment_id).join(User, Payment.user_id == User.user_id).subquery())

        # 금액/수단/상태 필터
        if amount is not None:
            conditions.append(Payment.amount == amount)
        if payment_method:
            conditions.append(Payment.payment_method == payment_method)
        if payment_status:
            conditions.append(Payment.payment_status == payment_status)

        # 날짜 범위 (created_at)
        if start_dt is not None:
            conditions.append(Payment.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Payment.created_at <= end_dt)

        # 검색 (all 또는 특정 필드)
        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(
                        Payment.user_id.like(kw),
                        User.user_id.like(kw),
                        User.nickname.like(kw),
                        User.email.like(kw),
                        User.phone.like(kw),
                    )
                )
            elif search_type == "user_id":
                # 결제의 user_id 또는 사용자 user_id 모두 고려
                conditions.append(or_(Payment.user_id.like(kw), User.user_id.like(kw)))
            elif search_type == "nickname":
                conditions.append(User.nickname.like(kw))
            elif search_type == "email":
                conditions.append(User.email.like(kw))
            elif search_type == "phone":
                conditions.append(User.phone.like(kw))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(Payment.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(stmt)
        rows: List[Tuple[Payment, User]] = list(result.all())

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        return rows, total

    async def get_detail_with_user(self, payment_id: int) -> Optional[Tuple[Payment, User]]:
        stmt = (
            select(Payment, User)
            .join(User, Payment.user_id == User.user_id)
            .where(Payment.payment_id == payment_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        return row


