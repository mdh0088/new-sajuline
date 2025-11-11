"""
상담사 신청 관리 API (관리자 백엔드)

- 상세 수정: multipart/form-data (이미지 업로드 포함)
- 목록 조회: 필터/페이징
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from src.common.response import ok, APIResponse, APIResponseBuilder
from src.schemas.counselor_application_schema import (
    CounselorApplicationListParams,
    CounselorApplicationListItem,
    CounselorApplicationDetailUpdate,
    CounselorApplicationDetailResponse,
    CounselorApplicationResponse,
    CounselorApplicationStatusUpdate,
)
from src.services.counselor_application_service import CounselorApplicationService
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db as get_db_maria
from src.repositories.counselor_application_repository import CounselorApplicationRepository
from src.services.security import get_current_user
from src.schemas.auth_schema import TokenPayload
from src.common.utils.auth_utils import verify_admin_role


router = APIRouter(prefix="/counselor-applications", tags=["counselor-applications"])


def _get_application_service(
    db: AsyncSession = Depends(get_db_maria),
) -> CounselorApplicationService:
    return CounselorApplicationService(CounselorApplicationRepository(db))


@router.get("/list", response_model=APIResponse, summary="상담사 신청 목록 조회")
async def get_application_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|name|nickname|email"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    specialties: Optional[List[str]] = Query(None, description="전문 분야 필터 (예: ['TARO','SAJU'])"),
    application_status: Optional[str] = Query(None, description="신청 상태: PENDING|APPROVED|REJECTED"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    #current_user: TokenPayload = Depends(get_current_user),
    application_service: CounselorApplicationService = Depends(_get_application_service),
):
    """상담사 신청 목록 조회 (페이징 + 필터)"""
    #verify_admin_role(current_user)
    params = CounselorApplicationListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        specialties=specialties,
        application_status=application_status,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    items, page, limit, total = await application_service.get_application_list(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in items],
        page=page,
        limit=limit,
        total=total,
        message="상담사 신청 목록 조회 성공",
    )


@router.get("/detail", response_model=APIResponse[CounselorApplicationResponse], summary="상담사 신청 상세 조회")
async def get_application_detail(
    application_id: int = Query(..., description="신청 ID"),
    application_service: CounselorApplicationService = Depends(_get_application_service),
    #current_user: TokenPayload = Depends(get_current_user),
):
    """상담사 신청 상세 정보 조회"""
    #verify_admin_role(current_user)
    application = await application_service.get_detail(application_id)
    return ok(
        data=CounselorApplicationResponse.model_validate(application, from_attributes=True),
        message="상담사 신청 상세 조회 성공",
    )


@router.patch(
    "/{application_id}/status",
    response_model=APIResponse,
    summary="상담사 신청 상태 변경 (간단 버전)",
    description="application_id와 상태값만으로 신청 상태를 변경합니다.",
)
async def update_application_status(
    application_id: int,
    status_update: CounselorApplicationStatusUpdate,
    application_service: CounselorApplicationService = Depends(_get_application_service),
    #current_user: TokenPayload = Depends(get_current_user),
):
    """상담사 신청 상태 변경"""
    #verify_admin_role(current_user)
    await application_service.update_status(
        application_id=application_id,
        application_status=status_update.application_status,
        admin_note=status_update.admin_note,
        reviewed_by=status_update.reviewed_by,
    )
    return ok(
        data={
            "application_id": application_id,
            "application_status": status_update.application_status
        },
        message="신청 상태 변경 성공"
    )


@router.patch(
    "/{application_id}",
    response_model=APIResponse[CounselorApplicationDetailResponse],
    summary="상담사 신청 상세 수정 (이미지 업로드 포함)",
    description="multipart/form-data로 텍스트 필드와 이미지 파일을 함께 전송합니다.",
)
async def update_application_detail(
    application_id: int,
    # multipart fields
    name: Optional[str] = Form(default=None),
    nickname: Optional[str] = Form(default=None),
    email: Optional[str] = Form(default=None),
    phone: Optional[str] = Form(default=None),
    address: Optional[str] = Form(default=None),
    specialties: Optional[str] = Form(default=None),
    keywords: Optional[str] = Form(default=None),
    introduction: Optional[str] = Form(default=None),
    application_status: Optional[str] = Form(default=None),
    admin_note: Optional[str] = Form(default=None),
    reviewed_by: Optional[int] = Form(default=None),
    selected_image: Optional[UploadFile] = File(default=None),
    upload_image1: Optional[UploadFile] = File(default=None),
    upload_image2: Optional[UploadFile] = File(default=None),
    upload_image3: Optional[UploadFile] = File(default=None),
    #current_user: TokenPayload = Depends(get_current_user),
    application_service: CounselorApplicationService = Depends(_get_application_service),
):
    """상담사 신청 상세 정보 수정"""
    #verify_admin_role(current_user)
    form = CounselorApplicationDetailUpdate(
        name=name,
        nickname=nickname,
        email=email,
        phone=phone,
        address=address,
        specialties=specialties,
        keywords=keywords,
        introduction=introduction,
        application_status=application_status,
        admin_note=admin_note,
        reviewed_by=reviewed_by,
    )
    data = await application_service.update_application_detail(
        application_id=application_id,
        form=form,
        selected_image=selected_image,
        upload_image1=upload_image1,
        upload_image2=upload_image2,
        upload_image3=upload_image3,
    )
    return ok(data=data, message="상담사 신청 정보 수정 성공")
