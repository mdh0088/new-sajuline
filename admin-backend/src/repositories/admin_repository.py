"""
관리자 Repository - t_admin 접근
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.admin_model import Admin


class AdminRepository:
    """관리자 데이터 접근 레이어"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, admin_id: str) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.admin_id == admin_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_login_id(self, login_id: str) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.login_id == login_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login(self, admin_id: str) -> bool:
        from datetime import datetime

        stmt = (
            update(Admin)
            .where(Admin.admin_id == admin_id)
            .values(last_login_at=datetime.utcnow(), updated_at=datetime.utcnow())
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0


