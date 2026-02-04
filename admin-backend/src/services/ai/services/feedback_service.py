"""
AI 피드백 서비스.

Stories: 5-1
FRs: FR-024, FR-026
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_feedback_model import AIFeedback
from src.schemas.ai.feedback_schema import AIFeedbackRequest


class AIFeedbackService:
    """AI 피드백 서비스"""

    def __init__(self, db: AsyncSession):
        """
        Args:
            db: 비동기 데이터베이스 세션
        """
        self.db = db

    async def save_feedback(
        self, admin_id: str, feedback: AIFeedbackRequest
    ) -> AIFeedback:
        """
        피드백 저장.

        Args:
            admin_id: 관리자 ID
            feedback: 피드백 요청 데이터

        Returns:
            저장된 AIFeedback 모델 인스턴스
        """
        db_feedback = AIFeedback(
            admin_id=admin_id,
            query_id=feedback.query_id,
            rating=feedback.rating,
            comment=feedback.comment,
        )

        self.db.add(db_feedback)
        await self.db.commit()
        await self.db.refresh(db_feedback)

        return db_feedback

    async def get_feedback_by_query(
        self, query_id: Optional[str] = None, admin_id: Optional[str] = None
    ) -> list[AIFeedback]:
        """
        조건에 따라 피드백 조회.

        Args:
            query_id: 질의 ID (선택)
            admin_id: 관리자 ID (선택)

        Returns:
            AIFeedback 모델 리스트
        """
        stmt = select(AIFeedback)

        if query_id is not None:
            stmt = stmt.where(AIFeedback.query_id == query_id)

        if admin_id is not None:
            stmt = stmt.where(AIFeedback.admin_id == admin_id)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
