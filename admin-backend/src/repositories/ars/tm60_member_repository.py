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
        가장 최근 m_fdate 기준으로 우선 선택
        """
        code_list = list({c for c in codes if c})
        if not code_list:
            return {}
        rows: List[Tuple[str, str, Optional[datetime]]] = (
            self.db.query(Tm60Member.m_code, Tm60Member.m_state, Tm60Member.m_fdate)
            .filter(Tm60Member.m_code.in_(code_list))
            .all()
        )
        result: Dict[str, Tuple[str, Optional[datetime]]] = {}
        for code, state, fdate in rows:
            prev = result.get(code)
            if prev is None or (fdate and (prev[1] is None or fdate > prev[1])):
                result[code] = (state, fdate)
        return {k: v[0] for k, v in result.items()}

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


