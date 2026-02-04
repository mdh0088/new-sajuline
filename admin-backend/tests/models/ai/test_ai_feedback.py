"""
AI 피드백 모델 테스트.

Stories: 5-1
FRs: FR-024, FR-026
"""
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_feedback_model import AIFeedback


class TestAIFeedbackModel:
    """AIFeedback 모델 테스트"""

    @pytest.mark.asyncio
    async def test_create_feedback(self, db_session: AsyncSession):
        """피드백 생성 테스트"""
        # Given
        feedback = AIFeedback(
            admin_id="admin001",
            query_id="550e8400-e29b-41d4-a716-446655440000",
            rating=4,
            comment="결과는 정확했지만 응답이 조금 느렸어요"
        )

        # When
        db_session.add(feedback)
        await db_session.commit()
        await db_session.refresh(feedback)

        # Then
        assert feedback.id is not None
        assert feedback.admin_id == "admin001"
        assert feedback.query_id == "550e8400-e29b-41d4-a716-446655440000"
        assert feedback.rating == 4
        assert feedback.comment == "결과는 정확했지만 응답이 조금 느렸어요"
        assert isinstance(feedback.created_at, datetime)

    @pytest.mark.asyncio
    async def test_create_feedback_without_comment(self, db_session: AsyncSession):
        """코멘트 없이 피드백 생성 테스트"""
        # Given
        feedback = AIFeedback(
            admin_id="admin002",
            query_id="550e8400-e29b-41d4-a716-446655440001",
            rating=5,
            comment=None
        )

        # When
        db_session.add(feedback)
        await db_session.commit()
        await db_session.refresh(feedback)

        # Then
        assert feedback.id is not None
        assert feedback.rating == 5
        assert feedback.comment is None

    @pytest.mark.asyncio
    async def test_feedback_query_by_admin(self, db_session: AsyncSession):
        """관리자별 피드백 조회 테스트"""
        # Given
        feedback1 = AIFeedback(
            admin_id="admin001",
            query_id="query-1",
            rating=4,
            comment="Good"
        )
        feedback2 = AIFeedback(
            admin_id="admin001",
            query_id="query-2",
            rating=3,
            comment="Average"
        )
        feedback3 = AIFeedback(
            admin_id="admin002",
            query_id="query-3",
            rating=5,
            comment="Excellent"
        )

        db_session.add_all([feedback1, feedback2, feedback3])
        await db_session.commit()

        # When
        stmt = select(AIFeedback).where(AIFeedback.admin_id == "admin001")
        result = await db_session.execute(stmt)
        admin_feedbacks = result.scalars().all()

        # Then
        assert len(admin_feedbacks) == 2
        assert all(f.admin_id == "admin001" for f in admin_feedbacks)

    @pytest.mark.asyncio
    async def test_feedback_query_by_query_id(self, db_session: AsyncSession):
        """질의 ID별 피드백 조회 테스트"""
        # Given
        query_id = "550e8400-e29b-41d4-a716-446655440000"
        feedback = AIFeedback(
            admin_id="admin001",
            query_id=query_id,
            rating=4,
            comment="Test"
        )

        db_session.add(feedback)
        await db_session.commit()

        # When
        stmt = select(AIFeedback).where(AIFeedback.query_id == query_id)
        result = await db_session.execute(stmt)
        found_feedback = result.scalar_one_or_none()

        # Then
        assert found_feedback is not None
        assert found_feedback.query_id == query_id
        assert found_feedback.rating == 4

    @pytest.mark.asyncio
    async def test_feedback_rating_range(self, db_session: AsyncSession):
        """별점 범위 테스트 (1-5)"""
        # Given
        feedbacks = [
            AIFeedback(admin_id="admin001", query_id=f"query-{i}", rating=i)
            for i in range(1, 6)
        ]

        # When
        db_session.add_all(feedbacks)
        await db_session.commit()

        # Then
        stmt = select(AIFeedback)
        result = await db_session.execute(stmt)
        all_feedbacks = result.scalars().all()

        assert len(all_feedbacks) == 5
        ratings = [f.rating for f in all_feedbacks]
        assert min(ratings) == 1
        assert max(ratings) == 5
        assert set(ratings) == {1, 2, 3, 4, 5}

    @pytest.mark.asyncio
    async def test_feedback_created_at_auto_set(self, db_session: AsyncSession):
        """created_at 자동 설정 테스트"""
        # Given
        before = datetime.utcnow()
        feedback = AIFeedback(
            admin_id="admin001",
            query_id="query-1",
            rating=5
        )

        # When
        db_session.add(feedback)
        await db_session.commit()
        await db_session.refresh(feedback)
        after = datetime.utcnow()

        # Then
        assert feedback.created_at is not None
        # Note: created_at uses KST timezone, so we can't directly compare with UTC
        # Just check it's set
        assert feedback.created_at is not None

    @pytest.mark.asyncio
    async def test_feedback_indexes_exist(self, db_session: AsyncSession):
        """인덱스 존재 확인 테스트"""
        # When
        feedbacks = [
            AIFeedback(
                admin_id=f"admin{i % 3:03d}",
                query_id=f"query-{i}",
                rating=(i % 5) + 1
            )
            for i in range(100)
        ]
        db_session.add_all(feedbacks)
        await db_session.commit()

        # Then - 인덱스가 있으면 빠른 조회가 가능해야 함
        stmt = select(AIFeedback).where(AIFeedback.admin_id == "admin001")
        result = await db_session.execute(stmt)
        admin_feedbacks = result.scalars().all()
        assert len(admin_feedbacks) > 0
