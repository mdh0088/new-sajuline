"""
관리자 백엔드 TM60 사용자 Repository (MSSQL: tm60_users)
"""
import asyncio
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from src.models.ars.tm60_users_model import Tm60Users


class Tm60UsersRepository:
    def __init__(self, mssql: Session):
        self.mssql = mssql

    async def find_by_user_ids(self, user_ids: List[str]) -> Dict[str, List[Tm60Users]]:
        """여러 user_id(u_id)로 tm60_users를 일괄 조회하여 매핑 반환
        반환 형식: { user_id: [Tm60Users, ...] }
        동기 세션을 스레드풀에서 실행하여 비동기 루프 블로킹 방지
        """

        ids = [uid for uid in set(user_ids) if uid]
        if not ids:
            return {}

        def _sync_query() -> Dict[str, List[Tm60Users]]:
            rows: List[Tm60Users] = (
                self.mssql.query(Tm60Users)
                .filter(Tm60Users.u_id.in_(ids))
                .all()
            )
            result: Dict[str, List[Tm60Users]] = {}
            for r in rows:
                result.setdefault(r.u_id, []).append(r)
            return result

        return await asyncio.to_thread(_sync_query)

    async def find_all_by_user_id(self, user_id: str) -> List[Tm60Users]:
        """단일 user_id(u_id)로 tm60_users 전체 행 조회"""

        if not user_id:
            return []

        def _sync_query() -> List[Tm60Users]:
            return (
                self.mssql.query(Tm60Users)
                .filter(Tm60Users.u_id == user_id)
                .all()
            )

        return await asyncio.to_thread(_sync_query)

    async def adjust_points(self, user_id: str, delta: int) -> int:
        """u_point 증감 후 잔액 반환 (음수면 차감)"""
        if not user_id or delta == 0:
            return 0

        def _sync_update() -> int:
            user = self.mssql.query(Tm60Users).filter(Tm60Users.u_id == user_id).first()
            if not user:
                return -1
            new_points = (user.u_point or 0) + delta
            if new_points < 0:
                # 차감 시 음수 불가 → 0 아래로 내려가면 실패 의미로 -2 반환
                return -2
            user.u_point = new_points
            self.mssql.flush()
            self.mssql.commit()
            return new_points

        return await asyncio.to_thread(_sync_update)


