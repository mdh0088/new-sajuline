"""
포인트 상품 Repository 클래스
게스트 공개 목록 조회 등 데이터 액세스 전담
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc

from src.models.point_product_model import PointProduct
from src.common.logging import logger, get_logger_with_request_id


class PointProductRepository:
    """포인트 상품 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def list_public_products(self) -> list[PointProduct]:
        """
        게스트 공개용 상품 목록 조회
        - is_active = True
        - display_order ASC
        """
        log = get_logger_with_request_id()
        log.info("Listing public point products")
        stmt = (
            select(PointProduct)
            .where(PointProduct.is_active.is_(True))
            .order_by(asc(PointProduct.display_order))
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        log.info("Public point products fetched", count=len(items))
        return items



