"""
마일리지 상품 관리 API
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.mileage_product_repository import MileageProductRepository
from src.services.mileage_product_service import MileageProductService
from src.schemas.mileage_product_schema import (
    MileageProductCreateRequest,
    MileageProductUpdateRequest,
)
from src.common.response import APIResponse, APIResponseBuilder

router = APIRouter(prefix="/mileage", tags=["마일리지 상품 관리"])


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> MileageProductService:
    return MileageProductService(MileageProductRepository(db))


@router.get("/list", response_model=APIResponse)
async def list_products(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    service: MileageProductService = Depends(_get_service),
):
    """
    마일리지 상품 목록 조회 (페이징)
    - created_at desc 정렬
    """
    items, page, limit, total = await service.list_all(page, limit)
    return APIResponseBuilder.paginated(
        data=[item.model_dump() for item in items],
        page=page,
        limit=limit,
        total=total,
        message="마일리지 상품 목록 조회 성공",
    )


@router.get("/{mileage_id}", response_model=APIResponse)
async def get_product(
    mileage_id: int,
    service: Annotated[MileageProductService, Depends(_get_service)],
):
    """
    마일리지 상품 상세 조회
    """
    result = await service.get_detail(mileage_id)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="마일리지 상품 상세 조회 성공",
    )


@router.post("/create", response_model=APIResponse)
async def create_product(
    m_product_name: Annotated[str, Form()],
    m_product_value: Annotated[int, Form()],
    charge_point: Annotated[int, Form()],
    valid_from: Annotated[str, Form()],
    valid_until: Annotated[str, Form()],
    ord: Annotated[int, Form()] = 0,
    description: Annotated[str | None, Form()] = None,
    is_active: Annotated[bool, Form()] = True,
    image_file: UploadFile = File(...),
    service: MileageProductService = Depends(_get_service),
):
    """
    마일리지 상품 등록
    - 이미지는 S3 dev-upload/mileage에 업로드
    """
    from datetime import datetime

    payload = MileageProductCreateRequest(
        m_product_name=m_product_name,
        m_product_value=m_product_value,
        charge_point=charge_point,
        valid_from=datetime.fromisoformat(valid_from),
        valid_until=datetime.fromisoformat(valid_until),
        ord=ord,
        description=description,
        is_active=is_active,
    )
    result = await service.create(payload, image_file)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="마일리지 상품 등록 성공",
    )


@router.put("/{mileage_id}", response_model=APIResponse)
async def update_product(
    mileage_id: int,
    m_product_name: Annotated[str | None, Form()] = None,
    m_product_value: Annotated[int | None, Form()] = None,
    charge_point: Annotated[int | None, Form()] = None,
    valid_from: Annotated[str | None, Form()] = None,
    valid_until: Annotated[str | None, Form()] = None,
    ord: Annotated[int | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    is_active: Annotated[bool | None, Form()] = None,
    image_file: UploadFile | None = File(None),
    service: MileageProductService = Depends(_get_service),
):
    """
    마일리지 상품 수정
    - 이미지는 선택적으로 업로드
    """
    from datetime import datetime

    payload = MileageProductUpdateRequest(
        m_product_name=m_product_name,
        m_product_value=m_product_value,
        charge_point=charge_point,
        valid_from=datetime.fromisoformat(valid_from) if valid_from else None,
        valid_until=datetime.fromisoformat(valid_until) if valid_until else None,
        ord=ord,
        description=description,
        is_active=is_active,
    )
    result = await service.update(mileage_id, payload, image_file)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="마일리지 상품 수정 성공",
    )


@router.delete("/{mileage_id}", response_model=APIResponse)
async def delete_product(
    mileage_id: int,
    service: Annotated[MileageProductService, Depends(_get_service)],
):
    """
    마일리지 상품 삭제
    """
    result = await service.delete(mileage_id)
    return APIResponseBuilder.success(
        data=result.model_dump(),
        message="마일리지 상품 삭제 성공",
    )