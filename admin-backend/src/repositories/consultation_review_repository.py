"""
상담 후기 Repository
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, or_, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.consultation_review_model import ConsultationReview
from src.models.user_model import User
from src.models.counselor_model import Counselor


class ConsultationReviewRepository:
    """상담 후기 Repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list_with_users(
        self,
        page: int,
        limit: int,
        search_type: str,
        search_name: Optional[str],
        user_id: Optional[str],
        counselor_id: Optional[str],
        start_dt: Optional[str],
        end_dt: Optional[str],
    ) -> tuple[list, int]:
        """
        후기 목록 조회 (User, Counselor JOIN)
        """
        # 기본 쿼리
        # user_nickname: User 테이블 JOIN 우선, 없으면 테이블의 user_nickname 사용
        stmt = (
            select(
                ConsultationReview,
                func.coalesce(User.nickname, ConsultationReview.user_nickname).label("user_nickname"),
                Counselor.nickname.label("counselor_nickname"),
            )
            .outerjoin(User, ConsultationReview.user_id == User.user_id)
            .outerjoin(Counselor, ConsultationReview.counselor_id == Counselor.counselor_id)
        )

        # 검색 조건
        conditions = []

        # 검색어 필터
        if search_name:
            if search_type == "all":
                conditions.append(
                    or_(
                        ConsultationReview.content.like(f"%{search_name}%"),
                        ConsultationReview.counselor_reply.like(f"%{search_name}%"),
                    )
                )
            elif search_type == "content":
                conditions.append(ConsultationReview.content.like(f"%{search_name}%"))
            elif search_type == "reply_content":
                conditions.append(ConsultationReview.counselor_reply.like(f"%{search_name}%"))

        # user_id 필터
        if user_id:
            conditions.append(ConsultationReview.user_id == user_id)

        # counselor_id 필터
        if counselor_id:
            conditions.append(ConsultationReview.counselor_id == counselor_id)

        # 날짜 범위 필터
        if start_dt:
            start_date = datetime.strptime(start_dt, "%Y-%m-%d")
            conditions.append(ConsultationReview.created_at >= start_date)
        if end_dt:
            end_date = datetime.strptime(end_dt, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            conditions.append(ConsultationReview.created_at <= end_date)

        # 조건 적용
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 전체 개수
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 페이징 및 정렬
        offset = (page - 1) * limit
        stmt = stmt.order_by(ConsultationReview.created_at.desc()).offset(offset).limit(limit)

        # 데이터 조회
        result = await self.session.execute(stmt)
        rows = result.all()

        # 결과 변환 (review, user_nickname, counselor_nickname)
        items = []
        for row in rows:
            review_dict = {
                **{c.name: getattr(row.ConsultationReview, c.name) for c in ConsultationReview.__table__.columns},
                "user_nickname": row.user_nickname,
                "counselor_nickname": row.counselor_nickname,
            }
            items.append(review_dict)

        return items, total

    async def get_by_id_with_users(self, review_id: int) -> Optional[dict]:
        """
        후기 상세 조회 (User, Counselor JOIN)
        """
        # user_nickname: User 테이블 JOIN 우선, 없으면 테이블의 user_nickname 사용
        stmt = (
            select(
                ConsultationReview,
                func.coalesce(User.nickname, ConsultationReview.user_nickname).label("user_nickname"),
                Counselor.nickname.label("counselor_nickname"),
            )
            .outerjoin(User, ConsultationReview.user_id == User.user_id)
            .outerjoin(Counselor, ConsultationReview.counselor_id == Counselor.counselor_id)
            .where(ConsultationReview.review_id == review_id)
        )

        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            return None

        # 결과 변환
        review_dict = {
            **{c.name: getattr(row.ConsultationReview, c.name) for c in ConsultationReview.__table__.columns},
            "user_nickname": row.user_nickname,
            "counselor_nickname": row.counselor_nickname,
        }

        return review_dict

    async def get_by_id(self, review_id: int) -> Optional[ConsultationReview]:
        """
        후기 단건 조회 (수정용)
        """
        stmt = select(ConsultationReview).where(ConsultationReview.review_id == review_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, review: ConsultationReview) -> ConsultationReview:
        """
        후기 수정
        """
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def create(self, review: ConsultationReview) -> ConsultationReview:
        """
        후기 생성
        """
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def get_next_dummy_session_id(self) -> int:
        """
        더미 리뷰용 session_id 생성 (0 또는 음수)
        session_id가 unique이므로 기존 더미 session_id 중 최솟값 - 1 반환
        """
        stmt = select(func.min(ConsultationReview.session_id)).where(
            ConsultationReview.session_id <= 0
        )
        result = await self.session.execute(stmt)
        min_session_id = result.scalar()

        if min_session_id is None:
            return 0  # 첫 더미 리뷰는 session_id = 0
        return min_session_id - 1  # 이후 더미 리뷰는 -1, -2, -3...