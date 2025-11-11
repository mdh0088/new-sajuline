"""
알림 로그 레포지토리
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.models.notification_model import NotificationLog


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_logs_by_user(self, user_id: str) -> List[NotificationLog]:
        stmt = (
            select(NotificationLog)
            .where(
                NotificationLog.recipient_type == "USER",
                NotificationLog.recipient_id == user_id,
            )
            .order_by(desc(NotificationLog.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())






























