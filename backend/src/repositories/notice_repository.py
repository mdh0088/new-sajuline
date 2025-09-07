"""
공지사항 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
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