"""
Notification Template Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from src.models.notification_template_model import NotificationChannel


class NotificationTemplateBase(BaseModel):
    """Base schema for Notification Template"""
    template_code: str = Field(..., min_length=1, max_length=50, description="Template code")
    template_name: str = Field(..., min_length=1, max_length=100, description="Template name")
    channel: NotificationChannel = Field(..., description="Channel: KAKAO, SMS, EMAIL, PUSH")
    content_template: str = Field(..., min_length=1, description="Content template")
    variables: Optional[Dict[str, Any]] = Field(None, description="Template variables (JSON)")
    button_info: Optional[Dict[str, Any]] = Field(None, description="Button info (JSON)")
    is_active: bool = Field(True, description="Active status")


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating Notification Template"""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating Notification Template"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=100)
    content_template: Optional[str] = Field(None, min_length=1)
    variables: Optional[Dict[str, Any]] = None
    button_info: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema for Notification Template response"""
    template_id: int = Field(..., description="Template ID")
    created_at: datetime = Field(..., description="Created at")
    updated_at: Optional[datetime] = Field(None, description="Updated at")

    model_config = ConfigDict(from_attributes=True)
