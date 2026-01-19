"""
TM60 채팅로그 Repository 클래스
ARS 시스템 연동 - MSSQL tm60_chatlog 테이블 전용 (읽기 전용)
"""
import asyncio
import calendar
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
        - 조건: chatstart >= 해당월 첫날, chatend <= 해당월 마지막날 23:59:59
        Returns: (sum_realchattm, sum_usepoint)
        """
        log = get_logger_with_request_id()
        log.info("Getting monthly stats by m_code", m_code=m_code, yyyy=yyyy, mm=mm)

        # 해당 월의 날짜 범위 계산
        year = int(yyyy)
        month = int(mm)
        first_day = f"{yyyy}-{mm}-01 00:00:00"
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = f"{yyyy}-{mm}-{last_day_num:02d} 23:59:59"

        def _sync_get_stats() -> tuple[int, int]:
            try:
                sum_realchattm, sum_usepoint = (
                    self.mssql_session.query(
                        func.coalesce(func.sum(Tm60Chatlog.realchattm), 0),
                        func.coalesce(func.sum(Tm60Chatlog.usepoint), 0)
                    )
                    .filter(
                        and_(
                            Tm60Chatlog.m_code == m_code,
                            Tm60Chatlog.chatstart >= first_day,
                            Tm60Chatlog.chatend <= last_day,
                            Tm60Chatlog.success == 1,
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
    async def get_consultation_count_by_m_code(self, m_code: str) -> int:
        """
        상담사 코드(m_code) 기준 상담 건수
        - 조건: usepoint > 0 AND m_code = #{m_code}
        """
        log = get_logger_with_request_id()
        log.info("Getting consultation count by m_code", m_code=m_code)

        def _sync_get_count() -> int:
            try:
                count = (
                    self.mssql_session.query(func.count(Tm60Chatlog.idx))
                    .filter(
                        and_(
                            Tm60Chatlog.m_code == m_code,
                            Tm60Chatlog.usepoint > 0,
                        )
                    )
                    .scalar()
                ) or 0
                return int(count)
            except Exception as e:
                log.warning("Failed to get consultation count by m_code", m_code=m_code, error=str(e))
                raise BaseAppException(f"상담 건수 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_count)

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

    @logger.catch(reraise=True)
    async def get_consultation_counts_by_m_codes_recent_days(
        self,
        m_codes: list[str],
        days: int = 7
    ) -> list[tuple[str, int]]:
        """
        여러 상담사 코드(m_code)에 대해 최근 N일간 상담 건수 일괄 조회 (HOT 정렬용)
        - 조건: starttm >= (오늘 - days일) AND m_code IN (m_codes)
        - Returns: [(m_code, count), ...]
        """
        log = get_logger_with_request_id()
        log.info("Getting recent consultation counts by m_codes", m_codes_count=len(m_codes), days=days)

        if not m_codes:
            return []

        from datetime import datetime, timedelta
        # 최근 N일 기준 날짜 계산 (starttm은 'yyyy-mm-dd hh:mm:ss' 문자열)
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")

        def _sync_get_counts() -> list[tuple[str, int]]:
            try:
                results = (
                    self.mssql_session.query(
                        Tm60Chatlog.m_code,
                        func.count(Tm60Chatlog.idx)
                    )
                    .filter(
                        and_(
                            Tm60Chatlog.m_code.in_(m_codes),
                            Tm60Chatlog.starttm >= start_date,
                        )
                    )
                    .group_by(Tm60Chatlog.m_code)
                    .all()
                )
                log.info("Recent consultation counts fetched", result_count=len(results))
                return [(str(m_code), int(cnt)) for m_code, cnt in results]
            except Exception as e:
                log.warning("Failed to get recent consultation counts", error=str(e))
                raise BaseAppException(f"최근 상담 건수 조회 실패: {str(e)}", status_code=500)

        return await asyncio.to_thread(_sync_get_counts)