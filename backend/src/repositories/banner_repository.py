"""
배너 Repository 클래스
게스트 공개 조회 및 클릭 카운트 증가 기능 제공
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, asc, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import logger, get_logger_with_request_id
from src.models.banner_model import Banner, BannerType


class BannerRepository:
    """배너 데이터 액세스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @logger.catch(reraise=True)
    async def list_public_main_banners(self) -> list[Banner]:
        """
        메인 배너 공개 목록 조회
        - banner_type = 'MAIN'
        - is_active = True
        - valid_from <= now <= valid_until
        - display_order ASC
        """
        log = get_logger_with_request_id()
        log.info("Listing public MAIN banners")

        now = datetime.utcnow()
        stmt = (
            select(Banner)
            .where(
                and_(
                    Banner.banner_type == BannerType.MAIN.value,
                    Banner.is_active.is_(True),
                    Banner.valid_from <= now,
                    Banner.valid_until >= now,
                )
            )
            .order_by(asc(Banner.display_order))
        )

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        log.info("Public MAIN banners fetched", count=len(items))
        return items

    @logger.catch(reraise=True)
    async def increment_click_count(self, banner_id: int) -> bool:
        """특정 배너의 클릭 카운트를 1 증가"""
        log = get_logger_with_request_id()
        log.info("Incrementing banner click count", banner_id=banner_id)

        stmt = (
            update(Banner)
            .where(Banner.banner_id == banner_id)
            .values(click_count=Banner.click_count + 1)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        log.info("Banner click count incremented", banner_id=banner_id, success=success)
        return success


