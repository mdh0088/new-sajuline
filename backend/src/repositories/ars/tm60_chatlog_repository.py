"""
TM60 채팅로그 Repository 클래스
ARS 시스템 연동 - MSSQL tm60_chatlog 테이블 전용 (읽기 전용)
"""
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.ars.tm60_chatlog_model import Tm60Chatlog
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class Tm60ChatlogRepository:
    """TM60 채팅로그 데이터 액세스 클래스 (ARS 시스템 연동, 읽기 전용)"""
    
    def __init__(self, mssql_session: Session):
        """MSSQL 세션 주입"""
        self.mssql_session = mssql_session
    
    @logger.catch(reraise=True)
    async def get_consultation_count_by_user_id(self, user_id: str) -> int:
        """
        사용자 ID별 상담 내역 수 조회
        조건: usepoint 필드가 0 이상이어야 함
        """
        log = get_logger_with_request_id()
        log.info("Getting consultation count for user", user_id=user_id)
        
        def _sync_get_consultation_count() -> int:
            """동기 MSSQL 조회"""
            try:
                count = (
                    self.mssql_session.query(func.count(Tm60Chatlog.idx))
                    .filter(
                        and_(
                            Tm60Chatlog.u_id == user_id,
                            Tm60Chatlog.usepoint >= 0
                        )
                    )
                    .scalar()
                ) or 0
                
                log.info(
                    "Consultation count retrieved", 
                    user_id=user_id, 
                    count=count
                )
                return count
                
            except Exception as e:
                log.warning(
                    "Failed to get consultation count", 
                    user_id=user_id, 
                    error=str(e)
                )
                raise BaseAppException(
                    f"상담 내역 수 조회 실패: {str(e)}", 
                    status_code=500
                )
        
        try:
            # 스레드 풀에서 동기 작업 실행하여 이벤트 루프 블로킹 방지
            return await asyncio.to_thread(_sync_get_consultation_count)
        except BaseAppException:
            # 기존 예외는 그대로 재발생
            raise
        except Exception as e:
            log.warning(
                "Failed to get consultation count", 
                user_id=user_id, 
                error=str(e)
            )
            raise BaseAppException(
                f"상담 내역 수 조회 실패: {str(e)}", 
                status_code=500
            )