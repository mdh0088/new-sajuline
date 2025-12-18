"""
Notification Repository Layer
Data access logic for notification templates and logs
"""
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

KST = ZoneInfo("Asia/Seoul")
from sqlalchemy import select, update

from src.models.notification_template_model import NotificationTemplate
from src.models.notification_log_model import NotificationLog, RecipientType, SendStatus
from src.models.notification_template_model import NotificationChannel
from src.common.logging import logger, get_logger_with_request_id


class NotificationRepository:
    """Notification Repository"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================
    # NotificationTemplate Read Operations
    # ==========================================

    @logger.catch(reraise=True)
    async def get_template_by_code(self, template_code: str) -> Optional[NotificationTemplate]:
        """Get template by code"""
        log = get_logger_with_request_id()
        log.info("Looking up template by code", template_code=template_code)

        stmt = select(NotificationTemplate).where(NotificationTemplate.template_code == template_code)
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()

        log.info("Template lookup by code completed", template_code=template_code, found=template is not None)
        return template

    # ==========================================
    # NotificationLog Operations
    # ==========================================

    @logger.catch(reraise=True)
    async def create_log(
        self,
        recipient_type: RecipientType,
        recipient_id: str,
        channel: NotificationChannel,
        content: str,
        template_id: Optional[int] = None,
        title: Optional[str] = None,
        variables: Optional[dict] = None,
    ) -> NotificationLog:
        """Create notification log"""
        log = get_logger_with_request_id()
        log.info("Creating notification log", recipient_id=recipient_id, channel=channel)

        notification_log = NotificationLog(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            channel=channel,
            template_id=template_id,
            title=title,
            content=content,
            variables=variables,
            send_status=SendStatus.PENDING,
        )

        self.db.add(notification_log)
        await self.db.flush()
        await self.db.refresh(notification_log)

        log.info("Notification log created", log_id=notification_log.log_id)
        return notification_log

    @logger.catch(reraise=True)
    async def update_log_status(
        self,
        log_id: int,
        send_status: SendStatus,
        provider_response: Optional[dict] = None,
        failed_reason: Optional[str] = None,
        increment_retry: bool = False,
    ) -> bool:
        """Update log status (success/failed)"""
        log = get_logger_with_request_id()
        log.info("Updating log status", log_id=log_id, send_status=send_status)

        update_dict = {
            "send_status": send_status,
        }

        # Set sent_at on success
        if send_status == SendStatus.SUCCESS:
            update_dict["sent_at"] = datetime.now(KST)

        # Set failed_reason on failure
        if send_status == SendStatus.FAILED and failed_reason:
            update_dict["failed_reason"] = failed_reason

        # Increment retry count
        if increment_retry:
            # Get current retry count
            stmt_select = select(NotificationLog.retry_count).where(NotificationLog.log_id == log_id)
            result = await self.db.execute(stmt_select)
            current_retry = result.scalar_one_or_none()
            if current_retry is not None:
                update_dict["retry_count"] = current_retry + 1

        # Set provider response
        if provider_response:
            update_dict["provider_response"] = provider_response

        stmt = (
            update(NotificationLog)
            .where(NotificationLog.log_id == log_id)
            .values(**update_dict)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        updated = result.rowcount > 0

        log.info("Log status updated", log_id=log_id, send_status=send_status, updated=updated)
        return updated
