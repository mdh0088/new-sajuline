"""
TM60 멤버 Repository 클래스 (ARS 시스템 연동)
- MSSQL tm60_member 테이블 상태 업데이트 전용
"""
import asyncio
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.models.ars.tm60_member_model import Tm60Member
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class Tm60MemberRepository:
    """TM60 멤버 데이터 액세스 클래스 (ARS 시스템 연동)"""

    def __init__(self, mssql_session: Session):
        self.mssql_session = mssql_session

    @logger.catch(reraise=True)
    async def update_member_state_by_m_id(self, m_id: str, m_state: str) -> bool:
        """
        tm60_member.m_id 기준으로 m_state 업데이트
        - m_state: '1' | '2' | '3' 등 단일 문자
        Returns: 업데이트 성공 여부
        """
        log = get_logger_with_request_id()
        log.info("Updating tm60_member.m_state", m_id=m_id, m_state=m_state)

        def _sync_update() -> bool:
            try:
                # 존재하지 않는 컬럼으로 인한 SELECT 오류를 피하기 위해 직접 UPDATE 쿼리 수행
                affected = (
                    self.mssql_session.query(Tm60Member)
                    .filter(Tm60Member.m_id == m_id)
                    .update({Tm60Member.m_state: m_state}, synchronize_session=False)
                )
                if affected == 0:
                    log.warning("tm60_member not found", m_id=m_id)
                    self.mssql_session.rollback()
                    return False
                self.mssql_session.commit()
                log.info("tm60_member.m_state updated", m_id=m_id, m_state=m_state)
                return True
            except Exception as e:
                self.mssql_session.rollback()
                log.warning("tm60_member update failed", m_id=m_id, error=str(e))
                raise BaseAppException(f"ARS 멤버 상태 업데이트 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_update)

    @logger.catch(reraise=True)
    async def get_state_map_by_codes(self, m_codes: list[str], *, m_state: Optional[str] = None) -> dict[str, str]:
        """
        m_code 목록으로 tm60_member 조회하여 { m_code: m_state } 매핑 반환
        - 선택적으로 m_state 조건 적용
        - 다중 결과가 있을 경우 가장 최근 가입일(m_fdate) 우선
        """
        log = get_logger_with_request_id()
        log.info("Fetching tm60_member state map by codes", count=len(m_codes), m_state=m_state)

        def _sync_get_map() -> dict[str, str]:
            try:
                if not m_codes:
                    return {}
                q = (
                    self.mssql_session.query(Tm60Member.m_code, Tm60Member.m_state, Tm60Member.m_fdate)
                    .filter(Tm60Member.m_code.in_(m_codes))
                )
                if m_state is not None:
                    q = q.filter(Tm60Member.m_state == m_state)
                rows = q.all()
                # 최신 m_fdate 우선으로 집계
                result: dict[str, tuple[str, Optional[datetime]]] = {}
                for code, state, fdate in rows:
                    prev = result.get(code)
                    if prev is None or (fdate and prev[1] and fdate > prev[1]) or (prev is None):
                        result[code] = (state, fdate)
                return {k: v[0] for k, v in result.items()}
            except Exception as e:
                log.warning("Failed to fetch tm60_member state map", error=str(e))
                return {}

        return await asyncio.to_thread(_sync_get_map)

    @logger.catch(reraise=True)
    async def get_all_members_state(self) -> list[dict[str, str]]:
        """
        전체 tm60_member 조회하여 m_code, m_state 목록 반환
        - 중복 m_code가 있을 경우 최신 m_fdate 우선
        Returns: [{"m_code": "001", "m_state": "1"}, ...]
        """
        log = get_logger_with_request_id()
        log.info("Fetching all tm60_members state")

        def _sync_get_all() -> list[dict[str, str]]:
            try:
                from datetime import datetime
                rows = (
                    self.mssql_session.query(Tm60Member.m_code, Tm60Member.m_state, Tm60Member.m_fdate)
                    .all()
                )
                # 중복 m_code 처리: 최신 m_fdate 우선
                result: dict[str, tuple[str, Optional[datetime]]] = {}
                for code, state, fdate in rows:
                    prev = result.get(code)
                    if prev is None or (fdate and prev[1] and fdate > prev[1]):
                        result[code] = (state, fdate)
                items = [{"m_code": k, "m_state": v[0]} for k, v in result.items()]
                log.info("All tm60_members state fetched", count=len(items))
                return items
            except Exception as e:
                log.warning("Failed to fetch all tm60_members state", error=str(e))
                return []

        return await asyncio.to_thread(_sync_get_all)


