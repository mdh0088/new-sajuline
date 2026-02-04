"""
피드백 분석 서비스.

피드백 통계, 트렌드 분석, 내보내기 기능을 제공합니다.

Stories: STORY-5-3
FRs: FR-027
"""

import csv
import io
from datetime import date, timedelta
from time import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import get_logger
from src.exceptions.custom_exceptions import BusinessException
from src.models.ai.ai_feedback_model import AIFeedback
from src.models.ai.ai_query_history_model import AIQueryHistory
from src.schemas.ai.feedback_analytics_schema import (
    FeedbackStatsResponse,
    FeedbackTrendsResponse,
    LowScoreFeedbackItem,
    RatingDistribution,
    TrendPoint,
)

logger = get_logger(__name__)


class FeedbackAnalyticsService:
    """피드백 분석 서비스."""

    def __init__(self, db: AsyncSession):
        """초기화.

        Args:
            db: 데이터베이스 세션
        """
        self.db = db

    async def get_stats(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> FeedbackStatsResponse:
        """피드백 통계 조회.

        Args:
            start_date: 조회 시작일 (Optional)
            end_date: 조회 종료일 (Optional)

        Returns:
            FeedbackStatsResponse: 피드백 통계

        Raises:
            BusinessException: 날짜 범위가 유효하지 않을 때
        """
        start_time = time()

        # 날짜 범위 검증
        if start_date and end_date and start_date > end_date:
            logger.warning(
                "invalid_date_range",
                extra={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                },
            )
            raise BusinessException(
                status_code=400,
                error_code="INVALID_DATE_RANGE",
                message="시작일이 종료일보다 늦을 수 없습니다",
            )

        try:
            query = select(AIFeedback)

            if start_date:
                query = query.where(AIFeedback.created_at >= start_date)
            if end_date:
                query = query.where(AIFeedback.created_at <= end_date)

            result = await self.db.execute(query)
            feedbacks = result.scalars().all()
        except Exception as e:
            logger.error(
                "feedback_stats_query_failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise BusinessException(
                status_code=500,
                error_code="DATABASE_ERROR",
                message="피드백 통계 조회 중 오류가 발생했습니다",
            )

        if not feedbacks:
            logger.info(
                "feedback_stats_no_data",
                extra={
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                },
            )
            return FeedbackStatsResponse(
                total_count=0,
                average_rating=0.0,
                rating_distribution=[],
                feedback_with_comments=0,
                feedback_with_comments_pct=0.0,
                period_start=start_date,
                period_end=end_date,
            )

        # 통계 계산
        total = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total
        with_comments = sum(1 for f in feedbacks if f.comment)

        # 분포 계산
        distribution: dict[int, int] = {}
        for f in feedbacks:
            distribution[f.rating] = distribution.get(f.rating, 0) + 1

        rating_dist = [
            RatingDistribution(
                rating=r, count=c, percentage=round(c / total * 100, 1)
            )
            for r, c in sorted(distribution.items())
        ]

        duration_ms = int((time() - start_time) * 1000)
        logger.info(
            "feedback_stats_computed",
            extra={
                "total_count": total,
                "average_rating": round(avg_rating, 2),
                "duration_ms": duration_ms,
            },
        )

        return FeedbackStatsResponse(
            total_count=total,
            average_rating=round(avg_rating, 2),
            rating_distribution=rating_dist,
            feedback_with_comments=with_comments,
            feedback_with_comments_pct=round(with_comments / total * 100, 1),
            period_start=start_date,
            period_end=end_date,
        )

    async def get_low_score_feedbacks(
        self, threshold: int = 2, limit: int = 20
    ) -> list[LowScoreFeedbackItem]:
        """낮은 점수 피드백 조회.

        Args:
            threshold: 점수 임계값 (이하 조회)
            limit: 최대 개수

        Returns:
            list[LowScoreFeedbackItem]: 낮은 점수 피드백 목록

        Raises:
            BusinessException: DB 조회 실패 시
        """
        start_time = time()

        try:
            # NOTE: AIQueryHistory.query_id에 인덱스 필요 (성능 최적화)
            query = (
                select(AIFeedback, AIQueryHistory.question)
                .outerjoin(
                    AIQueryHistory, AIFeedback.query_id == AIQueryHistory.query_id
                )
                .where(AIFeedback.rating <= threshold)
                .order_by(AIFeedback.created_at.desc())
                .limit(limit)
            )

            result = await self.db.execute(query)
            rows = result.all()

            feedbacks = [
                LowScoreFeedbackItem(
                    id=feedback.id,
                    query_id=feedback.query_id,
                    question=question,
                    rating=feedback.rating,
                    comment=feedback.comment,
                    admin_id=feedback.admin_id,
                    created_at=feedback.created_at,
                )
                for feedback, question in rows
            ]

            duration_ms = int((time() - start_time) * 1000)
            logger.info(
                "low_score_feedbacks_retrieved",
                extra={
                    "threshold": threshold,
                    "count": len(feedbacks),
                    "duration_ms": duration_ms,
                },
            )

            return feedbacks

        except Exception as e:
            logger.error(
                "low_score_feedbacks_query_failed",
                extra={"error": str(e), "threshold": threshold},
                exc_info=True,
            )
            raise BusinessException(
                status_code=500,
                error_code="DATABASE_ERROR",
                message="낮은 점수 피드백 조회 중 오류가 발생했습니다",
            )

    async def export_feedbacks(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        format: str = "csv",
    ) -> str | list[dict]:
        """피드백 내보내기.

        Args:
            start_date: 조회 시작일 (Optional)
            end_date: 조회 종료일 (Optional)
            format: 내보내기 형식 (csv, json)

        Returns:
            str | list[dict]: CSV 문자열 또는 JSON 데이터

        Raises:
            BusinessException: 날짜 범위 오류 또는 DB 조회 실패 시
        """
        start_time = time()

        # 날짜 범위 검증
        if start_date and end_date and start_date > end_date:
            logger.warning(
                "invalid_date_range_export",
                extra={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                },
            )
            raise BusinessException(
                status_code=400,
                error_code="INVALID_DATE_RANGE",
                message="시작일이 종료일보다 늦을 수 없습니다",
            )

        try:
            query = select(AIFeedback)

            if start_date:
                query = query.where(AIFeedback.created_at >= start_date)
            if end_date:
                query = query.where(AIFeedback.created_at <= end_date)

            query = query.order_by(AIFeedback.created_at.desc())
            result = await self.db.execute(query)
            feedbacks = result.scalars().all()

            if format == "json":
                data = [
                    {
                        "id": f.id,
                        "query_id": f.query_id,
                        "rating": f.rating,
                        "comment": f.comment,
                        "admin_id": f.admin_id,
                        "created_at": f.created_at.isoformat(),
                    }
                    for f in feedbacks
                ]

                duration_ms = int((time() - start_time) * 1000)
                logger.info(
                    "feedbacks_exported_json",
                    extra={"count": len(data), "duration_ms": duration_ms},
                )

                return data

            # CSV 형식 (UTF-8 BOM 추가 - Excel 호환성)
            output = io.StringIO()
            output.write("\ufeff")  # UTF-8 BOM for Excel
            writer = csv.writer(output)
            writer.writerow(
                ["ID", "Query ID", "Rating", "Comment", "Admin ID", "Created At"]
            )

            for f in feedbacks:
                writer.writerow(
                    [
                        f.id,
                        f.query_id,
                        f.rating,
                        f.comment or "",
                        f.admin_id,
                        f.created_at.isoformat(),
                    ]
                )

            csv_data = output.getvalue()

            duration_ms = int((time() - start_time) * 1000)
            logger.info(
                "feedbacks_exported_csv",
                extra={"count": len(feedbacks), "duration_ms": duration_ms},
            )

            return csv_data

        except BusinessException:
            raise
        except Exception as e:
            logger.error(
                "feedback_export_failed",
                extra={"error": str(e), "format": format},
                exc_info=True,
            )
            raise BusinessException(
                status_code=500,
                error_code="DATABASE_ERROR",
                message="피드백 내보내기 중 오류가 발생했습니다",
            )

    async def get_trends(
        self, period: str = "daily", days: int = 30
    ) -> FeedbackTrendsResponse:
        """피드백 트렌드 조회.

        Args:
            period: 기간 타입 (daily, weekly, monthly)
            days: 조회할 일수

        Returns:
            FeedbackTrendsResponse: 피드백 트렌드

        Raises:
            BusinessException: DB 조회 실패 시
        """
        start_time = time()
        start_date = date.today() - timedelta(days=days)

        try:
            query = (
                select(AIFeedback)
                .where(AIFeedback.created_at >= start_date)
                .order_by(AIFeedback.created_at)
            )

            result = await self.db.execute(query)
            feedbacks = result.scalars().all()

            # 기간별 그룹화
            grouped: dict[str, dict[str, int]] = {}
            for f in feedbacks:
                if period == "daily":
                    key = f.created_at.strftime("%Y-%m-%d")
                elif period == "weekly":
                    # 주의 시작일 (월요일)
                    week_start = f.created_at - timedelta(
                        days=f.created_at.weekday()
                    )
                    key = week_start.strftime("%Y-%m-%d")
                else:  # monthly
                    key = f.created_at.strftime("%Y-%m")

                if key not in grouped:
                    grouped[key] = {"count": 0, "total_rating": 0}
                grouped[key]["count"] += 1
                grouped[key]["total_rating"] += f.rating

            data_points = [
                TrendPoint(
                    date=k,
                    count=v["count"],
                    average_rating=round(v["total_rating"] / v["count"], 2),
                )
                for k, v in sorted(grouped.items())
            ]

            total_count = sum(p.count for p in data_points)
            overall_avg = (
                sum(p.average_rating * p.count for p in data_points) / total_count
                if total_count > 0
                else 0.0
            )

            duration_ms = int((time() - start_time) * 1000)
            logger.info(
                "feedback_trends_computed",
                extra={
                    "period": period,
                    "days": days,
                    "total_count": total_count,
                    "duration_ms": duration_ms,
                },
            )

            return FeedbackTrendsResponse(
                period=period,
                data_points=data_points,
                total_count=total_count,
                overall_average=round(overall_avg, 2),
            )

        except Exception as e:
            logger.error(
                "feedback_trends_query_failed",
                extra={"error": str(e), "period": period, "days": days},
                exc_info=True,
            )
            raise BusinessException(
                status_code=500,
                error_code="DATABASE_ERROR",
                message="피드백 트렌드 조회 중 오류가 발생했습니다",
            )
