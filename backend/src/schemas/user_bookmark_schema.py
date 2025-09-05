"""
사용자 북마크 관련 Pydantic 스키마
"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserBookmarkBase(BaseModel):
    """사용자 북마크 기본 스키마"""
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    counselor_id: str = Field(..., min_length=1, max_length=100, description="상담사 ID")


class UserBookmarkCreate(UserBookmarkBase):
    """사용자 북마크 생성 요청 스키마"""
    pass


class UserBookmarkResponse(UserBookmarkBase):
    """사용자 북마크 응답 스키마"""
    bookmark_id: int = Field(..., description="북마크 ID")
    created_at: datetime = Field(..., description="등록일")
    
    model_config = ConfigDict(from_attributes=True)


class UserBookmarkCount(BaseModel):
    """사용자별 북마크 수 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    bookmark_count: int = Field(..., ge=0, description="북마크 수")


class UserBookmarkListResponse(BaseModel):
    """사용자 북마크 목록 응답 스키마"""
    bookmarks: list[UserBookmarkResponse] = Field(..., description="북마크 목록")
    total: int = Field(..., description="전체 북마크 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")