"""
BannerRepository - t_banner 접근 레이어
"""
from typing import List, Optional

from sqlalchemy import select, func, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.banner_model import Banner


class BannerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Banner]:
        stmt = select(Banner).order_by(Banner.display_order, Banner.banner_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type(self, banner_type: str) -> List[Banner]:
        """특정 타입의 배너 목록 조회"""
        stmt = (
            select(Banner)
            .where(Banner.banner_type == banner_type)
            .order_by(Banner.display_order, Banner.banner_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        stmt = select(func.count(Banner.banner_id))
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def get_by_id(self, banner_id: int) -> Optional[Banner]:
        stmt = select(Banner).where(Banner.banner_id == banner_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, banner_code: str) -> Optional[Banner]:
        stmt = select(Banner).where(Banner.banner_code == banner_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_max_banner_code_number(self) -> int:
        """BNR_ 접두사를 제외한 최대 배너 코드 번호 조회 (삭제된 레코드 포함)"""
        stmt = select(Banner.banner_code).order_by(Banner.banner_id.desc()).limit(100)
        result = await self.db.execute(stmt)
        codes = result.scalars().all()

        max_num = 0
        for code in codes:
            if code and code.startswith("BNR_"):
                try:
                    num = int(code.replace("BNR_", ""))
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        return max_num

    async def create(self, **fields) -> Banner:
        stmt = insert(Banner).values(**fields)
        await self.db.execute(stmt)
        result = await self.db.execute(select(Banner).where(Banner.banner_code == fields["banner_code"]))
        return result.scalar_one()

    async def partial_update(self, banner_id: int, **fields) -> bool:
        if not fields:
            return False
        stmt = (
            update(Banner)
            .where(Banner.banner_id == banner_id)
            .values(**fields)
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_id(self, banner_id: int) -> bool:
        stmt = delete(Banner).where(Banner.banner_id == banner_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def get_active_banners_by_type(self, banner_type: str) -> List[Banner]:
        """특정 타입의 활성화된 배너 목록을 display_order 순으로 조회"""
        stmt = (
            select(Banner)
            .where(Banner.is_active == True, Banner.banner_type == banner_type)
            .order_by(Banner.display_order, Banner.banner_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def reorder_active_banners_by_type(self, banner_type: str) -> None:
        """특정 타입의 활성화된 배너들의 순서를 1부터 순차적으로 재정렬"""
        active_banners = await self.get_active_banners_by_type(banner_type)

        for idx, banner in enumerate(active_banners, start=1):
            if banner.display_order != idx:
                await self.partial_update(banner.banner_id, display_order=idx)


