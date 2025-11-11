"""
1:1 문의 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import List, Tuple

from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.inquiry_model import Inquiry
from src.schemas.inquiry_schema import InquirySummary, UserInquiryCreateRequest, InquiryResponse, UserAdminInquiryCreateRequest
from src.repositories.inquiry_repository import InquiryRepository


class InquiryService:
    """1:1 문의 비즈니스 로직 서비스"""
    
    def __init__(self, inquiry_repo: InquiryRepository):
        self.inquiry_repo = inquiry_repo
    
    async def get_counselor_user_inquiries(
        self,
        counselor_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[InquirySummary], int, int, int]:
        """
        상담문의 목록 조회 (APIResponseBuilder.paginated용)
        inquirer_type='USER' AND counselor_id=#{counselor_id}
        Returns: (inquiries, page, limit, total)
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor user inquiries", 
                counselor_id=counselor_id, 
                page=page, 
                limit=limit)
        
        # 파라미터 유효성 검사
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        # 문의 목록 조회
        inquiries, total = await self.inquiry_repo.get_counselor_user_inquiries(
            counselor_id=counselor_id,
            page=page,
            limit=limit
        )
        
        # 응답 데이터 변환
        inquiry_summaries = []
        for inquiry in inquiries:
            summary = InquirySummary.model_validate(inquiry)
            summary.has_reply = bool(inquiry.reply_content)
            inquiry_summaries.append(summary)
        
        log.info("Counselor user inquiries retrieved", 
                counselor_id=counselor_id, 
                count=len(inquiry_summaries), 
                total=total)
        
        return inquiry_summaries, page, limit, total

    async def get_counselor_user_inquiries_count(
        self,
        counselor_id: str
    ) -> int:
        """
        상담문의 개수만 조회 (최적화된 count 전용)
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor user inquiries count", counselor_id=counselor_id)

        total = await self.inquiry_repo.get_count_counselor_user_inquiries(
            counselor_id=counselor_id
        )

        log.info("Counselor user inquiries count retrieved", counselor_id=counselor_id, total=total)
        return total

    async def get_counselor_admin_inquiries(
        self,
        counselor_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[InquirySummary], int, int, int]:
        """
        관리자 문의 목록 조회 (APIResponseBuilder.paginated용)
        inquirer_type='COUNSELOR' AND inquirer_id=#{counselor_id}
        Returns: (inquiries, page, limit, total)
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor admin inquiries", 
                counselor_id=counselor_id, 
                page=page, 
                limit=limit)
        
        # 파라미터 유효성 검사
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        # 문의 목록 조회
        inquiries, total = await self.inquiry_repo.get_counselor_admin_inquiries(
            counselor_id=counselor_id,
            page=page,
            limit=limit
        )
        
        # 응답 데이터 변환
        inquiry_summaries = []
        for inquiry in inquiries:
            summary = InquirySummary.model_validate(inquiry)
            summary.has_reply = bool(inquiry.reply_content)
            inquiry_summaries.append(summary)
        
        log.info("Counselor admin inquiries retrieved", 
                counselor_id=counselor_id, 
                count=len(inquiry_summaries), 
                total=total)
        
        return inquiry_summaries, page, limit, total

    async def get_counselor_admin_inquiries_count(
        self,
        counselor_id: str
    ) -> int:
        """
        관리자 문의 개수만 조회 (최적화된 count 전용)
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor admin inquiries count", counselor_id=counselor_id)

        total = await self.inquiry_repo.get_count_counselor_admin_inquiries(
            counselor_id=counselor_id
        )

        log.info("Counselor admin inquiries count retrieved", counselor_id=counselor_id, total=total)
        return total

    async def create_user_inquiry(
        self,
        *,
        user_id: str,
        payload: UserInquiryCreateRequest
    ) -> InquiryResponse:
        """사용자 → 상담사 1:1 문의 생성"""
        log = get_logger_with_request_id()
        log.info("Creating user inquiry (service)", user_id=user_id, counselor_id=payload.counselor_id)

        if not payload.content or not payload.counselor_id:
            raise ValidationError("counselor_id와 content는 필수입니다.")

        inquiry = await self.inquiry_repo.create_user_inquiry(
            user_id=user_id,
            counselor_id=payload.counselor_id,
            content=payload.content,
            category=payload.category,
            title=payload.title
        )

        response = InquiryResponse.model_validate(inquiry)
        return response

    async def get_user_admin_inquiries(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[InquirySummary], int, int, int]:
        """
        사용자 → 관리자 문의 목록 조회 (APIResponseBuilder.paginated용)
        inquirer_id=#{user_id} AND category='USER_TO_ADMIN'
        Returns: (inquiries, page, limit, total)
        """
        log = get_logger_with_request_id()
        log.info("Getting user admin inquiries",
                user_id=user_id,
                page=page,
                limit=limit)

        # 파라미터 유효성 검사
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        # 문의 목록 조회
        inquiries, total = await self.inquiry_repo.get_user_admin_inquiries(
            user_id=user_id,
            page=page,
            limit=limit
        )

        # 응답 데이터 변환
        inquiry_summaries = []
        for inquiry in inquiries:
            summary = InquirySummary.model_validate(inquiry)
            summary.has_reply = bool(inquiry.reply_content)
            inquiry_summaries.append(summary)

        log.info("User admin inquiries retrieved",
                user_id=user_id,
                count=len(inquiry_summaries),
                total=total)

        return inquiry_summaries, page, limit, total

    async def create_user_admin_inquiry(
        self,
        *,
        user_id: str,
        payload: UserAdminInquiryCreateRequest
    ) -> InquiryResponse:
        """사용자 → 관리자 1:1 문의 생성"""
        log = get_logger_with_request_id()
        log.info("Creating user admin inquiry (service)", user_id=user_id, inquiry_type=payload.inquiry_type)

        if not payload.content:
            raise ValidationError("content는 필수입니다.")

        inquiry = await self.inquiry_repo.create_user_admin_inquiry(
            user_id=user_id,
            inquiry_type=payload.inquiry_type,
            content=payload.content,
            title=payload.title
        )

        response = InquiryResponse.model_validate(inquiry)
        return response

    async def get_user_admin_inquiry_detail(
        self,
        inquiry_id: int,
        user_id: str
    ) -> InquiryResponse:
        """
        사용자 → 관리자 문의 상세 조회
        """
        log = get_logger_with_request_id()
        log.info("Getting user admin inquiry detail (service)",
                inquiry_id=inquiry_id,
                user_id=user_id)

        # 파라미터 유효성 검사
        if not inquiry_id or inquiry_id <= 0:
            raise ValidationError("inquiry_id는 필수이며 0보다 커야 합니다.")

        # 문의 상세 조회
        inquiry = await self.inquiry_repo.get_user_admin_inquiry_detail(
            inquiry_id=inquiry_id,
            user_id=user_id
        )

        # 응답 데이터 변환
        response = InquiryResponse.model_validate(inquiry)

        log.info("User admin inquiry detail retrieved (service)",
                inquiry_id=inquiry_id,
                user_id=user_id)

        return response