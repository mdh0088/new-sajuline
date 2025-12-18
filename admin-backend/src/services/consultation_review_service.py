"""
ConsultationReviewService - 비즈니스 로직
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from src.repositories.consultation_review_repository import ConsultationReviewRepository

KST = ZoneInfo("Asia/Seoul")
from src.schemas.consultation_review_schema import (
    ConsultationReviewItem,
    ConsultationReviewListParams,
    ConsultationReviewUpdateRequest,
)
from src.exceptions.custom_exceptions import NotFoundError


class ConsultationReviewService:
    def __init__(self, repo: ConsultationReviewRepository):
        self.repo = repo

    async def get_review_list(
        self, params: ConsultationReviewListParams
    ) -> tuple[list[ConsultationReviewItem], int, int, int]:
        """후기 목록 조회 (페이징)"""
        items, total = await self.repo.get_list_with_users(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name,
            user_id=params.user_id,
            counselor_id=params.counselor_id,
            start_dt=params.start_dt,
            end_dt=params.end_dt,
        )

        return (
            [ConsultationReviewItem(**item) for item in items],
            params.page,
            params.limit,
            total,
        )

    async def get_review_detail(self, review_id: int) -> ConsultationReviewItem:
        """후기 상세 조회"""
        review_dict = await self.repo.get_by_id_with_users(review_id)
        if not review_dict:
            raise NotFoundError(f"후기 {review_id}를 찾을 수 없습니다.")
        return ConsultationReviewItem(**review_dict)

    async def update_review(
        self, review_id: int, payload: ConsultationReviewUpdateRequest
    ) -> ConsultationReviewItem:
        """후기 수정"""
        review = await self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError(f"후기 {review_id}를 찾을 수 없습니다.")

        # content 수정
        if payload.content is not None:
            review.content = payload.content

        # counselor_reply 수정
        if payload.counselor_reply is not None:
            review.counselor_reply = payload.counselor_reply
            # 답변을 처음 작성하는 경우 counselor_replied_at 설정
            if review.counselor_replied_at is None and payload.counselor_reply:
                review.counselor_replied_at = datetime.now(KST)

        # is_visible 수정
        if payload.is_visible is not None:
            review.is_visible = payload.is_visible

        # is_best 수정
        if payload.is_best is not None:
            review.is_best = payload.is_best

        # rating 수정
        if payload.rating is not None:
            review.rating = payload.rating

        # review_tags 수정
        if payload.review_tags is not None:
            review.review_tags = payload.review_tags

        updated = await self.repo.update(review)

        # 수정 후 상세 정보 반환 (JOIN 포함)
        review_dict = await self.repo.get_by_id_with_users(review_id)
        return ConsultationReviewItem(**review_dict)