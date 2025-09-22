"""
포인트 상품 서비스 클래스
비즈니스 로직과 DTO 매핑
"""
from src.common.logging import get_logger_with_request_id
from src.repositories.point_product_repository import PointProductRepository
from src.schemas.point_product_schema import PointProductResponse


class PointProductService:
    """포인트 상품 비즈니스 로직 서비스"""

    def __init__(self, repo: PointProductRepository):
        self.repo = repo

    async def list_public_products(self) -> list[PointProductResponse]:
        log = get_logger_with_request_id()
        log.info("Service: list public point products")
        items = await self.repo.list_public_products()
        return [PointProductResponse.model_validate(x) for x in items]

    async def get_product(self, product_id: int) -> PointProductResponse | None:
        item = await self.repo.get_by_id(product_id)
        return PointProductResponse.model_validate(item) if item else None



