"""
배너(Banner) Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class BannerItem(BaseModel):
    banner_id: int
    banner_code: str
    banner_name: str
    banner_type: str
    image_url: str
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    link_target: str
    display_order: int
    is_active: bool
    valid_from: datetime
    valid_until: datetime
    click_count: int
    impression_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BannerListResponse(BaseModel):
    items: List[BannerItem]
    total: int


class BannerCreateRequest(BaseModel):
    banner_name: str
    banner_type: str
    link_url: Optional[str] = None
    link_target: str = Field(default="SELF")
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    valid_from: datetime
    valid_until: datetime
    # 서버에서 업로드된 파일명을 직접 지정하고 싶을 때 사용 (이미지 업로드 없을 경우)
    image_url: Optional[str] = None


class BannerUpdateRequest(BaseModel):
    banner_id: int = Field(..., description="수정 대상 PK")
    banner_name: Optional[str] = None
    banner_type: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    link_target: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class BannerDeleteResponse(BaseModel):
    banner_id: int
    deleted: bool


