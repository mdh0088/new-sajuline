"""
관리자 백엔드 상담사 신청 서비스: 목록 조회/상세 수정(+S3 업로드)/상담사 전환
"""
from typing import Tuple, List, Optional
from datetime import datetime, timezone, timedelta
from json import loads

# 한국 표준시 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.repositories.counselor_application_repository import CounselorApplicationRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.schemas.counselor_application_schema import (
    CounselorApplicationListParams,
    CounselorApplicationListItem,
    CounselorApplicationDetailUpdate,
    CounselorApplicationDetailResponse,
    CounselorConversionRequest,
    CounselorConversionResponse,
)
from src.common.storage.s3 import upload_public_image
from src.services.auth_service import AuthService


class CounselorApplicationService:
    """상담사 신청 비즈니스 로직 (관리자)"""

    def __init__(
        self,
        application_repo: CounselorApplicationRepository,
        counselor_repo: Optional[CounselorRepository] = None,
        tm60_repo: Optional[Tm60MemberRepository] = None,
    ):
        self.application_repo = application_repo
        self.counselor_repo = counselor_repo
        self.tm60_repo = tm60_repo
        self.auth_service = AuthService()

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

    async def convert_to_counselor(
        self,
        *,
        request: CounselorConversionRequest,
    ) -> CounselorConversionResponse:
        """상담사 신청자를 정식 상담사로 전환

        - t_counselor 중복 체크: counselor_code, email, nickname, phone
        - t_counselor 삽입 (MariaDB)
        - tm60_members 삽입 (MSSQL)
        - 트랜잭션 처리 (두 DB 모두 커밋 또는 롤백)
        """
        if not self.counselor_repo:
            raise ValidationError("CounselorRepository가 초기화되지 않았습니다")
        if not self.tm60_repo:
            raise ValidationError("Tm60MemberRepository가 초기화되지 않았습니다")

        # 1. t_counselor 중복 체크 (counselor_code, email, nickname, phone)
        existing_code = await self.counselor_repo.get_by_counselor_code(request.counselor_code)
        if existing_code:
            raise ValidationError(f"상담사 코드 '{request.counselor_code}'는 이미 사용 중입니다")

        existing_email = await self.counselor_repo.get_by_id(request.email)
        if existing_email:
            raise ValidationError(f"이메일 '{request.email}'은 이미 사용 중입니다")

        existing_nickname = await self.counselor_repo.get_by_nickname(request.nickname)
        if existing_nickname:
            raise ValidationError(f"닉네임 '{request.nickname}'은 이미 사용 중입니다")

        existing_phone = await self.counselor_repo.get_by_phone(request.phone)
        if existing_phone:
            raise ValidationError(f"전화번호 '{request.phone}'는 이미 사용 중입니다")

        # 2. 비밀번호 해싱 (phone + '!')
        default_password = f"{request.phone}!"
        hashed_password = self.auth_service.hash_password(default_password)

        # 3. t_counselor 데이터 매핑
        counselor_data = {
            "counselor_id": request.email,  # email -> counselor_id
            "counselor_code": request.counselor_code,
            "password_hash": hashed_password,  # password_hash 필드 사용
            "name": request.name,
            "nickname": request.nickname,
            "phone": request.phone,
            "specialty_types": request.specialty_types,
            "keywords": request.keywords,
            "introduction_short": request.introduction,  # introduction -> introduction_short
            "profile_image_url": request.upload_image1,  # upload_image1 -> profile_image_url
            "is_show": True,
            "is_out": False,
            "created_at": datetime.utcnow(),
            "approved_at": datetime.utcnow(),  # 상담사 전환 승인 시간
        }

        # 4. tm60_members 데이터 매핑 (한글 필드는 euc-kr 인코딩)
        def encode_euckr(text: str) -> bytes:
            """한글을 euc-kr로 인코딩"""
            try:
                return text.encode('euc-kr')
            except Exception:
                return text.encode('utf-8')

        # MSSQL datetime은 timezone-naive만 지원하므로 tzinfo 제거
        kst_now = datetime.now(KST).replace(tzinfo=None)
        tm60_data = {
            "m_code": request.counselor_code,  # counselor_code -> m_code
            "m_name": encode_euckr(request.name),  # name -> m_name (euc-kr 바이트)
            "m_nickname": encode_euckr(request.nickname),  # nickname -> m_nickname (euc-kr 바이트)
            "m_tel": request.phone,  # phone -> m_tel
            "m_tel1": request.phone,  # phone -> m_tel1
            "m_tel2": request.phone,  # phone -> m_tel2
            "m_mobile": request.phone,  # phone -> m_mobile
            "m_id": request.email,  # email -> m_id
            "m_state": "3",  # 디폴트 상태값
            "m_prate": 800,  # 디폴트 요율
            "m_fdate": kst_now,  # 가입일 (KST)
        }

        counselor = None
        try:
            # 5. t_counselor 삽입 (MariaDB async - flush만 수행)
            counselor = await self.counselor_repo.create(counselor_data)

            # 6. tm60_members 삽입 (MSSQL sync - flush만 수행)
            import asyncio
            tm60_member = await asyncio.to_thread(self.tm60_repo.create, tm60_data)

            # 7. 신청 상태를 APPROVED로 변경 (email로 조회 후 업데이트)
            application = await self.application_repo.get_by_email(request.email)
            if application:
                await self.application_repo.partial_update(
                    application.application_id,
                    application_status="APPROVED",
                    reviewed_at=datetime.utcnow(),
                )

            # 8. 두 DB 모두 성공 시 commit (FastAPI 의존성이 자동 처리)
            # MariaDB commit은 get_db()가 자동 처리
            # MSSQL commit도 get_db_mssql()이 자동 처리

            return CounselorConversionResponse(
                counselor_id=counselor.counselor_id,
                counselor_code=counselor.counselor_code,
                name=counselor.name,
                nickname=counselor.nickname,
                message="상담사 전환이 완료되었습니다",
            )
        except Exception as e:
            # 에러 발생 시 두 DB 모두 rollback (FastAPI 의존성이 자동 처리)
            raise ValidationError(f"상담사 전환 중 오류가 발생했습니다: {str(e)}")
