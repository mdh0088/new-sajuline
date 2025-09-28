"""
상담사 Repository - t_counselor 접근 (관리자 백엔드)
"""
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func, desc
from datetime import datetime

from src.models.counselor_model import Counselor


class CounselorRepository:
    """상담사 데이터 접근 레이어 (관리자)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, counselor_id: str) -> Optional[Counselor]:
        stmt = select(Counselor).where(Counselor.counselor_id == counselor_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login(self, counselor_id: str) -> bool:
        from datetime import datetime

        stmt = (
            update(Counselor)
            .where(Counselor.counselor_id == counselor_id)
            .values(last_login_at=datetime.utcnow(), updated_at=datetime.utcnow())
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def get_list(
        self,
        *,
        page: int,
        limit: int,
        search_type: str | None,
        search_name: str | None,
        specialties: List[str] | None,
        is_show: Optional[bool],
        is_out: Optional[bool],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Counselor], int]:
        """상담사 목록 조회 (페이징)

        - 기본 정렬: created_at DESC
        - specialty_types: JSON 문자열 내 값 OR 매칭 (예: %"TARO"%)
        - search_type=all: name/nickname/counselor_id OR LIKE
        - start_dt/end_dt: created_at BETWEEN
        """
        conditions = []

        if is_show is not None:
            conditions.append(Counselor.is_show.is_(is_show))
        if is_out is not None:
            conditions.append(Counselor.is_out.is_(is_out))

        if start_dt is not None:
            conditions.append(Counselor.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Counselor.created_at <= end_dt)

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(
                        Counselor.name.like(kw),
                        Counselor.nickname.like(kw),
                        Counselor.counselor_id.like(kw),
                    )
                )
            elif search_type == "name":
                conditions.append(Counselor.name.like(kw))
            elif search_type == "nickname":
                conditions.append(Counselor.nickname.like(kw))
            elif search_type == "counselor_id":
                conditions.append(Counselor.counselor_id.like(kw))

        if specialties:
            like_clauses = []
            for sp in specialties:
                if sp:
                    like_clauses.append(Counselor.specialty_types.like(f'%"{sp}"%'))
            if like_clauses:
                conditions.append(or_(*like_clauses))

        stmt = select(Counselor)
        count_stmt = select(func.count(Counselor.counselor_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(Counselor.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = list(result.scalars().all())
        total = count_result.scalar() or 0
        return items, total


