"""
알림 로그 서비스
"""
from typing import List

from src.repositories.notification_repository import NotificationRepository
from src.schemas.notification_schema import NotificationLogItem


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def get_user_logs(self, user_id: str) -> List[NotificationLogItem]:
        rows = await self.repo.find_logs_by_user(user_id)
        return [NotificationLogItem.model_validate(r, from_attributes=True) for r in rows]





























