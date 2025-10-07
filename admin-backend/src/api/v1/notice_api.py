"""
공지사항 관리 API (관리자 백엔드)

- 목록 조회: 필터/페이징, 검색 규칙 반영
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, APIResponseBuilder, ok
from src.core.database import get_db as get_db_maria
from src.repositories.notice_repository import NoticeRepository
from src.services.notice_service import NoticeService
from src.schemas.notice_schema import (
    NoticeListParams,
    NoticeDetailResponse,
    NoticeCreateRequest,
    NoticeUpdateRequest,
    NoticeDeleteResponse,
)
from src.services.security import get_current_user
from src.schemas.auth_schema import TokenPayload
from src.common.utils.auth_utils import verify_admin_role


router = APIRouter(prefix="/notices", tags=["notices"])


def _get_notice_service(db: AsyncSession = Depends(get_db_maria)) -> NoticeService:
    return NoticeService(NoticeRepository(db))


@router.get("/list", response_model=APIResponse, summary="공지사항 목록 조회")
async def get_notice_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|title|content"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    target_audience_param: Optional[str] = Query(None, alias="target_audience", description="ALL|USER|COUNSELOR"),
    target_audientce_param: Optional[str] = Query(None, alias="target_audientce", description="(오탈자 호환) ALL|USER|COUNSELOR"),
    notice_type: Optional[str] = Query(None, description="공지 타입 (예: GENERAL)"),
    is_important: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    start_dt: Optional[str] = Query(None, description="등록일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="등록일 종료 yyyy-mm-dd"),
    service: NoticeService = Depends(_get_notice_service),
):
    params = NoticeListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        target_audience=(target_audience_param or target_audientce_param),
        notice_type=notice_type,
        is_important=is_important,
        is_active=is_active,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    items, page, limit, total = await service.get_notice_list(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in items],
        page=page,
        limit=limit,
        total=total,
        message="공지 목록 조회 성공",
    )


@router.get("/detail", response_model=APIResponse[NoticeDetailResponse], summary="공지사항 상세 조회")
async def get_notice_detail(
    notice_id: int = Query(..., description="공지 PK"),
    service: NoticeService = Depends(_get_notice_service),
):
    data = await service.get_detail(notice_id)
    return ok(data=data, message="공지 상세 조회 성공")


@router.post("/create", response_model=APIResponse[NoticeDetailResponse], summary="공지사항 등록")
async def create_notice(
    payload: NoticeCreateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: NoticeService = Depends(_get_notice_service),
):
    #verify_admin_role(current_user)
    data = await service.create(payload, created_by=1)  # 임시: 관리자 ID 1
    return ok(data=data, message="공지 등록 성공")


@router.post("/update", response_model=APIResponse[NoticeDetailResponse], summary="공지사항 수정")
async def update_notice(
    payload: NoticeUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: NoticeService = Depends(_get_notice_service),
):
    #verify_admin_role(current_user)
    data = await service.update(payload)
    return ok(data=data, message="공지 수정 성공")


@router.delete("/delete", response_model=APIResponse[NoticeDeleteResponse], summary="공지사항 삭제")
async def delete_notice(
    notice_id: int = Query(..., description="공지 PK"),
    #current_user: TokenPayload = Depends(get_current_user),
    service: NoticeService = Depends(_get_notice_service),
):
    #verify_admin_role(current_user)
    data = await service.delete(notice_id)
    return ok(data=data, message="공지 삭제 성공")



