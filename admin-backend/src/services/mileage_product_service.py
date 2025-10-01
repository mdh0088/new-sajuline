"""
MileageProductService - 비즈니스 로직
"""
from __future__ import annotations

from fastapi import UploadFile

from src.repositories.mileage_product_repository import MileageProductRepository
from src.schemas.mileage_product_schema import (
    MileageProductItem,
    MileageProductListResponse,
    MileageProductCreateRequest,
    MileageProductUpdateRequest,
    MileageProductDeleteResponse,
)
from src.models.mileage_product_model import MileageProduct
from src.common.storage.s3 import upload_public_image
from src.exceptions.custom_exceptions import NotFoundError, ValidationError


class MileageProductService:
    def __init__(self, repo: MileageProductRepository):
        self.repo = repo

    async def list_all(self, page: int, limit: int) -> tuple[list[MileageProductItem], int, int, int]:
        """마일리지 상품 페이징 조회"""
        items, total = await self.repo.get_all_paginated(page, limit)
        return (
            [MileageProductItem.model_validate(i) for i in items],
            page,
            limit,
            total,
        )

    async def get_detail(self, mileage_id: int) -> MileageProductItem:
        """마일리지 상품 상세 조회"""
        product = await self.repo.get_by_id(mileage_id)
        if not product:
            raise NotFoundError(f"마일리지 상품 {mileage_id}를 찾을 수 없습니다.")
        return MileageProductItem.model_validate(product)

    async def create(
        self, payload: MileageProductCreateRequest, image_file: UploadFile
    ) -> MileageProductItem:
        """마일리지 상품 등록"""
        if not image_file.filename:
            raise ValidationError("이미지 파일이 필요합니다.")

        # S3에 이미지 업로드
        content = await image_file.read()
        m_product_img = upload_public_image(
            subdirectory="mileage", content=content, original_name=image_file.filename
        )

        # 상품 생성
        product = MileageProduct(
            m_product_name=payload.m_product_name,
            m_product_value=payload.m_product_value,
            charge_point=payload.charge_point,
            m_product_img=m_product_img,
            image_url=image_file.filename,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
            ord=payload.ord,
            description=payload.description,
            is_active=payload.is_active,
        )

        created = await self.repo.create(product)
        return MileageProductItem.model_validate(created)

    async def update(
        self,
        mileage_id: int,
        payload: MileageProductUpdateRequest,
        image_file: UploadFile | None = None,
    ) -> MileageProductItem:
        """마일리지 상품 수정"""
        product = await self.repo.get_by_id(mileage_id)
        if not product:
            raise NotFoundError(f"마일리지 상품 {mileage_id}를 찾을 수 없습니다.")

        # 이미지 업로드가 있는 경우
        if image_file:
            if not image_file.filename:
                raise ValidationError("이미지 파일명이 유효하지 않습니다.")

            content = await image_file.read()
            m_product_img = upload_public_image(
                subdirectory="mileage", content=content, original_name=image_file.filename
            )
            product.m_product_img = m_product_img
            product.image_url = image_file.filename

        # 나머지 필드 업데이트
        if payload.m_product_name is not None:
            product.m_product_name = payload.m_product_name
        if payload.m_product_value is not None:
            product.m_product_value = payload.m_product_value
        if payload.charge_point is not None:
            product.charge_point = payload.charge_point
        if payload.valid_from is not None:
            product.valid_from = payload.valid_from
        if payload.valid_until is not None:
            product.valid_until = payload.valid_until
        if payload.ord is not None:
            product.ord = payload.ord
        if payload.description is not None:
            product.description = payload.description
        if payload.is_active is not None:
            product.is_active = payload.is_active

        updated = await self.repo.update(product)
        return MileageProductItem.model_validate(updated)

    async def delete(self, mileage_id: int) -> MileageProductDeleteResponse:
        """마일리지 상품 삭제"""
        product = await self.repo.get_by_id(mileage_id)
        if not product:
            raise NotFoundError(f"마일리지 상품 {mileage_id}를 찾을 수 없습니다.")

        await self.repo.delete(product)
        return MileageProductDeleteResponse(message="삭제되었습니다.", deleted_id=mileage_id)