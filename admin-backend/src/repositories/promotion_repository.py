"""
PromotionRepository - t_event 접근 레이어
"""
from typing import List, Optional

from sqlalchemy import select, func, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event_model import Event


class PromotionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Event]:
        stmt = select(Event).order_by(Event.valid_from.desc(), Event.event_id.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        stmt = select(func.count(Event.event_id))
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        stmt = select(Event).where(Event.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **fields) -> Event:
        stmt = insert(Event).values(**fields)
        await self.db.execute(stmt)
        result = await self.db.execute(select(Event).where(Event.event_code == fields["event_code"]))
        return result.scalar_one()

    async def partial_update(self, event_id: int, **fields) -> bool:
        if not fields:
            return False
        stmt = (
            update(Event)
            .where(Event.event_id == event_id)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_id(self, event_id: int) -> bool:
        stmt = delete(Event).where(Event.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0


