"""
상담 후기 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.engine import Result

from src.models.consultation_review_model import ConsultationReview
from src.schemas.consultation_review_schema import ConsultationReviewCreate, ConsultationReviewUpdate
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class ConsultationReviewRepository:
    """상담 후기 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create(self, review_data: ConsultationReviewCreate) -> ConsultationReview:
        """상담 후기 생성"""
        review = ConsultationReview(
            session_id=review_data.session_id,
            user_id=review_data.user_id,
            counselor_id=review_data.counselor_id,
            rating=review_data.rating,
            content=review_data.content,
            is_visible=review_data.is_visible
        )
        
        self.db.add(review)
        await self.db.flush()
        await self.db.refresh(review)
        return review
    
    @logger.catch(reraise=True)
    async def get_list_by_user_id(
        self,
        user_id: str,
        is_visible: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConsultationReview]:
        """사용자 ID별 후기 목록 조회"""
        log = get_logger_with_request_id()
        log.info("Getting reviews by user ID", user_id=user_id, is_visible=is_visible)
        
        stmt = select(ConsultationReview).where(ConsultationReview.user_id == user_id)
        
        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)
        
        stmt = stmt.offset(skip).limit(limit).order_by(ConsultationReview.created_at.desc())
        
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())
        
        log.info("Reviews lookup by user completed", user_id=user_id, count=len(reviews))
        return reviews
    
    @logger.catch(reraise=True)
    async def get_count_by_user_id(
        self,
        user_id: str,
        is_visible: Optional[bool] = None
    ) -> int:
        """사용자 ID별 후기 총 개수"""
        stmt = select(func.count(ConsultationReview.review_id)).where(
            ConsultationReview.user_id == user_id
        )
        
        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    @logger.catch(reraise=True)
    async def get_list_by_counselor_id(
        self,
        counselor_id: str,
        is_visible: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConsultationReview]:
        """상담사 ID별 후기 목록 조회"""
        log = get_logger_with_request_id()
        log.info("Getting reviews by counselor ID", counselor_id=counselor_id, is_visible=is_visible)
        
        stmt = select(ConsultationReview).where(ConsultationReview.counselor_id == counselor_id)
        
        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)
        
        stmt = stmt.offset(skip).limit(limit).order_by(ConsultationReview.created_at.desc())
        
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())
        
        log.info("Reviews lookup by counselor completed", counselor_id=counselor_id, count=len(reviews))
        return reviews
    
    @logger.catch(reraise=True)
    async def get_count_by_counselor_id(
        self,
        counselor_id: str,
        is_visible: Optional[bool] = None
    ) -> int:
        """상담사 ID별 후기 총 개수"""
        stmt = select(func.count(ConsultationReview.review_id)).where(
            ConsultationReview.counselor_id == counselor_id
        )
        
        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    @logger.catch(reraise=True)
    async def update(self, review_id: int, update_data: ConsultationReviewUpdate) -> bool:
        """후기 수정"""
        log = get_logger_with_request_id()
        log.info("Updating review", review_id=review_id)
        
        # None이 아닌 필드만 업데이트
        update_values = {}
        if update_data.rating is not None:
            update_values["rating"] = update_data.rating
        if update_data.content is not None:
            update_values["content"] = update_data.content
        if update_data.is_visible is not None:
            update_values["is_visible"] = update_data.is_visible
        
        if not update_values:
            log.warning("No fields to update", review_id=review_id)
            return False
        
        update_values["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(ConsultationReview)
            .where(ConsultationReview.review_id == review_id)
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Review update completed", review_id=review_id, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def add_counselor_reply(self, review_id: int, counselor_reply: str) -> bool:
        """상담사 답변 추가"""
        log = get_logger_with_request_id()
        log.info("Adding counselor reply", review_id=review_id)
        
        stmt = (
            update(ConsultationReview)
            .where(ConsultationReview.review_id == review_id)
            .values(
                counselor_reply=counselor_reply,
                counselor_replied_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Counselor reply added", review_id=review_id, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def set_best_review(self, review_id: int, is_best: bool = True) -> bool:
        """베스트 후기 설정/해제"""
        log = get_logger_with_request_id()
        log.info("Setting best review", review_id=review_id, is_best=is_best)
        
        stmt = (
            update(ConsultationReview)
            .where(ConsultationReview.review_id == review_id)
            .values(
                is_best=is_best,
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Best review status updated", review_id=review_id, is_best=is_best, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def increment_like_count(self, review_id: int) -> bool:
        """좋아요 수 증가"""
        stmt = (
            update(ConsultationReview)
            .where(ConsultationReview.review_id == review_id)
            .values(
                like_count=ConsultationReview.like_count + 1,
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def decrement_like_count(self, review_id: int) -> bool:
        """좋아요 수 감소"""
        stmt = (
            update(ConsultationReview)
            .where(and_(
                ConsultationReview.review_id == review_id,
                ConsultationReview.like_count > 0
            ))
            .values(
                like_count=ConsultationReview.like_count - 1,
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def delete(self, review_id: int) -> bool:
        """후기 삭제"""
        log = get_logger_with_request_id()
        log.info("Deleting review", review_id=review_id)
        
        stmt = delete(ConsultationReview).where(ConsultationReview.review_id == review_id)
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Review deletion completed", review_id=review_id, success=success)
        return success