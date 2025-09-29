"""
BannerService - 배너 비즈니스 로직
"""
from __future__ import annotations

from typing import Optional
from fastapi import UploadFile

from src.repositories.banner_repository import BannerRepository
from src.schemas.banner_schema import (
    BannerItem,
    BannerListResponse,
    BannerCreateRequest,
    BannerUpdateRequest,
    BannerDeleteResponse,
)
from src.common.storage.s3 import upload_public_image
from src.exceptions.custom_exceptions import NotFoundError


class BannerService:
    def __init__(self, repo: BannerRepository):
        self.repo = repo

    async def list_all(self) -> BannerListResponse:
        items = await self.repo.get_all()
        total = await self.repo.count_all()
        return BannerListResponse(items=[BannerItem.model_validate(i) for i in items], total=total)

    async def get_detail(self, banner_id: int) -> BannerItem:
        row = await self.repo.get_by_id(banner_id)
        if row is None:
            raise NotFoundError("배너를 찾을 수 없습니다")
        return BannerItem.model_validate(row)

    async def create(self, payload: BannerCreateRequest, image: Optional[UploadFile] = None) -> BannerItem:
        # banner_code = "BNR_" + 전체 row count
        total = await self.repo.count_all()
        banner_code = f"BNR_{total + 1}"

        # 이미지 업로드 처리: s3_directory 하위 dev-upload/banner 에 저장 (subdirectory="banner")
        image_filename = payload.image_url
        if image and image.filename:
            content = await image.read()
            image_filename = upload_public_image(subdirectory="banner", content=content, original_name=image.filename)

        created = await self.repo.create(
            banner_code=banner_code,
            banner_name=payload.banner_name,
            banner_type=payload.banner_type,
            image_url=image_filename or "",
            link_url=payload.link_url,
            link_target=payload.link_target,
            display_order=payload.display_order,
            is_active=payload.is_active,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
        )
        return BannerItem.model_validate(created)

    async def update(self, payload: BannerUpdateRequest, image: Optional[UploadFile] = None) -> BannerItem:
        updates = {k: v for k, v in payload.model_dump().items() if k != "banner_id" and v is not None}

        # 이미지가 새로 업로드된 경우 우선 처리
        if image and image.filename:
            content = await image.read()
            new_filename = upload_public_image(subdirectory="banner", content=content, original_name=image.filename)
            updates["image_url"] = new_filename

        await self.repo.partial_update(payload.banner_id, **updates)
        refetched = await self.repo.get_by_id(payload.banner_id)
        if refetched is None:
            raise NotFoundError("배너를 찾을 수 없습니다")
        return BannerItem.model_validate(refetched)

    async def delete(self, banner_id: int) -> BannerDeleteResponse:
        deleted = await self.repo.delete_by_id(banner_id)
        return BannerDeleteResponse(banner_id=banner_id, deleted=deleted)


