"""
AICorrectionService 테스트.

Stories: 5-2
FRs: FR25
"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from zoneinfo import ZoneInfo

from src.services.ai.services.correction_service import AICorrectionService
from src.schemas.ai.correction_schema import CorrectionRequest

KST = ZoneInfo("Asia/Seoul")


@pytest.fixture
def mock_db():
    """Mock 데이터베이스 세션."""
    db = AsyncMock()
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def correction_service(mock_db):
    """CorrectionService fixture."""
    return AICorrectionService(mock_db)


class TestAICorrectionService:
    """AICorrectionService 테스트."""

    @pytest.mark.asyncio
    async def test_save_correction_success(self, correction_service, mock_db):
        """수정 저장 성공 테스트 (AC3, AC5)."""
        # Given
        admin_id = "admin1"
        query_id = "query-123"
        correction_request = CorrectionRequest(
            corrected_answer="수정된 정확한 답변입니다",
            correction_reason="숫자가 잘못되었습니다"
        )

        # Mock query history
        mock_history = Mock()
        mock_history.id = 1
        mock_history.admin_id = admin_id
        mock_history.query_id = query_id
        mock_history.question = "테스트 질문"
        mock_history.answer_summary = "원본 답변"
        mock_history.db_scope = "mariadb"
        mock_history.status = "success"

        # Mock DB execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_history)
        mock_db.execute.return_value = mock_result

        # Mock refresh to set id
        async def mock_refresh(obj):
            obj.id = 1
        mock_db.refresh = AsyncMock(side_effect=mock_refresh)

        # When
        result = await correction_service.save_correction(
            admin_id=admin_id,
            query_id=query_id,
            correction=correction_request
        )

        # Then
        assert result is not None
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_save_correction_query_not_found(
        self, correction_service, mock_db
    ):
        """존재하지 않는 질의 수정 시 에러 (AC3)."""
        # Given
        admin_id = "admin1"
        query_id = "nonexistent-query"
        correction_request = CorrectionRequest(
            corrected_answer="수정된 답변입니다"
        )

        # Mock DB - query not found
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute.return_value = mock_result

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            await correction_service.save_correction(
                admin_id=admin_id,
                query_id=query_id,
                correction=correction_request
            )

        assert "Query not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_corrections(self, correction_service, mock_db):
        """특정 질의의 수정 이력 조회 테스트 (AC4)."""
        # Given
        query_id = "query-123"
        now = datetime.now(KST)

        # Mock corrections
        mock_correction1 = Mock()
        mock_correction1.id = 1
        mock_correction1.admin_id = "admin1"
        mock_correction1.query_id = query_id
        mock_correction1.original_answer = "원본1"
        mock_correction1.corrected_answer = "수정1"
        mock_correction1.is_training_data = True
        mock_correction1.reviewed = False
        mock_correction1.created_at = now

        mock_correction2 = Mock()
        mock_correction2.id = 2
        mock_correction2.admin_id = "admin2"
        mock_correction2.query_id = query_id
        mock_correction2.original_answer = "원본2"
        mock_correction2.corrected_answer = "수정2"
        mock_correction2.is_training_data = True
        mock_correction2.reviewed = True
        mock_correction2.created_at = now

        mock_corrections = [mock_correction1, mock_correction2]

        # Mock DB execute result
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=mock_corrections)
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute.return_value = mock_result

        # When
        corrections = await correction_service.get_corrections(query_id)

        # Then
        assert len(corrections) == 2
        assert corrections[0].id == 1
        assert corrections[1].id == 2

    @pytest.mark.asyncio
    async def test_get_corrections_empty(self, correction_service, mock_db):
        """수정 이력이 없는 경우 테스트 (AC4)."""
        # Given
        query_id = "query-no-corrections"

        # Mock DB execute result - empty
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute.return_value = mock_result

        # When
        corrections = await correction_service.get_corrections(query_id)

        # Then
        assert len(corrections) == 0

    @pytest.mark.asyncio
    async def test_get_training_data_default(self, correction_service, mock_db):
        """학습 데이터 조회 - 기본 옵션 테스트 (AC5)."""
        # Given
        now = datetime.now(KST)
        # Mock correction
        mock_correction = Mock()
        mock_correction.id = 1
        mock_correction.admin_id = "admin1"
        mock_correction.query_id = "query-1"
        mock_correction.original_answer = "원본"
        mock_correction.corrected_answer = "수정"
        mock_correction.is_training_data = True
        mock_correction.reviewed = True
        mock_correction.created_at = now

        mock_corrections = [mock_correction]

        # Mock DB execute result
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=mock_corrections)
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute.return_value = mock_result

        # When
        training_data = await correction_service.get_training_data()

        # Then
        assert len(training_data) == 1
        assert training_data[0].is_training_data is True
        assert training_data[0].reviewed is True

    @pytest.mark.asyncio
    async def test_get_training_data_include_not_reviewed(
        self, correction_service, mock_db
    ):
        """학습 데이터 조회 - 미검토 포함 테스트 (AC5)."""
        # Given
        now = datetime.now(KST)
        # Mock corrections
        mock_correction1 = Mock()
        mock_correction1.id = 1
        mock_correction1.admin_id = "admin1"
        mock_correction1.query_id = "query-1"
        mock_correction1.original_answer = "원본1"
        mock_correction1.corrected_answer = "수정1"
        mock_correction1.is_training_data = True
        mock_correction1.reviewed = True
        mock_correction1.created_at = now

        mock_correction2 = Mock()
        mock_correction2.id = 2
        mock_correction2.admin_id = "admin2"
        mock_correction2.query_id = "query-2"
        mock_correction2.original_answer = "원본2"
        mock_correction2.corrected_answer = "수정2"
        mock_correction2.is_training_data = True
        mock_correction2.reviewed = False
        mock_correction2.created_at = now

        mock_corrections = [mock_correction1, mock_correction2]

        # Mock DB execute result
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=mock_corrections)
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute.return_value = mock_result

        # When
        training_data = await correction_service.get_training_data(
            limit=100,
            reviewed_only=False  # 미검토 포함
        )

        # Then
        assert len(training_data) == 2
        assert training_data[1].reviewed is False

    @pytest.mark.asyncio
    async def test_get_training_data_limit(self, correction_service, mock_db):
        """학습 데이터 조회 - limit 테스트 (AC5)."""
        # Given
        limit = 50
        now = datetime.now(KST)
        # Mock corrections
        mock_corrections = []
        for i in range(limit):
            mock_correction = Mock()
            mock_correction.id = i
            mock_correction.admin_id = f"admin{i}"
            mock_correction.query_id = f"query-{i}"
            mock_correction.original_answer = f"원본{i}"
            mock_correction.corrected_answer = f"수정{i}"
            mock_correction.is_training_data = True
            mock_correction.reviewed = True
            mock_correction.created_at = now
            mock_corrections.append(mock_correction)

        # Mock DB execute result
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=mock_corrections)
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute.return_value = mock_result

        # When
        training_data = await correction_service.get_training_data(limit=limit)

        # Then
        assert len(training_data) == limit
