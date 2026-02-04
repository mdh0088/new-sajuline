"""
피드백 분석 서비스 단위 테스트.

Stories: STORY-5-3
FRs: FR-027
"""

import pytest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai.services.feedback_analytics_service import (
    FeedbackAnalyticsService,
)
from src.models.ai.ai_feedback_model import AIFeedback

KST = ZoneInfo("Asia/Seoul")


class TestFeedbackAnalyticsService:
    """FeedbackAnalyticsService 단위 테스트."""

    def test_service_initialization(self):
        """서비스 초기화 테스트."""
        mock_db = AsyncMock(spec=AsyncSession)
        service = FeedbackAnalyticsService(db=mock_db)

        assert service.db is mock_db

    @pytest.mark.asyncio
    async def test_get_stats_with_no_data(self):
        """데이터 없을 때 통계 조회."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        stats = await service.get_stats()

        assert stats.total_count == 0
        assert stats.average_rating == 0.0
        assert stats.rating_distribution == []
        assert stats.feedback_with_comments == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self):
        """피드백 데이터가 있을 때 통계 조회."""
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock 피드백 데이터
        feedbacks = [
            MagicMock(rating=5, comment="Good"),
            MagicMock(rating=4, comment="Nice"),
            MagicMock(rating=3, comment=None),
        ]

        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = feedbacks
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        stats = await service.get_stats()

        assert stats.total_count == 3
        assert stats.average_rating == 4.0  # (5+4+3)/3
        assert stats.feedback_with_comments == 2
        assert stats.feedback_with_comments_pct == pytest.approx(66.7, rel=0.1)

    @pytest.mark.asyncio
    async def test_get_low_score_feedbacks(self):
        """낮은 점수 피드백 조회."""
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock 데이터
        mock_feedback = MagicMock(
            id=1,
            query_id="query-001",
            rating=2,
            comment="Bad",
            admin_id="admin1",
            created_at=datetime.now(KST),
        )

        mock_result = AsyncMock()
        mock_result.all.return_value = [(mock_feedback, "Test question")]
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        feedbacks = await service.get_low_score_feedbacks(threshold=2, limit=10)

        assert len(feedbacks) == 1
        assert feedbacks[0].rating == 2

    @pytest.mark.asyncio
    async def test_export_feedbacks_csv(self):
        """피드백 CSV 내보내기."""
        mock_db = AsyncMock(spec=AsyncSession)

        feedbacks = [
            MagicMock(
                id=1,
                query_id="query-001",
                rating=5,
                comment="Good",
                admin_id="admin1",
                created_at=datetime.now(KST),
            ),
        ]

        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = feedbacks
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        csv_data = await service.export_feedbacks(format="csv")

        assert isinstance(csv_data, str)
        assert "ID,Query ID,Rating,Comment,Admin ID,Created At" in csv_data
        assert "query-001" in csv_data

    @pytest.mark.asyncio
    async def test_export_feedbacks_json(self):
        """피드백 JSON 내보내기."""
        mock_db = AsyncMock(spec=AsyncSession)

        feedbacks = [
            MagicMock(
                id=1,
                query_id="query-001",
                rating=5,
                comment="Good",
                admin_id="admin1",
                created_at=datetime.now(KST),
            ),
        ]

        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = feedbacks
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        json_data = await service.export_feedbacks(format="json")

        assert isinstance(json_data, list)
        assert len(json_data) == 1
        assert "id" in json_data[0]
        assert "query_id" in json_data[0]

    @pytest.mark.asyncio
    async def test_get_trends_daily(self):
        """일별 트렌드 조회."""
        mock_db = AsyncMock(spec=AsyncSession)

        feedbacks = [
            MagicMock(
                rating=5,
                created_at=datetime.now(KST),
            ),
            MagicMock(
                rating=4,
                created_at=datetime.now(KST),
            ),
        ]

        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = feedbacks
        mock_db.execute.return_value = mock_result

        service = FeedbackAnalyticsService(db=mock_db)
        trends = await service.get_trends(period="daily", days=7)

        assert trends.period == "daily"
        assert trends.total_count == 2
