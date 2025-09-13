"""
상담사 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.counselor_model import Counselor
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
    async def update_last_login(self, counselor_id: str) -> bool:
        """마지막 로그인 시간 업데이트"""
        from sqlalchemy import update
        from datetime import datetime
        
        stmt = (
            update(Counselor)
            .where(Counselor.counselor_id == counselor_id)
            .values(
                last_login_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
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