"""
AI 피드백 서비스 테스트.

Stories: 5-1
FRs: FR-024, FR-026
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai.services.feedback_service import AIFeedbackService
from src.schemas.ai.feedback_schema import AIFeedbackRequest
from src.models.ai.ai_feedback_model import AIFeedback


class TestAIFeedbackService:
    """AIFeedbackService 테스트"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock 데이터베이스 세션"""
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def feedback_service(self, mock_db_session):
        """AIFeedbackService 인스턴스"""
        return AIFeedbackService(db=mock_db_session)

    @pytest.mark.asyncio
    async def test_save_feedback_with_comment(self, feedback_service, mock_db_session):
        """코멘트가 있는 피드백 저장 테스트"""
        # Given
        admin_id = "admin001"
        feedback_request = AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440000",
            rating=4,
            comment="결과는 정확했지만 응답이 조금 느렸어요"
        )

        # Mock refresh to set the id
        async def mock_refresh(instance):
            instance.id = 1

        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

        # When
        result = await feedback_service.save_feedback(
            admin_id=admin_id,
            feedback=feedback_request
        )

        # Then
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert mock_db_session.refresh.called

        # Verify the saved feedback
        saved_feedback = mock_db_session.add.call_args[0][0]
        assert isinstance(saved_feedback, AIFeedback)
        assert saved_feedback.admin_id == admin_id
        assert saved_feedback.query_id == feedback_request.query_id
        assert saved_feedback.rating == feedback_request.rating
        assert saved_feedback.comment == feedback_request.comment

    @pytest.mark.asyncio
    async def test_save_feedback_without_comment(self, feedback_service, mock_db_session):
        """코멘트 없이 피드백 저장 테스트"""
        # Given
        admin_id = "admin002"
        feedback_request = AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440001",
            rating=5
        )

        # Mock refresh to set the id
        async def mock_refresh(instance):
            instance.id = 2

        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

        # When
        result = await feedback_service.save_feedback(
            admin_id=admin_id,
            feedback=feedback_request
        )

        # Then
        saved_feedback = mock_db_session.add.call_args[0][0]
        assert saved_feedback.comment is None

    @pytest.mark.asyncio
    async def test_save_feedback_returns_feedback_model(self, feedback_service, mock_db_session):
        """피드백 저장 시 AIFeedback 모델 반환 테스트"""
        # Given
        admin_id = "admin003"
        feedback_request = AIFeedbackRequest(
            query_id="test-query-id",
            rating=3,
            comment="Average"
        )

        # Mock refresh to set the id
        async def mock_refresh(instance):
            instance.id = 3

        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

        # When
        result = await feedback_service.save_feedback(
            admin_id=admin_id,
            feedback=feedback_request
        )

        # Then
        assert isinstance(result, AIFeedback)
        assert result.admin_id == admin_id
        assert result.query_id == feedback_request.query_id
        assert result.rating == feedback_request.rating

    @pytest.mark.asyncio
    async def test_get_feedback_by_query_id(self, feedback_service, mock_db_session):
        """질의 ID로 피드백 조회 테스트"""
        # Given
        query_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_feedback = AIFeedback(
            id=1,
            admin_id="admin001",
            query_id=query_id,
            rating=4,
            comment="Test"
        )

        # Mock execute result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_feedback]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await feedback_service.get_feedback_by_query(query_id=query_id)

        # Then
        assert mock_db_session.execute.called
        assert len(result) == 1
        assert result[0].query_id == query_id

    @pytest.mark.asyncio
    async def test_get_feedback_by_admin_id(self, feedback_service, mock_db_session):
        """관리자 ID로 피드백 조회 테스트"""
        # Given
        admin_id = "admin001"
        mock_feedbacks = [
            AIFeedback(
                id=1,
                admin_id=admin_id,
                query_id="query-1",
                rating=4,
                comment="Good"
            ),
            AIFeedback(
                id=2,
                admin_id=admin_id,
                query_id="query-2",
                rating=3,
                comment="Average"
            )
        ]

        # Mock execute result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_feedbacks
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await feedback_service.get_feedback_by_query(admin_id=admin_id)

        # Then
        assert len(result) == 2
        assert all(f.admin_id == admin_id for f in result)

    @pytest.mark.asyncio
    async def test_get_feedback_no_results(self, feedback_service, mock_db_session):
        """피드백 조회 결과 없음 테스트"""
        # Given
        query_id = "non-existent-query-id"

        # Mock execute result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await feedback_service.get_feedback_by_query(query_id=query_id)

        # Then
        assert len(result) == 0
