"""
Notification Log Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from src.models.notification_log_model import RecipientType, SendStatus
from src.models.notification_template_model import NotificationChannel


class NotificationLogBase(BaseModel):
    """Base schema for Notification Log"""
    recipient_type: RecipientType = Field(..., description="Recipient type: USER, COUNSELOR")
    recipient_id: str = Field(..., min_length=1, max_length=100, description="Recipient ID")
    channel: NotificationChannel = Field(..., description="Channel: KAKAO, SMS, EMAIL, PUSH")
    template_id: Optional[int] = Field(None, description="Template ID")
    title: Optional[str] = Field(None, max_length=200, description="Title")
    content: str = Field(..., min_length=1, description="Content")
    variables: Optional[Dict[str, Any]] = Field(None, description="Template variables (JSON)")


class NotificationLogCreate(NotificationLogBase):
    """Schema for creating Notification Log"""
    pass


class NotificationLogResponse(NotificationLogBase):
    """Schema for Notification Log response"""
    log_id: int = Field(..., description="Log ID")
    send_status: SendStatus = Field(..., description="Send status: PENDING, SUCCESS, FAILED")
    provider_response: Optional[Dict[str, Any]] = Field(None, description="Provider response (JSON)")
    sent_at: Optional[datetime] = Field(None, description="Sent at")
    read_at: Optional[datetime] = Field(None, description="Read at")
    failed_reason: Optional[str] = Field(None, description="Failed reason")
    retry_count: int = Field(..., description="Retry count")
    created_at: datetime = Field(..., description="Created at")

    model_config = ConfigDict(from_attributes=True)


class KakaoAlimTalkSendRequest(BaseModel):
    """Schema for Kakao AlimTalk send request"""
    template_code: str = Field(..., description="Template code")
    recipient_phone: str = Field(..., description="Recipient phone number")
    variables: Optional[Dict[str, str]] = Field(None, description="Template variables")
    recipient_id: Optional[str] = Field(None, description="Recipient ID (optional)")
    recipient_type: RecipientType = Field(default=RecipientType.USER, description="Recipient type")


class KakaoAlimTalkSendResponse(BaseModel):
    """Schema for Kakao AlimTalk send response"""
    success: bool = Field(..., description="Send success")
    log_id: int = Field(..., description="Log ID")
    message: str = Field(..., description="Response message")
    code: Optional[str] = Field(None, description="Response code")
