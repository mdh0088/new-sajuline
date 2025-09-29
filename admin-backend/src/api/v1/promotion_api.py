"""
프로모션(기획전) 관리 API (관리자 백엔드)

- 목록 조회 / 상세 조회 / 등록 / 수정 / 삭제
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.promotion_repository import PromotionRepository
from src.services.promotion_service import PromotionService
from src.schemas.promotion_schema import (
    PromotionListResponse,
    PromotionItem,
    PromotionDeleteResponse,
    PromotionCreateRequest,
    PromotionUpdateRequest,
)


router = APIRouter(prefix="/promotions", tags=["promotions"])


def _get_service(db: AsyncSession = Depends(get_db_maria)) -> PromotionService:
    return PromotionService(PromotionRepository(db))


@router.get("/list", response_model=APIResponse[PromotionListResponse], summary="프로모션 목록 조회")
async def list_promotions(service: PromotionService = Depends(_get_service)):
    data = await service.list_all()
    return ok(data=data, message="프로모션 목록 조회 성공")


@router.get("/detail", response_model=APIResponse[PromotionItem], summary="프로모션 상세 조회")
async def get_promotion_detail(
    event_id: int = Query(..., description="프로모션 PK"),
    service: PromotionService = Depends(_get_service),
):
    data = await service.get_detail(event_id)
    return ok(data=data, message="프로모션 상세 조회 성공")


@router.post("/create", response_model=APIResponse[PromotionItem], summary="프로모션 등록", description="multipart/form-data 지원. banner 이미지 필드명=banner_image")
async def create_promotion(
    event_name: str = Form(...),
    event_type: str = Form(...),
    description: Optional[str] = Form(default=None),
    terms: Optional[str] = Form(default=None),
    reward_type: str = Form(...),
    reward_value: int = Form(...),
    max_participants: Optional[int] = Form(default=None),
    is_active: bool = Form(default=True),
    valid_from: str = Form(...),
    valid_until: str = Form(...),
    metadata: Optional[str] = Form(default=None, description="JSON 문자열"),
    banner_image: UploadFile | None = File(default=None),
    banner_image_url: Optional[str] = Form(default=None),
    service: PromotionService = Depends(_get_service),
):
    from datetime import datetime
    import json
    def _parse_dt(s: str):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError("날짜 형식이 올바르지 않습니다. 예: 2024-10-31 15:00:00.000")

    metadata_obj = None
    if metadata:
        try:
            metadata_obj = json.loads(metadata)
        except Exception:
            metadata_obj = None

    payload = PromotionCreateRequest(
        event_name=event_name,
        event_type=event_type,
        description=description,
        terms=terms,
        reward_type=reward_type,
        reward_value=reward_value,
        max_participants=max_participants,
        is_active=is_active,
        valid_from=_parse_dt(valid_from),
        valid_until=_parse_dt(valid_until),
        metadata=metadata_obj,
        banner_image_url=banner_image_url,
    )
    data = await service.create(payload, banner_image=banner_image)
    return ok(data=data, message="프로모션 등록 성공")


@router.post("/update", response_model=APIResponse[PromotionItem], summary="프로모션 수정", description="multipart/form-data 지원. banner 이미지 필드명=banner_image")
async def update_promotion(
    event_id: int = Form(...),
    event_name: Optional[str] = Form(default=None),
    event_type: Optional[str] = Form(default=None),
    description: Optional[str] = Form(default=None),
    terms: Optional[str] = Form(default=None),
    reward_type: Optional[str] = Form(default=None),
    reward_value: Optional[int] = Form(default=None),
    max_participants: Optional[int] = Form(default=None),
    is_active: Optional[bool] = Form(default=None),
    valid_from: Optional[str] = Form(default=None),
    valid_until: Optional[str] = Form(default=None),
    metadata: Optional[str] = Form(default=None, description="JSON 문자열"),
    banner_image: UploadFile | None = File(default=None),
    banner_image_url: Optional[str] = Form(default=None),
    service: PromotionService = Depends(_get_service),
):
    from datetime import datetime
    import json
    def _parse_optional_dt(s: Optional[str]):
        if not s:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError("날짜 형식이 올바르지 않습니다. 예: 2024-10-31 15:00:00.000")

    metadata_obj = None
    if metadata:
        try:
            metadata_obj = json.loads(metadata)
        except Exception:
            metadata_obj = None

    payload = PromotionUpdateRequest(
        event_id=event_id,
        event_name=event_name,
        event_type=event_type,
        description=description,
        terms=terms,
        reward_type=reward_type,
        reward_value=reward_value,
        max_participants=max_participants,
        is_active=is_active,
        valid_from=_parse_optional_dt(valid_from),
        valid_until=_parse_optional_dt(valid_until),
        metadata=metadata_obj,
        banner_image_url=banner_image_url,
    )
    data = await service.update(payload, banner_image=banner_image)
    return ok(data=data, message="프로모션 수정 성공")


@router.delete("/delete", response_model=APIResponse[PromotionDeleteResponse], summary="프로모션 삭제")
async def delete_promotion(
    event_id: int = Query(..., description="프로모션 PK"),
    service: PromotionService = Depends(_get_service),
):
    data = await service.delete(event_id)
    return ok(data=data, message="프로모션 삭제 성공")


