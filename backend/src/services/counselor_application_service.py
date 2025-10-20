"""
상담사 지원 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
import json
from typing import List, Optional

from fastapi import UploadFile

from src.repositories.counselor_application_repository import CounselorApplicationRepository
from src.models.counselor_application_model import CounselorApplication
from src.schemas.counselor_application_schema import CounselorApplicationCreate, CounselorApplicationResponse
from src.common.storage.s3 import upload_public_image
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError


class CounselorApplicationService:
    """상담사 지원 비즈니스 로직 서비스"""

    def __init__(self, application_repo: CounselorApplicationRepository):
        self.application_repo = application_repo

    async def create_application(
        self,
        application_data: CounselorApplicationCreate,
        photo_files: Optional[List[UploadFile]] = None
    ) -> CounselorApplicationResponse:
        """
        상담사 지원 생성
        """
        log = get_logger_with_request_id()
        log.info("Creating counselor application", nickname=application_data.nickname)

        # 중복 체크
        if await self.application_repo.exists_by_nickname(application_data.nickname):
            raise ValidationError("이미 사용 중인 닉네임입니다.")

        if await self.application_repo.exists_by_email(application_data.email):
            raise ValidationError("이미 등록된 이메일입니다.")

        if await self.application_repo.exists_by_phone(application_data.phone):
            raise ValidationError("이미 등록된 전화번호입니다.")

        # 파일 업로드 처리 (최대 3개)
        upload_image1 = None
        upload_image2 = None
        upload_image3 = None

        if photo_files:
            if len(photo_files) > 3:
                raise ValidationError("사진은 최대 3장까지 업로드 가능합니다.")

            for idx, photo in enumerate(photo_files):
                if photo.size and photo.size > 5 * 1024 * 1024:  # 5MB
                    raise ValidationError(f"파일 크기는 5MB를 초과할 수 없습니다: {photo.filename}")

                # 파일 읽기
                content = await photo.read()

                # S3 업로드 (파일명만 반환)
                filename = upload_public_image(
                    subdirectory="counselor_applications",
                    content=content,
                    original_name=photo.filename or "image.png"
                )

                if idx == 0:
                    upload_image1 = filename
                elif idx == 1:
                    upload_image2 = filename
                elif idx == 2:
                    upload_image3 = filename

        # specialty_types를 JSON 문자열로 변환
        specialty_types_json = json.dumps(application_data.specialty_types, ensure_ascii=False)

        # 모델 생성
        application = CounselorApplication(
            name=application_data.name,
            nickname=application_data.nickname,
            email=application_data.email,
            phone=application_data.phone,
            address=application_data.address,
            specialty_types=specialty_types_json,
            keywords=application_data.keywords,
            introduction=application_data.introduction,
            upload_image1=upload_image1,
            upload_image2=upload_image2,
            upload_image3=upload_image3,
            application_status="PENDING"
        )

        # DB 저장
        created_application = await self.application_repo.create(application)

        # 응답 데이터 생성 - specialty_types JSON 파싱
        specialty_types_list = None
        if created_application.specialty_types:
            specialty_types_list = json.loads(created_application.specialty_types)

        response = CounselorApplicationResponse(
            application_id=created_application.application_id,
            name=created_application.name,
            nickname=created_application.nickname,
            email=created_application.email,
            phone=created_application.phone,
            address=created_application.address,
            specialty_types=specialty_types_list,
            keywords=created_application.keywords,
            introduction=created_application.introduction,
            upload_image1=created_application.upload_image1,
            upload_image2=created_application.upload_image2,
            upload_image3=created_application.upload_image3,
            application_status=created_application.application_status,
            admin_note=created_application.admin_note,
            reviewed_by=created_application.reviewed_by,
            reviewed_at=created_application.reviewed_at,
            created_at=created_application.created_at,
            updated_at=created_application.updated_at
        )

        log.info("Counselor application created successfully", application_id=created_application.application_id)
        return response
