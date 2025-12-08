"""
알림톡 발송 대기 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete as sqla_delete

from src.models.notification_wait_model import NotificationWait
from src.common.logging import logger, get_logger_with_request_id


class NotificationWaitRepository:
    """알림톡 발송 대기 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def create(self, user_id: str, counselor_id: str) -> NotificationWait:
        """알림 대기 등록"""
        log = get_logger_with_request_id()
        log.info("Creating notification wait", user_id=user_id, counselor_id=counselor_id)

        notification_wait = NotificationWait(
            user_id=user_id,
            counselor_id=counselor_id,
            is_send=False
        )

        self.db.add(notification_wait)
        await self.db.flush()
        await self.db.refresh(notification_wait)

        log.info("Notification wait created", wait_idx=notification_wait.wait_idx)
        return notification_wait

    @logger.catch(reraise=True)
    async def exists(self, user_id: str, counselor_id: str) -> bool:
        """특정 사용자-상담사 알림 대기 존재 여부 확인 (미발송 건만)"""
        log = get_logger_with_request_id()
        log.info("Checking notification wait existence", user_id=user_id, counselor_id=counselor_id)

        stmt = (
            select(func.count(NotificationWait.wait_idx))
            .where(
                and_(
                    NotificationWait.user_id == user_id,
                    NotificationWait.counselor_id == counselor_id,
                    NotificationWait.is_send == False
                )
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar() or 0

        log.info("Notification wait existence check completed", exists=(count > 0))
        return count > 0

    @logger.catch(reraise=True)
    async def delete(self, user_id: str, counselor_id: str) -> int:
        """특정 사용자-상담사 알림 대기 삭제 (미발송 건만)"""
        log = get_logger_with_request_id()
        log.info("Deleting notification wait", user_id=user_id, counselor_id=counselor_id)

        stmt = (
            sqla_delete(NotificationWait)
            .where(
                and_(
                    NotificationWait.user_id == user_id,
                    NotificationWait.counselor_id == counselor_id,
                    NotificationWait.is_send == False
                )
            )
        )
        result = await self.db.execute(stmt)
        deleted_count = result.rowcount or 0

        log.info("Notification wait deleted", deleted_count=deleted_count)
        return deleted_count

    @logger.catch(reraise=True)
    async def get_list_by_counselor(self, counselor_id: str) -> list[NotificationWait]:
        """상담사별 미발송 알림 대기 목록 조회 (알림 발송 시 사용)"""
        log = get_logger_with_request_id()
        log.info("Getting notification wait list by counselor", counselor_id=counselor_id)

        stmt = (
            select(NotificationWait)
            .where(
                and_(
                    NotificationWait.counselor_id == counselor_id,
                    NotificationWait.is_send == False
                )
            )
            .order_by(NotificationWait.created_at.asc())
        )
        result = await self.db.execute(stmt)
        notifications = list(result.scalars().all())

        log.info("Notification wait list retrieved", counselor_id=counselor_id, count=len(notifications))
        return notifications

    @logger.catch(reraise=True)
    async def mark_all_as_sent(self, counselor_id: str) -> int:
        """상담사의 모든 미발송 알림 발송 완료 처리"""
        log = get_logger_with_request_id()
        log.info("Marking all notification waits as sent", counselor_id=counselor_id)

        stmt = (
            select(NotificationWait)
            .where(
                and_(
                    NotificationWait.counselor_id == counselor_id,
                    NotificationWait.is_send == False
                )
            )
        )
        result = await self.db.execute(stmt)
        notifications = list(result.scalars().all())

        count = 0
        for notification in notifications:
            notification.is_send = True
            count += 1

        if count > 0:
            await self.db.flush()

        log.info("All notification waits marked as sent", counselor_id=counselor_id, count=count)
        return count
