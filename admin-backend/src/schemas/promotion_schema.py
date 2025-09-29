"""
프로모션(기획전) Pydantic 스키마 - t_event 기반
"""
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field, ConfigDict


class PromotionItem(BaseModel):
    event_id: int
    event_code: str
    event_name: str
    event_type: str
    description: Optional[str] = None
    terms: Optional[str] = None
    banner_image_url: Optional[str] = None
    reward_type: str
    reward_value: int
    max_participants: Optional[int] = None
    current_participants: int
    is_active: bool
    valid_from: datetime
    valid_until: datetime
    # ORM 속성명(metadata_json) ↔ 응답 필드(metadata) 매핑
    metadata: Optional[Any] = Field(default=None, alias="metadata_json")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PromotionListResponse(BaseModel):
    items: List[PromotionItem]
    total: int


class PromotionCreateRequest(BaseModel):
    event_name: str
    event_type: str
    description: Optional[str] = None
    terms: Optional[str] = None
    reward_type: str
    reward_value: int
    max_participants: Optional[int] = None
    is_active: bool = Field(default=True)
    valid_from: datetime
    valid_until: datetime
    metadata: Optional[Any] = None
    banner_image_url: Optional[str] = None


class PromotionUpdateRequest(BaseModel):
    event_id: int
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    terms: Optional[str] = None
    reward_type: Optional[str] = None
    reward_value: Optional[int] = None
    max_participants: Optional[int] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    metadata: Optional[Any] = None
    banner_image_url: Optional[str] = None


class PromotionDeleteResponse(BaseModel):
    event_id: int
    deleted: bool
