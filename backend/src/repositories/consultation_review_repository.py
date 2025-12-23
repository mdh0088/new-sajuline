"""
상담 후기 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

KST = ZoneInfo("Asia/Seoul")
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
            review_tags=(
                json.dumps(review_data.review_tags, ensure_ascii=False)
                if getattr(review_data, "review_tags", None)
                else None
            ),
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
    async def get_average_rating_by_user_id(self, user_id: str, *, visible_only: bool = True) -> float:
        """사용자 ID별 평균 평점 (기본: 공개 후기만)"""
        stmt = select(func.avg(ConsultationReview.rating)).where(ConsultationReview.user_id == user_id)
        if visible_only:
            stmt = stmt.where(ConsultationReview.is_visible == True)  # noqa: E712
        result = await self.db.execute(stmt)
        avg_val = result.scalar()
        try:
            return float(avg_val) if avg_val is not None else 0.0
        except Exception:
            return 0.0

    @logger.catch(reraise=True)
    async def get_average_rating_by_counselor_id(self, counselor_id: str, *, visible_only: bool = True) -> float:
        """상담사 ID별 평균 평점 (기본: 공개 후기만)"""
        log = get_logger_with_request_id()
        log.info("Getting average rating by counselor", counselor_id=counselor_id, visible_only=visible_only)
        stmt = select(func.avg(ConsultationReview.rating)).where(ConsultationReview.counselor_id == counselor_id)
        if visible_only:
            stmt = stmt.where(ConsultationReview.is_visible == True)  # noqa: E712
        result = await self.db.execute(stmt)
        avg_val = result.scalar()
        try:
            value = float(avg_val) if avg_val is not None else 0.0
            log.info("Average rating computed", counselor_id=counselor_id, average=value)
            return value
        except Exception:
            return 0.0

    @logger.catch(reraise=True)
    async def get_session_ids_by_user_id(self, user_id: str, *, visible_only: bool = True) -> List[int]:
        """해당 사용자의 (기본: 공개) 후기들의 session_id 목록 조회"""
        stmt = select(ConsultationReview.session_id).where(ConsultationReview.user_id == user_id)
        #if visible_only:
        #    stmt = stmt.where(ConsultationReview.is_visible == True)  # noqa: E712
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [int(r) for r in rows] if rows else []

    @logger.catch(reraise=True)
    async def get_by_id(self, review_id: int) -> Optional[ConsultationReview]:
        """리뷰 PK로 단건 조회"""
        stmt = select(ConsultationReview).where(ConsultationReview.review_id == review_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    @logger.catch(reraise=True)
    async def get_by_session_id(self, session_id: int) -> Optional[ConsultationReview]:
        """세션 ID로 단건 조회 (유니크)"""
        stmt = select(ConsultationReview).where(ConsultationReview.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
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
    async def get_review_counts_by_counselor_ids(
        self,
        counselor_ids: List[str],
        is_visible: Optional[bool] = True
    ) -> List[tuple]:
        """여러 상담사의 리뷰 개수 일괄 조회 (정렬용)"""
        if not counselor_ids:
            return []

        stmt = select(
            ConsultationReview.counselor_id,
            func.count(ConsultationReview.review_id).label('review_count')
        ).where(
            ConsultationReview.counselor_id.in_(counselor_ids)
        )

        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)

        stmt = stmt.group_by(ConsultationReview.counselor_id)

        result = await self.db.execute(stmt)
        return list(result.all())

    @logger.catch(reraise=True)
    async def get_all_reviews(
        self,
        is_visible: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConsultationReview]:
        """전체 후기 목록 조회 (공개 페이지용)"""
        log = get_logger_with_request_id()
        log.info("Getting all reviews", is_visible=is_visible, skip=skip, limit=limit)

        stmt = select(ConsultationReview)

        if is_visible is not None:
            stmt = stmt.where(ConsultationReview.is_visible == is_visible)

        stmt = stmt.offset(skip).limit(limit).order_by(ConsultationReview.created_at.desc())

        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())

        log.info("All reviews lookup completed", count=len(reviews))
        return reviews

    @logger.catch(reraise=True)
    async def get_all_reviews_count(
        self,
        is_visible: Optional[bool] = True
    ) -> int:
        """전체 후기 총 개수"""
        stmt = select(func.count(ConsultationReview.review_id))

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
        if getattr(update_data, "review_tags", None) is not None:
            # accept both list and pre-serialized string
            if isinstance(update_data.review_tags, str):
                update_values["review_tags"] = update_data.review_tags
            else:
                update_values["review_tags"] = json.dumps(update_data.review_tags or [], ensure_ascii=False)
        
        if not update_values:
            log.warning("No fields to update", review_id=review_id)
            return False
        
        update_values["updated_at"] = datetime.now(KST)
        
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
    async def update_by_session_id(self, *, user_id: str, session_id: int, update_data: ConsultationReviewUpdate) -> bool:
        """세션 ID로 후기 수정 (작성자 확인은 서비스 레벨에서 수행)"""
        log = get_logger_with_request_id()
        log.info("Updating review by session_id", session_id=session_id, user_id=user_id)

        update_values = {}
        if update_data.rating is not None:
            update_values["rating"] = update_data.rating
        if update_data.content is not None:
            update_values["content"] = update_data.content
        if update_data.is_visible is not None:
            update_values["is_visible"] = update_data.is_visible
        if getattr(update_data, "review_tags", None) is not None:
            if isinstance(update_data.review_tags, str):
                update_values["review_tags"] = update_data.review_tags
            else:
                update_values["review_tags"] = json.dumps(update_data.review_tags or [], ensure_ascii=False)

        if not update_values:
            log.warning("No fields to update (by session_id)")
            return False

        update_values["updated_at"] = datetime.now(KST)

        stmt = (
            update(ConsultationReview)
            .where(
                and_(
                    ConsultationReview.session_id == session_id,
                    ConsultationReview.user_id == user_id,
                )
            )
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        log.info("Review update-by-session completed", session_id=session_id, success=success)
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
                counselor_replied_at=datetime.now(KST),
                updated_at=datetime.now(KST)
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
                updated_at=datetime.now(KST)
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
                updated_at=datetime.now(KST)
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
                updated_at=datetime.now(KST)
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

    @logger.catch(reraise=True)
    async def soft_delete(self, review_id: int) -> bool:
        """후기 소프트 삭제: is_visible=false로 변경"""
        log = get_logger_with_request_id()
        log.info("Soft deleting review (set is_visible=false)", review_id=review_id)

        stmt = (
            update(ConsultationReview)
            .where(ConsultationReview.review_id == review_id)
            .values(is_visible=False, updated_at=datetime.now(KST))
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        log.info("Soft delete completed", review_id=review_id, success=success)
        return success