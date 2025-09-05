"""
상담 후기 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, validator


class ConsultationReviewBase(BaseModel):
    """상담 후기 기본 스키마"""
    session_id: int = Field(..., description="상담 세션 ID")
    user_id: str = Field(..., description="사용자 ID")
    counselor_id: str = Field(..., description="상담사 ID")
    rating: int = Field(..., ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    is_visible: bool = Field(default=True, description="공개 여부")


class ConsultationReviewCreate(ConsultationReviewBase):
    """상담 후기 생성 요청 스키마"""
    pass


class ConsultationReviewUpdate(BaseModel):
    """상담 후기 수정 요청 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
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


class ConsultationReviewSummary(BaseModel):
    """상담 후기 요약 정보 (목록 조회용)"""
    review_id: int = Field(..., description="후기 ID")
    user_id: str = Field(..., description="사용자 ID")
    counselor_id: str = Field(..., description="상담사 ID")
    rating: int = Field(..., description="평점 (1-5)")
    content: Optional[str] = Field(None, description="후기 내용")
    is_best: bool = Field(..., description="베스트 후기")
    like_count: int = Field(..., description="좋아요 수")
    created_at: datetime = Field(..., description="생성일시")
    has_reply: bool = Field(..., description="상담사 답변 여부")
    
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