"""
상담사 신청 Repository - t_counselor_application 접근 (관리자 백엔드)
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func, desc

from src.models.counselor_application_model import CounselorApplication


class CounselorApplicationRepository:
    """상담사 신청 데이터 접근 레이어 (관리자)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, application_id: int) -> Optional[CounselorApplication]:
        """신청 ID로 단건 조회"""
        stmt = select(CounselorApplication).where(
            CounselorApplication.application_id == application_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[CounselorApplication]:
        """이메일로 단건 조회"""
        stmt = select(CounselorApplication).where(
            CounselorApplication.email == email
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def partial_update(
        self,
        application_id: int,
        **fields,
    ) -> bool:
        """부분 업데이트. None 값은 무시.

        사용 예:
        await repo.partial_update(
            application_id=1,
            application_status="APPROVED",
            admin_note="승인 완료",
        )
        """
        updates = {k: v for k, v in fields.items() if v is not None}
        if not updates:
            return False
        updates["updated_at"] = datetime.utcnow()
        stmt = (
            update(CounselorApplication)
            .where(CounselorApplication.application_id == application_id)
            .values(**updates)
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
        application_status: str | None,
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> Tuple[List[CounselorApplication], int]:
        """상담사 신청 목록 조회 (페이징)

        - 기본 정렬: created_at DESC
        - specialty_types: JSON 문자열 내 값 OR 매칭 (예: %"TARO"%)
        - search_type=all: name/nickname/email OR LIKE
        - start_dt/end_dt: created_at BETWEEN
        - application_status: PENDING|APPROVED|REJECTED 필터
        """
        conditions = []

        # 신청 상태 필터
        if application_status:
            conditions.append(CounselorApplication.application_status == application_status)

        # 날짜 범위 필터
        if start_dt is not None:
            conditions.append(CounselorApplication.created_at >= start_dt)
        if end_dt is not None:
            conditions.append(CounselorApplication.created_at <= end_dt)

        # 검색 조건
        if search_name:
            kw = f"%{search_name}%"
            if not search_type or search_type == "all":
                conditions.append(
                    or_(
                        CounselorApplication.name.like(kw),
                        CounselorApplication.nickname.like(kw),
                        CounselorApplication.email.like(kw),
                    )
                )
            elif search_type == "name":
                conditions.append(CounselorApplication.name.like(kw))
            elif search_type == "nickname":
                conditions.append(CounselorApplication.nickname.like(kw))
            elif search_type == "email":
                conditions.append(CounselorApplication.email.like(kw))

        # 전문 분야 필터
        if specialties:
            like_clauses = []
            for sp in specialties:
                if sp:
                    like_clauses.append(CounselorApplication.specialty_types.like(f'%"{sp}"%'))
            if like_clauses:
                conditions.append(or_(*like_clauses))

        # 메인 쿼리
        stmt = select(CounselorApplication)
        count_stmt = select(func.count(CounselorApplication.application_id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        # 정렬 및 페이징
        stmt = stmt.order_by(desc(CounselorApplication.created_at))
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        # 실행
        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = list(result.scalars().all())
        total = count_result.scalar() or 0
        return items, total
