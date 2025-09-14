"""
상담 후기 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
import json


class ConsultationReviewBase(BaseModel):
    """상담 후기 기본 스키마"""
    session_id: int = Field(..., description="상담 세션 ID")
    user_id: str = Field(..., description="사용자 ID")
    counselor_id: str = Field(..., description="상담사 ID")
    rating: int = Field(..., ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    review_tags: Optional[List[str]] = Field(default=None, description="리뷰 태그 배열")
    is_visible: bool = Field(default=True, description="공개 여부")


class ConsultationReviewCreate(ConsultationReviewBase):
    """상담 후기 생성 요청 스키마"""
    pass


class ConsultationReviewUpdate(BaseModel):
    """상담 후기 수정 요청 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    review_tags: Optional[List[str]] = Field(None, description="리뷰 태그 배열")
    is_visible: Optional[bool] = Field(None, description="공개 여부")


class CounselorReplyCreate(BaseModel):
    """상담사 답변 생성 요청 스키마"""
    counselor_reply: str = Field(..., min_length=1, description="상담사 답변")


class ConsultationReviewResponse(ConsultationReviewBase):
    """상담 후기 응답 스키마"""
    review_id: int = Field(..., description="후기 ID")
    counselor_reply: Optional[str] = Field(None, description="상담사 답변")
    is_best: bool = Field(..., description="베스트 후기")
    like_count: int = Field(..., description="좋아요 수")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    counselor_replied_at: Optional[datetime] = Field(None, description="상담사 답변 일시")
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator("review_tags", mode="before")
    @classmethod
    def _coerce_review_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else None
            except Exception:
                return None
        return None


class ConsultationReviewSummary(BaseModel):
    """상담 후기 요약 정보 (목록 조회용)"""
    review_id: int = Field(..., description="후기 ID")
    user_id: str = Field(..., description="사용자 ID")
    counselor_id: str = Field(..., description="상담사 ID")
    rating: int = Field(..., description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    counselor_reply: Optional[str] = Field(None, description="상담사 답변")
    counselor_replied_at: Optional[datetime] = Field(None, description="상담사 답변 일시")
    is_best: bool = Field(..., description="베스트 후기")
    like_count: int = Field(..., description="좋아요 수")
    created_at: datetime = Field(..., description="생성일시")
    has_reply: bool = Field(False, description="상담사 답변 여부")
    
    model_config = ConfigDict(from_attributes=True)


class ConsultationReviewListResponse(BaseModel):
    """상담 후기 목록 응답 스키마"""
    reviews: list[ConsultationReviewSummary] = Field(..., description="후기 목록")
    total: int = Field(..., description="전체 후기 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


class UserReviewCountResponse(BaseModel):
    """사용자 후기 개수 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    review_count: int = Field(..., description="작성한 후기 수")
    visible_review_count: int = Field(..., description="공개 후기 수")


class UserReviewSummary(BaseModel):
    """/user/review 상단 요약 정보"""
    total_my_reviews: int = Field(..., description="작성한 후기 수 (is_visible=true)")
    total_pending_reviews: int = Field(..., description="작성 대기 수")
    average_rating: float = Field(..., description="평균 평점")
    earned_points: int = Field(..., description="받은 포인트 (작성한 후기 * 100)")


class CounselorBriefInfo(BaseModel):
    nickname: str | None = Field(None)
    profile_image_url: str | None = Field(None)


class UserReviewItem(BaseModel):
    """작성한 후기 목록 아이템"""
    review_id: int
    session_id: int
    rating: int
    content: str | None = None
    counselor_reply: str | None = None
    review_tags: list[str] | None = None
    is_best: bool
    created_at: datetime
    counselor_replied_at: datetime | None = None
    realchattm: int | None = None
    counselor: CounselorBriefInfo | None = None

    @field_validator("review_tags", mode="before")
    @classmethod
    def _coerce_user_item_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else None
            except Exception:
                return None
        return None


class UserReviewList(BaseModel):
    items: list[UserReviewItem]
    total: int
    page: int
    limit: int


class PendingReviewItem(BaseModel):
    """작성 대기 목록 아이템"""
    session_id: int
    starttm: str | None = None
    realchattm: int | None = None
    counselor: CounselorBriefInfo | None = None


class PendingReviewList(BaseModel):
    items: list[PendingReviewItem]
    total: int
    page: int
    limit: int


class UserReviewCreateRequest(BaseModel):
    """사용자 후기 생성 요청 (엔드포인트 입력용)"""
    session_id: int
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None
    review_tags: Optional[List[str]] = None


class UserReviewUpdateRequest(BaseModel):
    """사용자 후기 수정 요청 (세션 기준)"""
    session_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None
    review_tags: Optional[List[str]] = None