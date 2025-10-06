"""
포인트 거래 레포지토리 (관리자)
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from src.models.point_transaction_model import PointTransaction


class PointTransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transaction(
        self,
        *,
        user_id: str,
        transaction_type: str,
        currency_type: str,
        amount: int,
        balance_after: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> PointTransaction:
        tx = PointTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            created_at=datetime.utcnow(),
        )
        self.db.add(tx)
        await self.db.flush()
        await self.db.refresh(tx)
        return tx

    async def find_mileage_use_logs(self, user_id: str) -> List[PointTransaction]:
        stmt = (
            select(PointTransaction)
            .where(
                PointTransaction.user_id == user_id,
                func.upper(PointTransaction.transaction_type) == "USE",
                PointTransaction.currency_type == "MILEAGE_PRODUCT",
            )
            .order_by(desc(PointTransaction.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_mileage_earn_logs(self, user_id: str) -> List[PointTransaction]:
        """마일리지 적립 내역 조회 (EARN, CHARGE, ADMIN 타입 포함)"""
        stmt = (
            select(PointTransaction)
            .where(
                PointTransaction.user_id == user_id,
                PointTransaction.amount > 0,  # 양수 금액만 (적립/충전/지급)
            )
            .order_by(desc(PointTransaction.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


