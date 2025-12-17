"""
TM60 Mobile 서비스 (ARS 시스템 연동)
- 포인트 상담 전화 연결 시 모바일 플랫폼 정보 기록
"""
from src.repositories.ars.tm60_mobile_repository import Tm60MobileRepository
from src.common.logging import get_logger_with_request_id


class Tm60MobileService:
    """TM60 Mobile 통화 기록 관련 서비스"""

    def __init__(self, repo: Tm60MobileRepository):
        self.repo = repo

    async def register_call(self, user_id: str, counselor_code: str, platform: str) -> bool:
        """
        포인트 상담 전화 연결 시 통화 기록 등록
        - 레거시 PHP call_by_point 로직과 동일
        """
        log = get_logger_with_request_id()
        log.info("Registering call by point via service", user_id=user_id, counselor_code=counselor_code, platform=platform)
        return await self.repo.create(mb_id=user_id, mb_code=counselor_code, mb_platform=platform)

    async def get_recent_calls(self, user_id: str, limit: int = 10) -> list:
        """특정 유저의 최근 통화 기록 조회"""
        records = await self.repo.get_recent_by_user_id(user_id, limit)
        return [record.to_dict() for record in records]

    async def get_call_count(self, user_id: str) -> int:
        """특정 유저의 통화 기록 수 조회"""
        return await self.repo.get_count_by_user_id(user_id)
