"""
알림톡 발송 대기 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NotificationWaitBase(BaseModel):
    """알림 대기 기본 스키마"""
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    counselor_id: str = Field(..., min_length=1, max_length=100, description="상담사 ID")


class NotificationWaitCreate(BaseModel):
    """알림 대기 생성 요청 스키마 (프론트엔드에서 counselor_id만 전달)"""
    counselor_id: str = Field(..., min_length=1, max_length=100, description="상담사 ID")


class NotificationWaitResponse(NotificationWaitBase):
    """알림 대기 응답 스키마"""
    wait_idx: int = Field(..., description="대기 ID")
    is_send: bool = Field(..., description="발송 유무")
    created_at: datetime = Field(..., description="등록일")

    model_config = ConfigDict(from_attributes=True)


class NotificationWaitCheckResponse(BaseModel):
    """알림 대기 등록 여부 응답 스키마"""
    is_registered: bool = Field(..., description="알림 대기 등록 여부")
    wait_idx: Optional[int] = Field(None, description="대기 ID (등록된 경우)")


class NotificationWaitListResponse(BaseModel):
    """알림 대기 목록 응답 스키마"""
    items: list[NotificationWaitResponse] = Field(..., description="알림 대기 목록")
    total: int = Field(..., ge=0, description="전체 개수")
    page: int = Field(..., ge=1, description="현재 페이지")
    limit: int = Field(..., ge=1, description="페이지당 항목 수")
