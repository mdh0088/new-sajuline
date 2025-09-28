"""
tm60_member Repository (MSSQL 동기 세션)
"""
from typing import Dict, Iterable

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.ars.tm60_member_model import Tm60Member


class Tm60MemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_states_by_codes(self, codes: Iterable[str]) -> Dict[str, str]:
        code_list = list({c for c in codes if c})
        if not code_list:
            return {}
        stmt = select(Tm60Member.m_code, Tm60Member.m_state).where(Tm60Member.m_code.in_(code_list))
        rows = self.db.execute(stmt).all()
        return {row[0]: row[1] for row in rows}


