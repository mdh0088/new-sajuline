"""
1:1 문의 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.engine import Result

from src.models.inquiry_model import Inquiry, InquirerType
from src.schemas.inquiry_schema import InquiryCreate, InquiryUpdate, InquiryListParams
from src.common.logging import logger, get_logger_with_request_id


class InquiryRepository:
    """1:1 문의 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def get_counselor_user_inquiries(
        self,
        counselor_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Inquiry], int]:
        """
        상담문의 목록 조회
        - inquirer_type = 'USER' AND counselor_id = #{counselor_id}
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor user inquiries", counselor_id=counselor_id)
        
        skip = (page - 1) * limit
        
        # 목록 조회
        stmt = select(Inquiry).where(
            and_(
                Inquiry.inquirer_type == InquirerType.USER,
                Inquiry.counselor_id == counselor_id
            )
        ).offset(skip).limit(limit).order_by(Inquiry.created_at.desc())
        
        result = await self.db.execute(stmt)
        inquiries = list(result.scalars().all())
        
        # 전체 개수 조회
        count_stmt = select(func.count(Inquiry.inquiry_id)).where(
            and_(
                Inquiry.inquirer_type == InquirerType.USER,
                Inquiry.counselor_id == counselor_id
            )
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        log.info("Counselor user inquiries retrieved", 
                counselor_id=counselor_id, 
                count=len(inquiries), 
                total=total)
        
        return inquiries, total
    
    @logger.catch(reraise=True)
    async def get_counselor_admin_inquiries(
        self,
        counselor_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Inquiry], int]:
        """
        관리자 문의 목록 조회
        - inquirer_type = 'COUNSELOR' AND inquirer_id = #{counselor_id}
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor admin inquiries", counselor_id=counselor_id)
        
        skip = (page - 1) * limit
        
        # 목록 조회
        stmt = select(Inquiry).where(
            and_(
                Inquiry.inquirer_type == InquirerType.COUNSELOR,
                Inquiry.inquirer_id == counselor_id
            )
        ).offset(skip).limit(limit).order_by(Inquiry.created_at.desc())
        
        result = await self.db.execute(stmt)
        inquiries = list(result.scalars().all())
        
        # 전체 개수 조회
        count_stmt = select(func.count(Inquiry.inquiry_id)).where(
            and_(
                Inquiry.inquirer_type == InquirerType.COUNSELOR,
                Inquiry.inquirer_id == counselor_id
            )
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        log.info("Counselor admin inquiries retrieved", 
                counselor_id=counselor_id, 
                count=len(inquiries), 
                total=total)
        
        return inquiries, total