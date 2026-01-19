"""
User 도메인 Provider

레포지토리/서비스 의존성 주입 표준화
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...common.database.session import get_db
from ..application.services import UserApplicationService
from .repositories import MariaDBUserRepository


async def get_user_repository(
    db_session: AsyncSession = Depends(get_db),
):
    return MariaDBUserRepository(db_session)


async def get_user_service(
    user_repository = Depends(get_user_repository),
) -> UserApplicationService:
    return UserApplicationService(user_repository)


