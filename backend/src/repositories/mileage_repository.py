"""
마일리지 상품 Repository 클래스
데이터 액세스 전담
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.models.mileage_product_model import MileageProduct
from src.common.logging import logger, get_logger_with_request_id


class MileageProductRepository:
    """마일리지 상품 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def list_active_products(self) -> list[MileageProduct]:
        """
        활성 마일리지 상품 목록 조회
        - is_active = True
        - created_at DESC 정렬
        """
        log = get_logger_with_request_id()
        log.info("Listing active mileage products")
        stmt = (
            select(MileageProduct)
            .where(MileageProduct.is_active.is_(True))
            .order_by(desc(MileageProduct.created_at))
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        log.info("Active mileage products fetched", count=len(items))
        return items

    @logger.catch(reraise=True)
    async def get_by_id(self, mileage_id: int) -> MileageProduct | None:
        """마일리지 상품 ID로 조회"""
        log = get_logger_with_request_id()
        log.info("Get mileage product by id", mileage_id=mileage_id)
        stmt = select(MileageProduct).where(MileageProduct.mileage_id == mileage_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
