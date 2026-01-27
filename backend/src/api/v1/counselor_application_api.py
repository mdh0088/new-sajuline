"""
상담사 지원 API 엔드포인트
"""
import json
from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile, status, HTTPException

from src.core.dependencies import CounselorApplicationServiceDep, MariaSessionDep
from src.schemas.counselor_application_schema import CounselorApplicationCreate, CounselorApplicationResponse
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException, ValidationError

router = APIRouter(prefix="/counselor-applications", tags=["counselor-applications"])


@router.post(
    "",
    response_model=APIResponse[CounselorApplicationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="상담사 신청",
    description="상담사 신청서를 제출합니다. 최대 3개의 사진을 첨부할 수 있습니다."
)
async def create_counselor_application(
    db: MariaSessionDep,
    application_service: CounselorApplicationServiceDep,
    name: str = Form(..., description="실명"),
    nickname: str = Form(..., description="희망 활동명"),
    email: str = Form(..., description="이메일"),
    phone: str = Form(..., description="전화번호"),
    address: str = Form(None, description="주소"),
    specialty_types: str = Form(..., description='신청 분야 JSON 배열 예: ["TARO","SAJU"]'),
    keywords: str = Form(None, description="키워드"),
    introduction: str = Form(None, description="자기소개"),
    photos: List[UploadFile] = File(None, description="사진 (최대 3개, 각 5MB 이하)")
):
    """상담사 신청 생성"""
    log = get_logger_with_request_id()

    try:
        # specialty_types JSON 파싱
        try:
            specialty_types_list = json.loads(specialty_types)
        except json.JSONDecodeError:
            raise ValidationError("specialty_types는 유효한 JSON 배열이어야 합니다.")

        # 스키마 검증
        application_data = CounselorApplicationCreate(
            name=name,
            nickname=nickname,
            email=email,
            phone=phone,
            address=address,
            specialty_types=specialty_types_list,
            keywords=keywords,
            introduction=introduction
        )

        # 서비스 실행
        result = await application_service.create_application(
            application_data=application_data,
            photo_files=photos
        )

        await db.commit()

        log.info("Counselor application created", application_id=result.application_id)
        return ok(data=result, message="상담사 신청이 완료되었습니다.")

    except (ValidationError, BaseAppException) as e:
        await db.rollback()
        log.warning("Application error in counselor application", error=str(e))
        raise  # 전역 예외 핸들러에서 APIResponse 형태로 변환
    except Exception as e:
        await db.rollback()
        log.error("Unexpected error in counselor application", error=str(e))
        raise  # 전역 예외 핸들러에서 처리
