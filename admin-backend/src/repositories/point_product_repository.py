"""
PointProductRepository - t_point_product 접근 레이어
"""
from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, func, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.point_product_model import PointProduct


class PointProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[PointProduct]:
        stmt = select(PointProduct).order_by(PointProduct.display_order, PointProduct.product_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        stmt = select(func.count(PointProduct.product_id))
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def create(self, **fields) -> PointProduct:
        stmt = insert(PointProduct).values(**fields)
        await self.db.execute(stmt)
        # 생성된 레코드 재조회 (product_code는 unique)
        result = await self.db.execute(
            select(PointProduct).where(PointProduct.product_code == fields["product_code"])  # type: ignore[index]
        )
        return result.scalar_one()

    async def get_by_id(self, product_id: int) -> Optional[PointProduct]:
        stmt = select(PointProduct).where(PointProduct.product_id == product_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def partial_update(self, product_id: int, **fields) -> bool:
        if not fields:
            return False
        fields["updated_at"] = datetime.utcnow()
        stmt = (
            update(PointProduct)
            .where(PointProduct.product_id == product_id)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0



