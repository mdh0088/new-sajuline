"""
상담사 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Dict
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from src.models.counselor_model import Counselor

KST = ZoneInfo("Asia/Seoul")
from src.common.logging import logger, get_logger_with_request_id


class CounselorRepository:
    """상담사 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def exists_by_counselor_id(self, counselor_id: str) -> bool:
        """상담사 ID/EMAIL 존재 여부 확인"""
        stmt = select(Counselor.counselor_id).where(Counselor.counselor_id == counselor_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def exists_by_nickname(self, nickname: str) -> bool:
        """상담사 닉네임 존재 여부 확인"""
        stmt = select(Counselor.counselor_id).where(Counselor.nickname == nickname)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def exists_by_phone(self, phone: str) -> bool:
        """상담사 전화번호 존재 여부 확인"""
        stmt = select(Counselor.counselor_id).where(Counselor.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def get_by_id(self, counselor_id: str) -> Optional[Counselor]:
        """상담사 ID로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up counselor by ID", counselor_id=counselor_id)

        stmt = select(Counselor).where(Counselor.counselor_id == counselor_id)
        result = await self.db.execute(stmt)
        counselor = result.scalar_one_or_none()

        log.info("Counselor lookup completed", counselor_id=counselor_id, found=counselor is not None)
        return counselor

    @logger.catch(reraise=True)
    async def get_by_nickname(self, nickname: str) -> Optional[Counselor]:
        """상담사 닉네임으로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up counselor by nickname", nickname=nickname)

        stmt = select(Counselor).where(Counselor.nickname == nickname)
        result = await self.db.execute(stmt)
        counselor = result.scalar_one_or_none()

        log.info("Counselor lookup completed", nickname=nickname, found=counselor is not None)
        return counselor
    
    @logger.catch(reraise=True)
    async def update_last_login(self, counselor_id: str) -> bool:
        """마지막 로그인 시간 업데이트"""
        stmt = (
            update(Counselor)
            .where(Counselor.counselor_id == counselor_id)
            .values(
                last_login_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    @logger.catch(reraise=True)
    async def partial_update(
        self,
        counselor_id: str,
        *,
        counselor_status: Optional[str] = None,
        work_time: Optional[str] = None,
        introduction_short: Optional[str] = None,
        greeting_message: Optional[str] = None,
        career_info: Optional[str] = None
    ) -> bool:
        """전달된 값만 부분 업데이트"""
        from src.models.counselor_model import Counselor
        update_values = {}
        if counselor_status is not None:
            update_values[Counselor.counselor_status.key] = counselor_status
        if work_time is not None:
            update_values[Counselor.work_time.key] = work_time
        if introduction_short is not None:
            update_values[Counselor.introduction_short.key] = introduction_short
        if greeting_message is not None:
            update_values[Counselor.greeting_message.key] = greeting_message
        if career_info is not None:
            update_values[Counselor.career_info.key] = career_info

        if not update_values:
            return False

        stmt = (
            update(Counselor)
            .where(Counselor.counselor_id == counselor_id)
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    @logger.catch(reraise=True)
    async def get_by_counselor_code(self, counselor_code: str) -> Optional[Counselor]:
        """상담사 코드로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up counselor by code", counselor_code=counselor_code)
        stmt = select(Counselor).where(Counselor.counselor_code == counselor_code)
        result = await self.db.execute(stmt)
        counselor = result.scalar_one_or_none()
        log.info(
            "Counselor lookup completed",
            counselor_code=counselor_code,
            found=counselor is not None
        )
        return counselor

    @logger.catch(reraise=True)
    async def get_by_counselor_codes(self, counselor_codes: List[str]) -> Dict[str, Counselor]:
        """상담사 코드 목록으로 일괄 조회하여 매핑 반환"""
        if not counselor_codes:
            return {}
        stmt = select(Counselor).where(Counselor.counselor_code.in_(counselor_codes))
        result = await self.db.execute(stmt)
        counselors: List[Counselor] = list(result.scalars().all())
        return {c.counselor_code: c for c in counselors}

    @logger.catch(reraise=True)
    async def update_status_by_code(
        self,
        counselor_code: str,
        new_status: str
    ) -> tuple[bool, str | None]:
        """
        counselor_code로 상담사 상태 업데이트
        Returns: (성공여부, 이전 상태값)
        """
        log = get_logger_with_request_id()
        log.info("Updating counselor status by code", counselor_code=counselor_code, new_status=new_status)

        # 현재 상태 조회
        stmt = select(Counselor.counselor_id, Counselor.counselor_status).where(
            Counselor.counselor_code == counselor_code
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()

        if not row:
            log.warning("Counselor not found by code", counselor_code=counselor_code)
            return False, None

        counselor_id, old_status = row

        # 상태가 동일하면 업데이트 불필요
        if old_status == new_status:
            return True, old_status

        # 업데이트 실행
        update_stmt = (
            update(Counselor)
            .where(Counselor.counselor_code == counselor_code)
            .values(counselor_status=new_status)
            .execution_options(synchronize_session="evaluate")
        )
        await self.db.execute(update_stmt)

        log.info("Counselor status updated", counselor_code=counselor_code, old_status=old_status, new_status=new_status)
        return True, old_status

    @logger.catch(reraise=True)
    async def get_counselor_id_by_code(self, counselor_code: str) -> str | None:
        """counselor_code로 counselor_id 조회"""
        stmt = select(Counselor.counselor_id).where(Counselor.counselor_code == counselor_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    @logger.catch(reraise=True)
    async def find_codes_by_filters(
        self,
        *,
        is_best: Optional[bool] = None,
        is_new: Optional[bool] = None,
        cs_specialties: Optional[List[str]] = None,
        cs_keywords: Optional[List[str]] = None,
        search_name: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        공개 검색용: t_counselor에서 기본 노출 조건과 필터를 적용하여
        counselor_code / counselor_id 목록을 반환합니다.

        - is_out = false AND is_show = true
        - is_best, is_new (옵션)
        - specialty_types: 문자열(JSON) LIKE 매칭 (예: %"TARO"%)
        - keywords: 쉼표 구분 문자열 LIKE 매칭
        - search_name: nickname LIKE
        """
        log = get_logger_with_request_id()
        log.info(
            "Searching counselor codes by filters",
            is_best=is_best,
            is_new=is_new,
            cs_specialties=cs_specialties,
            cs_keywords=cs_keywords,
            search_name=search_name,
        )

        stmt = select(Counselor.counselor_code, Counselor.counselor_id).where(
            and_(
                Counselor.is_out.is_(False),
                Counselor.is_show.is_(True),
            )
        )

        if is_best is not None:
            stmt = stmt.where(Counselor.is_best.is_(is_best))
        if is_new is not None:
            stmt = stmt.where(Counselor.is_new.is_(is_new))

        # specialty_types LIKE match for each entry
        if cs_specialties:
            specs = [s for s in cs_specialties if s]
            if specs:
                like_clauses = []
                for sp in specs:
                    # JSON 문자열 내 값 매칭: "TARO"
                    like_clauses.append(Counselor.specialty_types.like(f'%"{sp}"%'))
                # 다중 전문분야는 OR 매칭 (선택한 것 중 하나라도 포함)
                stmt = stmt.where(or_(*like_clauses))

        # keywords LIKE match: nickname OR keywords에서 각 키워드를 OR 검색
        if cs_keywords:
            kws = [k for k in cs_keywords if k]
            if kws:
                kw_clauses = []
                for k in kws:
                    # 각 키워드마다 (nickname OR keywords) 조건 추가
                    kw_clauses.append(
                        or_(
                            Counselor.nickname.like(f"%{k}%"),
                            Counselor.keywords.like(f"%{k}%")
                        )
                    )
                # 모든 키워드 조건을 OR로 연결
                stmt = stmt.where(or_(*kw_clauses))

        if search_name:
            # nickname OR keywords LIKE 검색 (OR 조건)
            stmt = stmt.where(
                or_(
                    Counselor.nickname.like(f"%{search_name}%"),
                    Counselor.keywords.like(f"%{search_name}%")
                )
            )

        result = await self.db.execute(stmt)
        rows = list(result.all())
        items: List[Dict[str, str]] = [
            {"counselor_code": r[0], "counselor_id": r[1]} for r in rows
        ]
        log.info("Counselor code search completed", count=len(items))
        return items