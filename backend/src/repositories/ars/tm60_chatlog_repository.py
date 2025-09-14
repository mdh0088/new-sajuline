"""
TM60 채팅로그 Repository 클래스
ARS 시스템 연동 - MSSQL tm60_chatlog 테이블 전용 (읽기 전용)
"""
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, not_, desc

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

    @logger.catch(reraise=True)
    async def get_monthly_stats_by_m_code(self, m_code: str, yyyy: str, mm: str) -> tuple[int, int]:
        """
        멤버 코드(m_code)와 연월(yyyy, mm)로 월별 합계 집계
        - 조건: usepoint > 0
        Returns: (sum_realchattm, sum_usepoint)
        """
        log = get_logger_with_request_id()
        log.info("Getting monthly stats by m_code", m_code=m_code, yyyy=yyyy, mm=mm)

        def _sync_get_stats() -> tuple[int, int]:
            try:
                sum_realchattm, sum_usepoint = (
                    self.mssql_session.query(
                        func.coalesce(func.sum(Tm60Chatlog.realchattm), 0),
                        func.coalesce(func.sum(Tm60Chatlog.usepoint), 0)
                    )
                    .filter(
                        and_(
                            Tm60Chatlog.usepoint > 0,
                            Tm60Chatlog.m_code == m_code,
                            Tm60Chatlog.yyyy == yyyy,
                            Tm60Chatlog.mm == mm,
                        )
                    )
                    .one()
                )
                return int(sum_realchattm or 0), int(sum_usepoint or 0)
            except Exception as e:
                log.warning("Failed to get monthly stats by m_code", m_code=m_code, yyyy=yyyy, mm=mm, error=str(e))
                raise BaseAppException(f"월별 상담 통계 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_stats)

    @logger.catch(reraise=True)
    async def get_by_idx_list(self, idx_list: list[int]) -> list[Tm60Chatlog]:
        """idx 목록으로 다건 조회"""
        log = get_logger_with_request_id()
        log.info("Fetching tm60_chatlog by idx list", count=len(idx_list))

        def _sync_get_by_idx_list() -> list[Tm60Chatlog]:
            try:
                if not idx_list:
                    return []
                rows = (
                    self.mssql_session.query(Tm60Chatlog)
                    .filter(Tm60Chatlog.idx.in_(idx_list))
                    .all()
                )
                return list(rows)
            except Exception as e:
                log.warning("Failed to fetch tm60_chatlog by idx list", error=str(e))
                raise BaseAppException(f"채팅로그 다건 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_by_idx_list)

    @logger.catch(reraise=True)
    async def get_pending_sessions(
        self,
        *,
        user_id: str,
        exclude_session_ids: list[int],
        page: int,
        limit: int,
    ) -> tuple[list[Tm60Chatlog], int]:
        """
        작성 대기 목록 조회
        - where usepoint > 0 and u_id = user_id and idx not in (exclude_session_ids)
        - order by starttm desc
        - pagination
        """
        log = get_logger_with_request_id()
        log.info("Fetching pending sessions", user_id=user_id, exclude=len(exclude_session_ids), page=page, limit=limit)

        def _sync_get_pending() -> tuple[list[Tm60Chatlog], int]:
            try:
                base = (
                    self.mssql_session.query(Tm60Chatlog)
                    .filter(
                        and_(
                            Tm60Chatlog.u_id == user_id,
                            Tm60Chatlog.usepoint > 0,
                            not_(Tm60Chatlog.idx.in_(exclude_session_ids or [0]))
                        )
                    )
                )
                total = int(base.count())
                rows = (
                    base.order_by(desc(Tm60Chatlog.starttm))
                    .offset(max(0, (page - 1) * limit))
                    .limit(limit)
                    .all()
                )
                return list(rows), total
            except Exception as e:
                log.warning("Failed to fetch pending sessions", error=str(e))
                raise BaseAppException(f"작성 대기 목록 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_pending)

    @logger.catch(reraise=True)
    async def get_usage_logs(
        self,
        user_id: str,
        start_dt_str: str,
        end_dt_str: str,
        order_type: str,
        page: int,
        limit: int,
    ) -> tuple[list[Tm60Chatlog], int]:
        """
        포인트 사용 내역 (tm60_chatlog)
        - where usepoint > 0 and u_id = user_id
        - 날짜 필터: chatstart 또는 chatend가 [start_dt, end_dt] 범위 내
        - 정렬: latest(chatstart desc), highest(usepoint desc), lowest(usepoint asc)
        """
        log = get_logger_with_request_id()
        log.info("Getting usage logs", user_id=user_id, start=start_dt_str, end=end_dt_str, order_type=order_type)

        # 문자열 날짜 경계 생성 (YYYY-MM-DD HH:MM:SS)
        start_bound = f"{start_dt_str} 00:00:00"
        end_bound = f"{end_dt_str} 23:59:59"

        def _sync_get_usage_logs() -> tuple[list[Tm60Chatlog], int]:
            try:
                base_query = (
                    self.mssql_session.query(Tm60Chatlog)
                    .filter(
                        and_(
                            Tm60Chatlog.u_id == user_id,
                            Tm60Chatlog.usepoint > 0,
                            or_(
                                and_(Tm60Chatlog.chatstart >= start_bound, Tm60Chatlog.chatstart <= end_bound),
                                and_(Tm60Chatlog.chatend >= start_bound, Tm60Chatlog.chatend <= end_bound),
                            ),
                        )
                    )
                )

                total: int = int(base_query.count())

                if order_type == "latest":
                    base_query = base_query.order_by(Tm60Chatlog.chatstart.desc())
                elif order_type == "highest":
                    base_query = base_query.order_by(Tm60Chatlog.usepoint.desc())
                elif order_type == "lowest":
                    base_query = base_query.order_by(Tm60Chatlog.usepoint.asc())
                else:
                    base_query = base_query.order_by(Tm60Chatlog.chatstart.desc())

                rows: list[Tm60Chatlog] = list(base_query.offset(max(0, (page - 1) * limit)).limit(limit).all())
                log.info("Usage logs fetched", user_id=user_id, count=len(rows), total=total, page=page, limit=limit)
                return rows, total
            except Exception as e:
                log.warning("Failed to get usage logs", user_id=user_id, error=str(e))
                raise BaseAppException(f"포인트 사용 내역 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_usage_logs)