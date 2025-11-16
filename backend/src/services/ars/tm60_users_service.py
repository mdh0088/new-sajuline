"""
TM60 사용자 서비스 (ARS 시스템 연동)
- 비즈니스 규칙 적용 및 저장소 호출 래퍼
"""
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.common.logging import get_logger_with_request_id


class Tm60UsersService:
    """TM60 사용자 관련 서비스"""

    def __init__(self, repo: Tm60UsersRepository):
        self.repo = repo

    async def create_user(self, user_id: str, phone: str | None, nickname: str | None) -> bool:
        """TM60 사용자 생성 (필드 정제 포함)"""
        log = get_logger_with_request_id()
        log.info("Creating TM60 user via service", user_id=user_id)
        return await self.repo.create(user_id=user_id, phone=phone or "", nickname=nickname or "")

    async def get_user_points(self, user_id: str) -> int:
        """TM60 사용자 포인트 조회"""
        return await self.repo.get_user_points(user_id)

    async def update_user_points(self, user_id: str, point_amount: int) -> int:
        """TM60 사용자 포인트 증가/감소 (증가: 양수, 감소: 음수)"""
        return await self.repo.update_user_points(user_id, point_amount)

    async def delete_user_by_phone(self, phone: str) -> bool:
        """TM60 사용자 삭제 (전화번호 기반)"""
        log = get_logger_with_request_id()
        log.info("Deleting TM60 user by phone via service", phone=phone)
        return await self.repo.delete_by_phone(phone)


