"""
마일리지 상품 Repository
"""
from __future__ import annotations

from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.mileage_product_model import MileageProduct


class MileageProductRepository:
    """마일리지 상품 Repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_paginated(self, page: int, limit: int) -> tuple[list[MileageProduct], int]:
        """
        마일리지 상품 페이징 조회 (created_at desc 정렬)
        """
        # 전체 개수
        count_stmt = select(func.count(MileageProduct.mileage_id))
        count_result = await self.session.execute(count_stmt)
        total = int(count_result.scalar() or 0)

        # 페이징 데이터
        offset = (page - 1) * limit
        stmt = (
            select(MileageProduct)
            .order_by(desc(MileageProduct.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, mileage_id: int) -> MileageProduct | None:
        """
        마일리지 상품 단건 조회
        """
        stmt = select(MileageProduct).where(MileageProduct.mileage_id == mileage_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, product: MileageProduct) -> MileageProduct:
        """
        마일리지 상품 생성
        """
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update(self, product: MileageProduct) -> MileageProduct:
        """
        마일리지 상품 수정
        """
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def delete(self, product: MileageProduct) -> None:
        """
        마일리지 상품 삭제
        """
        await self.session.delete(product)
        await self.session.flush()