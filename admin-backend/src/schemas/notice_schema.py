"""
공지사항(Notice) 스키마
"""
from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel, Field, ConfigDict


class NoticeListParams(BaseModel):
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    search_type: str = Field(default="all", description="검색: all|title|content")
    search_name: Optional[str] = Field(default=None, description="검색 키워드")
    target_audience: Optional[str] = Field(default=None, description="ALL|USER|COUNSELOR")
    notice_type: Optional[str] = Field(default=None, description="공지 타입 (예: GENERAL)")
    is_important: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    start_dt: Optional[str] = Field(default=None, description="등록일 시작 yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="등록일 종료 yyyy-mm-dd")


class NoticeListItem(BaseModel):
    notice_id: int
    notice_type: str
    target_audience: str
    title: str
    is_important: bool
    is_active: bool
    view_count: int
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoticeListResponse(BaseModel):
    items: List[NoticeListItem]
    total: int


class NoticeDetailResponse(BaseModel):
    notice: NoticeListItem


class NoticeCreateRequest(BaseModel):
    notice_type: Optional[str] = Field(default="GENERAL")
    title: str
    content: str
    target_audience: Optional[str] = Field(default="ALL")
    is_important: bool = Field(default=False)


class NoticeUpdateRequest(BaseModel):
    notice_id: int
    notice_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    target_audience: Optional[str] = None
    is_important: Optional[bool] = None


class NoticeDeleteResponse(BaseModel):
    notice_id: int
    deleted: bool


