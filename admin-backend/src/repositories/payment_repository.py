"""
결제 Repository (관리자 백엔드)
"""
from __future__ import annotations

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from calendar import monthrange

from sqlalchemy.ext.asyncio import AsyncSession

KST = ZoneInfo("Asia/Seoul")
from sqlalchemy import select, and_, or_, func, desc, extract
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

        # COUNT 쿼리 - Payment만 카운트
        count_stmt = (
            select(func.count(Payment.payment_id))
            .select_from(Payment)
            .join(User, Payment.user_id == User.user_id)
        )

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

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """결제 ID로 결제 정보 조회"""
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_cancel_info(
        self,
        payment_id: int,
        cancel_amount: int,
        cancelled_at: datetime,
        payment_status: str = "CANCEL"
    ) -> Payment:
        """결제 취소 정보 업데이트"""
        payment = await self.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"결제를 찾을 수 없습니다: payment_id={payment_id}")

        payment.cancel_amount = cancel_amount
        payment.cancelled_at = cancelled_at
        payment.payment_status = payment_status
        payment.updated_at = datetime.now(KST)

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    # ===== 수익 통계 메서드 =====

    async def get_daily_revenue(
        self,
        year: int,
        month: int
    ) -> List[Dict[str, Any]]:
        """
        일별 수익 통계 조회 (SUCCESS 상태만)
        - 해당 월의 모든 날에 대해 데이터 반환 (데이터 없는 날도 0으로)
        """
        start_date = datetime(year, month, 1, tzinfo=KST)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59, tzinfo=KST)

        # 일별 집계 쿼리
        stmt = (
            select(
                func.date(Payment.paid_at).label("date"),
                func.sum(Payment.amount).label("total_amount"),
                func.count(Payment.payment_id).label("count")
            )
            .where(
                and_(
                    Payment.payment_status == "SUCCESS",
                    Payment.paid_at >= start_date,
                    Payment.paid_at <= end_date
                )
            )
            .group_by(func.date(Payment.paid_at))
            .order_by(func.date(Payment.paid_at))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # 날짜별 데이터 매핑
        data_map = {str(row.date): {"total_amount": int(row.total_amount or 0), "count": int(row.count or 0)} for row in rows}

        # 해당 월의 모든 날짜에 대해 결과 생성
        items = []
        for day in range(1, last_day + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in data_map:
                items.append({
                    "label": date_str,
                    "total_amount": data_map[date_str]["total_amount"],
                    "count": data_map[date_str]["count"]
                })
            else:
                items.append({
                    "label": date_str,
                    "total_amount": 0,
                    "count": 0
                })

        return items

    async def get_monthly_revenue(
        self,
        year: int
    ) -> List[Dict[str, Any]]:
        """
        월별 수익 통계 조회 (SUCCESS 상태만)
        - 해당 연도의 모든 월에 대해 데이터 반환
        """
        start_date = datetime(year, 1, 1, tzinfo=KST)
        end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=KST)

        # 월별 집계 쿼리
        stmt = (
            select(
                extract("month", Payment.paid_at).label("month"),
                func.sum(Payment.amount).label("total_amount"),
                func.count(Payment.payment_id).label("count")
            )
            .where(
                and_(
                    Payment.payment_status == "SUCCESS",
                    Payment.paid_at >= start_date,
                    Payment.paid_at <= end_date
                )
            )
            .group_by(extract("month", Payment.paid_at))
            .order_by(extract("month", Payment.paid_at))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # 월별 데이터 매핑
        data_map = {int(row.month): {"total_amount": int(row.total_amount or 0), "count": int(row.count or 0)} for row in rows}

        # 1~12월 모든 월에 대해 결과 생성
        items = []
        for month in range(1, 13):
            month_label = f"{year}-{month:02d}"
            if month in data_map:
                items.append({
                    "label": month_label,
                    "total_amount": data_map[month]["total_amount"],
                    "count": data_map[month]["count"]
                })
            else:
                items.append({
                    "label": month_label,
                    "total_amount": 0,
                    "count": 0
                })

        return items

    async def get_yearly_revenue(
        self,
        start_year: int = None,
        end_year: int = None
    ) -> List[Dict[str, Any]]:
        """
        연별 수익 통계 조회 (SUCCESS 상태만)
        - 기본: 최근 5년간 데이터
        """
        now = datetime.now(KST)
        if end_year is None:
            end_year = now.year
        if start_year is None:
            start_year = end_year - 4  # 최근 5년

        start_date = datetime(start_year, 1, 1, tzinfo=KST)
        end_date = datetime(end_year, 12, 31, 23, 59, 59, tzinfo=KST)

        # 연별 집계 쿼리
        stmt = (
            select(
                extract("year", Payment.paid_at).label("year"),
                func.sum(Payment.amount).label("total_amount"),
                func.count(Payment.payment_id).label("count")
            )
            .where(
                and_(
                    Payment.payment_status == "SUCCESS",
                    Payment.paid_at >= start_date,
                    Payment.paid_at <= end_date
                )
            )
            .group_by(extract("year", Payment.paid_at))
            .order_by(extract("year", Payment.paid_at))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # 연별 데이터 매핑
        data_map = {int(row.year): {"total_amount": int(row.total_amount or 0), "count": int(row.count or 0)} for row in rows}

        # 지정된 연도 범위의 모든 연도에 대해 결과 생성
        items = []
        for year in range(start_year, end_year + 1):
            year_label = str(year)
            if year in data_map:
                items.append({
                    "label": year_label,
                    "total_amount": data_map[year]["total_amount"],
                    "count": data_map[year]["count"]
                })
            else:
                items.append({
                    "label": year_label,
                    "total_amount": 0,
                    "count": 0
                })

        return items



