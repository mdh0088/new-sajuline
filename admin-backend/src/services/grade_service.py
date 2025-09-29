"""
등급 서비스 (관리자 백엔드)
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import UploadFile

from src.repositories.grade_repository import GradeRepository
from src.schemas.grade_schema import (
    GradeItem,
    GradeListResponse,
    GradeDetailResponse,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradeDeleteResponse,
    UsersByGradeResponse,
    UsersByGradeItem,
)
from src.exceptions.custom_exceptions import NotFoundError
from src.common.storage.s3 import upload_public_image
from src.repositories.user_repository import UserRepository


class GradeService:
    def __init__(self, grade_repo: GradeRepository, user_repo: UserRepository | None = None):
        self.grade_repo = grade_repo
        self.user_repo = user_repo

    async def get_all(self) -> GradeListResponse:
        rows = await self.grade_repo.get_all_desc_by_level()
        items: List[GradeItem] = [GradeItem.model_validate(r, from_attributes=True) for r in rows]
        return GradeListResponse(grades=items, total=len(items))

    async def get_detail(self, grade_code: str) -> GradeDetailResponse:
        row = await self.grade_repo.get_by_code(grade_code)
        if row is None:
            raise NotFoundError("등급을 찾을 수 없습니다")
        return GradeDetailResponse(grade=GradeItem.model_validate(row, from_attributes=True))

    async def create_with_image(
        self,
        *,
        payload: GradeCreateRequest,
        image: Optional[UploadFile] = None,
    ) -> GradeDetailResponse:
        filename: Optional[str] = None
        if image is not None:
            content = await image.read()
            if content:
                filename = upload_public_image(subdirectory="grade", content=content, original_name=image.filename or "image.png")
        fields = payload.model_dump(exclude_none=True)
        if filename:
            fields["grade_image_url"] = filename
        row = await self.grade_repo.create(**fields)
        return GradeDetailResponse(grade=GradeItem.model_validate(row, from_attributes=True))

    async def update_with_image(
        self,
        *,
        payload: GradeUpdateRequest,
        image: Optional[UploadFile] = None,
    ) -> GradeDetailResponse:
        current = await self.grade_repo.get_by_code(payload.grade_code)
        if current is None:
            raise NotFoundError("등급을 찾을 수 없습니다")

        updates = payload.model_dump(exclude_none=True)
        updates.pop("grade_code", None)

        if image is not None:
            content = await image.read()
            if content:
                filename = upload_public_image(subdirectory="grade", content=content, original_name=image.filename or "image.png")
                updates["grade_image_url"] = filename

        updated = await self.grade_repo.partial_update(current.grade_code, **updates)
        if not updated:
            # 변경사항 없거나 실패 시 최신값 반환
            refreshed = await self.grade_repo.get_by_code(current.grade_code)
            if refreshed is None:
                raise NotFoundError("등급을 찾을 수 없습니다")
            return GradeDetailResponse(grade=GradeItem.model_validate(refreshed, from_attributes=True))

        refreshed = await self.grade_repo.get_by_code(current.grade_code)
        return GradeDetailResponse(grade=GradeItem.model_validate(refreshed, from_attributes=True))

    async def delete(self, grade_code: str) -> GradeDeleteResponse:
        # 존재 확인 후 삭제
        current = await self.grade_repo.get_by_code(grade_code)
        if current is None:
            # 없는 경우에도 일관 응답 (deleted=False)
            return GradeDeleteResponse(grade_code=grade_code, deleted=False)
        deleted = await self.grade_repo.delete(grade_code)
        return GradeDeleteResponse(grade_code=grade_code, deleted=bool(deleted))

    async def get_users_by_grade(self, grade_code: str) -> UsersByGradeResponse:
        if self.user_repo is None:
            # 방어: 의존성 누락 시 빈 응답
            return UsersByGradeResponse(users=[], total=0)
        rows = await self.user_repo.get_all_by_grade(grade_code)
        items = [UsersByGradeItem.model_validate(r, from_attributes=True) for r in rows]
        return UsersByGradeResponse(users=items, total=len(items))


