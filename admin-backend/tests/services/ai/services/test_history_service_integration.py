"""
AI 질의 히스토리 서비스 실제 DB 통합 테스트.

Stories: 4-1
Issue: #7 - 실제 DB 통합 테스트 추가
"""
import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_query_history_model import AIQueryHistory
from src.services.ai.services.history_service import AIHistoryService


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIHistoryServiceIntegration:
    """실제 DB를 사용한 통합 테스트 (테스트 DB 필요)."""

    async def test_save_and_get_history_integration(self, db_session: AsyncSession):
        """히스토리 저장 후 조회 통합 테스트."""
        # Given: 히스토리 데이터 준비
        admin_id = f"test_admin_{uuid4().hex[:8]}"
        query_id = str(uuid4())

        history = AIQueryHistory(
            admin_id=admin_id,
            query_id=query_id,
            question="통합 테스트 질문",
            answer_summary="통합 테스트 답변",
            db_scope="mariadb",
            execution_time_ms=150,
            row_count=5,
            status="success",
        )

        # When: 히스토리 저장
        service = AIHistoryService(db=db_session)
        await service.save_query(history)

        # Then: 저장된 히스토리 조회 확인
        result = await db_session.execute(
            select(AIQueryHistory).where(AIQueryHistory.query_id == query_id)
        )
        saved_history = result.scalar_one_or_none()

        assert saved_history is not None
        assert saved_history.admin_id == admin_id
        assert saved_history.question == "통합 테스트 질문"
        assert saved_history.answer_summary == "통합 테스트 답변"
        assert saved_history.execution_time_ms == 150
        assert saved_history.row_count == 5
        assert saved_history.status == "success"

        # 정리
        await db_session.delete(saved_history)
        await db_session.commit()

    async def test_get_history_ordering_integration(self, db_session: AsyncSession):
        """히스토리 조회 시 최신순 정렬 통합 테스트."""
        # Given: 여러 히스토리 데이터 생성
        admin_id = f"test_admin_{uuid4().hex[:8]}"
        histories = []

        for i in range(3):
            history = AIQueryHistory(
                admin_id=admin_id,
                query_id=str(uuid4()),
                question=f"질문 {i}",
                answer_summary=f"답변 {i}",
                db_scope="mariadb",
                status="success",
            )
            histories.append(history)
            db_session.add(history)

        await db_session.commit()

        # When: 히스토리 조회
        service = AIHistoryService(db=db_session)
        result = await service.get_history(admin_id=admin_id, limit=10)

        # Then: 최신순으로 정렬되었는지 확인
        assert len(result) == 3
        assert result[0].question == "질문 2"  # 마지막 생성 = 최신
        assert result[1].question == "질문 1"
        assert result[2].question == "질문 0"  # 첫 생성 = 가장 오래됨

        # 정리
        for h in histories:
            await db_session.delete(h)
        await db_session.commit()

    async def test_get_history_with_search_integration(self, db_session: AsyncSession):
        """히스토리 검색 기능 통합 테스트."""
        # Given: 검색 테스트용 히스토리 생성
        admin_id = f"test_admin_{uuid4().hex[:8]}"

        history1 = AIQueryHistory(
            admin_id=admin_id,
            query_id=str(uuid4()),
            question="오늘 매출 조회",
            answer_summary="매출: 1,000,000원",
            db_scope="mariadb",
            status="success",
        )
        history2 = AIQueryHistory(
            admin_id=admin_id,
            query_id=str(uuid4()),
            question="신규 가입자 수",
            answer_summary="가입자: 50명",
            db_scope="mariadb",
            status="success",
        )

        db_session.add(history1)
        db_session.add(history2)
        await db_session.commit()

        # When: "매출" 키워드로 검색
        service = AIHistoryService(db=db_session)
        result = await service.get_history(admin_id=admin_id, search="매출", limit=10)

        # Then: 매출 관련 히스토리만 조회
        assert len(result) == 1
        assert result[0].question == "오늘 매출 조회"
        assert "매출" in result[0].question

        # 정리
        await db_session.delete(history1)
        await db_session.delete(history2)
        await db_session.commit()

    async def test_get_history_limit_integration(self, db_session: AsyncSession):
        """히스토리 limit 파라미터 통합 테스트."""
        # Given: 10개 히스토리 생성
        admin_id = f"test_admin_{uuid4().hex[:8]}"
        histories = []

        for i in range(10):
            history = AIQueryHistory(
                admin_id=admin_id,
                query_id=str(uuid4()),
                question=f"질문 {i}",
                answer_summary=f"답변 {i}",
                db_scope="mariadb",
                status="success",
            )
            histories.append(history)
            db_session.add(history)

        await db_session.commit()

        # When: limit=5로 조회
        service = AIHistoryService(db=db_session)
        result = await service.get_history(admin_id=admin_id, limit=5)

        # Then: 5개만 반환
        assert len(result) == 5

        # 정리
        for h in histories:
            await db_session.delete(h)
        await db_session.commit()

    async def test_get_history_user_isolation_integration(self, db_session: AsyncSession):
        """사용자별 히스토리 격리 통합 테스트."""
        # Given: 서로 다른 사용자의 히스토리 생성
        admin1_id = f"test_admin_1_{uuid4().hex[:8]}"
        admin2_id = f"test_admin_2_{uuid4().hex[:8]}"

        history1 = AIQueryHistory(
            admin_id=admin1_id,
            query_id=str(uuid4()),
            question="관리자1 질문",
            db_scope="mariadb",
            status="success",
        )
        history2 = AIQueryHistory(
            admin_id=admin2_id,
            query_id=str(uuid4()),
            question="관리자2 질문",
            db_scope="mariadb",
            status="success",
        )

        db_session.add(history1)
        db_session.add(history2)
        await db_session.commit()

        # When: 관리자1의 히스토리 조회
        service = AIHistoryService(db=db_session)
        result = await service.get_history(admin_id=admin1_id, limit=10)

        # Then: 관리자1의 히스토리만 반환
        assert len(result) == 1
        assert result[0].admin_id == admin1_id
        assert result[0].question == "관리자1 질문"

        # 정리
        await db_session.delete(history1)
        await db_session.delete(history2)
        await db_session.commit()
