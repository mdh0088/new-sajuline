"""
상담 후기 관리 API
"""
from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.services.consultation_review_service import ConsultationReviewService
from src.schemas.consultation_review_schema import (
    ConsultationReviewListParams,
    ConsultationReviewUpdateRequest,
)
from src.common.response import APIResponse, APIResponseBuilder

router = APIRouter(prefix="/consultation-reviews", tags=["상담 후기 관리"])


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ConsultationReviewService:
    return ConsultationReviewService(ConsultationReviewRepository(db))


@router.get("/list", response_model=APIResponse, summary="상담 후기 목록 조회")
async def get_review_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|content|reply_content"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    counselor_id: Optional[str] = Query(None, description="상담사 ID"),
    start_dt: Optional[str] = Query(None, description="검색 시작일 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="검색 종료일 yyyy-mm-dd"),
    service: ConsultationReviewService = Depends(_get_service),
):
    """
    상담 후기 목록 조회 (페이징, 검색)
    - User, Counselor JOIN하여 닉네임 포함
    - created_at desc 정렬
    """
    params = ConsultationReviewListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        user_id=user_id,
        counselor_id=counselor_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    items, page, limit, total = await service.get_review_list(params)
    return APIResponseBuilder.paginated(
        data=[item.model_dump() for item in items],
        page=page,
        limit=limit,
        total=total,
        message="상담 후기 목록 조회 성공",
    )


@router.get("/{review_id}", response_model=APIResponse, summary="상담 후기 상세 조회")
async def get_review_detail(
    review_id: int,
    service: Annotated[ConsultationReviewService, Depends(_get_service)],
):
    """
    상담 후기 상세 조회
    - User, Counselor JOIN하여 닉네임 포함
    """
    result = await service.get_review_detail(review_id)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="상담 후기 상세 조회 성공",
    )


@router.put("/{review_id}", response_model=APIResponse, summary="상담 후기 수정")
async def update_review(
    review_id: int,
    payload: ConsultationReviewUpdateRequest,
    service: Annotated[ConsultationReviewService, Depends(_get_service)],
):
    """
    상담 후기 수정
    - content, counselor_reply 수정 가능
    """
    result = await service.update_review(review_id, payload)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="상담 후기 수정 성공",
    )