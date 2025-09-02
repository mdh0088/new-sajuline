"""
상담사 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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