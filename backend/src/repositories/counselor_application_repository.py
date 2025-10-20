"""
상담사 지원 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.counselor_application_model import CounselorApplication
from src.common.logging import logger, get_logger_with_request_id


class CounselorApplicationRepository:
    """상담사 지원 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def create(self, application: CounselorApplication) -> CounselorApplication:
        """상담사 지원 생성"""
        log = get_logger_with_request_id()
        log.info("Creating counselor application", nickname=application.nickname)

        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)

        log.info("Counselor application created", application_id=application.application_id)
        return application

    @logger.catch(reraise=True)
    async def get_by_id(self, application_id: int) -> Optional[CounselorApplication]:
        """상담사 지원 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up counselor application", application_id=application_id)

        stmt = select(CounselorApplication).where(CounselorApplication.application_id == application_id)
        result = await self.db.execute(stmt)
        application = result.scalar_one_or_none()

        log.info("Counselor application lookup completed", application_id=application_id, found=application is not None)
        return application

    @logger.catch(reraise=True)
    async def exists_by_nickname(self, nickname: str) -> bool:
        """닉네임 중복 확인"""
        stmt = select(CounselorApplication).where(CounselorApplication.nickname == nickname)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @logger.catch(reraise=True)
    async def exists_by_email(self, email: str) -> bool:
        """이메일 중복 확인"""
        stmt = select(CounselorApplication).where(CounselorApplication.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @logger.catch(reraise=True)
    async def exists_by_phone(self, phone: str) -> bool:
        """전화번호 중복 확인"""
        stmt = select(CounselorApplication).where(CounselorApplication.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
