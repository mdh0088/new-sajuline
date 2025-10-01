"""
PointProductService - 비즈니스 로직
"""
from __future__ import annotations

from typing import List

from src.repositories.point_product_repository import PointProductRepository
from src.schemas.point_product_schema import (
    PointProductItem,
    PointProductListResponse,
    PointProductCreateRequest,
    PointProductUpdateRequest,
    PointProductDeleteResponse,
)


class PointProductService:
    def __init__(self, repo: PointProductRepository):
        self.repo = repo

    async def list_all(self) -> PointProductListResponse:
        items = await self.repo.get_all()
        total = await self.repo.count_all()
        return PointProductListResponse(
            items=[PointProductItem.model_validate(i) for i in items],
            total=total,
        )

    async def create(self, payload: PointProductCreateRequest) -> PointProductItem:
        # product_code = "POINT_" + 전체 row count + 1
        total = await self.repo.count_all()
        product_code = f"POINT_{total + 1}"

        created = await self.repo.create(
            product_code=product_code,
            product_name=payload.product_name,
            point_amount=payload.point_amount,
            price=payload.price,
            bonus_point=int(payload.bonus_point or 0),
            discount_rate=float(payload.discount_rate or 0),
            display_order=payload.display_order or 0,
            is_active=bool(payload.is_active),
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
        )
        return PointProductItem.model_validate(created)

    async def update(self, payload: PointProductUpdateRequest) -> PointProductItem:
        updates = {
            k: v
            for k, v in payload.model_dump().items()
            if k != "product_id" and v is not None
        }
        if "bonus_point" in updates and updates["bonus_point"] is not None:
            updates["bonus_point"] = int(updates["bonus_point"])  # 정수 저장
        if "discount_rate" in updates and updates["discount_rate"] is not None:
            updates["discount_rate"] = float(updates["discount_rate"])  # 소수 저장

        await self.repo.partial_update(payload.product_id, **updates)
        refetched = await self.repo.get_by_id(payload.product_id)
        assert refetched is not None
        return PointProductItem.model_validate(refetched)

    async def disable(self, product_id: int) -> PointProductDeleteResponse:
        updated = await self.repo.partial_update(product_id, is_active=False)
        return PointProductDeleteResponse(product_id=product_id, updated=updated)



