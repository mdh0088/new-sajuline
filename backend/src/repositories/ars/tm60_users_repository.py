"""
TM60 사용자 Repository 클래스
ARS 시스템 연동 - MSSQL tm60_users 테이블 전용
"""
import asyncio
from typing import Optional
from datetime import datetime, timezone, timedelta

# 한국 표준시 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

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
                # MSSQL datetime은 timezone-naive만 지원하므로 tzinfo 제거
                kst_now = datetime.now(KST).replace(tzinfo=None)
                tm60_user = Tm60Users(
                    u_id=user_id,
                    u_tel=phone or "",
                    u_kname=nickname or "",  # 빈 문자열로 처리
                    u_passwd="",  # 빈 문자열 (프로토타입 로직 따름)
                    regdate=kst_now,
                    u_fdate=kst_now,
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
    
    @logger.catch(reraise=True)
    async def update_user_points(self, user_id: str, point_amount: int) -> int:
        """
        TM60 사용자 포인트 업데이트
        - 기존 u_point에 point_amount를 더함 (증가)
        - 음수 point_amount로 차감도 가능
        - 업데이트 후 새로운 포인트 잔액 반환
        """
        log = get_logger_with_request_id()
        log.info("Updating TM60 user points", 
                user_id=user_id, 
                point_amount=point_amount)
        
        def _sync_update_user_points() -> int:
            """동기 MSSQL 포인트 업데이트"""
            try:
                # 사용자 존재 확인
                tm60_user = self.mssql_session.query(Tm60Users).filter(Tm60Users.u_id == user_id).first()
                if not tm60_user:
                    log.warning("TM60 user not found for point update", user_id=user_id)
                    raise BaseAppException(f"포인트 업데이트 대상 사용자를 찾을 수 없습니다: {user_id}", status_code=404)
                
                # 현재 포인트 조회 및 업데이트
                current_points = tm60_user.u_point or 0
                new_points = current_points + point_amount
                
                if new_points < 0:
                    log.warning("Insufficient points for update", 
                              user_id=user_id, 
                              current_points=current_points,
                              point_amount=point_amount,
                              new_points=new_points)
                    raise BaseAppException(f"포인트가 부족합니다. 현재: {current_points}, 요청: {point_amount}", status_code=400)
                
                # 포인트 업데이트
                tm60_user.u_point = new_points
                self.mssql_session.flush()
                self.mssql_session.commit()
                
                log.info("TM60 user points updated successfully", 
                        user_id=user_id,
                        current_points=current_points,
                        point_amount=point_amount, 
                        new_points=new_points,
                        tm60_idx=tm60_user.idx)
                return new_points
                
            except BaseAppException:
                # 기존 예외는 그대로 재발생
                self.mssql_session.rollback()
                raise
            except Exception as e:
                log.warning("TM60 user points update failed", 
                          user_id=user_id, 
                          point_amount=point_amount,
                          error=str(e))
                self.mssql_session.rollback()
                raise BaseAppException(f"ARS 시스템 포인트 업데이트 실패: {str(e)}", status_code=500)
        
        try:
            # 스레드 풀에서 동기 작업 실행하여 이벤트 루프 블로킹 방지
            return await asyncio.to_thread(_sync_update_user_points)
        except BaseAppException:
            # 기존 예외는 그대로 재발생
            raise
        except Exception as e:
            log.warning("TM60 user points update failed", 
                      user_id=user_id, 
                      point_amount=point_amount,
                      error=str(e))
            raise BaseAppException(f"ARS 시스템 포인트 업데이트 실패: {str(e)}", status_code=500)
    
    @logger.catch(reraise=True)
    async def get_user_points(self, user_id: str) -> int:
        """TM60 사용자의 현재 포인트 조회"""
        log = get_logger_with_request_id()
        log.info("Getting TM60 user points", user_id=user_id)
        
        def _sync_get_user_points() -> int:
            """동기 MSSQL 포인트 조회"""
            try:
                tm60_user = self.mssql_session.query(Tm60Users).filter(Tm60Users.u_id == user_id).first()
                if not tm60_user:
                    log.warning("TM60 user not found for points query", user_id=user_id)
                    return 0
                
                current_points = tm60_user.u_point or 0
                log.info("TM60 user points retrieved", 
                        user_id=user_id, 
                        points=current_points)
                return current_points
                
            except Exception as e:
                log.warning("TM60 user points query failed", user_id=user_id, error=str(e))
                raise BaseAppException(f"ARS 시스템 포인트 조회 실패: {str(e)}", status_code=500)
        
        try:
            return await asyncio.to_thread(_sync_get_user_points)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning("TM60 user points query failed", user_id=user_id, error=str(e))
            raise BaseAppException(f"ARS 시스템 포인트 조회 실패: {str(e)}", status_code=500)

    @logger.catch(reraise=True)
    async def delete_by_phone(self, phone: str) -> bool:
        """전화번호로 TM60 사용자 삭제"""
        log = get_logger_with_request_id()
        log.info("Deleting TM60 user by phone", phone=phone)

        def _sync_delete_by_phone() -> bool:
            """동기 MSSQL 삭제"""
            try:
                # 사용자 조회
                tm60_user = self.mssql_session.query(Tm60Users).filter(Tm60Users.u_tel == phone).first()
                if not tm60_user:
                    log.warning("TM60 user not found for deletion", phone=phone)
                    return False

                # 삭제 실행
                self.mssql_session.delete(tm60_user)
                self.mssql_session.flush()
                self.mssql_session.commit()

                log.info("TM60 user deleted successfully", phone=phone, tm60_idx=tm60_user.idx)
                return True

            except Exception as e:
                log.warning("TM60 user deletion failed", phone=phone, error=str(e))
                self.mssql_session.rollback()
                raise BaseAppException(f"ARS 시스템 사용자 삭제 실패: {str(e)}", status_code=500)

        try:
            return await asyncio.to_thread(_sync_delete_by_phone)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning("TM60 user deletion failed", phone=phone, error=str(e))
            raise BaseAppException(f"ARS 시스템 사용자 삭제 실패: {str(e)}", status_code=500)