"""
TM60 사용자 Repository 클래스
ARS 시스템 연동 - MSSQL tm60_users 테이블 전용
"""
import asyncio
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.ars.tm60_users_model import Tm60Users
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class Tm60UsersRepository:
    """TM60 사용자 데이터 액세스 클래스 (ARS 시스템 연동)"""
    
    def __init__(self, mssql_session: Session):
        """MSSQL 세션 주입"""
        self.mssql_session = mssql_session
    
    @logger.catch(reraise=True)
    async def create(self, user_id: str, phone: str, nickname: str) -> bool:
        """
        TM60 사용자 생성 (ARS 시스템 연동)
        스레드 풀에서 동기 MSSQL 작업 실행하여 이벤트 루프 블로킹 방지
        """
        log = get_logger_with_request_id()
        log.info("Creating TM60 user", user_id=user_id, phone=phone)
        
        def _sync_create_tm60() -> bool:
            """동기 MSSQL 작업"""
            try:
                tm60_user = Tm60Users(
                    u_id=user_id,
                    u_tel=phone or "",
                    u_kname=nickname or "",  # 빈 문자열로 처리
                    u_passwd="",  # 빈 문자열 (프로토타입 로직 따름)
                    regdate=datetime.utcnow(),
                    u_fdate=datetime.utcnow(),
                    # 기본값들은 모델에서 자동 설정됨
                )
                
                self.mssql_session.add(tm60_user)
                self.mssql_session.flush()
                self.mssql_session.commit()
                
                log.info("TM60 user created successfully", user_id=user_id, tm60_idx=tm60_user.idx)
                return True
                
            except Exception as e:
                log.warning("TM60 user creation failed", user_id=user_id, error=str(e))
                self.mssql_session.rollback()
                raise BaseAppException(f"ARS 시스템 사용자 생성 실패: {str(e)}", status_code=500)
        
        try:
            # 스레드 풀에서 동기 작업 실행하여 이벤트 루프 블로킹 방지
            return await asyncio.to_thread(_sync_create_tm60)
        except BaseAppException:
            # 기존 예외는 그대로 재발생
            raise
        except Exception as e:
            log.warning("TM60 user creation failed", user_id=user_id, error=str(e))
            raise BaseAppException(f"ARS 시스템 사용자 생성 실패: {str(e)}", status_code=500)
    
    @logger.catch(reraise=True)
    async def get_by_user_id(self, user_id: str) -> Optional[Tm60Users]:
        """사용자 ID로 TM60 사용자 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up TM60 user by user ID", user_id=user_id)
        
        def _sync_get_by_user_id() -> Optional[Tm60Users]:
            """동기 MSSQL 조회"""
            try:
                tm60_user = self.mssql_session.query(Tm60Users).filter(Tm60Users.u_id == user_id).first()
                log.info("TM60 user lookup completed", user_id=user_id, found=tm60_user is not None)
                return tm60_user
                
            except Exception as e:
                log.warning("TM60 user lookup failed", user_id=user_id, error=str(e))
                raise BaseAppException(f"ARS 시스템 사용자 조회 실패: {str(e)}", status_code=500)
        
        try:
            return await asyncio.to_thread(_sync_get_by_user_id)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning("TM60 user lookup failed", user_id=user_id, error=str(e))
            raise BaseAppException(f"ARS 시스템 사용자 조회 실패: {str(e)}", status_code=500)
    
    @logger.catch(reraise=True)
    async def exists_by_user_id(self, user_id: str) -> bool:
        """사용자 ID 존재 여부 확인"""
        log = get_logger_with_request_id()
        log.info("Checking TM60 user existence", user_id=user_id)
        
        def _sync_exists_by_user_id() -> bool:
            """동기 MSSQL 존재 여부 확인"""
            try:
                exists = self.mssql_session.query(Tm60Users.idx).filter(Tm60Users.u_id == user_id).first() is not None
                log.info("TM60 user existence check completed", user_id=user_id, exists=exists)
                return exists
                
            except Exception as e:
                log.warning("TM60 user existence check failed", user_id=user_id, error=str(e))
                raise BaseAppException(f"ARS 시스템 사용자 존재 확인 실패: {str(e)}", status_code=500)
        
        try:
            return await asyncio.to_thread(_sync_exists_by_user_id)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning("TM60 user existence check failed", user_id=user_id, error=str(e))
            raise BaseAppException(f"ARS 시스템 사용자 존재 확인 실패: {str(e)}", status_code=500)