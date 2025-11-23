"""
알림 로그 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class NotificationLogItem(BaseModel):
    log_id: int
    recipient_type: str
    recipient_id: str
    channel: str
    template_id: Optional[int] = None
    title: Optional[str] = None
    content: str
    variables: Optional[dict] = None
    send_status: str
    provider_response: Optional[dict] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    retry_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationLogListResponse(BaseModel):
    logs: List[NotificationLogItem]






































