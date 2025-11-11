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

    @logger.catch(reraise=True)
    async def get_count_counselor_user_inquiries(self, counselor_id: str) -> int:
        """
        상담문의 개수만 조회 (최적화)
        - inquirer_type = 'USER' AND counselor_id = #{counselor_id}
        """
        count_stmt = select(func.count(Inquiry.inquiry_id)).where(
            and_(
                Inquiry.inquirer_type == InquirerType.USER,
                Inquiry.counselor_id == counselor_id
            )
        )
        count_result = await self.db.execute(count_stmt)
        return count_result.scalar() or 0

    @logger.catch(reraise=True)
    async def get_count_counselor_admin_inquiries(self, counselor_id: str) -> int:
        """
        관리자 문의 개수만 조회 (최적화)
        - inquirer_type = 'COUNSELOR' AND inquirer_id = #{counselor_id}
        """
        count_stmt = select(func.count(Inquiry.inquiry_id)).where(
            and_(
                Inquiry.inquirer_type == InquirerType.COUNSELOR,
                Inquiry.inquirer_id == counselor_id
            )
        )
        count_result = await self.db.execute(count_stmt)
        return count_result.scalar() or 0

    @logger.catch(reraise=True)
    async def create_user_inquiry(
        self,
        *,
        user_id: str,
        counselor_id: str,
        content: str,
        category: Optional[str] = None,
        title: Optional[str] = None
    ) -> Inquiry:
        """
        사용자 → 상담사 1:1 문의 생성
        - inquirer_type = USER
        - inquirer_id = user_id
        - counselor_id = counselor_id
        """
        log = get_logger_with_request_id()
        log.info("Creating user inquiry", user_id=user_id, counselor_id=counselor_id)

        inquiry = Inquiry(
            inquirer_type=InquirerType.USER.value,
            inquirer_id=user_id,
            counselor_id=counselor_id,
            category=category,
            title=title,
            content=content,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(inquiry)
        await self.db.flush()
        await self.db.refresh(inquiry)

        log.info("User inquiry created", inquiry_id=inquiry.inquiry_id)
        return inquiry

    @logger.catch(reraise=True)
    async def get_user_admin_inquiries(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Inquiry], int]:
        """
        사용자 → 관리자 문의 목록 조회
        - inquirer_id = user_id
        - category = 'USER_TO_ADMIN'
        - created_at DESC 정렬
        """
        log = get_logger_with_request_id()
        log.info("Getting user admin inquiries", user_id=user_id)

        skip = (page - 1) * limit

        # 목록 조회
        stmt = select(Inquiry).where(
            and_(
                Inquiry.inquirer_id == user_id,
                Inquiry.category == 'USER_TO_ADMIN'
            )
        ).offset(skip).limit(limit).order_by(Inquiry.created_at.desc())

        result = await self.db.execute(stmt)
        inquiries = list(result.scalars().all())

        # 전체 개수 조회
        count_stmt = select(func.count(Inquiry.inquiry_id)).where(
            and_(
                Inquiry.inquirer_id == user_id,
                Inquiry.category == 'USER_TO_ADMIN'
            )
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        log.info("User admin inquiries retrieved",
                user_id=user_id,
                count=len(inquiries),
                total=total)

        return inquiries, total

    @logger.catch(reraise=True)
    async def create_user_admin_inquiry(
        self,
        *,
        user_id: str,
        inquiry_type: str,
        content: str,
        title: Optional[str] = None
    ) -> Inquiry:
        """
        사용자 → 관리자 1:1 문의 생성
        - inquirer_type = USER
        - inquirer_id = user_id
        - category = 'USER_TO_ADMIN'
        - inquiry_type = PAY, ACCOUNT, CS, EVENT, ETC
        """
        log = get_logger_with_request_id()
        log.info("Creating user admin inquiry", user_id=user_id, inquiry_type=inquiry_type)

        inquiry = Inquiry(
            inquirer_type=InquirerType.USER.value,
            inquirer_id=user_id,
            counselor_id=None,  # 관리자 문의는 counselor_id가 없음
            category='USER_TO_ADMIN',
            title=title,
            content=content,
            inquiry_type=inquiry_type,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(inquiry)
        await self.db.flush()
        await self.db.refresh(inquiry)

        log.info("User admin inquiry created", inquiry_id=inquiry.inquiry_id)
        return inquiry

    @logger.catch(reraise=True)
    async def get_user_admin_inquiry_detail(
        self,
        inquiry_id: int,
        user_id: str
    ) -> Inquiry:
        """
        사용자 → 관리자 문의 상세 조회
        - inquiry_id = #{inquiry_id}
        - inquirer_id = #{user_id}
        - category = 'USER_TO_ADMIN'
        """
        log = get_logger_with_request_id()
        log.info("Getting user admin inquiry detail", inquiry_id=inquiry_id, user_id=user_id)

        stmt = select(Inquiry).where(
            and_(
                Inquiry.inquiry_id == inquiry_id,
                Inquiry.inquirer_id == user_id,
                Inquiry.category == 'USER_TO_ADMIN'
            )
        )

        result = await self.db.execute(stmt)
        inquiry = result.scalar_one_or_none()

        if not inquiry:
            log.warning("User admin inquiry not found", inquiry_id=inquiry_id, user_id=user_id)
            raise Exception(f"문의를 찾을 수 없습니다. (inquiry_id={inquiry_id})")

        log.info("User admin inquiry detail retrieved", inquiry_id=inquiry_id)
        return inquiry