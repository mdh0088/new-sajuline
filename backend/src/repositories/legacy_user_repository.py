"""
레거시 사용자 Repository 클래스
TBL_USER 테이블 대상
"""
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.legacy_user_model import LegacyUser
from src.common.logging import logger, get_logger_with_request_id


class LegacyUserRepository:
    """레거시 사용자 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def get_by_id(self, user_id: str) -> Optional[LegacyUser]:
        """사용자 ID로 조회"""
        log = get_logger_with_request_id()
        try:
            stmt = select(LegacyUser).where(LegacyUser.USER_ID == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                log.info("User found by ID", user_id=user_id, nickname=user.NICK_NAME)
            else:
                log.info("User not found by ID", user_id=user_id)

            return user
        except Exception as e:
            log.error("Error getting user by ID", user_id=user_id, error=str(e))
            raise

    @logger.catch(reraise=True)
    async def get_by_email(self, email: str) -> Optional[LegacyUser]:
        """이메일로 조회"""
        log = get_logger_with_request_id()
        try:
            stmt = select(LegacyUser).where(LegacyUser.EMAIL == email)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                log.info("User found by email", email=email, user_id=user.USER_ID)
            else:
                log.info("User not found by email", email=email)

            return user
        except Exception as e:
            log.error("Error getting user by email", email=email, error=str(e))
            raise

    @logger.catch(reraise=True)
    async def update_last_login(self, user_id: str) -> bool:
        """마지막 로그인 시간 업데이트"""
        log = get_logger_with_request_id()
        try:
            stmt = update(LegacyUser).where(
                LegacyUser.USER_ID == user_id
            ).values(
                LAST_LOGIN=datetime.utcnow(),
                UPDATE_DATE=datetime.utcnow()
            )

            result = await self.db.execute(stmt)
            await self.db.commit()

            success = result.rowcount > 0
            if success:
                log.info("Last login updated", user_id=user_id)
            else:
                log.warning("Failed to update last login", user_id=user_id)

            return success
        except Exception as e:
            log.error("Error updating last login", user_id=user_id, error=str(e))
            await self.db.rollback()
            return False