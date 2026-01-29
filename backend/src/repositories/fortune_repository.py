"""
운세 이력 Repository 클래스

Story 2.3 Task 3: fortune_histories 테이블 데이터 액세스 (AC: 1, 3)
"""
from datetime import date
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.fortune_history_model import FortuneHistory
from src.common.logging import logger, get_logger_with_request_id


class FortuneRepository:
    """운세 이력 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def create_fortune_history(
        self,
        user_id: str,
        fortune_type: str,
        target_date: date,
        content: str,
        ai_model: str,
        prompt_version: str
    ) -> FortuneHistory:
        """
        운세 이력 생성

        Args:
            user_id: 사용자 ID
            fortune_type: 운세 유형 (daily, weekly, monthly, yearly)
            target_date: 운세 대상 날짜
            content: AI 생성 운세 내용 (JSON 직렬화된 문자열)
            ai_model: 사용된 AI 모델
            prompt_version: 프롬프트 버전

        Returns:
            FortuneHistory: 생성된 운세 이력
        """
        log = get_logger_with_request_id()
        log.info(
            "Creating fortune history",
            user_id=user_id,
            fortune_type=fortune_type,
            target_date=str(target_date)
        )

        history = FortuneHistory(
            id=str(uuid4()),
            user_id=user_id,
            fortune_type=fortune_type,
            target_date=target_date,
            content=content,
            ai_model=ai_model,
            prompt_version=prompt_version
        )

        self.db.add(history)
        await self.db.flush()
        await self.db.refresh(history)

        log.info(
            "Fortune history created",
            history_id=history.id,
            user_id=user_id
        )
        return history

    @logger.catch(reraise=True)
    async def get_fortune_by_user_date(
        self,
        user_id: str,
        fortune_type: str,
        target_date: date
    ) -> Optional[FortuneHistory]:
        """
        사용자+날짜+유형으로 운세 이력 조회

        Args:
            user_id: 사용자 ID
            fortune_type: 운세 유형
            target_date: 운세 대상 날짜

        Returns:
            FortuneHistory | None: 운세 이력 또는 None
        """
        log = get_logger_with_request_id()
        log.info(
            "Looking up fortune history",
            user_id=user_id,
            fortune_type=fortune_type,
            target_date=str(target_date)
        )

        stmt = select(FortuneHistory).where(
            FortuneHistory.user_id == user_id,
            FortuneHistory.fortune_type == fortune_type,
            FortuneHistory.target_date == target_date
        )
        result = await self.db.execute(stmt)
        history = result.scalar_one_or_none()

        log.info(
            "Fortune history lookup completed",
            user_id=user_id,
            found=history is not None
        )
        return history
