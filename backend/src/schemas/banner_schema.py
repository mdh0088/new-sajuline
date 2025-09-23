"""
배너 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.banner_model import BannerType, LinkTarget


class BannerBase(BaseModel):
    banner_code: str = Field(..., min_length=1, max_length=50, description="배너 코드")
    banner_name: str = Field(..., min_length=1, max_length=100, description="배너명")
    banner_type: BannerType = Field(default=BannerType.MAIN, description="배너 타입")
    image_url: str = Field(..., max_length=500, description="이미지 URL")
    mobile_image_url: Optional[str] = Field(None, max_length=500, description="모바일 이미지 URL")
    link_url: Optional[str] = Field(None, max_length=500, description="링크 URL")
    link_target: LinkTarget = Field(default=LinkTarget.SELF, description="링크 타겟")
    display_order: int = Field(default=0, ge=0, description="노출 순서")
    is_active: bool = Field(default=True, description="활성화 여부")
    valid_from: datetime = Field(..., description="시작일시")
    valid_until: datetime = Field(..., description="종료일시")


class BannerResponse(BannerBase):
    banner_id: int = Field(..., description="배너 ID")
    click_count: int = Field(default=0, ge=0, description="클릭수")
    impression_count: int = Field(default=0, ge=0, description="노출수")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    model_config = ConfigDict(from_attributes=True)


