"""
PromotionService - 프로모션(기획전) 비즈니스 로직
"""
from __future__ import annotations

from typing import Optional
from fastapi import UploadFile

from src.repositories.promotion_repository import PromotionRepository
from src.schemas.promotion_schema import (
    PromotionItem,
    PromotionListResponse,
    PromotionCreateRequest,
    PromotionUpdateRequest,
    PromotionDeleteResponse,
)
from src.common.storage.s3 import upload_public_image
from src.exceptions.custom_exceptions import NotFoundError


class PromotionService:
    def __init__(self, repo: PromotionRepository):
        self.repo = repo

    async def list_all(self) -> PromotionListResponse:
        items = await self.repo.get_all()
        total = await self.repo.count_all()
        return PromotionListResponse(items=[PromotionItem.model_validate(i) for i in items], total=total)

    async def get_detail(self, event_id: int) -> PromotionItem:
        row = await self.repo.get_by_id(event_id)
        if row is None:
            raise NotFoundError("프로모션을 찾을 수 없습니다")
        return PromotionItem.model_validate(row)

    async def create(self, payload: PromotionCreateRequest, banner_image: Optional[UploadFile] = None) -> PromotionItem:
        # event_code = "EVT_" + 전체 row count + 1
        total = await self.repo.count_all()
        event_code = f"EVT_{total + 1}"

        banner_image_url = payload.banner_image_url
        if banner_image and banner_image.filename:
            content = await banner_image.read()
            banner_image_url = upload_public_image(subdirectory="banner", content=content, original_name=banner_image.filename)

        created = await self.repo.create(
            event_code=event_code,
            event_name=payload.event_name,
            event_type=payload.event_type,
            description=payload.description,
            terms=payload.terms,
            reward_type=payload.reward_type,
            reward_value=payload.reward_value,
            max_participants=payload.max_participants,
            current_participants=0,
            is_active=payload.is_active,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
            metadata=payload.metadata,
            banner_image_url=banner_image_url,
        )
        return PromotionItem.model_validate(created)

    async def update(self, payload: PromotionUpdateRequest, banner_image: Optional[UploadFile] = None) -> PromotionItem:
        updates = {k: v for k, v in payload.model_dump().items() if k != "event_id" and v is not None}

        if banner_image and banner_image.filename:
            content = await banner_image.read()
            new_filename = upload_public_image(subdirectory="banner", content=content, original_name=banner_image.filename)
            updates["banner_image_url"] = new_filename

        # ORM 속성명 대응: metadata -> metadata_json
        if "metadata" in updates:
            updates["metadata_json"] = updates.pop("metadata")

        await self.repo.partial_update(payload.event_id, **updates)
        refetched = await self.repo.get_by_id(payload.event_id)
        if refetched is None:
            raise NotFoundError("프로모션을 찾을 수 없습니다")
        return PromotionItem.model_validate(refetched)

    async def delete(self, event_id: int) -> PromotionDeleteResponse:
        deleted = await self.repo.delete_by_id(event_id)
        return PromotionDeleteResponse(event_id=event_id, deleted=deleted)
