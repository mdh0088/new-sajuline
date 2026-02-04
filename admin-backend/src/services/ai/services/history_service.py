"""
AI 질의 히스토리 서비스.

Stories: 4-1
FRs: FR19
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai.ai_query_history_model import AIQueryHistory


class AIHistoryService:
    """AI 질의 히스토리 서비스.

    AC3: 최근 질의 히스토리 표시 (최대 20개)
    AC4: 히스토리 항목 클릭 시 질의 재실행
    AC5: 히스토리 검색 기능
    """

    def __init__(self, db: AsyncSession):
        """서비스 초기화.

        Args:
            db: 데이터베이스 세션
        """
        self.db = db

    async def save_query(self, history: AIQueryHistory) -> None:
        """질의 히스토리 저장.

        Args:
            history: 저장할 히스토리 객체
        """
        self.db.add(history)
        await self.db.commit()

    async def get_history(
        self,
        admin_id: str,
        limit: int = 20,
        search: str | None = None
    ) -> list[AIQueryHistory]:
        """히스토리 조회.

        AC3: 최근 질의 히스토리 표시 (최대 20개)
        AC5: 히스토리 검색 기능

        Args:
            admin_id: 관리자 ID
            limit: 조회할 최대 개수 (기본값: 20)
            search: 검색어 (question 필드에서 검색)

        Returns:
            list[AIQueryHistory]: 히스토리 목록 (최신순)
        """
        # 기본 쿼리
        query = select(AIQueryHistory).where(
            AIQueryHistory.admin_id == admin_id
        ).order_by(AIQueryHistory.created_at.desc())

        # 검색어 필터링 (AC5)
        if search:
            query = query.where(
                AIQueryHistory.question.ilike(f"%{search}%")
            )

        # limit 적용
        query = query.limit(limit)

        # 실행
        result = await self.db.execute(query)
        return list(result.scalars().all())
