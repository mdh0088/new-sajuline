"""
tm60_member Repository (MSSQL) - 단일 클래스로 통합
"""
import asyncio
from typing import Optional, List, Dict, Tuple, Iterable
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from src.models.ars.tm60_member_model import Tm60Member


class Tm60MemberRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_latest_by_code(self, m_code: str) -> Optional[Tm60Member]:
        """m_code로 최근 가입순(m_fdate DESC) 단일 행 조회 (to_thread로 안전 실행)"""

        def _sync_get() -> Optional[Tm60Member]:
            q = self.db.query(Tm60Member).filter(Tm60Member.m_code == m_code)
            return q.first()

        return await asyncio.to_thread(_sync_get)

    def get_states_by_codes(self, codes: Iterable[str]) -> Dict[str, str]:
        """
        코드 목록으로 상태 맵 조회 { m_code: m_state }
        """
        code_list = list({c for c in codes if c})
        if not code_list:
            return {}
        rows = (
            self.db.query(Tm60Member.m_code, Tm60Member.m_state)
            .filter(Tm60Member.m_code.in_(code_list))
            .all()
        )
        # 단순 매핑: m_code -> m_state
        result = {code: state for code, state in rows if code and state}
        return result

    def update_state_by_code(self, *, m_code: str, m_state: str) -> bool:
        """m_code로 tm60_member.m_state 값을 갱신

        Returns: 업데이트가 1건 이상이면 True
        """
        if not m_code or not m_state:
            return False
        stmt = (
            update(Tm60Member)
            .where(Tm60Member.m_code == m_code)
            .values(m_state=m_state)
        )
        result = self.db.execute(stmt)
        affected = result.rowcount if hasattr(result, "rowcount") else 0
        if affected and affected > 0:
            self.db.commit()
            return True
        self.db.rollback()
        return False

    def update_tel_by_code(self, *, m_code: str, m_tel: str) -> bool:
        """m_code로 tm60_member.m_tel 값을 갱신

        Returns: 업데이트가 1건 이상이면 True
        """
        if not m_code or not m_tel:
            return False
        stmt = (
            update(Tm60Member)
            .where(Tm60Member.m_code == m_code)
            .values(m_tel=m_tel)
        )
        result = self.db.execute(stmt)
        affected = result.rowcount if hasattr(result, "rowcount") else 0
        if affected and affected > 0:
            self.db.commit()
            return True
        self.db.rollback()
        return False

    def create(self, member_data: dict) -> Tm60Member:
        """새 tm60_member 생성 (flush만 수행, commit은 외부에서)"""
        member = Tm60Member(**member_data)
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member


