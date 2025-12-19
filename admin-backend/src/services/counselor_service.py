"""
관리자 백엔드 상담사 서비스: 목록 조회/인증/상세 수정(+S3 업로드)
"""
from typing import Tuple, List, Optional
from datetime import datetime
from json import loads

from fastapi import UploadFile

from src.exceptions.custom_exceptions import AuthenticationError, NotFoundError, ValidationError
from src.repositories.counselor_repository import CounselorRepository
from src.services.auth_service import AuthService
from src.schemas.counselor_schema import (
    CounselorListParams,
    CounselorListItem,
    CounselorDetailUpdate,
    CounselorDetailResponse,
)
from src.core.database import get_db_mssql
from sqlalchemy.orm import Session
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.services.ars.tm60_member_service import Tm60MemberService
from src.common.storage.s3 import upload_public_image


class CounselorService:
    """상담사 비즈니스 로직 (관리자)"""

    def __init__(self, counselor_repo: CounselorRepository, auth_service: AuthService, tm60_member_service: Tm60MemberService | None = None):
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
        self.tm60_member_service = tm60_member_service

    async def login(self, counselor_id: str, password: str) -> Tuple[str, dict]:
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor or not counselor.password_hash:
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        if counselor.is_out:
            raise AuthenticationError("탈퇴한 상담사 계정입니다")

        if counselor.approved_at is None:
            raise AuthenticationError("승인되지 않은 상담사 계정입니다")

        if not self.auth_service.verify_password(password, counselor.password_hash):
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        access_token = self.auth_service.create_access_token(user_id=counselor.counselor_id, email=counselor.counselor_id, role="counselor")

        await self.counselor_repo.update_last_login(counselor.counselor_id)

        summary = {
            "user_id": counselor.counselor_id,
            "email": counselor.counselor_id,
            "nickname": counselor.nickname,
        }

        return access_token, summary

    async def get_detail(self, counselor_id: str):
        """상담사 상세 + TM60 멤버 단건 조회"""
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        member = None
        if self.tm60_member_service is not None and getattr(counselor, "counselor_code", None):
            member = await self.tm60_member_service.get_member_by_code(counselor.counselor_code)

        return counselor, member

    async def get_counselor_list(self, params: CounselorListParams) -> tuple[List[CounselorListItem], int, int, int]:
        """상담사 목록 조회 (페이징) - tm60_member.m_state 포함"""
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

        items, total = await self.counselor_repo.get_list(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=(params.search_name or None),
            specialties=params.specialties or None,
            is_show=params.is_show,
            is_out=params.is_out,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        # tm60_member.m_state 조인 (m_code = counselor_code)
        code_list = [c.counselor_code for c in items if c.counselor_code]
        state_map: dict[str, str] = {}
        if code_list:
            # 동기 MSSQL 세션을 안전하게 열어 일괄 조회
            for mssql in get_db_mssql():
                repo = Tm60MemberRepository(mssql)
                state_map = repo.get_states_by_codes(code_list)
                break

        resp_items: List[CounselorListItem] = []
        for c in items:
            sp_list = None
            try:
                if isinstance(c.specialty_types, str) and c.specialty_types:
                    parsed = loads(c.specialty_types)
                    if isinstance(parsed, list):
                        sp_list = [x for x in parsed if x]
            except Exception:
                sp_list = None
            resp_items.append(CounselorListItem.model_validate({
                "counselor_id": c.counselor_id,
                "counselor_code": c.counselor_code,
                "name": c.name,
                "nickname": c.nickname,
                "phone": c.phone,
                "profile_image_url": c.profile_image_url,
                "introduction_short": c.introduction_short,
                "greeting_message": c.greeting_message,
                "career_info": c.career_info,
                "grade": c.grade,
                "specialty_types": sp_list,
                "keywords": c.keywords,
                "work_time": c.work_time,
                "rating_avg": c.rating_avg,
                "rating_count": c.rating_count,
                "consultation_count": c.consultation_count,
                "consultation_time_total": c.consultation_time_total,
                "after_amount": c.after_amount,
                "before_amount": c.before_amount or "",
                "is_best": bool(c.is_best) if c.is_best is not None else None,
                "is_new": bool(c.is_new) if c.is_new is not None else None,
                "is_show": bool(c.is_show),
                "is_out": bool(c.is_out),
                "approved_at": c.approved_at,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "last_login_at": c.last_login_at,
                "withdrawn_at": c.withdrawn_at,
                "m_state": state_map.get(c.counselor_code),
            }))

        return resp_items, params.page, params.limit, total

    async def update_show_status(self, *, counselor_id: str, is_show: bool) -> None:
        """상담사 노출여부만 수정"""
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        await self.counselor_repo.partial_update(counselor_id, is_show=is_show)

    async def update_counselor_detail(
        self,
        *,
        counselor_id: str,
        form: CounselorDetailUpdate,
        profile_image: Optional[UploadFile] = None,
    ) -> CounselorDetailResponse:
        """상담사 상세 정보 수정 + 프로필 이미지 S3 업로드

        - 파일이 있으면 dev-upload/cs/ 하위로 업로드 후 filename 저장
        - specialties는 문자열(JSON) 그대로 저장
        - password가 오면 해시 후 password_hash 교체
        - before_amount는 문자열/정수 허용 → 문자열로 저장
        """
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        updates: dict = {}

        # 단순 매핑 필드들
        simple_fields = [
            "is_show",
            "name",
            "nickname",
            "phone",
            "specialties",
            "counselor_code",
            "grade",
            "after_amount",
            "work_time",
            "is_new",
            "introduction_short",
            "greeting_message",
            "career_info",
            "keywords",
        ]

        for f in simple_fields:
            val = getattr(form, f, None)
            if val is not None:
                key = f
                if f == "specialties":
                    key = "specialty_types"
                updates[key] = val if f != "before_amount" else str(val)

        # before_amount: 별도 처리 (문자열로 저장)
        if form.before_amount is not None:
            updates["before_amount"] = str(form.before_amount)

        # 비밀번호 변경
        if form.password:
            if len(form.password) < 6:
                raise ValidationError("비밀번호는 6자 이상이어야 합니다")
            updates["password_hash"] = self.auth_service.hash_password(form.password)

        # 이미지 업로드
        if profile_image is not None:
            content = await profile_image.read()
            if not content:
                raise ValidationError("이미지 파일이 비어있습니다")
            filename = upload_public_image(subdirectory="cs", content=content, original_name=profile_image.filename or "image.png")
            updates["profile_image_url"] = filename

        # phone 변경 시 tm60_member.m_tel도 동기화
        if form.phone and self.tm60_member_service is not None:
            counselor_code = getattr(counselor, "counselor_code", None)
            if counselor_code:
                self.tm60_member_service.update_tel_by_code(m_code=counselor_code, m_tel=form.phone)

        updated = await self.counselor_repo.partial_update(counselor_id, **updates)
        if not updated:
            # 변경사항 없으면 현재 상태 반환
            counselor = await self.counselor_repo.get_by_id(counselor_id)
            if not counselor:
                raise NotFoundError("상담사를 찾을 수 없습니다")
        else:
            counselor = await self.counselor_repo.get_by_id(counselor_id)

        return CounselorDetailResponse.model_validate(counselor)


