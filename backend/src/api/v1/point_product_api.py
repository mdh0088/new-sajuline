"""
포인트 상품 공개 API (게스트 접근 가능)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria
from src.repositories.point_product_repository import PointProductRepository
from src.services.point_product_service import PointProductService
from src.schemas.point_product_schema import PointProductResponse
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id


router = APIRouter(prefix="/point-products", tags=["point-products"])


def get_repo(db: AsyncSession = Depends(get_db_maria)) -> PointProductRepository:
    return PointProductRepository(db)


def get_service(repo: PointProductRepository = Depends(get_repo)) -> PointProductService:
    return PointProductService(repo)


@router.get("/public", response_model=APIResponse[list[PointProductResponse]], summary="포인트 상품 목록(공개)")
async def list_public_point_products(
    service: PointProductService = Depends(get_service)
) -> APIResponse[list[PointProductResponse]]:
    """
    공개 포인트 상품 목록 조회
    - 권한 체크 없음(게스트 가능)
    - is_active=True만 노출
    - display_order ASC 정렬
    """
    log = get_logger_with_request_id()
    log.info("API: list public point products")
    items = await service.list_public_products()
    return ok(data=items, message="상품 목록 조회 성공")



