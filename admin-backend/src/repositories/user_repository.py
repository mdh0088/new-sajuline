"""
관리자 백엔드 사용자 Repository
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update

from src.models.user_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        join_type: Optional[str],
        grade: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[User], int]:
        """유저 목록 조회 (페이징)
        - 기본 정렬: created_at DESC
        - search_type=all: nickname/email/phone OR LIKE
        - join_type, grade: 정확 일치
        - created_at 범위 필터
        """
        conditions = []

        if join_type:
            conditions.append(User.join_type == join_type)
        if grade:
            conditions.append(User.grade_code == grade)

        if start_dt is not None:
            conditions.append(User.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(User.created_at <= end_dt)

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(
                        User.nickname.like(kw),
                        User.email.like(kw),
                        User.phone.like(kw),
                    )
                )
            elif search_type == "nickname":
                conditions.append(User.nickname.like(kw))
            elif search_type == "email":
                conditions.append(User.email.like(kw))
            elif search_type == "phone":
                conditions.append(User.phone.like(kw))

        stmt = select(User)
        count_stmt = select(func.count(User.user_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(User.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = list(result.scalars().all())
        total = count_result.scalar() or 0
        return items, total

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def partial_update(self, user_id: str, **fields) -> bool:
        """부분 업데이트. None 값은 무시."""
        updates = {k: v for k, v in fields.items() if v is not None}
        if not updates:
            return False
        updates["updated_at"] = datetime.utcnow()
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(**updates)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def get_all_by_grade(self, grade_code: str) -> List[User]:
        """지정된 grade_code의 모든 사용자 created_at DESC 정렬로 조회 (페이징 없음)"""
        stmt = (
            select(User)
            .where(User.grade_code == grade_code)
            .order_by(desc(User.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


