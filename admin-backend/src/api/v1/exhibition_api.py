"""
기획전(Exhibition) 관리 API (관리자 백엔드)

Frontend 호환성을 위한 exhibition 경로 제공
실제 데이터는 t_event 테이블(promotion)을 사용

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


router = APIRouter(prefix="/exhibition", tags=["exhibition"])


def _get_service(db: AsyncSession = Depends(get_db_maria)) -> PromotionService:
    return PromotionService(PromotionRepository(db))


@router.post("/exhibitions", response_model=APIResponse[PromotionListResponse], summary="기획전 목록 조회 (POST)")
async def list_exhibitions_post(service: PromotionService = Depends(_get_service)):
    """Frontend 호환성을 위한 POST 방식 목록 조회"""
    data = await service.list_all()
    return ok(data=data, message="기획전 목록 조회 성공")


@router.get("/exhibitions", response_model=APIResponse[PromotionListResponse], summary="기획전 목록 조회 (GET)")
async def list_exhibitions_get(service: PromotionService = Depends(_get_service)):
    """GET 방식 목록 조회"""
    data = await service.list_all()
    return ok(data=data, message="기획전 목록 조회 성공")


@router.get("/{event_id}", response_model=APIResponse[PromotionItem], summary="기획전 상세 조회")
async def get_exhibition_detail(
    event_id: int,
    service: PromotionService = Depends(_get_service),
):
    """Frontend 호환성을 위한 경로 파라미터 방식 상세 조회"""
    data = await service.get_detail(event_id)
    return ok(data=data, message="기획전 상세 조회 성공")


@router.post("/create-exhibition", response_model=APIResponse[PromotionItem], summary="기획전 등록", description="multipart/form-data 지원")
async def create_exhibition(
    event_name: str = Form(...),
    event_type: str = Form(...),
    description: Optional[str] = Form(default=None),
    terms: Optional[str] = Form(default=None),
    reward_type: str = Form(...),
    reward_value: int = Form(...),
    max_participants: Optional[int] = Form(default=None),
    is_active: str = Form(default="true"),  # FormData는 문자열로 전송됨
    valid_from: str = Form(...),
    valid_until: str = Form(...),
    metadata: Optional[str] = Form(default=None, description="JSON 문자열"),
    banner_image: UploadFile | None = File(default=None),
    banner_image_url: Optional[str] = Form(default=None),
    service: PromotionService = Depends(_get_service),
):
    from datetime import datetime
    import json
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Creating exhibition - event_name: {event_name}, event_type: {event_type}")
        logger.info(f"is_active received: {is_active} (type: {type(is_active)})")
        logger.info(f"metadata received: {metadata}")

        def _parse_dt(s: str):
            # ISO 8601 형식 (T 포함) 및 일반 형식 모두 지원
            for fmt in (
                "%Y-%m-%dT%H:%M:%S.%f",  # ISO with milliseconds
                "%Y-%m-%dT%H:%M:%S",     # ISO without milliseconds
                "%Y-%m-%d %H:%M:%S.%f",  # Space separated with milliseconds
                "%Y-%m-%d %H:%M:%S",     # Space separated
                "%Y-%m-%d"               # Date only
            ):
                try:
                    return datetime.strptime(s, fmt)
                except ValueError:
                    continue
            raise ValueError(f"날짜 형식이 올바르지 않습니다. 받은 값: {s}, 예: 2024-10-31 15:00:00 또는 2024-10-31T15:00:00")

        def _parse_bool(s: str) -> bool:
            """문자열을 boolean으로 변환"""
            if isinstance(s, bool):
                return s
            return s.lower() in ('true', '1', 'yes', 'y')

        metadata_obj = None
        if metadata:
            try:
                metadata_obj = json.loads(metadata)
                logger.info(f"Parsed metadata: {metadata_obj}")
            except Exception as e:
                logger.error(f"Failed to parse metadata: {e}")
                metadata_obj = None

        payload = PromotionCreateRequest(
            event_name=event_name,
            event_type=event_type,
            description=description,
            terms=terms,
            reward_type=reward_type,
            reward_value=reward_value,
            max_participants=max_participants,
            is_active=_parse_bool(is_active),
            valid_from=_parse_dt(valid_from),
            valid_until=_parse_dt(valid_until),
            metadata=metadata_obj,
            banner_image_url=banner_image_url,
        )
        logger.info(f"Created payload: {payload}")
        data = await service.create(payload, banner_image=banner_image)
        return ok(data=data, message="기획전 등록 성공")
    except Exception as e:
        logger.error(f"Error creating exhibition: {e}", exc_info=True)
        raise


@router.patch("/modify-exhibition", response_model=APIResponse[PromotionItem], summary="기획전 수정", description="multipart/form-data 지원")
async def update_exhibition(
    event_id: int = Form(...),
    event_name: Optional[str] = Form(default=None),
    event_type: Optional[str] = Form(default=None),
    description: Optional[str] = Form(default=None),
    terms: Optional[str] = Form(default=None),
    reward_type: Optional[str] = Form(default=None),
    reward_value: Optional[int] = Form(default=None),
    max_participants: Optional[int] = Form(default=None),
    is_active: Optional[str] = Form(default=None),  # FormData는 문자열로 전송됨
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
        # ISO 8601 형식 (T 포함) 및 일반 형식 모두 지원
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO with milliseconds
            "%Y-%m-%dT%H:%M:%S",     # ISO without milliseconds
            "%Y-%m-%d %H:%M:%S.%f",  # Space separated with milliseconds
            "%Y-%m-%d %H:%M:%S",     # Space separated
            "%Y-%m-%d"               # Date only
        ):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError(f"날짜 형식이 올바르지 않습니다. 받은 값: {s}, 예: 2024-10-31 15:00:00 또는 2024-10-31T15:00:00")

    def _parse_optional_bool(s: Optional[str]) -> Optional[bool]:
        """문자열을 boolean으로 변환"""
        if s is None:
            return None
        if isinstance(s, bool):
            return s
        return s.lower() in ('true', '1', 'yes', 'y')

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
        is_active=_parse_optional_bool(is_active),
        valid_from=_parse_optional_dt(valid_from),
        valid_until=_parse_optional_dt(valid_until),
        metadata=metadata_obj,
        banner_image_url=banner_image_url,
    )
    data = await service.update(payload, banner_image=banner_image)
    return ok(data=data, message="기획전 수정 성공")


@router.delete("/{event_id}", response_model=APIResponse[PromotionDeleteResponse], summary="기획전 삭제")
async def delete_exhibition(
    event_id: int,
    service: PromotionService = Depends(_get_service),
):
    """Frontend 호환성을 위한 경로 파라미터 방식 삭제"""
    data = await service.delete(event_id)
    return ok(data=data, message="기획전 삭제 성공")
