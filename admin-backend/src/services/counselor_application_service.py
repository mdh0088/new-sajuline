"""
관리자 백엔드 상담사 신청 서비스: 목록 조회/상세 수정(+S3 업로드)
"""
from typing import Tuple, List, Optional
from datetime import datetime
from json import loads

from fastapi import UploadFile

from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.repositories.counselor_application_repository import CounselorApplicationRepository
from src.schemas.counselor_application_schema import (
    CounselorApplicationListParams,
    CounselorApplicationListItem,
    CounselorApplicationDetailUpdate,
    CounselorApplicationDetailResponse,
)
from src.common.storage.s3 import upload_public_image


class CounselorApplicationService:
    """상담사 신청 비즈니스 로직 (관리자)"""

    def __init__(self, application_repo: CounselorApplicationRepository):
        self.application_repo = application_repo

    async def get_detail(self, application_id: int):
        """상담사 신청 상세 조회"""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundError("상담사 신청을 찾을 수 없습니다")
        return application

    async def get_application_list(
        self, params: CounselorApplicationListParams
    ) -> tuple[List[CounselorApplicationListItem], int, int, int]:
        """상담사 신청 목록 조회 (페이징)"""
        # 페이지/리밋 정정
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
                # 당일 23:59:59 포함을 위해 하루 끝으로 보정
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            # 형식 오류는 필터 미적용
            start_dt = start_dt or None
            end_dt = end_dt or None

        items, total = await self.application_repo.get_list(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=(params.search_name or None),
            specialties=params.specialties or None,
            application_status=params.application_status or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        resp_items: List[CounselorApplicationListItem] = []
        for app in items:
            sp_list = None
            try:
                if isinstance(app.specialty_types, str) and app.specialty_types:
                    parsed = loads(app.specialty_types)
                    if isinstance(parsed, list):
                        sp_list = [x for x in parsed if x]
            except Exception:
                sp_list = None

            resp_items.append(
                CounselorApplicationListItem.model_validate({
                    "application_id": app.application_id,
                    "name": app.name,
                    "nickname": app.nickname,
                    "email": app.email,
                    "phone": app.phone,
                    "address": app.address,
                    "specialty_types": sp_list,
                    "keywords": app.keywords,
                    "introduction": app.introduction,
                    "selected_image_url": app.selected_image_url,
                    "upload_image1": app.upload_image1,
                    "upload_image2": app.upload_image2,
                    "upload_image3": app.upload_image3,
                    "application_status": app.application_status,
                    "admin_note": app.admin_note,
                    "reviewed_by": app.reviewed_by,
                    "reviewed_at": app.reviewed_at,
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                })
            )

        return resp_items, params.page, params.limit, total

    async def update_status(
        self,
        *,
        application_id: int,
        application_status: str,
        admin_note: Optional[str] = None,
        reviewed_by: Optional[int] = None,
    ) -> None:
        """상담사 신청 상태만 수정"""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundError("상담사 신청을 찾을 수 없습니다")

        updates = {
            "application_status": application_status,
            "reviewed_at": datetime.utcnow(),
        }
        if admin_note is not None:
            updates["admin_note"] = admin_note
        if reviewed_by is not None:
            updates["reviewed_by"] = reviewed_by

        await self.application_repo.partial_update(application_id, **updates)

    async def update_application_detail(
        self,
        *,
        application_id: int,
        form: CounselorApplicationDetailUpdate,
        selected_image: Optional[UploadFile] = None,
        upload_image1: Optional[UploadFile] = None,
        upload_image2: Optional[UploadFile] = None,
        upload_image3: Optional[UploadFile] = None,
    ) -> CounselorApplicationDetailResponse:
        """상담사 신청 상세 정보 수정 + 이미지 S3 업로드

        - 이미지 파일이 있으면 dev-upload/application/ 하위로 업로드 후 filename 저장
        - specialties는 문자열(JSON) 그대로 저장
        """
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundError("상담사 신청을 찾을 수 없습니다")

        updates: dict = {}

        # 단순 매핑 필드들
        simple_fields = [
            "name",
            "nickname",
            "email",
            "phone",
            "address",
            "specialties",
            "keywords",
            "introduction",
            "application_status",
            "admin_note",
            "reviewed_by",
        ]

        for f in simple_fields:
            val = getattr(form, f, None)
            if val is not None:
                key = f
                if f == "specialties":
                    key = "specialty_types"
                updates[key] = val

        # 상태 변경 시 reviewed_at 자동 설정
        if form.application_status and form.application_status != application.application_status:
            updates["reviewed_at"] = datetime.utcnow()

        # 이미지 업로드
        if selected_image is not None:
            content = await selected_image.read()
            if content:
                filename = upload_public_image(
                    subdirectory="application",
                    content=content,
                    original_name=selected_image.filename or "selected.png"
                )
                updates["selected_image_url"] = filename

        if upload_image1 is not None:
            content = await upload_image1.read()
            if content:
                filename = upload_public_image(
                    subdirectory="application",
                    content=content,
                    original_name=upload_image1.filename or "upload1.png"
                )
                updates["upload_image1"] = filename

        if upload_image2 is not None:
            content = await upload_image2.read()
            if content:
                filename = upload_public_image(
                    subdirectory="application",
                    content=content,
                    original_name=upload_image2.filename or "upload2.png"
                )
                updates["upload_image2"] = filename

        if upload_image3 is not None:
            content = await upload_image3.read()
            if content:
                filename = upload_public_image(
                    subdirectory="application",
                    content=content,
                    original_name=upload_image3.filename or "upload3.png"
                )
                updates["upload_image3"] = filename

        updated = await self.application_repo.partial_update(application_id, **updates)
        if not updated:
            # 변경사항 없으면 현재 상태 반환
            application = await self.application_repo.get_by_id(application_id)
            if not application:
                raise NotFoundError("상담사 신청을 찾을 수 없습니다")
        else:
            application = await self.application_repo.get_by_id(application_id)

        return CounselorApplicationDetailResponse.model_validate(application)
