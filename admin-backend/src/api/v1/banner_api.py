"""
배너 관리 API (관리자 백엔드)

- 목록 조회: 전체 반환
- 상세 조회: banner_id로 단건 조회
- 등록: S3 업로드(subdirectory="banner"), banner_code = BNR_총개수+1
- 수정: banner_id 기준 부분 업데이트, 이미지 재업로드 지원
- 삭제: 물리 삭제
"""
from typing import Optional

from fastapi import APIRouter, Depends, Body, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.banner_repository import BannerRepository
from src.services.banner_service import BannerService
from src.schemas.banner_schema import (
    BannerListResponse,
    BannerItem,
    BannerCreateRequest,
    BannerUpdateRequest,
    BannerDeleteResponse,
)


router = APIRouter(prefix="/banners", tags=["banners"])


def _get_service(db: AsyncSession = Depends(get_db_maria)) -> BannerService:
    return BannerService(BannerRepository(db))


@router.get("/list", response_model=APIResponse[BannerListResponse], summary="배너 목록 조회")
async def list_banners(service: BannerService = Depends(_get_service)):
    data = await service.list_all()
    return ok(data=data, message="배너 목록 조회 성공")


@router.get("/detail", response_model=APIResponse[BannerItem], summary="배너 상세 조회")
async def get_banner_detail(
    banner_id: int = Query(..., description="배너 PK"),
    service: BannerService = Depends(_get_service),
):
    data = await service.get_detail(banner_id)
    return ok(data=data, message="배너 상세 조회 성공")


@router.post("/create", response_model=APIResponse[BannerItem], summary="배너 등록", description="multipart/form-data 지원. image 파일 필드명=image")
async def create_banner(
    banner_name: str = Form(...),
    banner_type: str = Form(...),
    link_url: Optional[str] = Form(default=None),
    link_target: str = Form(default="SELF"),
    display_order: int = Form(default=0),
    is_active: bool = Form(default=True),
    valid_from: str = Form(..., description="YYYY-MM-DD HH:MM:SS[.mmm]"),
    valid_until: str = Form(..., description="YYYY-MM-DD HH:MM:SS[.mmm]"),
    image: UploadFile | None = File(default=None),
    image_url: Optional[str] = Form(default=None, description="이미 업로드된 파일명 직접 지정 시 사용"),
    service: BannerService = Depends(_get_service),
):
    # 문자열로 받은 날짜를 파싱하여 datetime으로 변환
    from datetime import datetime
    def _parse_dt(s: str) -> datetime:
        # 지원 포맷: 'YYYY-MM-DD HH:MM:SS' 또는 'YYYY-MM-DD HH:MM:SS.mmm'
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError("날짜 형식이 올바르지 않습니다. 예: 2024-10-31 15:00:00.000")

    payload = BannerCreateRequest(
        banner_name=banner_name,
        banner_type=banner_type,
        link_url=link_url,
        link_target=link_target,
        display_order=display_order,
        is_active=is_active,
        valid_from=_parse_dt(valid_from),
        valid_until=_parse_dt(valid_until),
        image_url=image_url,
    )
    data = await service.create(payload, image=image)
    return ok(data=data, message="배너 등록 성공")


@router.post("/update", response_model=APIResponse[BannerItem], summary="배너 수정", description="multipart/form-data 지원. image 파일 필드명=image")
async def update_banner(
    banner_id: int = Form(...),
    banner_name: Optional[str] = Form(default=None),
    banner_type: Optional[str] = Form(default=None),
    link_url: Optional[str] = Form(default=None),
    link_target: Optional[str] = Form(default=None),
    display_order: Optional[int] = Form(default=None),
    is_active: Optional[bool] = Form(default=None),
    valid_from: Optional[str] = Form(default=None),
    valid_until: Optional[str] = Form(default=None),
    image: UploadFile | None = File(default=None),
    image_url: Optional[str] = Form(default=None),
    service: BannerService = Depends(_get_service),
):
    from datetime import datetime
    def _parse_optional_dt(s: Optional[str]):
        if not s:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError("날짜 형식이 올바르지 않습니다. 예: 2024-10-31 15:00:00.000")

    payload = BannerUpdateRequest(
        banner_id=banner_id,
        banner_name=banner_name,
        banner_type=banner_type,
        image_url=image_url,
        link_url=link_url,
        link_target=link_target,
        display_order=display_order,
        is_active=is_active,
        valid_from=_parse_optional_dt(valid_from),
        valid_until=_parse_optional_dt(valid_until),
    )
    data = await service.update(payload, image=image)
    return ok(data=data, message="배너 수정 성공")


@router.delete("/delete", response_model=APIResponse[BannerDeleteResponse], summary="배너 삭제")
async def delete_banner(
    banner_id: int = Query(..., description="배너 PK"),
    service: BannerService = Depends(_get_service),
):
    data = await service.delete(banner_id)
    return ok(data=data, message="배너 삭제 성공")


