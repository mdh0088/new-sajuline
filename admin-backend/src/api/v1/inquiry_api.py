"""
상담사 문의 API (관리자 백엔드)

- 상담사 문의 목록 조회: inquirer_type='COUNSELOR' AND category='CS_TO_ADMIN'
- 상담사 문의 상세 조회
- 상담사 문의 수정(관리자 답변)
- 상담사 문의 삭제
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, APIResponseBuilder, ok
from src.core.database import get_db as get_db_maria
from src.repositories.inquiry_repository import InquiryRepository
from src.services.inquiry_service import InquiryService
from src.schemas.inquiry_schema import (
    InquiryListParams,
    InquiryReplyUpdateRequest,
    InquiryUpdateRequest,
    UserInquiryListParams,
    UserToCsListParams,
)
from src.services.security import get_current_user
from src.schemas.auth_schema import TokenPayload
from src.common.utils.auth_utils import verify_admin_role


router = APIRouter(prefix="/inquiries", tags=["inquiries"])


def _get_inquiry_service(db: AsyncSession = Depends(get_db_maria)) -> InquiryService:
    return InquiryService(InquiryRepository(db))


@router.get("/list", response_model=APIResponse, summary="상담사 문의 목록 조회")
async def list_counselor_inquiries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|user_title|user_content|reply_content"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    counselor_id: Optional[str] = Query(None, description="상담사 ID (inquirer_id와 매칭)"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    params = InquiryListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        counselor_id=counselor_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    data = await service.list_counselor_inquiries(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in data.items],
        page=data.page,
        limit=data.limit,
        total=data.total,
        message="상담사 문의 목록 조회 성공",
    )


@router.get("/detail", response_model=APIResponse, summary="상담사 문의 상세 조회")
async def get_counselor_inquiry_detail(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.get_counselor_inquiry_detail(inquiry_id)
    return ok(data=data.model_dump(), message="상담사 문의 상세 조회 성공")


@router.post("/reply", response_model=APIResponse, summary="상담사 문의 관리자 답변 수정")
async def update_counselor_inquiry_reply(
    payload: InquiryReplyUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_counselor_inquiry_reply(payload, admin_id=1)
    return ok(data=data.model_dump(), message="상담사 문의 답변 수정 성공")


@router.put("/update", response_model=APIResponse, summary="상담사 문의 수정 (제목/내용/답변)")
async def update_counselor_inquiry(
    payload: InquiryUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_counselor_inquiry(payload, admin_id=1)
    return ok(data=data.model_dump(), message="상담사 문의 수정 성공")


@router.delete("/delete", response_model=APIResponse, summary="상담사 문의 삭제")
async def delete_counselor_inquiry(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.delete_counselor_inquiry(inquiry_id)
    return ok(data=data.model_dump(), message="상담사 문의 삭제 성공")


# =============================
# 1:1 고객센터 문의 (USER_TO_ADMIN)
# =============================
@router.get("/user/list", response_model=APIResponse, summary="1:1 고객센터 문의 목록 조회")
async def list_user_inquiries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|title|content"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    user_id: Optional[str] = Query(None, description="사용자 ID (inquirer_id와 매칭)"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    params = UserInquiryListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        user_id=user_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    data = await service.list_user_inquiries(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in data.items],
        page=data.page,
        limit=data.limit,
        total=data.total,
        message="고객센터 문의 목록 조회 성공",
    )


@router.get("/user/detail", response_model=APIResponse, summary="1:1 고객센터 문의 상세 조회")
async def get_user_inquiry_detail(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.get_user_inquiry_detail(inquiry_id)
    return ok(data=data.model_dump(), message="고객센터 문의 상세 조회 성공")


@router.post("/user/reply", response_model=APIResponse, summary="1:1 고객센터 문의 관리자 답변 수정")
async def update_user_inquiry_reply(
    payload: InquiryReplyUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_user_inquiry_reply(payload, admin_id=1)
    return ok(data=data.model_dump(), message="고객센터 문의 답변 수정 성공")


@router.put("/user/update", response_model=APIResponse, summary="1:1 고객센터 문의 수정 (제목/내용/답변)")
async def update_user_inquiry(
    payload: InquiryUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_user_inquiry(payload, admin_id=1)
    return ok(data=data.model_dump(), message="고객센터 문의 수정 성공")


@router.delete("/user/delete", response_model=APIResponse, summary="1:1 고객센터 문의 삭제")
async def delete_user_inquiry(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.delete_user_inquiry(inquiry_id)
    return ok(data=data.model_dump(), message="고객센터 문의 삭제 성공")


# =============================
# 1:1 상담사 문의 (USER_TO_CS)
# =============================
@router.get("/user-to-cs/list", response_model=APIResponse, summary="1:1 상담사 문의 목록 조회")
async def list_user_to_cs_inquiries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|user_title|user_content|reply_content"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    user_id: Optional[str] = Query(None, description="사용자 ID (inquirer_id와 매칭)"),
    counselor_id: Optional[str] = Query(None, description="상담사 ID (counselor_id와 매칭)"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    params = UserToCsListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        user_id=user_id,
        counselor_id=counselor_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    data = await service.list_user_to_cs_inquiries(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in data.items],
        page=data.page,
        limit=data.limit,
        total=data.total,
        message="1:1 상담사 문의 목록 조회 성공",
    )


@router.get("/user-to-cs/detail", response_model=APIResponse, summary="1:1 상담사 문의 상세 조회")
async def get_user_to_cs_detail(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.get_user_to_cs_detail(inquiry_id)
    return ok(data=data.model_dump(), message="1:1 상담사 문의 상세 조회 성공")


@router.post("/user-to-cs/reply", response_model=APIResponse, summary="1:1 상담사 문의 답변 수정")
async def update_user_to_cs_reply(
    payload: InquiryReplyUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_user_to_cs_reply(payload, admin_id=1)
    return ok(data=data.model_dump(), message="1:1 상담사 문의 답변 수정 성공")


@router.put("/user-to-cs/update", response_model=APIResponse, summary="1:1 상담사 문의 수정 (제목/내용/답변)")
async def update_user_to_cs_inquiry(
    payload: InquiryUpdateRequest = Body(...),
    #current_user: TokenPayload = Depends(get_current_user),
    service: InquiryService = Depends(_get_inquiry_service),
):
    #verify_admin_role(current_user)
    data = await service.update_user_to_cs_inquiry(payload, admin_id=1)
    return ok(data=data.model_dump(), message="1:1 상담사 문의 수정 성공")


@router.delete("/user-to-cs/delete", response_model=APIResponse, summary="1:1 상담사 문의 삭제")
async def delete_user_to_cs(
    inquiry_id: int = Query(..., description="문의 ID"),
    service: InquiryService = Depends(_get_inquiry_service),
):
    data = await service.delete_user_to_cs(inquiry_id)
    return ok(data=data.model_dump(), message="1:1 상담사 문의 삭제 성공")

