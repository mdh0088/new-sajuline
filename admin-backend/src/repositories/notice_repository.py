"""
NoticeRepository - t_notice 접근 레이어
"""
from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, and_, or_, func, desc, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notice_model import Notice


class NoticeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        target_audience: Optional[str],
        notice_type: Optional[str],
        is_important: Optional[bool],
        is_active: Optional[bool],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Notice], int]:
        """공지 목록 조회 (페이징)
        - 기본 정렬: created_at DESC
        - search_type=all: title OR content LIKE
        - target_audience, notice_type, is_important, is_active: 정확 일치
        - created_at 범위 필터
        """
        conditions = []

        if target_audience:
            conditions.append(Notice.target_audience == target_audience)
        if notice_type:
            conditions.append(Notice.notice_type == notice_type)
        if is_important is not None:
            conditions.append(Notice.is_important == is_important)
        if is_active is not None:
            conditions.append(Notice.is_active == is_active)

        if start_dt is not None:
            conditions.append(Notice.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Notice.created_at <= end_dt)

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(or_(Notice.title.like(kw), Notice.content.like(kw)))
            elif search_type == "title":
                conditions.append(Notice.title.like(kw))
            elif search_type == "content":
                conditions.append(Notice.content.like(kw))

        stmt = select(Notice)
        count_stmt = select(func.count(Notice.notice_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(Notice.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = list(result.scalars().all())
        total = int(count_result.scalar() or 0)
        return items, total

    async def get_by_id(self, notice_id: int) -> Optional[Notice]:
        stmt = select(Notice).where(Notice.notice_id == notice_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **fields) -> Notice:
        stmt = insert(Notice).values(**fields)
        await self.db.execute(stmt)
        # 생성된 레코드 재조회 (auto increment)
        # 가장 최근 created_at/notice_id 기준으로 가져오는 것은 부정확할 수 있으므로
        # title + created_by + created_at 범위를 이용할 수도 있으나 여기서는 select last insert를 대체: 재조회 위해 조건 구성
        # product처럼 unique 키가 없으므로, insert 후 다시 where 조건으로 동일성 보장되는 필드를 이용
        # 안전하게는 최대값 PK로 가져오되 동일 작성자의 최신 레코드를 대상으로 함
        stmt2 = (
            select(Notice)
            .where(
                and_(
                    Notice.title == fields.get("title"),
                    Notice.created_by == fields.get("created_by"),
                )
            )
            .order_by(desc(Notice.notice_id))
            .limit(1)
        )
        result = await self.db.execute(stmt2)
        row = result.scalar_one_or_none()
        if row is None:
            # fallback: 최신 PK
            result = await self.db.execute(select(Notice).order_by(desc(Notice.notice_id)).limit(1))
            row = result.scalar_one()
        return row

    async def partial_update(self, notice_id: int, **fields) -> bool:
        if not fields:
            return False
        stmt = (
            update(Notice)
            .where(Notice.notice_id == notice_id)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_id(self, notice_id: int) -> bool:
        stmt = delete(Notice).where(Notice.notice_id == notice_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0


