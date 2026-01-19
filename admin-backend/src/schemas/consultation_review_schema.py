"""
상담 후기 스키마
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConsultationReviewItem(BaseModel):
    """상담 후기 응답 아이템"""

    review_id: int
    session_id: int
    user_id: str
    user_nickname: str  # JOIN으로 가져온 사용자 닉네임
    counselor_id: str
    counselor_nickname: str  # JOIN으로 가져온 상담사 닉네임
    rating: int
    content: Optional[str] = None
    counselor_reply: Optional[str] = None
    review_tags: Optional[str] = None
    is_best: bool
    is_visible: bool
    like_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    counselor_replied_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsultationReviewListParams(BaseModel):
    """상담 후기 목록 조회 파라미터"""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search_type: str = Field(default="all", description="검색 타입: all|content|reply_content")
    search_name: Optional[str] = Field(None, description="검색 키워드")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    counselor_id: Optional[str] = Field(None, description="상담사 ID")
    start_dt: Optional[str] = Field(None, description="검색 시작일 (yyyy-mm-dd)")
    end_dt: Optional[str] = Field(None, description="검색 종료일 (yyyy-mm-dd)")


class ConsultationReviewUpdateRequest(BaseModel):
    """상담 후기 수정 요청"""

    content: Optional[str] = Field(None, description="후기 내용")
    counselor_reply: Optional[str] = Field(None, description="상담사 답변")
    is_visible: Optional[bool] = Field(None, description="노출 여부")
    is_best: Optional[bool] = Field(None, description="베스트 여부")
    rating: Optional[int] = Field(None, ge=1, le=5, description="별점 (1-5)")
    review_tags: Optional[str] = Field(None, description="후기 태그 (JSON 문자열)")


class ConsultationReviewCreateRequest(BaseModel):
    """더미 상담 후기 생성 요청"""

    user_id: str = Field(..., description="사용자 ID")
    user_nickname: str = Field(..., description="사용자 닉네임 (표시용)")
    counselor_id: str = Field(..., description="상담사 ID")
    rating: int = Field(..., ge=1, le=5, description="별점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    counselor_reply: Optional[str] = Field(None, description="상담사 답변")
    review_tags: Optional[str] = Field(None, description="후기 태그 (JSON 문자열)")
    is_visible: bool = Field(True, description="노출 여부")
    is_best: bool = Field(False, description="베스트 여부")