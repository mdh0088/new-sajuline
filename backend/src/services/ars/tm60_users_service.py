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
        """TM60 사용자 포인트 조회 - 임시로 MariaDB TBL_USER.MILEAGE 사용"""
        from src.repositories.user_repository import UserRepository
        from src.common.database.mariadb_manager import get_mariadb_session

        # MariaDB에서 MILEAGE 조회 (임시 해결책)
        try:
            session = get_mariadb_session()
            user_repo = UserRepository(session)
            user = await user_repo.get_by_id(user_id)
            if user and hasattr(user, 'mileage'):
                return user.mileage or 0
            return 0
        except Exception as e:
            log = get_logger_with_request_id()
            log.warning("Failed to get user points from MariaDB, falling back to MSSQL", user_id=user_id, error=str(e))
            # 실패시 기존 MSSQL 방식으로 폴백
            return await self.repo.get_user_points(user_id)

    async def update_user_points(self, user_id: str, point_amount: int) -> int:
        """TM60 사용자 포인트 증가/감소 (증가: 양수, 감소: 음수)"""
        return await self.repo.update_user_points(user_id, point_amount)


