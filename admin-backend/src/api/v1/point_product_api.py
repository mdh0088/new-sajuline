"""
포인트 상품 관리 API (관리자 백엔드)

- 목록 조회: 전체 반환
- 상품 추가: product_code = POINT_총개수+1 규칙으로 생성
- 상품 수정: 필드 부분 업데이트
- 상품 삭제: 실제 삭제 대신 is_active=False로 비활성화
"""
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.point_product_repository import PointProductRepository
from src.services.point_product_service import PointProductService
from src.schemas.point_product_schema import (
    PointProductListResponse,
    PointProductCreateRequest,
    PointProductUpdateRequest,
    PointProductDeleteRequest,
    PointProductDeleteResponse,
    PointProductItem,
)


router = APIRouter(prefix="/point-products", tags=["point-products"])


def _get_service(db: AsyncSession = Depends(get_db_maria)) -> PointProductService:
    return PointProductService(PointProductRepository(db))


@router.get("/list", response_model=APIResponse[PointProductListResponse], summary="포인트 상품 목록 조회")
async def list_products(service: PointProductService = Depends(_get_service)):
    data = await service.list_all()
    return ok(data=data, message="상품 목록 조회 성공")


@router.post("/create", response_model=APIResponse[PointProductItem], summary="포인트 상품 추가")
async def create_product(
    payload: PointProductCreateRequest = Body(...),
    service: PointProductService = Depends(_get_service),
):
    data = await service.create(payload)
    return ok(data=data, message="상품 등록 성공")


@router.post("/update", response_model=APIResponse[PointProductItem], summary="포인트 상품 수정")
async def update_product(
    payload: PointProductUpdateRequest = Body(...),
    service: PointProductService = Depends(_get_service),
):
    data = await service.update(payload)
    return ok(data=data, message="상품 수정 성공")


@router.post("/delete", response_model=APIResponse[PointProductDeleteResponse], summary="포인트 상품 비활성화")
async def delete_product(
    payload: PointProductDeleteRequest = Body(...),
    service: PointProductService = Depends(_get_service),
):
    data = await service.disable(payload.product_id)
    return ok(data=data, message="상품 비활성화 성공")


@router.delete("/delete", response_model=APIResponse[PointProductDeleteResponse], summary="포인트 상품 비활성화(DELETE)")
async def delete_product_query(
    product_id: int = Query(..., description="상품 PK"),
    service: PointProductService = Depends(_get_service),
):
    data = await service.disable(product_id)
    return ok(data=data, message="상품 비활성화 성공")


