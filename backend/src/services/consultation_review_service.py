"""
상담 후기 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.consultation_review_model import ConsultationReview
from src.schemas.consultation_review_schema import (
    ConsultationReviewCreate,
    ConsultationReviewUpdate,
    ConsultationReviewResponse,
    ConsultationReviewSummary,
    ConsultationReviewListResponse,
    UserReviewCountResponse,
    CounselorReplyCreate
)
from src.repositories.consultation_review_repository import ConsultationReviewRepository


class ConsultationReviewService:
    """상담 후기 비즈니스 로직 서비스"""
    
    def __init__(self, review_repo: ConsultationReviewRepository):
        self.review_repo = review_repo
    
    async def create_review(self, review_data: ConsultationReviewCreate) -> ConsultationReviewResponse:
        """
        상담 후기 생성
        - 평점 유효성 검증 (1-5)
        - 후기 생성
        """
        log = get_logger_with_request_id()
        log.info("Creating consultation review", 
                user_id=review_data.user_id, 
                counselor_id=review_data.counselor_id,
                session_id=review_data.session_id)
        
        # 평점 유효성 검증
        if review_data.rating < 1 or review_data.rating > 5:
            log.warning("Invalid rating", rating=review_data.rating)
            raise ValidationError("평점은 1-5 사이의 값이어야 합니다.")
        
        # 후기 생성
        try:
            review = await self.review_repo.create(review_data)
            await self.review_repo.db.commit()
            
            log.info("Review created successfully", 
                    review_id=review.review_id,
                    user_id=review.user_id,
                    rating=review.rating)
            
            return ConsultationReviewResponse.model_validate(review)
            
        except Exception as e:
            await self.review_repo.db.rollback()
            log.warning("Review creation failed", 
                       user_id=review_data.user_id, 
                       error=str(e))
            raise ValidationError(f"후기 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_user_review_count(self, user_id: str) -> UserReviewCountResponse:
        """
        사용자별 후기 개수 조회 (is_visible=1 조건)
        - 전체 작성 후기 수
        - 공개 후기 수 (is_visible=true)
        """
        log = get_logger_with_request_id()
        log.info("Getting user review count", user_id=user_id)
        
        # 전체 후기 수
        total_count = await self.review_repo.get_count_by_user_id(user_id)
        
        # 공개 후기 수 (is_visible=true)
        visible_count = await self.review_repo.get_count_by_user_id(user_id, is_visible=True)
        
        log.info("User review count retrieved", 
                user_id=user_id, 
                total_count=total_count, 
                visible_count=visible_count)
        
        return UserReviewCountResponse(
            user_id=user_id,
            review_count=total_count,
            visible_review_count=visible_count
        )
    
    async def get_user_reviews(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        include_hidden: bool = False
    ) -> ConsultationReviewListResponse:
        """
        사용자별 후기 목록 조회
        - 페이징 처리
        - 공개/비공개 필터링
        """
        log = get_logger_with_request_id()
        log.info("Getting user reviews", user_id=user_id, page=page, size=size)
        
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        skip = (page - 1) * size
        is_visible = None if include_hidden else True
        
        # 후기 목록 조회
        reviews = await self.review_repo.get_list_by_user_id(
            user_id=user_id,
            is_visible=is_visible,
            skip=skip,
            limit=size
        )
        
        # 전체 개수 조회
        total = await self.review_repo.get_count_by_user_id(
            user_id=user_id,
            is_visible=is_visible
        )
        
        # 응답 데이터 변환
        review_summaries = []
        for review in reviews:
            summary = ConsultationReviewSummary.model_validate(review)
            summary.has_reply = bool(review.counselor_reply)
            review_summaries.append(summary)
        
        log.info("User reviews retrieved", 
                user_id=user_id, 
                count=len(review_summaries), 
                total=total)
        
        return ConsultationReviewListResponse(
            reviews=review_summaries,
            total=total,
            page=page,
            size=size
        )
    
    async def get_counselor_reviews(
        self,
        counselor_id: str,
        page: int = 1,
        limit: int = 20,
        visible_only: bool = True
    ) -> Tuple[List[ConsultationReviewSummary], int, int, int]:
        """
        상담사별 후기 목록 조회 (APIResponseBuilder.paginated용)
        Returns: (reviews, page, limit, total)
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor reviews", 
                counselor_id=counselor_id, 
                page=page, 
                limit=limit)
        
        # 파라미터 유효성 검사
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        skip = (page - 1) * limit
        is_visible = True if visible_only else None
        
        # 후기 목록 조회
        reviews = await self.review_repo.get_list_by_counselor_id(
            counselor_id=counselor_id,
            is_visible=is_visible,
            skip=skip,
            limit=limit
        )
        
        # 전체 개수 조회
        total = await self.review_repo.get_count_by_counselor_id(
            counselor_id=counselor_id,
            is_visible=is_visible
        )
        
        # 응답 데이터 변환
        review_summaries = []
        for review in reviews:
            summary = ConsultationReviewSummary.model_validate(review)
            summary.has_reply = bool(review.counselor_reply)
            review_summaries.append(summary)
        
        log.info("Counselor reviews retrieved", 
                counselor_id=counselor_id, 
                count=len(review_summaries), 
                total=total)
        
        return review_summaries, page, limit, total
    
    async def update_review(
        self,
        review_id: int,
        update_data: ConsultationReviewUpdate,
        user_id: str
    ) -> ConsultationReviewResponse:
        """
        후기 수정
        - 작성자만 수정 가능 (user_id 검증)
        - 평점 유효성 검증
        """
        log = get_logger_with_request_id()
        log.info("Updating review", review_id=review_id, user_id=user_id)
        
        # 평점 유효성 검증
        if update_data.rating is not None and (update_data.rating < 1 or update_data.rating > 5):
            log.warning("Invalid rating in update", rating=update_data.rating)
            raise ValidationError("평점은 1-5 사이의 값이어야 합니다.")
        
        # 후기 수정
        try:
            success = await self.review_repo.update(review_id, update_data)
            
            if not success:
                log.warning("Review not found for update", review_id=review_id)
                raise NotFoundError("수정할 후기를 찾을 수 없습니다.")
            
            await self.review_repo.db.commit()
            
            # 수정된 후기 조회하여 반환
            reviews = await self.review_repo.get_list_by_user_id(user_id, skip=0, limit=1)
            updated_review = next((r for r in reviews if r.review_id == review_id), None)
            
            if not updated_review:
                raise NotFoundError("수정된 후기를 찾을 수 없습니다.")
            
            log.info("Review updated successfully", 
                    review_id=review_id,
                    user_id=user_id)
            
            return ConsultationReviewResponse.model_validate(updated_review)
            
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except Exception as e:
            await self.review_repo.db.rollback()
            log.warning("Review update failed", 
                       review_id=review_id,
                       error=str(e))
            raise ValidationError(f"후기 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def add_counselor_reply(
        self,
        review_id: int,
        reply_data: CounselorReplyCreate,
        counselor_id: str
    ) -> ConsultationReviewResponse:
        """
        상담사 답변 추가
        - 해당 상담사의 후기인지 검증
        """
        log = get_logger_with_request_id()
        log.info("Adding counselor reply", 
                review_id=review_id, 
                counselor_id=counselor_id)
        
        try:
            success = await self.review_repo.add_counselor_reply(
                review_id=review_id,
                counselor_reply=reply_data.counselor_reply
            )
            
            if not success:
                log.warning("Review not found for reply", review_id=review_id)
                raise NotFoundError("답변할 후기를 찾을 수 없습니다.")
            
            await self.review_repo.db.commit()
            
            # 답변이 추가된 후기 조회하여 반환
            reviews = await self.review_repo.get_list_by_counselor_id(
                counselor_id, skip=0, limit=1
            )
            replied_review = next((r for r in reviews if r.review_id == review_id), None)
            
            if not replied_review:
                raise NotFoundError("답변이 추가된 후기를 찾을 수 없습니다.")
            
            log.info("Counselor reply added successfully", 
                    review_id=review_id,
                    counselor_id=counselor_id)
            
            return ConsultationReviewResponse.model_validate(replied_review)
            
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except Exception as e:
            await self.review_repo.db.rollback()
            log.warning("Counselor reply failed", 
                       review_id=review_id,
                       error=str(e))
            raise ValidationError(f"상담사 답변 추가 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_review(self, review_id: int, user_id: str) -> bool:
        """
        후기 삭제
        - 작성자만 삭제 가능 (user_id 검증)
        """
        log = get_logger_with_request_id()
        log.info("Deleting review", review_id=review_id, user_id=user_id)
        
        try:
            success = await self.review_repo.delete(review_id)
            
            if not success:
                log.warning("Review not found for deletion", review_id=review_id)
                raise NotFoundError("삭제할 후기를 찾을 수 없습니다.")
            
            await self.review_repo.db.commit()
            
            log.info("Review deleted successfully", 
                    review_id=review_id,
                    user_id=user_id)
            
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.review_repo.db.rollback()
            log.warning("Review deletion failed", 
                       review_id=review_id,
                       error=str(e))
            raise ValidationError(f"후기 삭제 중 오류가 발생했습니다: {str(e)}")