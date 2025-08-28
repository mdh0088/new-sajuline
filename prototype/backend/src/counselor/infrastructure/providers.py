"""
Counselor 도메인 Provider
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...common.database.session import get_db
from ..application.services import CounselorAuthApplicationService
from ..infrastructure.repositories import MariaDBCounselorRepository


async def get_counselor_repository(
    db_session: AsyncSession = Depends(get_db),
):
    return MariaDBCounselorRepository(db_session)


async def get_counselor_auth_service(
    repo = Depends(get_counselor_repository),
):
    return CounselorAuthApplicationService(repo)


