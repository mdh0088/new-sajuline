"""
TM60 멤버 서비스 (ARS 시스템 연동)
- 비즈니스 규칙/매핑 적용 후 저장소 호출
"""
from typing import Optional

from sqlalchemy.orm import Session

from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.common.logging import get_logger_with_request_id


class Tm60MemberService:
    """TM60 멤버 상태 관련 서비스"""

    def __init__(self, repo: Tm60MemberRepository):
        self.repo = repo

    async def sync_state_from_counselor_status(self, counselor_id: str, counselor_status: str) -> bool:
        """
        상담사 상태 → TM60 멤버 m_state 매핑 및 동기화
        매핑: 1=WAITING, 2=CONSULTING, 3=ABSENT
        """
        log = get_logger_with_request_id()
        status_map = {
            'WAITING': '1',
            'CONSULTING': '2',
            'ABSENT': '3'
        }
        m_state = status_map.get(counselor_status)
        if not m_state:
            log.warning("Unknown counselor_status for mapping", counselor_status=counselor_status)
            return False
        return await self.repo.update_member_state_by_m_id(counselor_id, m_state)

    async def get_state_map_by_codes(self, m_codes: list[str], m_state: Optional[str] = None) -> dict[str, str]:
        """m_code 목록에 대한 상태 매핑 조회 (선택적으로 상태 필터)"""
        return await self.repo.get_state_map_by_codes(m_codes, m_state=m_state)


