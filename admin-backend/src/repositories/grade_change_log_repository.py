"""
등급 변경 로그 Repository (t_grade_change_log 접근 레이어)
"""
from typing import List, Optional, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select, insert, func, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.grade_change_log_model import GradeChangeLog
from src.models.user_model import User
from src.models.payment_model import Payment
from src.models.grade_model import Grade

KST = ZoneInfo("Asia/Seoul")


class GradeChangeLogRepository:
    """등급 변경 로그 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        grade_before: str,
        grade_after: str,
        purchase_amount: int,
        change_reason: str,
        admin_id: Optional[int] = None
    ) -> GradeChangeLog:
        """등급 변경 로그 생성"""
        stmt = insert(GradeChangeLog).values(
            user_id=user_id,
            grade_before=grade_before,
            grade_after=grade_after,
            purchase_amount=purchase_amount,
            change_reason=change_reason,
            admin_id=admin_id,
            created_at=datetime.now(KST)
        )
        await self.db.execute(stmt)

        # 생성된 로그 조회 (가장 최근 항목)
        result = await self.db.execute(
            select(GradeChangeLog)
            .where(GradeChangeLog.user_id == user_id)
            .order_by(desc(GradeChangeLog.log_id))
            .limit(1)
        )
        return result.scalar_one()

    async def bulk_create(
        self,
        logs: List[dict]
    ) -> int:
        """등급 변경 로그 대량 생성

        Args:
            logs: [{"user_id", "grade_before", "grade_after", "purchase_amount", "change_reason", "admin_id"}]

        Returns:
            생성된 로그 수
        """
        if not logs:
            return 0

        now = datetime.now(KST)
        for log in logs:
            log["created_at"] = now

        stmt = insert(GradeChangeLog).values(logs)
        result = await self.db.execute(stmt)
        return len(logs)

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[GradeChangeLog]:
        """사용자별 등급 변경 로그 조회 (최신순)"""
        stmt = (
            select(GradeChangeLog)
            .where(GradeChangeLog.user_id == user_id)
            .order_by(desc(GradeChangeLog.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_users(self) -> List[User]:
        """ACTIVE 상태인 모든 사용자 조회"""
        stmt = (
            select(User)
            .where(User.user_status == "ACTIVE")
            .order_by(User.user_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_previous_month_payment_totals(
        self,
        year: int,
        month: int
    ) -> List[Tuple[str, int]]:
        """전월 결제 금액 합산 조회 (SUCCESS 상태만)

        Args:
            year: 대상 연도
            month: 대상 월

        Returns:
            List[(user_id, total_amount)]
        """
        # 전월 시작일/종료일 계산
        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=KST)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=KST)
        else:
            end_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=KST)

        # 사용자별 결제 금액 합산 쿼리
        stmt = (
            select(
                Payment.user_id,
                func.coalesce(func.sum(Payment.amount), 0).label("total_amount")
            )
            .where(
                and_(
                    Payment.payment_status == "SUCCESS",
                    Payment.paid_at >= start_date,
                    Payment.paid_at < end_date
                )
            )
            .group_by(Payment.user_id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()
        return [(row.user_id, int(row.total_amount)) for row in rows]

    async def get_all_grades_ordered_by_amount(self) -> List[Grade]:
        """등급 목록 조회 (min_purchase_amount DESC 정렬)

        높은 금액 기준의 등급부터 순회하여 매칭하기 위해 내림차순 정렬
        """
        stmt = (
            select(Grade)
            .where(Grade.is_active == True)
            .order_by(desc(Grade.min_purchase_amount))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_lowest_grade(self) -> Optional[Grade]:
        """가장 낮은 등급 조회 (기본 등급)"""
        stmt = (
            select(Grade)
            .where(Grade.is_active == True)
            .order_by(asc(Grade.min_purchase_amount))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_grade(
        self,
        user_id: str,
        grade_code: str
    ) -> bool:
        """사용자 등급 업데이트"""
        from sqlalchemy import update
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                grade_code=grade_code,
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def bulk_update_user_grades(
        self,
        updates: List[Tuple[str, str]]
    ) -> int:
        """사용자 등급 대량 업데이트

        Args:
            updates: [(user_id, new_grade_code), ...]

        Returns:
            업데이트된 사용자 수
        """
        from sqlalchemy import update

        if not updates:
            return 0

        updated_count = 0
        now = datetime.now(KST)

        for user_id, grade_code in updates:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(
                    grade_code=grade_code,
                    updated_at=now
                )
                .execution_options(synchronize_session="evaluate")
            )
            result = await self.db.execute(stmt)
            updated_count += result.rowcount

        return updated_count

    async def get_batch_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        change_reason: str = "AUTO_BATCH"
    ) -> List[GradeChangeLog]:
        """기간별 배치 로그 조회"""
        stmt = (
            select(GradeChangeLog)
            .where(
                and_(
                    GradeChangeLog.change_reason == change_reason,
                    GradeChangeLog.created_at >= start_date,
                    GradeChangeLog.created_at <= end_date
                )
            )
            .order_by(desc(GradeChangeLog.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
