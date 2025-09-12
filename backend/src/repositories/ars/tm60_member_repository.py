"""
TM60 멤버 Repository 클래스 (ARS 시스템 연동)
- MSSQL tm60_member 테이블 상태 업데이트 전용
"""
import asyncio
from typing import Optional

from sqlalchemy.orm import Session

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


