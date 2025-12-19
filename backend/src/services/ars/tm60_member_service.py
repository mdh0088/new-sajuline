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

    async def sync_state_from_counselor_status(self, counselor_code: str, counselor_status: str) -> bool:
        """
        상담사 상태 → TM60 멤버 m_state 매핑 및 동기화
        - counselor_code: t_counselor.counselor_code = tm60_member.m_code
        - 매핑: 1=WAITING, 2=CONSULTING, 3=ABSENT
        """
        log = get_logger_with_request_id()
        if not counselor_code:
            log.warning("counselor_code is empty, skipping sync")
            return False
        status_map = {
            'WAITING': '1',
            'CONSULTING': '2',
            'ABSENT': '3'
        }
        m_state = status_map.get(counselor_status)
        if not m_state:
            log.warning("Unknown counselor_status for mapping", counselor_status=counselor_status)
            return False
        return await self.repo.update_member_state_by_m_code(counselor_code, m_state)

    async def get_state_map_by_codes(self, m_codes: list[str], m_state: Optional[str] = None) -> dict[str, str]:
        """m_code 목록에 대한 상태 매핑 조회 (선택적으로 상태 필터)"""
        return await self.repo.get_state_map_by_codes(m_codes, m_state=m_state)

    async def get_all_members_state(self) -> list[dict[str, str]]:
        """전체 tm60_member 상태 목록 조회"""
        return await self.repo.get_all_members_state()

    async def get_state_by_code(self, m_code: str) -> Optional[str]:
        """단일 m_code로 m_state 조회"""
        if not m_code:
            return None
        state_map = await self.repo.get_state_map_by_codes([m_code])
        return state_map.get(m_code)


