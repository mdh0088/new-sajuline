"""
InquiryRepository - 상담사 문의 레포지토리 (관리자 백엔드)
"""
from __future__ import annotations

from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.inquiry_model import Inquiry
from src.models.counselor_model import Counselor
from src.models.user_model import User


COUNSELOR_TYPE = "COUNSELOR"
COUNSELOR_CS_CATEGORY = "CS_TO_ADMIN"


class InquiryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list_with_counselor(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        counselor_id: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Tuple[Inquiry, Counselor]], int]:
        """
        상담사 문의 목록 조회 + 상담사 조인
        - 고정 조건: inquirer_type='COUNSELOR' AND category='CS_TO_ADMIN'
        - 검색: all -> title OR content OR reply_content LIKE, 그 외 해당 필드만
        - 날짜 범위: created_at BETWEEN
        - 상담사 필터: inquirer_id == counselor_id
        - 정렬: created_at DESC
        """

        conditions = [
            Inquiry.inquirer_type == COUNSELOR_TYPE,
            Inquiry.category == COUNSELOR_CS_CATEGORY,
        ]

        if start_dt is not None:
            conditions.append(Inquiry.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Inquiry.created_at <= end_dt)

        if counselor_id:
            conditions.append(Inquiry.inquirer_id.like(f"%{counselor_id}%"))

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(
                        Inquiry.title.like(kw),
                        Inquiry.content.like(kw),
                        Inquiry.reply_content.like(kw),
                    )
                )
            elif search_type == "user_title":
                conditions.append(Inquiry.title.like(kw))
            elif search_type == "user_content":
                conditions.append(Inquiry.content.like(kw))
            elif search_type == "reply_content":
                conditions.append(Inquiry.reply_content.like(kw))

        stmt = select(Inquiry, Counselor).join(
            Counselor, Inquiry.inquirer_id == Counselor.counselor_id
        )
        count_stmt = select(func.count()).select_from(
            select(Inquiry.inquiry_id)
            .join(Counselor, Inquiry.inquirer_id == Counselor.counselor_id)
            .where(and_(*conditions))
            .subquery()
        )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(Inquiry.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(stmt)
        rows = list(result.all())

        count_result = await self.db.execute(count_stmt)
        total = int(count_result.scalar() or 0)

        return rows, total

    async def get_detail_with_counselor(self, inquiry_id: int) -> Optional[Tuple[Inquiry, Counselor]]:
        stmt = (
            select(Inquiry, Counselor)
            .join(Counselor, Inquiry.inquirer_id == Counselor.counselor_id)
            .where(
                and_(
                    Inquiry.inquiry_id == inquiry_id,
                    Inquiry.inquirer_type == COUNSELOR_TYPE,
                    Inquiry.category == COUNSELOR_CS_CATEGORY,
                )
            )
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()
        return row

    async def update_reply(self, inquiry_id: int, reply_content: str, answered_at: Optional[datetime] = None) -> bool:
        values = {"reply_content": reply_content}
        if answered_at is not None:
            values["answered_at"] = answered_at
        stmt = (
            update(Inquiry)
            .where(
                and_(
                    Inquiry.inquiry_id == inquiry_id,
                    Inquiry.inquirer_type == COUNSELOR_TYPE,
                    Inquiry.category == COUNSELOR_CS_CATEGORY,
                )
            )
            .values(**values)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def update_inquiry(self, inquiry_id: int, **values) -> bool:
        """문의 제목/내용/답변 수정 (조건 없이 모든 타입)"""
        stmt = (
            update(Inquiry)
            .where(Inquiry.inquiry_id == inquiry_id)
            .values(**values)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def delete_by_id(self, inquiry_id: int) -> bool:
        """문의 삭제 (조건 없이 모든 타입)"""
        stmt = delete(Inquiry).where(Inquiry.inquiry_id == inquiry_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_user_list_with_user(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        user_id: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Tuple[Inquiry, User]], int]:
        """
        사용자 1:1 문의 목록 + 사용자 조인
        - 고정 조건: inquirer_type='USER' AND category='USER_TO_ADMIN'
        """
        conditions = [
            Inquiry.inquirer_type == "USER",
            Inquiry.category == "USER_TO_ADMIN",
        ]

        if start_dt is not None:
            conditions.append(Inquiry.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Inquiry.created_at <= end_dt)
        if user_id:
            conditions.append(Inquiry.inquirer_id.like(f"%{user_id}%"))

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(Inquiry.title.like(kw), Inquiry.content.like(kw), Inquiry.reply_content.like(kw))
                )
            elif search_type == "title":
                conditions.append(Inquiry.title.like(kw))
            elif search_type == "content":
                conditions.append(Inquiry.content.like(kw))

        stmt = select(Inquiry, User).join(User, Inquiry.inquirer_id == User.user_id)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(desc(Inquiry.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        count_stmt = select(func.count()).select_from(
            select(Inquiry.inquiry_id)
            .join(User, Inquiry.inquirer_id == User.user_id)
            .where(and_(*conditions))
            .subquery()
        )

        result = await self.db.execute(stmt)
        rows = list(result.all())
        count_result = await self.db.execute(count_stmt)
        total = int(count_result.scalar() or 0)
        return rows, total

    async def get_user_detail_with_user(self, inquiry_id: int) -> Optional[Tuple[Inquiry, User]]:
        stmt = (
            select(Inquiry, User)
            .join(User, Inquiry.inquirer_id == User.user_id)
            .where(
                and_(
                    Inquiry.inquiry_id == inquiry_id,
                    Inquiry.inquirer_type == "USER",
                    Inquiry.category == "USER_TO_ADMIN",
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.one_or_none()

    async def get_user_to_cs_list(
        self,
        *,
        page: int,
        limit: int,
        search_type: Optional[str],
        search_name: Optional[str],
        user_id: Optional[str],
        counselor_id: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[Tuple[Inquiry, User, Counselor]], int]:
        """
        1:1 상담사문의 목록 (USER → CS)
        - 조건: inquirer_type='USER' AND category='USER_TO_CS'
        - 조인: t_inquiry.inquirer_id = t_user.user_id, t_inquiry.counselor_id = t_counselor.counselor_id
        """
        conditions = [
            Inquiry.inquirer_type == "USER",
            Inquiry.category == "USER_TO_CS",
        ]

        if start_dt is not None:
            conditions.append(Inquiry.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(Inquiry.created_at <= end_dt)
        if user_id:
            conditions.append(Inquiry.inquirer_id.like(f"%{user_id}%"))
        if counselor_id:
            conditions.append(Inquiry.counselor_id.like(f"%{counselor_id}%"))

        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(Inquiry.title.like(kw), Inquiry.content.like(kw), Inquiry.reply_content.like(kw))
                )
            elif search_type == "user_title":
                conditions.append(Inquiry.title.like(kw))
            elif search_type == "user_content":
                conditions.append(Inquiry.content.like(kw))
            elif search_type == "reply_content":
                conditions.append(Inquiry.reply_content.like(kw))

        stmt = (
            select(Inquiry, User, Counselor)
            .join(User, Inquiry.inquirer_id == User.user_id)
            .join(Counselor, Inquiry.counselor_id == Counselor.counselor_id)
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(desc(Inquiry.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        count_stmt = select(func.count()).select_from(
            select(Inquiry.inquiry_id)
            .join(User, Inquiry.inquirer_id == User.user_id)
            .join(Counselor, Inquiry.counselor_id == Counselor.counselor_id)
            .where(and_(*conditions))
            .subquery()
        )

        result = await self.db.execute(stmt)
        rows = list(result.all())
        count_result = await self.db.execute(count_stmt)
        total = int(count_result.scalar() or 0)
        return rows, total

    async def get_user_to_cs_detail(self, inquiry_id: int) -> Optional[Tuple[Inquiry, User, Counselor]]:
        stmt = (
            select(Inquiry, User, Counselor)
            .join(User, Inquiry.inquirer_id == User.user_id)
            .join(Counselor, Inquiry.counselor_id == Counselor.counselor_id)
            .where(
                and_(
                    Inquiry.inquiry_id == inquiry_id,
                    Inquiry.inquirer_type == "USER",
                    Inquiry.category == "USER_TO_CS",
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.one_or_none()


