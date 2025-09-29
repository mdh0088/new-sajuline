"""
GradeRepository - t_grade 접근 레이어
"""
from typing import List, Optional

from sqlalchemy import select, desc, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.grade_model import Grade


class GradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_desc_by_level(self) -> List[Grade]:
        """전체 등급을 grade_level DESC로 정렬하여 반환 (페이징 없음)"""
        stmt = select(Grade).order_by(desc(Grade.grade_level))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, grade_code: str) -> Optional[Grade]:
        stmt = select(Grade).where(Grade.grade_code == grade_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **fields) -> Grade:
        stmt = insert(Grade).values(**fields)
        await self.db.execute(stmt)
        # 생성 후 반환
        result = await self.db.execute(select(Grade).where(Grade.grade_code == fields["grade_code"]))
        return result.scalar_one()

    async def partial_update(self, grade_code: str, **fields) -> bool:
        if not fields:
            return False
        stmt = (
            update(Grade)
            .where(Grade.grade_code == grade_code)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete(self, grade_code: str) -> bool:
        stmt = delete(Grade).where(Grade.grade_code == grade_code)
        result = await self.db.execute(stmt)
        return result.rowcount > 0


