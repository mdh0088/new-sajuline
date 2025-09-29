"""
BannerRepository - t_banner 접근 레이어
"""
from typing import List, Optional

from sqlalchemy import select, func, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.banner_model import Banner


class BannerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Banner]:
        stmt = select(Banner).order_by(Banner.display_order, Banner.banner_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        stmt = select(func.count(Banner.banner_id))
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def get_by_id(self, banner_id: int) -> Optional[Banner]:
        stmt = select(Banner).where(Banner.banner_id == banner_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, banner_code: str) -> Optional[Banner]:
        stmt = select(Banner).where(Banner.banner_code == banner_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **fields) -> Banner:
        stmt = insert(Banner).values(**fields)
        await self.db.execute(stmt)
        result = await self.db.execute(select(Banner).where(Banner.banner_code == fields["banner_code"]))
        return result.scalar_one()

    async def partial_update(self, banner_id: int, **fields) -> bool:
        if not fields:
            return False
        stmt = (
            update(Banner)
            .where(Banner.banner_id == banner_id)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_id(self, banner_id: int) -> bool:
        stmt = delete(Banner).where(Banner.banner_id == banner_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0


