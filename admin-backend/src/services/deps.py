"""
서비스/레포 의존성 주입 도우미
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db as get_db_maria
from src.repositories.admin_repository import AdminRepository
from src.repositories.counselor_repository import CounselorRepository
from src.services.admin_service import AdminService
from src.services.counselor_service import CounselorService
from src.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    return AuthService()


def get_admin_repository(db: AsyncSession = Depends(get_db_maria)) -> AdminRepository:
    return AdminRepository(db)


def get_counselor_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorRepository:
    return CounselorRepository(db)


def get_admin_service(
    admin_repo: AdminRepository = Depends(get_admin_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminService:
    return AdminService(admin_repo, auth_service)


def get_counselor_service(
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> CounselorService:
    return CounselorService(counselor_repo, auth_service)


