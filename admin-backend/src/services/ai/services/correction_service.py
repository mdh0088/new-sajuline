"""
AI 피드백 수정 서비스.

Stories: 5-2
FRs: FR25
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_feedback_correction import AIFeedbackCorrection
from src.models.ai.ai_query_history_model import AIQueryHistory
from src.schemas.ai.correction_schema import CorrectionRequest


class AICorrectionService:
    """AI 피드백 수정 서비스.

    AC3: 수정된 답변이 원본과 함께 저장된다
    AC4: 수정 이력이 관리된다
    AC5: 수정된 답변이 향후 학습 데이터로 표시된다
    """

    def __init__(self, db: AsyncSession):
        """서비스 초기화.

        Args:
            db: 데이터베이스 세션
        """
        self.db = db

    async def _get_query_history(
        self, query_id: str
    ) -> AIQueryHistory | None:
        """질의 히스토리 조회.

        Args:
            query_id: 질의 ID

        Returns:
            AIQueryHistory | None: 질의 히스토리 객체 또는 None
        """
        result = await self.db.execute(
            select(AIQueryHistory).where(AIQueryHistory.query_id == query_id)
        )
        return result.scalar_one_or_none()

    async def save_correction(
        self,
        admin_id: str,
        query_id: str,
        correction: CorrectionRequest
    ) -> AIFeedbackCorrection:
        """수정 저장 (AC3, AC5).

        Args:
            admin_id: 수정 제출자 ID
            query_id: 질의 ID
            correction: 수정 요청 데이터

        Returns:
            AIFeedbackCorrection: 저장된 수정 객체

        Raises:
            ValueError: 질의를 찾을 수 없는 경우
        """
        # 질의 히스토리 조회
        history = await self._get_query_history(query_id)
        if not history:
            raise ValueError(f"Query not found: {query_id}")

        # 수정 객체 생성
        db_correction = AIFeedbackCorrection(
            admin_id=admin_id,
            query_id=query_id,
            original_answer=history.answer_summary or "",
            corrected_answer=correction.corrected_answer,
            correction_reason=correction.correction_reason,
            is_training_data=True,  # AC5: 학습 데이터로 표시
            reviewed=False
        )

        # 저장 (refresh 제거 - 성능 최적화)
        self.db.add(db_correction)
        await self.db.commit()
        # ORM이 이미 ID를 설정하므로 refresh 불필요

        return db_correction

    async def get_corrections(
        self, query_id: str
    ) -> list[AIFeedbackCorrection]:
        """특정 질의의 수정 이력 조회 (AC4).

        Args:
            query_id: 질의 ID

        Returns:
            list[AIFeedbackCorrection]: 수정 이력 목록 (최신순)
        """
        result = await self.db.execute(
            select(AIFeedbackCorrection)
            .where(AIFeedbackCorrection.query_id == query_id)
            .order_by(AIFeedbackCorrection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_training_data(
        self,
        limit: int = 100,
        reviewed_only: bool = True
    ) -> list[AIFeedbackCorrection]:
        """학습 데이터 조회 (AC5).

        Args:
            limit: 조회할 최대 개수
            reviewed_only: 검토 완료된 데이터만 조회할지 여부

        Returns:
            list[AIFeedbackCorrection]: 학습 데이터 목록 (최신순)
        """
        query = select(AIFeedbackCorrection).where(
            AIFeedbackCorrection.is_training_data == True  # noqa: E712
        )

        if reviewed_only:
            query = query.where(AIFeedbackCorrection.reviewed == True)  # noqa: E712

        query = query.order_by(AIFeedbackCorrection.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
