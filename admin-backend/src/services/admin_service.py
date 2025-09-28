"""
관리자 서비스: 인증 및 로그인 로직
"""
from typing import Tuple

from src.exceptions.custom_exceptions import AuthenticationError
from src.repositories.admin_repository import AdminRepository
from src.services.auth_service import AuthService


class AdminService:
    """관리자 비즈니스 로직 서비스"""

    def __init__(self, admin_repo: AdminRepository, auth_service: AuthService):
        self.admin_repo = admin_repo
        self.auth_service = auth_service

    async def login(self, login_id: str, password: str) -> Tuple[str, dict]:
        admin = await self.admin_repo.get_by_login_id(login_id)
        if not admin or not admin.password_hash:
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        if not admin.is_active:
            raise AuthenticationError("비활성화된 관리자 계정입니다")

        if not self.auth_service.verify_password(password, admin.password_hash):
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        # JWT 발급 (role=admin)
        access_token = self.auth_service.create_access_token(user_id=admin.admin_id, email=admin.email, role="admin")

        # 최근 로그인 갱신
        await self.admin_repo.update_last_login(admin.admin_id)

        # 응답용 요약
        summary = {
            "user_id": admin.login_id,
            "email": admin.email,
            "nickname": admin.name,
        }

        return access_token, summary


