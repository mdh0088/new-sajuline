"""
Auth 도메인 Provider

레포지토리/서비스 의존성 주입 표준화
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session as SyncSession

from ...common.database.session import get_db
from ...common.database.mssql_session import get_mssql_db
from ...common.dependencies.providers import get_redis
from ..domain.ports import AuthRepositoryPort
from ..infrastructure.repositories import HybridAuthRepository
from ..application.services import AuthApplicationService
from ..application.social_auth_service import SocialAuthApplicationService
from ...user.domain.ports import UserRepositoryPort
from ...user.infrastructure.providers import get_user_repository
from ...counselor.domain.ports import CounselorRepositoryPort
from ...counselor.infrastructure.providers import get_counselor_repository
from src.ars.infrastructure.repositories import MSSQLARSUserRepository


async def get_auth_repository(
    db_session: AsyncSession = Depends(get_db),
    redis_client = Depends(get_redis),
):
    return HybridAuthRepository(db_session, redis_client)


async def get_auth_service(
    auth_repo: AuthRepositoryPort = Depends(get_auth_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    mssql_session: SyncSession = Depends(get_mssql_db),
    counselor_repo: CounselorRepositoryPort = Depends(get_counselor_repository),
) -> AuthApplicationService:
    ars_repo = MSSQLARSUserRepository(mssql_session)
    return AuthApplicationService(auth_repo, user_repo, ars_repo, counselor_repo)


async def get_social_auth_service(
    auth_repo: AuthRepositoryPort = Depends(get_auth_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    mssql_session: SyncSession = Depends(get_mssql_db),
    counselor_repo: CounselorRepositoryPort = Depends(get_counselor_repository),
) -> SocialAuthApplicationService:
    ars_repo = MSSQLARSUserRepository(mssql_session)
    auth_service = AuthApplicationService(auth_repo, user_repo, ars_repo, counselor_repo)
    return SocialAuthApplicationService(auth_repo, user_repo, ars_repo, auth_service)


