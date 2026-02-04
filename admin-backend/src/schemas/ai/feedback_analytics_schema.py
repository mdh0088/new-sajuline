"""
피드백 분석 관련 스키마.

피드백 통계, 트렌드 분석, 내보내기 기능을 위한 응답 모델입니다.

Stories: STORY-5-3
FRs: FR-027
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class RatingDistribution(BaseModel):
    """별점 분포."""

    rating: int = Field(..., ge=1, le=5, description="별점 (1-5)")
    count: int = Field(..., ge=0, description="해당 별점 개수")
    percentage: float = Field(..., ge=0, le=100, description="비율 (%)")


class FeedbackStatsResponse(BaseModel):
    """피드백 통계 응답."""

    total_count: int = Field(..., ge=0, description="전체 피드백 수")
    average_rating: float = Field(..., ge=0, le=5, description="평균 별점")
    rating_distribution: list[RatingDistribution] = Field(
        ..., description="별점 분포"
    )
    feedback_with_comments: int = Field(..., ge=0, description="코멘트가 있는 피드백 수")
    feedback_with_comments_pct: float = Field(
        ..., ge=0, le=100, description="코멘트 비율 (%)"
    )
    period_start: date | None = Field(None, description="조회 기간 시작일")
    period_end: date | None = Field(None, description="조회 기간 종료일")


class LowScoreFeedbackItem(BaseModel):
    """낮은 점수 피드백 항목."""

    id: int = Field(..., description="피드백 ID")
    query_id: str = Field(..., description="질의 ID")
    question: str | None = Field(None, description="원본 질문")
    rating: int = Field(..., ge=1, le=5, description="별점")
    comment: str | None = Field(None, description="피드백 코멘트")
    admin_id: str = Field(..., description="관리자 ID")  # Admin.admin_id는 String(100)
    created_at: datetime = Field(..., description="생성 시각")


class LowScoreFeedbackResponse(BaseModel):
    """낮은 점수 피드백 목록 응답."""

    feedbacks: list[LowScoreFeedbackItem] = Field(..., description="피드백 목록")
    total_count: int = Field(..., ge=0, description="전체 개수")
    threshold: int = Field(..., ge=1, le=5, description="점수 임계값")


class TrendPoint(BaseModel):
    """트렌드 데이터 포인트."""

    date: str = Field(..., description="날짜 (YYYY-MM-DD 또는 YYYY-MM)")
    count: int = Field(..., ge=0, description="피드백 수")
    average_rating: float = Field(..., ge=0, le=5, description="평균 별점")


class FeedbackTrendsResponse(BaseModel):
    """피드백 트렌드 응답."""

    period: str = Field(
        ..., description="기간 타입 (daily, weekly, monthly)"
    )
    data_points: list[TrendPoint] = Field(..., description="트렌드 데이터")
    total_count: int = Field(..., ge=0, description="전체 피드백 수")
    overall_average: float = Field(..., ge=0, le=5, description="전체 평균 별점")
