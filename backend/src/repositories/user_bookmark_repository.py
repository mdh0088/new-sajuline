"""
사용자 북마크 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sqla_delete

from src.models.user_bookmark_model import UserBookmark
from src.schemas.user_bookmark_schema import UserBookmarkCreate
from src.common.logging import logger, get_logger_with_request_id


class UserBookmarkRepository:
    """사용자 북마크 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create(self, bookmark_data: UserBookmarkCreate) -> UserBookmark:
        """북마크 생성"""
        bookmark = UserBookmark(
            user_id=bookmark_data.user_id,
            counselor_id=bookmark_data.counselor_id
        )
        
        self.db.add(bookmark)
        await self.db.flush()
        await self.db.refresh(bookmark)
        return bookmark
    
    @logger.catch(reraise=True)
    async def get_count_by_user(self, user_id: str) -> int:
        """사용자별 북마크 수 조회"""
        log = get_logger_with_request_id()
        log.info("Getting bookmark count by user", user_id=user_id)
        
        stmt = select(func.count(UserBookmark.bookmark_id)).where(UserBookmark.user_id == user_id)
        result = await self.db.execute(stmt)
        count = result.scalar() or 0
        
        log.info("Bookmark count lookup completed", user_id=user_id, count=count)
        return count
    
    @logger.catch(reraise=True)
    async def get_list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[UserBookmark]:
        """사용자별 북마크 목록 조회 (페이징)"""
        log = get_logger_with_request_id()
        log.info("Getting bookmark list by user", user_id=user_id, skip=skip, limit=limit)
        
        stmt = (
            select(UserBookmark)
            .where(UserBookmark.user_id == user_id)
            .order_by(UserBookmark.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        bookmarks = list(result.scalars().all())
        
        log.info("Bookmark list lookup completed", user_id=user_id, count=len(bookmarks))
        return bookmarks

    @logger.catch(reraise=True)
    async def exists(self, user_id: str, counselor_id: str) -> bool:
        """특정 사용자-상담사 북마크 존재 여부"""
        log = get_logger_with_request_id()
        log.info("Checking bookmark existence", user_id=user_id, counselor_id=counselor_id)

        stmt = (
            select(func.count(UserBookmark.bookmark_id))
            .where(
                (UserBookmark.user_id == user_id)
                & (UserBookmark.counselor_id == counselor_id)
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar() or 0
        return count > 0

    @logger.catch(reraise=True)
    async def delete(self, user_id: str, counselor_id: str) -> int:
        """특정 사용자-상담사 북마크 삭제 (영향 행 수 반환)"""
        log = get_logger_with_request_id()
        log.info("Deleting bookmark", user_id=user_id, counselor_id=counselor_id)

        stmt = (
            sqla_delete(UserBookmark)
            .where(
                (UserBookmark.user_id == user_id)
                & (UserBookmark.counselor_id == counselor_id)
            )
        )
        result = await self.db.execute(stmt)
        return result.rowcount or 0