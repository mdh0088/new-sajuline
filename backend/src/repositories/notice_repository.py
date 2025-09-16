"""
공지사항 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.engine import Result

from src.models.notice_model import Notice, NoticeType, TargetAudience
from src.schemas.notice_schema import NoticeListParams
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class NoticeRepository:
    """공지사항 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def get_by_id(self, notice_id: int) -> Optional[Notice]:
        """공지사항 ID로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up notice by ID", notice_id=notice_id)
        
        stmt = select(Notice).where(Notice.notice_id == notice_id)
        result = await self.db.execute(stmt)
        notice = result.scalar_one_or_none()
        
        log.info("Notice lookup completed", notice_id=notice_id, found=notice is not None)
        return notice
    
    @logger.catch(reraise=True)
    async def get_list(self, params: NoticeListParams) -> Tuple[List[Notice], int]:
        """공지사항 목록 조회 (페이징 포함)"""
        log = get_logger_with_request_id()
        log.info("Getting notice list", params=params.dict())
        
        # 기본 쿼리
        stmt = select(Notice)
        count_stmt = select(func.count(Notice.notice_id))
        
        # 필터 조건 적용
        conditions = []
        
        if params.notice_type:
            conditions.append(Notice.notice_type == params.notice_type)
        
        if params.target_audience:
            conditions.append(Notice.target_audience == params.target_audience)
        
        if params.is_active is not None:
            conditions.append(Notice.is_active == params.is_active)
        
        if params.is_important is not None:
            conditions.append(Notice.is_important == params.is_important)
        
        if params.search:
            search_condition = or_(
                Notice.title.contains(params.search),
                Notice.content.contains(params.search)
            )
            conditions.append(search_condition)
        
        # 조건 적용
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))
        
        # 정렬 및 페이징
        stmt = stmt.order_by(
            desc(Notice.is_important),  # 중요 공지 우선
            desc(Notice.created_at)     # 최신순
        )
        stmt = stmt.offset((params.page - 1) * params.limit).limit(params.limit)
        
        # 실행
        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)
        
        notices = list(result.scalars().all())
        total = count_result.scalar()
        
        log.info("Notice list retrieved", 
                count=len(notices), 
                total=total, 
                page=params.page, 
                limit=params.limit)
        
        return notices, total

    @logger.catch(reraise=True)
    async def get_public_list(self) -> List[Notice]:
        """게스트용 공지사항 전체 조회 (기본 조건/정렬)
        - is_active = True
        - target_audience = 'ALL' (요구사항의 'COMMON'에 해당)
        - 정렬: is_important DESC, created_at DESC
        """
        log = get_logger_with_request_id()
        log.info("Getting public notice list")

        stmt = (
            select(Notice)
            .where(
                and_(
                    Notice.is_active.is_(True),
                    Notice.target_audience == 'ALL'
                )
            )
            .order_by(desc(Notice.is_important), desc(Notice.created_at))
        )
        result = await self.db.execute(stmt)
        notices = list(result.scalars().all())
        log.info("Public notice list retrieved", count=len(notices))
        return notices

    @logger.catch(reraise=True)
    async def get_adjacent_ids(self, notice_id: int) -> Tuple[Optional[int], Optional[int]]:
        """현재 공지의 바로 이전/다음 notice_id 반환 (게스트 기준 필터 적용)
        - 기준 정렬: created_at DESC
        - before: 더 최신(created_at > current) 중 가장 가까운 항목
        - after: 더 과거(created_at < current) 중 가장 가까운 항목
        """
        log = get_logger_with_request_id()
        log.info("Getting adjacent notice IDs", notice_id=notice_id)

        # 현재 공지의 created_at 조회
        current_stmt = select(Notice.created_at).where(Notice.notice_id == notice_id)
        current_result = await self.db.execute(current_stmt)
        current_created_at = current_result.scalar_one_or_none()
        if current_created_at is None:
            log.warning("Current notice not found for adjacent lookup", notice_id=notice_id)
            return None, None

        # 이전(before): 더 최신 (created_at > current)
        before_stmt = (
            select(Notice.notice_id)
            .where(
                and_(
                    Notice.is_active.is_(True),
                    Notice.target_audience == 'ALL',
                    Notice.created_at > current_created_at
                )
            )
            .order_by(desc(Notice.created_at))
            .limit(1)
        )
        before_res = await self.db.execute(before_stmt)
        before_id = before_res.scalar_one_or_none()

        # 다음(after): 더 과거 (created_at < current)
        after_stmt = (
            select(Notice.notice_id)
            .where(
                and_(
                    Notice.is_active.is_(True),
                    Notice.target_audience == 'ALL',
                    Notice.created_at < current_created_at
                )
            )
            .order_by(desc(Notice.created_at))
            .limit(1)
        )
        after_res = await self.db.execute(after_stmt)
        after_id = after_res.scalar_one_or_none()

        log.info("Adjacent IDs resolved", before_notice_id=before_id, after_notice_id=after_id)
        return before_id, after_id

    @logger.catch(reraise=True)
    async def increment_view_count(self, notice_id: int) -> None:
        """조회수 1 증가 처리"""
        log = get_logger_with_request_id()
        log.info("Incrementing notice view_count", notice_id=notice_id)
        stmt = (
            update(Notice)
            .where(Notice.notice_id == notice_id)
            .values(view_count=Notice.view_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        log.info("View count incremented", notice_id=notice_id)