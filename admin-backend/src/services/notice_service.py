"""
NoticeService - 공지사항 비즈니스 로직
"""
from __future__ import annotations

from datetime import datetime

from src.repositories.notice_repository import NoticeRepository
from src.schemas.notice_schema import (
    NoticeListParams,
    NoticeListItem,
    NoticeDetail,
    NoticeListResponse,
    NoticeDetailResponse,
    NoticeCreateRequest,
    NoticeUpdateRequest,
    NoticeDeleteResponse,
)


class NoticeService:
    def __init__(self, repo: NoticeRepository):
        self.repo = repo

    async def get_notice_list(self, params: NoticeListParams) -> tuple[list[NoticeListItem], int, int, int]:
        # 페이지/리밋 보정
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        # 날짜 파싱 (yyyy-mm-dd)
        start_dt: datetime | None = None
        end_dt: datetime | None = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        rows, total = await self.repo.get_list(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            target_audience=params.target_audience or None,
            notice_type=params.notice_type or None,
            is_important=params.is_important,
            is_active=params.is_active,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items = [NoticeListItem.model_validate(r, from_attributes=True) for r in rows]
        return items, params.page, params.limit, total

    async def get_detail(self, notice_id: int) -> NoticeDetailResponse:
        row = await self.repo.get_by_id(notice_id)
        if row is None:
            from src.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("공지사항을 찾을 수 없습니다")
        return NoticeDetailResponse(notice=NoticeDetail.model_validate(row, from_attributes=True))

    async def create(self, payload: NoticeCreateRequest, *, created_by: int) -> NoticeDetailResponse:
        created = await self.repo.create(
            notice_type=payload.notice_type or "GENERAL",
            title=payload.title,
            content=payload.content,
            target_audience=payload.target_audience or "ALL",
            is_important=bool(payload.is_important),
            is_active=True,
            created_by=created_by,
        )
        return await self.get_detail(created.notice_id)

    async def update(self, payload: NoticeUpdateRequest) -> NoticeDetailResponse:
        # 존재 확인
        row = await self.repo.get_by_id(payload.notice_id)
        if row is None:
            from src.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("공지사항을 찾을 수 없습니다")

        updates = {
            k: v
            for k, v in payload.model_dump().items()
            if k not in ("notice_id",) and v is not None
        }
        await self.repo.partial_update(payload.notice_id, **updates)
        return await self.get_detail(payload.notice_id)

    async def delete(self, notice_id: int) -> NoticeDeleteResponse:
        deleted = await self.repo.delete_by_id(notice_id)
        return NoticeDeleteResponse(notice_id=notice_id, deleted=bool(deleted))


