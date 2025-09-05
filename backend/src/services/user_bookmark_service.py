"""
사용자 북마크 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import List

from src.exceptions.custom_exceptions import ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.user_bookmark_model import UserBookmark
from src.schemas.user_bookmark_schema import UserBookmarkResponse, UserBookmarkCount, UserBookmarkListResponse
from src.repositories.user_bookmark_repository import UserBookmarkRepository


class UserBookmarkService:
    """사용자 북마크 비즈니스 로직 서비스"""
    
    def __init__(self, bookmark_repo: UserBookmarkRepository):
        self.bookmark_repo = bookmark_repo
    
    async def get_bookmark_count_by_user(self, user_id: str) -> UserBookmarkCount:
        """
        사용자별 북마크한 수 조회
        - user_id로 해당 사용자가 북마크한 상담사 수를 반환
        """
        log = get_logger_with_request_id()
        log.info("Getting bookmark count for user", user_id=user_id)
        
        if not user_id:
            log.warning("User ID is empty")
            raise ValidationError("사용자 ID가 필요합니다.")
        
        count = await self.bookmark_repo.get_count_by_user(user_id)
        
        log.info("Bookmark count retrieved successfully", user_id=user_id, count=count)
        return UserBookmarkCount(
            user_id=user_id,
            bookmark_count=count
        )
    
    async def get_bookmark_list_by_user(
        self, 
        user_id: str, 
        page: int = 1, 
        size: int = 20
    ) -> UserBookmarkListResponse:
        """
        사용자별 북마크 목록 조회 (페이징)
        - 사용자가 북마크한 상담사 목록을 최신순으로 반환
        """
        log = get_logger_with_request_id()
        log.info("Getting bookmark list for user", user_id=user_id, page=page, size=size)
        
        if not user_id:
            log.warning("User ID is empty")
            raise ValidationError("사용자 ID가 필요합니다.")
        
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        skip = (page - 1) * size
        
        # 북마크 목록 조회
        bookmarks = await self.bookmark_repo.get_list_by_user(user_id, skip, size)
        
        # 전체 개수 조회
        total_count = await self.bookmark_repo.get_count_by_user(user_id)
        
        # 응답 데이터 변환
        bookmark_responses = [UserBookmarkResponse.model_validate(bookmark) for bookmark in bookmarks]
        
        log.info("Bookmark list retrieved successfully", 
                user_id=user_id, 
                page=page, 
                size=size, 
                count=len(bookmarks), 
                total=total_count)
        
        return UserBookmarkListResponse(
            bookmarks=bookmark_responses,
            total=total_count,
            page=page,
            size=size
        )