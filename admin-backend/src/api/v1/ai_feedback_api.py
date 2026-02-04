"""
AI 피드백 분석 API 엔드포인트.

Stories: STORY-5-3
FRs: FR-027
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies.rate_limit import rate_limit_dependency
from src.common.logging import get_logger
from src.common.utils.auth_utils import get_current_admin
from src.core.database import get_db
from src.models.admin_model import Admin
from src.schemas.ai.feedback_analytics_schema import (
    FeedbackStatsResponse,
    FeedbackTrendsResponse,
    LowScoreFeedbackResponse,
)
from src.services.ai.security.rbac import AIPermission, check_ai_permission
from src.services.ai.services.feedback_analytics_service import (
    FeedbackAnalyticsService,
)
from src.services.ai.utils.auth_logger import log_ai_access

logger = get_logger(__name__)

router = APIRouter(prefix="/ai/feedback", tags=["AI Feedback"])


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    start_date: date | None = Query(None, description="조회 시작일"),
    end_date: date | None = Query(None, description="조회 종료일"),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    db: AsyncSession = Depends(get_db),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> FeedbackStatsResponse:
    """
    피드백 통계 조회

    평균 점수, 별점 분포, 코멘트 비율 등의 통계를 제공합니다.

    Args:
        start_date: 조회 시작일 (선택)
        end_date: 조회 종료일 (선택)
        admin: 인증된 관리자
        permission: AI 권한 정보
        db: 데이터베이스 세션
        _rate_limit: Rate Limit 체크

    Returns:
        FeedbackStatsResponse: 피드백 통계
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/feedback/stats",
        status="success",
    )

    service = FeedbackAnalyticsService(db=db)
    stats = await service.get_stats(start_date=start_date, end_date=end_date)

    logger.info(
        "feedback_stats_retrieved",
        extra={
            "admin_id": admin.admin_id,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
            "total_count": stats.total_count,
            "average_rating": stats.average_rating,
        },
    )

    return stats


@router.get("/low-score", response_model=LowScoreFeedbackResponse)
async def get_low_score_feedback(
    threshold: int = Query(
        default=2, ge=1, le=5, description="점수 임계값 (이하 조회)"
    ),
    limit: int = Query(default=20, le=100, description="조회 개수"),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    db: AsyncSession = Depends(get_db),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> LowScoreFeedbackResponse:
    """
    낮은 점수 피드백 목록 조회

    AI 성능 개선을 위해 낮은 점수를 받은 피드백을 조회합니다.

    Args:
        threshold: 점수 임계값 (이하 조회)
        limit: 조회 개수 (최대 100)
        admin: 인증된 관리자
        permission: AI 권한 정보
        db: 데이터베이스 세션
        _rate_limit: Rate Limit 체크

    Returns:
        LowScoreFeedbackResponse: 낮은 점수 피드백 목록
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/feedback/low-score",
        status="success",
    )

    service = FeedbackAnalyticsService(db=db)
    feedbacks = await service.get_low_score_feedbacks(
        threshold=threshold, limit=limit
    )

    logger.info(
        "low_score_feedback_retrieved",
        extra={
            "admin_id": admin.admin_id,
            "threshold": threshold,
            "count": len(feedbacks),
        },
    )

    return LowScoreFeedbackResponse(
        feedbacks=feedbacks, total_count=len(feedbacks), threshold=threshold
    )


@router.get("/export")
async def export_feedback(
    start_date: date | None = Query(None, description="조회 시작일"),
    end_date: date | None = Query(None, description="조회 종료일"),
    format: str = Query(
        default="csv", regex="^(csv|json)$", description="내보내기 형식"
    ),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    db: AsyncSession = Depends(get_db),
    _rate_limit: Admin = Depends(rate_limit_dependency),
):
    """
    피드백 데이터 내보내기

    분석을 위해 피드백 데이터를 CSV 또는 JSON 형식으로 내보냅니다.

    Args:
        start_date: 조회 시작일 (선택)
        end_date: 조회 종료일 (선택)
        format: 내보내기 형식 (csv, json)
        admin: 인증된 관리자
        permission: AI 권한 정보
        db: 데이터베이스 세션
        _rate_limit: Rate Limit 체크

    Returns:
        StreamingResponse | JSONResponse: 내보내기 데이터
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/feedback/export",
        status="success",
    )

    service = FeedbackAnalyticsService(db=db)
    data = await service.export_feedbacks(
        start_date=start_date, end_date=end_date, format=format
    )

    logger.info(
        "feedback_exported",
        extra={
            "admin_id": admin.admin_id,
            "format": format,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        },
    )

    if format == "csv":
        return StreamingResponse(
            iter([data]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=feedback_export.csv"
            },
        )

    return JSONResponse(content={"feedbacks": data})


@router.get("/trends", response_model=FeedbackTrendsResponse)
async def get_feedback_trends(
    period: str = Query(
        default="daily",
        regex="^(daily|weekly|monthly)$",
        description="기간 타입",
    ),
    days: int = Query(default=30, le=90, description="조회할 일수"),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    db: AsyncSession = Depends(get_db),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> FeedbackTrendsResponse:
    """
    피드백 트렌드 조회

    시간에 따른 피드백 트렌드를 분석하여 품질 변화를 추적합니다.

    Args:
        period: 기간 타입 (daily, weekly, monthly)
        days: 조회할 일수 (최대 90일)
        admin: 인증된 관리자
        permission: AI 권한 정보
        db: 데이터베이스 세션
        _rate_limit: Rate Limit 체크

    Returns:
        FeedbackTrendsResponse: 피드백 트렌드
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/feedback/trends",
        status="success",
    )

    service = FeedbackAnalyticsService(db=db)
    trends = await service.get_trends(period=period, days=days)

    logger.info(
        "feedback_trends_retrieved",
        extra={
            "admin_id": admin.admin_id,
            "period": period,
            "days": days,
            "total_count": trends.total_count,
        },
    )

    return trends
