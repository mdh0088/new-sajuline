"""
상담사 문의 서비스 (관리자 백엔드)
"""
from __future__ import annotations

from typing import List
from datetime import datetime

from src.repositories.inquiry_repository import InquiryRepository
from src.schemas.inquiry_schema import (
    InquiryListParams,
    InquiryListResponse,
    InquiryWithCounselorItem,
    InquiryDetailResponse,
    InquiryReplyUpdateRequest,
    InquiryUpdateRequest,
    InquiryDeleteResponse,
    UserInquiryListParams,
    UserInquiryListResponse,
    InquiryWithUserItem,
    InquiryUserDetailResponse,
    UserToCsListParams,
    UserToCsListResponse,
    InquiryWithUserAndCounselorItem,
    UserToCsDetailResponse,
)


class InquiryService:
    def __init__(self, repo: InquiryRepository):
        self.repo = repo

    async def list_counselor_inquiries(self, params: InquiryListParams) -> InquiryListResponse:
        # 페이지/리밋 보정
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        # 날짜 파싱 (yyyy-mm-dd)
        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        rows, total = await self.repo.get_list_with_counselor(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            counselor_id=params.counselor_id or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items: List[InquiryWithCounselorItem] = []
        for inquiry, counselor in rows:
            inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
            counselor_dict = {c.name: getattr(counselor, c.name) for c in counselor.__table__.columns}
            items.append(InquiryWithCounselorItem(inquiry=inquiry_dict, counselor=counselor_dict))

        return InquiryListResponse(items=items, page=params.page, limit=params.limit, total=total)

    async def get_counselor_inquiry_detail(self, inquiry_id: int) -> InquiryDetailResponse:
        row = await self.repo.get_detail_with_counselor(inquiry_id)
        if not row:
            from src.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("상담사 문의를 찾을 수 없습니다")
        inquiry, counselor = row
        inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
        counselor_dict = {c.name: getattr(counselor, c.name) for c in counselor.__table__.columns}
        return InquiryDetailResponse(inquiry=inquiry_dict, counselor=counselor_dict)

    async def update_counselor_inquiry_reply(self, payload: InquiryReplyUpdateRequest, *, admin_id: str | None = None) -> InquiryDetailResponse:
        # 답변 내용 업데이트 (+ answered_at 설정)
        await self.repo.update_reply(payload.inquiry_id, payload.reply_content, answered_at=datetime.utcnow())
        return await self.get_counselor_inquiry_detail(payload.inquiry_id)

    async def update_counselor_inquiry(self, payload: InquiryUpdateRequest, *, admin_id: str | None = None) -> InquiryDetailResponse:
        # 문의 제목/내용/답변 수정
        values = {}
        if payload.title is not None:
            values['title'] = payload.title
        if payload.content is not None:
            values['content'] = payload.content
        if payload.reply_content is not None:
            values['reply_content'] = payload.reply_content
            values['answered_at'] = datetime.utcnow()
            # replied_by는 DB에 컬럼이 없으므로 제거

        if values:
            await self.repo.update_inquiry(payload.inquiry_id, **values)
        return await self.get_counselor_inquiry_detail(payload.inquiry_id)

    async def delete_counselor_inquiry(self, inquiry_id: int) -> InquiryDeleteResponse:
        deleted = await self.repo.delete_by_id(inquiry_id)
        return InquiryDeleteResponse(inquiry_id=inquiry_id, deleted=bool(deleted))

    # =============================
    # 사용자 1:1 문의 (USER_TO_ADMIN)
    # =============================
    async def list_user_inquiries(self, params: UserInquiryListParams) -> UserInquiryListResponse:
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        rows, total = await self.repo.get_user_list_with_user(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            user_id=params.user_id or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items: list[InquiryWithUserItem] = []
        for inquiry, user in rows:
            inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            items.append(InquiryWithUserItem(inquiry=inquiry_dict, user=user_dict))

        return UserInquiryListResponse(items=items, page=params.page, limit=params.limit, total=total)

    async def get_user_inquiry_detail(self, inquiry_id: int) -> InquiryUserDetailResponse:
        row = await self.repo.get_user_detail_with_user(inquiry_id)
        if not row:
            from src.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("고객센터 문의를 찾을 수 없습니다")
        inquiry, user = row
        inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return InquiryUserDetailResponse(inquiry=inquiry_dict, user=user_dict)

    async def update_user_inquiry_reply(self, payload: InquiryReplyUpdateRequest, *, admin_id: str | None = None) -> InquiryUserDetailResponse:
        await self.repo.update_reply(payload.inquiry_id, payload.reply_content, answered_at=datetime.utcnow())
        return await self.get_user_inquiry_detail(payload.inquiry_id)

    async def update_user_inquiry(self, payload: InquiryUpdateRequest, *, admin_id: str | None = None) -> InquiryUserDetailResponse:
        values = {}
        if payload.title is not None:
            values['title'] = payload.title
        if payload.content is not None:
            values['content'] = payload.content
        if payload.reply_content is not None:
            values['reply_content'] = payload.reply_content
            values['answered_at'] = datetime.utcnow()
            # replied_by는 DB에 컬럼이 없으므로 제거

        if values:
            await self.repo.update_inquiry(payload.inquiry_id, **values)
        return await self.get_user_inquiry_detail(payload.inquiry_id)

    async def delete_user_inquiry(self, inquiry_id: int) -> InquiryDeleteResponse:
        deleted = await self.repo.delete_by_id(inquiry_id)
        return InquiryDeleteResponse(inquiry_id=inquiry_id, deleted=bool(deleted))

    # =============================
    # 1:1 상담사 문의 (USER_TO_CS)
    # =============================
    async def list_user_to_cs_inquiries(self, params: UserToCsListParams) -> UserToCsListResponse:
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        rows, total = await self.repo.get_user_to_cs_list(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            user_id=params.user_id or None,
            counselor_id=params.counselor_id or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items: list[InquiryWithUserAndCounselorItem] = []
        for inquiry, user, counselor in rows:
            inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            counselor_dict = {c.name: getattr(counselor, c.name) for c in counselor.__table__.columns}
            items.append(InquiryWithUserAndCounselorItem(inquiry=inquiry_dict, user=user_dict, counselor=counselor_dict))

        return UserToCsListResponse(items=items, page=params.page, limit=params.limit, total=total)

    async def get_user_to_cs_detail(self, inquiry_id: int) -> UserToCsDetailResponse:
        row = await self.repo.get_user_to_cs_detail(inquiry_id)
        if not row:
            from src.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("1:1 상담사 문의를 찾을 수 없습니다")
        inquiry, user, counselor = row
        inquiry_dict = {c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns}
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        counselor_dict = {c.name: getattr(counselor, c.name) for c in counselor.__table__.columns}
        return UserToCsDetailResponse(inquiry=inquiry_dict, user=user_dict, counselor=counselor_dict)

    async def update_user_to_cs_reply(self, payload: InquiryReplyUpdateRequest, *, admin_id: str | None = None) -> UserToCsDetailResponse:
        await self.repo.update_reply(payload.inquiry_id, payload.reply_content, answered_at=datetime.utcnow())
        return await self.get_user_to_cs_detail(payload.inquiry_id)

    async def update_user_to_cs_inquiry(self, payload: InquiryUpdateRequest, *, admin_id: str | None = None) -> UserToCsDetailResponse:
        values = {}
        if payload.title is not None:
            values['title'] = payload.title
        if payload.content is not None:
            values['content'] = payload.content
        if payload.reply_content is not None:
            values['reply_content'] = payload.reply_content
            values['answered_at'] = datetime.utcnow()
            # replied_by는 DB에 컬럼이 없으므로 제거

        if values:
            await self.repo.update_inquiry(payload.inquiry_id, **values)
        return await self.get_user_to_cs_detail(payload.inquiry_id)

    async def delete_user_to_cs(self, inquiry_id: int) -> InquiryDeleteResponse:
        deleted = await self.repo.delete_by_id(inquiry_id)
        return InquiryDeleteResponse(inquiry_id=inquiry_id, deleted=bool(deleted))


