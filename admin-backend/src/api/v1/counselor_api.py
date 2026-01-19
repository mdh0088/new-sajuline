"""
상담사 관리 API (관리자 백엔드)

- 상세 수정: multipart/form-data (이미지 업로드 포함)
- 목록 조회: 필터/페이징
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from src.common.response import ok, APIResponse, APIResponseBuilder
from src.schemas.counselor_schema import (
    CounselorListParams,
    CounselorListItem,
    CounselorDetailUpdate,
    CounselorDetailResponse,
    CounselorFullDetailResponse,
    CounselorStateUpdateRequest,
    CounselorStateUpdateResponse,
    CounselorResponse,
)
from src.schemas.ars.tm60_member_schema import Tm60MemberResponse
from src.services.counselor_service import CounselorService
from src.services.counselor_status_service import CounselorStatusService
from src.services.auth_service import AuthService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.core.database import get_db as get_db_maria, get_db_mssql
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.services.ars.tm60_member_service import Tm60MemberService
from src.repositories.admin_repository import AdminRepository
from src.services.security import get_current_user
from src.schemas.auth_schema import TokenPayload
from src.common.utils.auth_utils import verify_admin_role


router = APIRouter(prefix="/counselors", tags=["counselors"])


def _get_auth_service() -> AuthService:
    return AuthService()


def _get_tm60_service(mssql: Session = Depends(get_db_mssql)) -> Tm60MemberService:
    return Tm60MemberService(Tm60MemberRepository(mssql))


def _get_counselor_service(
    db: AsyncSession = Depends(get_db_maria),
    auth: AuthService = Depends(_get_auth_service),
    tm60: Tm60MemberService = Depends(_get_tm60_service),
) -> CounselorService:
    return CounselorService(CounselorRepository(db), auth, tm60)


def _get_counselor_status_service(
    db: AsyncSession = Depends(get_db_maria),
    tm60: Tm60MemberService = Depends(_get_tm60_service),
) -> CounselorStatusService:
    return CounselorStatusService(db=db, tm60_member_service_factory=lambda: tm60)


@router.get("/list", response_model=APIResponse, summary="상담사 목록 조회")
async def get_counselor_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|name|nickname|counselor_id"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    specialties: Optional[List[str]] = Query(None, description="전문 분야 필터 (예: ['TARO','SAJU'])"),
    is_show: Optional[bool] = Query(None, description="노출 여부"),
    is_out: Optional[bool] = Query(None, description="탈퇴 여부"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    #current_user: TokenPayload = Depends(get_current_user),
    counselor_service: CounselorService = Depends(_get_counselor_service),
):
    #verify_admin_role(current_user)
    params = CounselorListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        specialties=specialties,
        is_show=is_show,
        is_out=is_out,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    items, page, limit, total = await counselor_service.get_counselor_list(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in items],
        page=page,
        limit=limit,
        total=total,
        message="상담사 목록 조회 성공",
    )


@router.get("/all", response_model=APIResponse, summary="전체 상담사 목록 조회 (셀렉트박스용)")
async def get_all_counselors(
    counselor_service: CounselorService = Depends(_get_counselor_service),
):
    """
    페이지네이션 없이 전체 상담사 목록을 조회합니다.
    셀렉트박스 등에서 사용하기 위한 간소화된 API입니다.
    """
    items = await counselor_service.get_all_counselors()
    return ok(
        data=[{"counselor_id": i.counselor_id, "nickname": i.nickname, "name": i.name} for i in items],
        message="전체 상담사 목록 조회 성공",
    )


@router.patch(
    "/{counselor_id}/show",
    response_model=APIResponse,
    summary="상담사 노출여부 수정 (간단 버전)",
    description="counselor_id와 is_show만으로 노출여부를 수정합니다.",
)
async def update_counselor_show(
    counselor_id: str,
    is_show: bool = Query(..., description="노출 여부"),
    counselor_service: CounselorService = Depends(_get_counselor_service),
):
    await counselor_service.update_show_status(counselor_id=counselor_id, is_show=is_show)
    return ok(data={"counselor_id": counselor_id, "is_show": is_show}, message="노출여부 수정 성공")


@router.patch(
    "/{counselor_id}",
    response_model=APIResponse[CounselorDetailResponse],
    summary="상담사 상세 수정 (이미지 업로드 포함)",
    description="multipart/form-data로 텍스트 필드와 이미지 파일을 함께 전송합니다.",
)
async def update_counselor_detail(
    counselor_id: str,
    # multipart fields
    is_show: Optional[bool] = Form(default=None),
    name: Optional[str] = Form(default=None),
    nickname: Optional[str] = Form(default=None),
    phone: Optional[str] = Form(default=None),
    password: Optional[str] = Form(default=None),
    specialties: Optional[str] = Form(default=None),
    counselor_code: Optional[str] = Form(default=None),
    grade: Optional[str] = Form(default=None),
    after_amount: Optional[int] = Form(default=None),
    before_amount: Optional[str] = Form(default=None),
    work_time: Optional[str] = Form(default=None),
    is_new: Optional[bool] = Form(default=None),
    introduction_short: Optional[str] = Form(default=None),
    greeting_message: Optional[str] = Form(default=None),
    career_info: Optional[str] = Form(default=None),
    keywords: Optional[str] = Form(default=None),
    profile_image: Optional[UploadFile] = File(default=None),
    #current_user: TokenPayload = Depends(get_current_user),
    counselor_service: CounselorService = Depends(_get_counselor_service),
):
    #verify_admin_role(current_user)
    form = CounselorDetailUpdate(
        is_show=is_show,
        name=name,
        nickname=nickname,
        phone=phone,
        password=password,
        specialties=specialties,
        counselor_code=counselor_code,
        grade=grade,
        after_amount=after_amount,
        before_amount=before_amount,
        work_time=work_time,
        is_new=is_new,
        introduction_short=introduction_short,
        greeting_message=greeting_message,
        career_info=career_info,
        keywords=keywords,
    )
    data = await counselor_service.update_counselor_detail(
        counselor_id=counselor_id,
        form=form,
        profile_image=profile_image,
    )
    return ok(data=data, message="상담사 정보 수정 성공")

@router.get("/detail", response_model=APIResponse[CounselorFullDetailResponse], summary="상담사 상세 조회")
async def get_counselor_detail(
    counselor_id: str = Query(..., description="상담사 ID"),
    counselor_service: CounselorService = Depends(_get_counselor_service),
    #current_user: TokenPayload = Depends(get_current_user),
):
    #verify_admin_role(current_user)
    counselor, member = await counselor_service.get_detail(counselor_id)

    # member를 dict로 변환 (Pydantic 스키마 사용)
    member_dict = None
    if member is not None:
        member_dict = Tm60MemberResponse.model_validate(member, from_attributes=True).model_dump()

    return ok(
        data=CounselorFullDetailResponse(
            counselor=CounselorResponse.model_validate(counselor, from_attributes=True),
            member=member_dict,
        ),
        message="상담사 상세 조회 성공",
    )

@router.post(
    "/state",
    response_model=APIResponse[CounselorStateUpdateResponse],
    summary="상담사 상태 수정",
    description=(
        "counselor_code를 MSSQL tm60_member.m_code에 매칭하여 해당 멤버의 m_state를 변경합니다.\n"
        "m_state: 1=대기중, 2=상담중, 3=부재중"
    ),
)
async def update_counselor_state(
    payload: CounselorStateUpdateRequest,
    service: CounselorStatusService = Depends(_get_counselor_status_service),
    #current_user: TokenPayload = Depends(get_current_user),
):
    #verify_admin_role(current_user)
    data = await service.update_state(payload)
    return ok(data=data, message="상담사 상태 수정 성공")
