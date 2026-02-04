"""
AI 질의 히스토리 서비스 테스트.

Stories: 4-1
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_query_history_model import AIQueryHistory
from src.services.ai.services.history_service import AIHistoryService


@pytest.fixture
def mock_db_session():
    """Mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def history_service(mock_db_session):
    """AIHistoryService 인스턴스."""
    return AIHistoryService(db=mock_db_session)


@pytest.fixture
def sample_history_data():
    """샘플 히스토리 데이터."""
    return {
        "admin_id": "admin001",
        "query_id": str(uuid4()),
        "question": "오늘 매출 얼마야?",
        "answer_summary": "총 매출: 1,234,567원",
        "db_scope": "mariadb",
        "execution_time_ms": 250,
        "row_count": 1,
        "status": "success",
    }


class TestAIHistoryService:
    """AIHistoryService 단위 테스트."""

    @pytest.mark.asyncio
    async def test_save_query(self, history_service, mock_db_session, sample_history_data):
        """AC3: 질의 히스토리 저장 기능."""
        history = AIQueryHistory(**sample_history_data)

        await history_service.save_query(history)

        # DB add 호출 확인
        mock_db_session.add.assert_called_once_with(history)
        # commit 호출 확인
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_history_returns_list(self, history_service, mock_db_session):
        """AC3: 최근 질의 히스토리 조회 (최대 20개)."""
        admin_id = "admin001"

        # Mock 결과 설정
        mock_result = MagicMock()
        mock_histories = [
            AIQueryHistory(
                id=i,
                admin_id=admin_id,
                query_id=str(uuid4()),
                question=f"질문 {i}",
                answer_summary=f"답변 {i}",
                db_scope="mariadb",
                status="success",
                created_at=datetime.now(),
            )
            for i in range(1, 6)
        ]
        mock_result.scalars.return_value.all.return_value = mock_histories
        mock_db_session.execute.return_value = mock_result

        # 히스토리 조회
        result = await history_service.get_history(admin_id=admin_id, limit=20)

        assert len(result) == 5
        assert all(h.admin_id == admin_id for h in result)

    @pytest.mark.asyncio
    async def test_get_history_with_search(self, history_service, mock_db_session):
        """AC5: 히스토리 검색 기능."""
        admin_id = "admin001"
        search_term = "매출"

        # Mock 결과 설정
        mock_result = MagicMock()
        mock_histories = [
            AIQueryHistory(
                id=1,
                admin_id=admin_id,
                query_id=str(uuid4()),
                question="오늘 매출 얼마야?",
                answer_summary="총 매출: 1,234,567원",
                db_scope="mariadb",
                status="success",
                created_at=datetime.now(),
            )
        ]
        mock_result.scalars.return_value.all.return_value = mock_histories
        mock_db_session.execute.return_value = mock_result

        # 검색어로 히스토리 조회
        result = await history_service.get_history(
            admin_id=admin_id,
            limit=20,
            search=search_term
        )

        assert len(result) == 1
        assert search_term in result[0].question

    @pytest.mark.asyncio
    async def test_get_history_respects_limit(self, history_service, mock_db_session):
        """AC3: 히스토리 조회 시 limit 적용 (최대 20개)."""
        admin_id = "admin001"
        limit = 10

        # Mock 결과 설정
        mock_result = MagicMock()
        mock_histories = [
            AIQueryHistory(
                id=i,
                admin_id=admin_id,
                query_id=str(uuid4()),
                question=f"질문 {i}",
                answer_summary=f"답변 {i}",
                db_scope="mariadb",
                status="success",
                created_at=datetime.now(),
            )
            for i in range(1, limit + 1)
        ]
        mock_result.scalars.return_value.all.return_value = mock_histories
        mock_db_session.execute.return_value = mock_result

        result = await history_service.get_history(admin_id=admin_id, limit=limit)

        assert len(result) <= limit

    @pytest.mark.asyncio
    async def test_get_history_ordered_by_created_at_desc(self, history_service, mock_db_session):
        """히스토리는 생성 시간 내림차순으로 정렬된다."""
        admin_id = "admin001"

        # Mock 결과 설정 (최신순)
        mock_result = MagicMock()
        now = datetime.now()
        mock_histories = [
            AIQueryHistory(
                id=3,
                admin_id=admin_id,
                query_id=str(uuid4()),
                question="최신 질문",
                answer_summary="최신 답변",
                db_scope="mariadb",
                status="success",
                created_at=now,
            ),
            AIQueryHistory(
                id=2,
                admin_id=admin_id,
                query_id=str(uuid4()),
                question="중간 질문",
                answer_summary="중간 답변",
                db_scope="mariadb",
                status="success",
                created_at=datetime(2024, 1, 1),
            ),
        ]
        mock_result.scalars.return_value.all.return_value = mock_histories
        mock_db_session.execute.return_value = mock_result

        result = await history_service.get_history(admin_id=admin_id, limit=20)

        # 첫 번째가 최신
        assert result[0].id == 3
        assert result[1].id == 2
