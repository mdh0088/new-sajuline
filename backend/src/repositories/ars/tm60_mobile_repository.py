"""
TM60 Mobile Repository 클래스
ARS 시스템 연동 - MSSQL tm60_mobile 테이블 전용
"""
import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.ars.tm60_mobile_model import Tm60Mobile
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class Tm60MobileRepository:
    """TM60 Mobile 데이터 액세스 클래스 (ARS 시스템 연동)"""

    def __init__(self, mssql_session: Session):
        """MSSQL 세션 주입"""
        self.mssql_session = mssql_session

    @logger.catch(reraise=True)
    async def create(self, mb_id: str, mb_code: str, mb_platform: str) -> bool:
        """
        tm60_mobile 테이블에 포인트 상담 통화 기록 INSERT
        스레드 풀에서 동기 MSSQL 작업 실행하여 이벤트 루프 블로킹 방지

        Args:
            mb_id: 유저 ID
            mb_code: 상담사 코드
            mb_platform: 플랫폼 타입 (1=Mobile web, 2=Android, 3=iOS)

        Returns:
            INSERT 성공 여부
        """
        log = get_logger_with_request_id()
        log.info(
            "Creating TM60 mobile record",
            mb_id=mb_id,
            mb_code=mb_code,
            mb_platform=mb_platform
        )

        def _sync_create_tm60_mobile() -> bool:
            """동기 MSSQL 작업"""
            try:
                tm60_mobile = Tm60Mobile(
                    mb_id=mb_id,
                    mb_code=mb_code,
                    mb_platform=mb_platform,
                    regdate=datetime.utcnow()
                )

                self.mssql_session.add(tm60_mobile)
                self.mssql_session.flush()
                self.mssql_session.commit()

                log.info(
                    "TM60 mobile record created successfully",
                    mb_id=mb_id,
                    mb_code=mb_code,
                    tm60_idx=tm60_mobile.idx
                )
                return True

            except Exception as e:
                log.warning(
                    "TM60 mobile record creation failed",
                    mb_id=mb_id,
                    mb_code=mb_code,
                    error=str(e)
                )
                self.mssql_session.rollback()
                raise BaseAppException(
                    f"ARS 시스템 모바일 통화 기록 생성 실패: {str(e)}",
                    status_code=500
                )

        try:
            # 스레드 풀에서 동기 작업 실행하여 이벤트 루프 블로킹 방지
            return await asyncio.to_thread(_sync_create_tm60_mobile)
        except BaseAppException:
            # 기존 예외는 그대로 재발생
            raise
        except Exception as e:
            log.warning(
                "TM60 mobile record creation failed",
                mb_id=mb_id,
                mb_code=mb_code,
                error=str(e)
            )
            raise BaseAppException(
                f"ARS 시스템 모바일 통화 기록 생성 실패: {str(e)}",
                status_code=500
            )

    @logger.catch(reraise=True)
    async def get_recent_by_user_id(
        self,
        mb_id: str,
        limit: int = 10
    ) -> list[Tm60Mobile]:
        """
        특정 유저의 최근 통화 기록 조회

        Args:
            mb_id: 유저 ID
            limit: 조회 개수 제한

        Returns:
            통화 기록 목록
        """
        log = get_logger_with_request_id()
        log.info("Getting recent mobile calls for user", mb_id=mb_id, limit=limit)

        def _sync_get_recent_by_user_id() -> list[Tm60Mobile]:
            """동기 MSSQL 조회"""
            try:
                rows = (
                    self.mssql_session.query(Tm60Mobile)
                    .filter(Tm60Mobile.mb_id == mb_id)
                    .order_by(Tm60Mobile.regdate.desc())
                    .limit(limit)
                    .all()
                )

                log.info(
                    "Recent mobile calls retrieved",
                    mb_id=mb_id,
                    count=len(rows)
                )
                return list(rows)

            except Exception as e:
                log.warning(
                    "Failed to get recent mobile calls",
                    mb_id=mb_id,
                    error=str(e)
                )
                raise BaseAppException(
                    f"ARS 시스템 모바일 통화 기록 조회 실패: {str(e)}",
                    status_code=500
                )

        try:
            return await asyncio.to_thread(_sync_get_recent_by_user_id)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning(
                "Failed to get recent mobile calls",
                mb_id=mb_id,
                error=str(e)
            )
            raise BaseAppException(
                f"ARS 시스템 모바일 통화 기록 조회 실패: {str(e)}",
                status_code=500
            )

    @logger.catch(reraise=True)
    async def get_count_by_user_id(self, mb_id: str) -> int:
        """
        특정 유저의 통화 기록 수 조회

        Args:
            mb_id: 유저 ID

        Returns:
            통화 기록 수
        """
        log = get_logger_with_request_id()
        log.info("Getting mobile call count for user", mb_id=mb_id)

        def _sync_get_count_by_user_id() -> int:
            """동기 MSSQL 조회"""
            try:
                from sqlalchemy import func
                count = (
                    self.mssql_session.query(func.count(Tm60Mobile.idx))
                    .filter(Tm60Mobile.mb_id == mb_id)
                    .scalar()
                ) or 0

                log.info(
                    "Mobile call count retrieved",
                    mb_id=mb_id,
                    count=count
                )
                return int(count)

            except Exception as e:
                log.warning(
                    "Failed to get mobile call count",
                    mb_id=mb_id,
                    error=str(e)
                )
                raise BaseAppException(
                    f"ARS 시스템 모바일 통화 기록 수 조회 실패: {str(e)}",
                    status_code=500
                )

        try:
            return await asyncio.to_thread(_sync_get_count_by_user_id)
        except BaseAppException:
            raise
        except Exception as e:
            log.warning(
                "Failed to get mobile call count",
                mb_id=mb_id,
                error=str(e)
            )
            raise BaseAppException(
                f"ARS 시스템 모바일 통화 기록 수 조회 실패: {str(e)}",
                status_code=500
            )
