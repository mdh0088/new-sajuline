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

    async def list_by_type(self, banner_type: str) -> BannerListResponse:
        """특정 타입의 배너 목록 조회"""
        items = await self.repo.get_by_type(banner_type)
        return BannerListResponse(items=[BannerItem.model_validate(i) for i in items], total=len(items))

    async def get_detail(self, banner_id: int) -> BannerItem:
        row = await self.repo.get_by_id(banner_id)
        if row is None:
            raise NotFoundError("배너를 찾을 수 없습니다")
        return BannerItem.model_validate(row)

    async def create(self, payload: BannerCreateRequest, image: Optional[UploadFile] = None) -> BannerItem:
        # banner_code = "BNR_" + 최대 배너 코드 번호 + 1 (삭제된 레코드도 고려)
        max_code_num = await self.repo.get_max_banner_code_number()
        banner_code = f"BNR_{max_code_num + 1}"

        # 이미지 업로드 처리: s3_directory 하위 dev-upload/banner 에 저장 (subdirectory="banner")
        image_filename = payload.image_url
        if image and image.filename:
            content = await image.read()
            image_filename = upload_public_image(subdirectory="banner", content=content, original_name=image.filename)

        # 활성 배너인 경우 마지막 순서로 배치 (같은 타입 내에서만)
        if payload.is_active:
            # 같은 타입의 활성 배너 개수 조회하여 마지막 순서로 배치
            active_banners = await self.repo.get_active_banners_by_type(payload.banner_type)
            display_order = len(active_banners) + 1
        else:
            # 비활성 배너는 순서 없음 (NULL)
            display_order = None

        created = await self.repo.create(
            banner_code=banner_code,
            banner_name=payload.banner_name,
            banner_type=payload.banner_type,
            image_url=image_filename or "",
            link_url=payload.link_url,
            link_target=payload.link_target,
            display_order=display_order,
            is_active=payload.is_active,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
        )

        # 마지막 순서로 추가되었으므로 재정렬 불필요
        return BannerItem.model_validate(created)

    async def update(self, payload: BannerUpdateRequest, image: Optional[UploadFile] = None) -> BannerItem:
        # 기존 배너 정보 조회
        current_banner = await self.repo.get_by_id(payload.banner_id)
        if current_banner is None:
            raise NotFoundError("배너를 찾을 수 없습니다")

        updates = {k: v for k, v in payload.model_dump().items() if k != "banner_id" and v is not None}

        # 이미지가 새로 업로드된 경우 우선 처리
        if image and image.filename:
            content = await image.read()
            new_filename = upload_public_image(subdirectory="banner", content=content, original_name=image.filename)
            updates["image_url"] = new_filename

        # 순서 변경 로직 (같은 타입 내에서만)
        old_is_active = current_banner.is_active
        old_display_order = current_banner.display_order
        old_banner_type = current_banner.banner_type
        new_is_active = updates.get("is_active", old_is_active)
        new_display_order = updates.get("display_order", old_display_order)
        new_banner_type = updates.get("banner_type", old_banner_type)

        # Case 1: 비활성 -> 활성 전환
        if not old_is_active and new_is_active:
            # 같은 타입의 활성 배너 개수 조회하여 마지막 순서로 배치
            active_banners = await self.repo.get_active_banners_by_type(new_banner_type)
            target_order = len(active_banners) + 1
            updates["display_order"] = target_order

        # Case 2: 활성 -> 비활성 전환
        elif old_is_active and not new_is_active:
            updates["display_order"] = None

        # Case 3: 활성 상태에서 순서만 변경 (같은 타입 내에서) - SWAP 방식
        elif old_is_active and new_is_active and old_display_order != new_display_order and old_banner_type == new_banner_type:
            target_order = new_display_order
            active_banners = await self.repo.get_active_banners_by_type(old_banner_type)

            # target_order 위치에 있는 배너 찾기
            target_banner = None
            for banner in active_banners:
                if banner.display_order == target_order and banner.banner_id != payload.banner_id:
                    target_banner = banner
                    break

            if target_banner:
                # SWAP: 현재 배너와 타겟 배너의 순서를 직접 교체
                # 1. 타겟 배너를 현재 배너의 순서로 이동
                await self.repo.partial_update(target_banner.banner_id, display_order=old_display_order)
                # 2. 현재 배너를 타겟 순서로 이동
                updates["display_order"] = target_order
            else:
                # 해당 순서에 배너가 없는 경우 (있을 수 없지만 안전장치)
                updates["display_order"] = target_order

        # Case 4: 타입 변경 (활성 배너)
        elif old_is_active and new_is_active and old_banner_type != new_banner_type:
            # 기존 타입에서는 제거, 새 타입에서는 추가
            target_order = new_display_order if new_display_order else 1
            new_type_banners = await self.repo.get_active_banners_by_type(new_banner_type)
            for banner in new_type_banners:
                if banner.display_order >= target_order:
                    await self.repo.partial_update(banner.banner_id, display_order=banner.display_order + 1)
            updates["display_order"] = target_order

        await self.repo.partial_update(payload.banner_id, **updates)

        # 순서 재정렬 (필요한 경우에만)
        # Case 1 (비활성->활성), Case 2 (활성->비활성), Case 4 (타입 변경)만 재정렬 필요
        # Case 3 (순서만 변경)은 이미 정확하게 배치했으므로 재정렬 불필요

        if not old_is_active and new_is_active:
            # Case 1: 비활성 -> 활성 (마지막 순서로 추가됨, 재정렬 불필요)
            pass
        elif old_is_active and not new_is_active:
            # Case 2: 활성 -> 비활성 (나머지 배너들 재정렬 필요)
            await self.repo.reorder_active_banners_by_type(old_banner_type)
        elif old_is_active and new_is_active and old_banner_type != new_banner_type:
            # Case 4: 타입 변경 (기존 타입과 새 타입 모두 재정렬)
            await self.repo.reorder_active_banners_by_type(old_banner_type)
            await self.repo.reorder_active_banners_by_type(new_banner_type)

        refetched = await self.repo.get_by_id(payload.banner_id)
        if refetched is None:
            raise NotFoundError("배너를 찾을 수 없습니다")
        return BannerItem.model_validate(refetched)

    async def delete(self, banner_id: int) -> BannerDeleteResponse:
        # 삭제 전 배너 정보 조회
        banner = await self.repo.get_by_id(banner_id)
        if banner and banner.is_active:
            banner_type = banner.banner_type
            # 활성 배너 삭제 시 같은 타입 내에서 순서 재정렬 필요
            deleted = await self.repo.delete_by_id(banner_id)
            if deleted:
                await self.repo.reorder_active_banners_by_type(banner_type)
            return BannerDeleteResponse(banner_id=banner_id, deleted=deleted)
        else:
            # 비활성 배너는 그냥 삭제
            deleted = await self.repo.delete_by_id(banner_id)
            return BannerDeleteResponse(banner_id=banner_id, deleted=deleted)


