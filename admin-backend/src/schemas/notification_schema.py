"""
알림 로그 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class NotificationLogItem(BaseModel):
    notification_seq: int
    recipient_type: str
    recipient_id: str
    channel: str
    template_code: Optional[str] = None
    title: Optional[str] = None
    content: str
    status: str
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    retry_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationLogListResponse(BaseModel):
    logs: List[NotificationLogItem]





