"""
공지사항 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime

from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.common.logging import get_logger_with_request_id

from src.models.notice_model import Notice
from src.schemas.notice_schema import NoticeResponse, NoticeListParams
from src.repositories.notice_repository import NoticeRepository


class NoticeService:
    """공지사항 비즈니스 로직 서비스"""
    
    def __init__(self, notice_repo: NoticeRepository):
        self.notice_repo = notice_repo
    
    async def get_notice_by_id(self, notice_id: int) -> NoticeResponse:
        """
        공지사항 단일 조회
        - ID로 공지사항 조회
        - 존재하지 않으면 NotFoundError 발생
        """
        log = get_logger_with_request_id()
        log.info("Getting notice by ID", notice_id=notice_id)
        
        notice = await self.notice_repo.get_by_id(notice_id)
        if not notice:
            log.warning("Notice not found", notice_id=notice_id)
            raise NotFoundError(f"공지사항을 찾을 수 없습니다. (ID: {notice_id})")
        
        log.info("Notice retrieved successfully", 
                notice_id=notice_id, 
                title=notice.title,
                notice_type=notice.notice_type)
        
        return NoticeResponse.model_validate(notice)
    
    async def get_notice_list(self, params: NoticeListParams) -> Tuple[List[NoticeResponse], int, int, int]:
        """
        공지사항 목록 조회 (APIResponseBuilder.paginated용)
        Returns: (notices, page, limit, total)
        """
        log = get_logger_with_request_id()
        log.info("Getting notice list", params=params.dict())
        
        # 파라미터 유효성 검사
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10
        
        # 검색어 정리
        if params.search:
            params.search = params.search.strip()
            if not params.search:
                params.search = None
        
        # 공지사항 목록 조회
        notices, total = await self.notice_repo.get_list(params)
        
        # 응답 생성
        notice_responses = [NoticeResponse.model_validate(notice) for notice in notices]
        
        log.info("Notice list retrieved successfully", 
                count=len(notices), 
                total=total, 
                page=params.page, 
                limit=params.limit)
        
        return notice_responses, params.page, params.limit, total