"""
AI 피드백 분석 API 통합 테스트.

Stories: STORY-5-3
FRs: FR-027
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from src.main import app
from src.models.admin_model import Admin


@pytest.fixture
def mock_admin():
    """Mock 관리자 fixture."""
    admin = MagicMock(spec=Admin)
    admin.admin_id = "admin123"
    admin.role = "admin"
    admin.is_active = True
    return admin


@pytest.fixture
def mock_feedback_data():
    """Mock 피드백 데이터."""
    return [
        MagicMock(
            id=1,
            query_id="query-001",
            admin_id="admin123",
            rating=5,
            comment="Very good",
            created_at=datetime.now(),
        ),
        MagicMock(
            id=2,
            query_id="query-002",
            admin_id="admin123",
            rating=3,
            comment=None,
            created_at=datetime.now() - timedelta(days=1),
        ),
        MagicMock(
            id=3,
            query_id="query-003",
            admin_id="admin123",
            rating=1,
            comment="Bad response",
            created_at=datetime.now() - timedelta(days=2),
        ),
    ]


class TestFeedbackStatsAPI:
    """피드백 통계 API 테스트."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self, mock_admin, mock_feedback_data):
        """통계 조회 성공."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = MagicMock(
                total_count=3,
                average_rating=3.0,
                rating_distribution=[
                    MagicMock(rating=1, count=1, percentage=33.3),
                    MagicMock(rating=3, count=1, percentage=33.3),
                    MagicMock(rating=5, count=1, percentage=33.3),
                ],
                feedback_with_comments=2,
                feedback_with_comments_pct=66.7,
                period_start=None,
                period_end=None,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 3
            assert data["average_rating"] == 3.0

    @pytest.mark.asyncio
    async def test_get_stats_with_date_range(self, mock_admin):
        """날짜 범위로 통계 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = MagicMock(
                total_count=1,
                average_rating=5.0,
                rating_distribution=[MagicMock(rating=5, count=1, percentage=100.0)],
                feedback_with_comments=1,
                feedback_with_comments_pct=100.0,
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/stats",
                    params={"start_date": "2024-01-01", "end_date": "2024-01-31"},
                )

            assert response.status_code == 200
            mock_get_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stats_invalid_date_range(self, mock_admin):
        """잘못된 날짜 범위로 통계 조회."""
        from src.exceptions.custom_exceptions import BusinessException

        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_stats",
            side_effect=BusinessException(
                status_code=400,
                error_code="INVALID_DATE_RANGE",
                message="시작일이 종료일보다 늦을 수 없습니다",
            ),
        ):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/stats",
                    params={"start_date": "2024-12-31", "end_date": "2024-01-01"},
                )

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_stats_no_data(self, mock_admin):
        """데이터 없을 때 통계 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = MagicMock(
                total_count=0,
                average_rating=0.0,
                rating_distribution=[],
                feedback_with_comments=0,
                feedback_with_comments_pct=0.0,
                period_start=None,
                period_end=None,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 0


class TestLowScoreFeedbackAPI:
    """낮은 점수 피드백 API 테스트."""

    @pytest.mark.asyncio
    async def test_get_low_score_success(self, mock_admin):
        """낮은 점수 피드백 조회 성공."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_low_score_feedbacks"
        ) as mock_get_low:
            mock_get_low.return_value = [
                MagicMock(
                    id=1,
                    query_id="query-001",
                    question="Test question",
                    rating=1,
                    comment="Bad",
                    admin_id="admin123",
                    created_at=datetime.now(),
                )
            ]

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/low-score")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 1
            assert data["threshold"] == 2

    @pytest.mark.asyncio
    async def test_get_low_score_custom_threshold(self, mock_admin):
        """커스텀 임계값으로 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_low_score_feedbacks"
        ) as mock_get_low:
            mock_get_low.return_value = []

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/low-score", params={"threshold": 3, "limit": 50}
                )

            assert response.status_code == 200
            mock_get_low.assert_called_once_with(threshold=3, limit=50)

    @pytest.mark.asyncio
    async def test_get_low_score_empty(self, mock_admin):
        """낮은 점수 피드백이 없을 때."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_low_score_feedbacks"
        ) as mock_get_low:
            mock_get_low.return_value = []

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/low-score")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 0


class TestFeedbackExportAPI:
    """피드백 내보내기 API 테스트."""

    @pytest.mark.asyncio
    async def test_export_csv_success(self, mock_admin):
        """CSV 내보내기 성공."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.export_feedbacks"
        ) as mock_export:
            mock_export.return_value = "\ufeffID,Query ID,Rating,Comment,Admin ID,Created At\n1,query-001,5,Good,admin123,2024-01-01T00:00:00"

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/export", params={"format": "csv"}
                )

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert "\ufeff" in response.text  # UTF-8 BOM 확인

    @pytest.mark.asyncio
    async def test_export_json_success(self, mock_admin):
        """JSON 내보내기 성공."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.export_feedbacks"
        ) as mock_export:
            mock_export.return_value = [
                {
                    "id": 1,
                    "query_id": "query-001",
                    "rating": 5,
                    "comment": "Good",
                    "admin_id": "admin123",
                    "created_at": "2024-01-01T00:00:00",
                }
            ]

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/export", params={"format": "json"}
                )

            assert response.status_code == 200
            data = response.json()
            assert "feedbacks" in data
            assert len(data["feedbacks"]) == 1

    @pytest.mark.asyncio
    async def test_export_with_date_range(self, mock_admin):
        """날짜 범위로 내보내기."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.export_feedbacks"
        ) as mock_export:
            mock_export.return_value = []

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/export",
                    params={
                        "format": "json",
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-31",
                    },
                )

            assert response.status_code == 200
            mock_export.assert_called_once()


class TestFeedbackTrendsAPI:
    """피드백 트렌드 API 테스트."""

    @pytest.mark.asyncio
    async def test_get_trends_daily(self, mock_admin):
        """일별 트렌드 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_trends"
        ) as mock_get_trends:
            mock_get_trends.return_value = MagicMock(
                period="daily",
                data_points=[
                    MagicMock(date="2024-01-01", count=5, average_rating=4.2),
                    MagicMock(date="2024-01-02", count=3, average_rating=3.8),
                ],
                total_count=8,
                overall_average=4.05,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/trends", params={"period": "daily", "days": 7}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["period"] == "daily"
            assert data["total_count"] == 8

    @pytest.mark.asyncio
    async def test_get_trends_weekly(self, mock_admin):
        """주별 트렌드 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_trends"
        ) as mock_get_trends:
            mock_get_trends.return_value = MagicMock(
                period="weekly",
                data_points=[MagicMock(date="2024-01-01", count=10, average_rating=4.0)],
                total_count=10,
                overall_average=4.0,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/trends",
                    params={"period": "weekly", "days": 30},
                )

            assert response.status_code == 200
            mock_get_trends.assert_called_once_with(period="weekly", days=30)

    @pytest.mark.asyncio
    async def test_get_trends_monthly(self, mock_admin):
        """월별 트렌드 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_trends"
        ) as mock_get_trends:
            mock_get_trends.return_value = MagicMock(
                period="monthly",
                data_points=[MagicMock(date="2024-01", count=50, average_rating=4.1)],
                total_count=50,
                overall_average=4.1,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/ai/feedback/trends",
                    params={"period": "monthly", "days": 90},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["period"] == "monthly"

    @pytest.mark.asyncio
    async def test_get_trends_no_data(self, mock_admin):
        """데이터 없을 때 트렌드 조회."""
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ), patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_trends"
        ) as mock_get_trends:
            mock_get_trends.return_value = MagicMock(
                period="daily",
                data_points=[],
                total_count=0,
                overall_average=0.0,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/trends")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 0


class TestRateLimiting:
    """Rate Limiting 테스트."""

    @pytest.mark.asyncio
    async def test_rate_limit_applied(self, mock_admin):
        """Rate Limiting이 적용되는지 확인."""
        # Rate Limit 의존성이 호출되는지 확인하는 테스트
        with patch(
            "src.api.v1.ai_feedback_api.get_current_admin", return_value=mock_admin
        ), patch(
            "src.api.v1.ai_feedback_api.check_ai_permission"
        ), patch(
            "src.api.v1.ai_feedback_api.rate_limit_dependency"
        ) as mock_rate_limit, patch(
            "src.services.ai.services.feedback_analytics_service.FeedbackAnalyticsService.get_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = MagicMock(
                total_count=0,
                average_rating=0.0,
                rating_distribution=[],
                feedback_with_comments=0,
                feedback_with_comments_pct=0.0,
                period_start=None,
                period_end=None,
            )

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/ai/feedback/stats")

            assert response.status_code == 200
            # Rate Limit 의존성이 호출되었는지 확인
            mock_rate_limit.assert_called()
