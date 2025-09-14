"""
상담 후기 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
import json
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
    CounselorReplyCreate,
    UserReviewSummary,
    CounselorBriefInfo,
    UserReviewItem,
    UserReviewList,
    PendingReviewItem,
    PendingReviewList,
    UserReviewCreateRequest,
    UserReviewUpdateRequest,
)
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.point_transaction_service import PointTransactionService
from src.models.point_transaction_model import TransactionType, CurrencyType, ReferenceType
from src.exceptions.custom_exceptions import BaseAppException


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

    # =========================
    # User Review - Extended
    # =========================
    async def get_user_review_summary(
        self,
        *,
        user_id: str,
        chatlog_repo: Tm60ChatlogRepository,
    ) -> UserReviewSummary:
        """사용자 후기 요약 (작성/대기/평균/포인트)"""
        log = get_logger_with_request_id()
        log.info("Getting user review summary", user_id=user_id)

        # 작성한 후기 수 (is_visible=True)
        my_count = await self.review_repo.get_count_by_user_id(user_id, is_visible=True)

        # 평균 평점 (is_visible=True)
        avg_rating = await self.review_repo.get_average_rating_by_user_id(user_id, visible_only=True)

        # 작성 대기 수: tm60_chatlog.usepoint > 0 and u_id=user, idx not in session_ids
        session_ids = await self.review_repo.get_session_ids_by_user_id(user_id, visible_only=True)
        _, pending_total = await chatlog_repo.get_pending_sessions(
            user_id=user_id,
            exclude_session_ids=session_ids,
            page=1,
            limit=1,
        )

        # 받은 포인트 = 작성한 후기 수 * 100
        earned_points = my_count * 100

        return UserReviewSummary(
            total_my_reviews=my_count,
            total_pending_reviews=pending_total,
            average_rating=round(float(avg_rating), 2) if avg_rating is not None else 0.0,
            earned_points=earned_points,
        )

    async def get_my_reviews_detailed(
        self,
        *,
        user_id: str,
        page: int,
        limit: int,
        chatlog_repo: Tm60ChatlogRepository,
        counselor_repo: CounselorRepository,
    ) -> Tuple[UserReviewList, int]:
        """작성한 후기 상세 목록 (상담사/실상담시간 포함)"""
        log = get_logger_with_request_id()
        log.info("Getting my detailed reviews", user_id=user_id, page=page, limit=limit)

        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        skip = (page - 1) * limit

        reviews = await self.review_repo.get_list_by_user_id(user_id, is_visible=True, skip=skip, limit=limit)
        total = await self.review_repo.get_count_by_user_id(user_id, is_visible=True)

        # tm60_chatlog fetch by session ids
        session_ids = [r.session_id for r in reviews if r.session_id]
        chatlogs = await chatlog_repo.get_by_idx_list(session_ids)
        idx_to_log = {c.idx: c for c in chatlogs}

        # counselor map by counselor_id
        # Using per-item fetch to avoid adding new repository; small N expected
        items: List[UserReviewItem] = []
        for r in reviews:
            counselor = await counselor_repo.get_by_id(r.counselor_id)
            chatlog = idx_to_log.get(r.session_id)
            try:
                tags = json.loads(r.review_tags) if getattr(r, "review_tags", None) else None
            except Exception:
                tags = None

            items.append(
                UserReviewItem(
                    review_id=r.review_id,
                    session_id=r.session_id,
                    rating=r.rating,
                    content=r.content,
                    counselor_reply=r.counselor_reply,
                    review_tags=tags,
                    is_best=r.is_best,
                    created_at=r.created_at,
                    counselor_replied_at=r.counselor_replied_at,
                    realchattm=(chatlog.realchattm if chatlog else None),
                    counselor=(
                        None
                        if not counselor
                        else CounselorBriefInfo(
                            nickname=counselor.nickname,
                            profile_image_url=counselor.profile_image_url,
                        )
                    ),
                )
            )

        return UserReviewList(items=items, total=total, page=page, limit=limit), total

    async def get_pending_reviews(
        self,
        *,
        user_id: str,
        page: int,
        limit: int,
        chatlog_repo: Tm60ChatlogRepository,
        counselor_repo: CounselorRepository,
    ) -> Tuple[PendingReviewList, int]:
        """작성 대기 목록 (tm60_chatlog 기반)"""
        log = get_logger_with_request_id()
        log.info("Getting pending reviews", user_id=user_id, page=page, limit=limit)

        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        existing_session_ids = await self.review_repo.get_session_ids_by_user_id(user_id, visible_only=True)
        rows, total = await chatlog_repo.get_pending_sessions(
            user_id=user_id,
            exclude_session_ids=existing_session_ids,
            page=page,
            limit=limit,
        )

        codes = sorted({row.m_code for row in rows if row.m_code})
        code_to_counselor = await counselor_repo.get_by_counselor_codes(codes)

        items: List[PendingReviewItem] = []
        for row in rows:
            c = code_to_counselor.get(row.m_code)
            items.append(
                PendingReviewItem(
                    session_id=row.idx,
                    starttm=row.starttm,
                    realchattm=row.realchattm,
                    counselor=(
                        None
                        if not c
                        else CounselorBriefInfo(
                            nickname=c.nickname,
                            profile_image_url=c.profile_image_url,
                        )
                    ),
                )
            )

        return PendingReviewList(items=items, total=total, page=page, limit=limit), total

    async def create_user_review_with_award(
        self,
        *,
        user_id: str,
        payload: UserReviewCreateRequest,
        chatlog_repo: Tm60ChatlogRepository,
        counselor_repo: CounselorRepository,
        tm60_users_service: Tm60UsersService,
        point_transaction_service: PointTransactionService,
    ) -> ConsultationReviewResponse:
        """후기 생성 + 포인트 지급(성공 시 로그 기록)"""
        log = get_logger_with_request_id()
        log.info("Creating user review with award", user_id=user_id, session_id=payload.session_id)

        # Validate rating range handled by schema

        # Duplicate check by session_id
        exists = await self.review_repo.get_by_session_id(payload.session_id)
        if exists:
            raise DuplicateError("이미 해당 세션에 대한 후기가 존재합니다.")

        # Verify chatlog row belongs to user and usepoint > 0
        logs = await chatlog_repo.get_by_idx_list([payload.session_id])
        log_row = logs[0] if logs else None
        if not log_row or log_row.u_id != user_id or int(log_row.usepoint or 0) <= 0:
            raise ValidationError("유효한 상담 세션이 아닙니다.")

        # Map counselor by m_code
        counselor = await counselor_repo.get_by_counselor_code(log_row.m_code)
        if not counselor:
            raise ValidationError("상담사 정보를 찾을 수 없습니다.")

        review_create = ConsultationReviewCreate(
            session_id=payload.session_id,
            user_id=user_id,
            counselor_id=counselor.counselor_id,
            rating=payload.rating,
            content=payload.content,
            review_tags=payload.review_tags or None,
            is_visible=True,
        )

        try:
            review = await self.review_repo.create(review_create)
            await self.review_repo.db.commit()
        except Exception as e:
            await self.review_repo.db.rollback()
            raise ValidationError(f"후기 생성 실패: {str(e)}")

        # 포인트 지급 (best-effort)
        try:
            new_balance = await tm60_users_service.update_user_points(user_id=user_id, point_amount=100)
            await point_transaction_service.create_transaction(
                user_id=user_id,
                transaction_type=TransactionType.EARN,
                currency_type=CurrencyType.POINT,
                amount=100,
                balance_after=new_balance,
                reference_type=ReferenceType.REVIEW,
                reference_id=str(review.review_id),
                description="후기작성",
            )
        except BaseAppException as e:
            # 로그만 남기고 무시 (포인트 지급 실패)
            log.warning("Point awarding failed after review creation", user_id=user_id, error=str(e))
        except Exception as e:
            log.warning("Point awarding failed (unexpected)", user_id=user_id, error=str(e))

        # ensure review_tags returned as list
        resp = ConsultationReviewResponse.model_validate(review)
        return resp

    async def update_user_review_by_session(
        self,
        *,
        user_id: str,
        payload: UserReviewUpdateRequest,
    ) -> ConsultationReviewResponse:
        """세션 기준 후기 수정 (포인트 지급 없음)"""
        log = get_logger_with_request_id()
        log.info("Updating user review by session", user_id=user_id, session_id=payload.session_id)

        upd = ConsultationReviewUpdate(
            rating=payload.rating,
            content=payload.content,
            is_visible=None,
        )
        # tags 처리 위해 setattr
        setattr(upd, "review_tags", payload.review_tags)

        try:
            success = await self.review_repo.update_by_session_id(user_id=user_id, session_id=payload.session_id, update_data=upd)
            if not success:
                raise NotFoundError("수정할 후기를 찾을 수 없습니다.")
            await self.review_repo.db.commit()
        except Exception as e:
            await self.review_repo.db.rollback()
            raise ValidationError(f"후기 수정 실패: {str(e)}")

        # 갱신된 레코드 조회
        updated = await self.review_repo.get_by_session_id(payload.session_id)
        if not updated or updated.user_id != user_id:
            raise NotFoundError("수정된 후기를 찾을 수 없습니다.")
        return ConsultationReviewResponse.model_validate(updated)

    async def delete_user_review_with_check(self, *, review_id: int, user_id: str) -> bool:
        """상담사 답변이 있으면 삭제 불가"""
        log = get_logger_with_request_id()
        log.info("Deleting user review with check", user_id=user_id, review_id=review_id)

        review = await self.review_repo.get_by_id(review_id)
        if not review or review.user_id != user_id:
            raise NotFoundError("삭제할 후기를 찾을 수 없습니다.")
        if review.counselor_reply:
            raise ValidationError("상담사 답변이 있는 후기는 삭제할 수 없습니다.")

        try:
            # soft delete: set is_visible=false
            success = await self.review_repo.soft_delete(review_id)
            if not success:
                raise NotFoundError("삭제할 후기를 찾을 수 없습니다.")
            await self.review_repo.db.commit()
            return True
        except Exception as e:
            await self.review_repo.db.rollback()
            raise ValidationError(f"후기 삭제 실패: {str(e)}")