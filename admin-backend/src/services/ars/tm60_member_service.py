"""
TM60 멤버 서비스 (MSSQL)
- 단일 클래스: 조회(get_member_by_code) + 상태 변경(update_state_by_code)
"""
from typing import Optional

from src.models.ars.tm60_member_model import Tm60Member
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository


class Tm60MemberService:
    def __init__(self, repo: Tm60MemberRepository):
        self.repo = repo

    async def get_member_by_code(self, m_code: str) -> Optional[Tm60Member]:
        return await self.repo.get_latest_by_code(m_code)

    def update_state_by_code(self, *, m_code: str, m_state: str) -> bool:
        if not m_code or not m_state:
            return False
        if m_state not in {"1", "2", "3"}:
            return False
        return self.repo.update_state_by_code(m_code=m_code, m_state=m_state)

    def update_tel_by_code(self, *, m_code: str, m_tel: str) -> bool:
        """m_code로 tm60_member.m_tel 값을 갱신"""
        if not m_code or not m_tel:
            return False
        return self.repo.update_tel_by_code(m_code=m_code, m_tel=m_tel)

    def update_prate_by_code(self, *, m_code: str, m_prate: int) -> bool:
        """m_code로 tm60_member.m_prate 값을 갱신"""
        if not m_code or m_prate is None:
            return False
        return self.repo.update_prate_by_code(m_code=m_code, m_prate=m_prate)


