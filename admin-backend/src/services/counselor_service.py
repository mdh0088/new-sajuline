"""
관리자 백엔드 상담사 서비스: 인증/로그인 최소 구현
"""
from typing import Tuple

from src.exceptions.custom_exceptions import AuthenticationError
from src.repositories.counselor_repository import CounselorRepository
from src.services.auth_service import AuthService


class CounselorService:
    """상담사 비즈니스 로직 (관리자)"""

    def __init__(self, counselor_repo: CounselorRepository, auth_service: AuthService):
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service

    async def login(self, counselor_id: str, password: str) -> Tuple[str, dict]:
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor or not counselor.password_hash:
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        if counselor.is_out:
            raise AuthenticationError("탈퇴한 상담사 계정입니다")

        if counselor.approved_at is None:
            raise AuthenticationError("승인되지 않은 상담사 계정입니다")

        if not self.auth_service.verify_password(password, counselor.password_hash):
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        access_token = self.auth_service.create_access_token(user_id=counselor.counselor_id, email=counselor.counselor_id, role="counselor")

        await self.counselor_repo.update_last_login(counselor.counselor_id)

        summary = {
            "user_id": counselor.counselor_id,
            "email": counselor.counselor_id,
            "nickname": counselor.nickname,
        }

        return access_token, summary


