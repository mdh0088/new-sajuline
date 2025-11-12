"""
상담사 신청 스키마 (관리자 백엔드)
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


class CounselorApplicationResponse(BaseModel):
    """상담사 신청 응답 스키마"""
    application_id: int
    name: str
    nickname: str
    email: str
    phone: str
    address: Optional[str] = None
    specialty_types: Optional[str] = None
    keywords: Optional[str] = None
    introduction: Optional[str] = None
    selected_image_url: Optional[str] = None
    upload_image1: Optional[str] = None
    upload_image2: Optional[str] = None
    upload_image3: Optional[str] = None
    application_status: str
    admin_note: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CounselorApplicationListParams(BaseModel):
    """상담사 신청 목록 조회 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    search_type: str = Field(default="all", description="검색 타입: all|name|nickname|email")
    search_name: Optional[str] = Field(default=None, description="검색 키워드")
    specialties: Optional[List[str]] = Field(
        default=None,
        description="전문 분야 필터 (예: ['TARO','SAJU','FORTUNE','EASY'])"
    )
    application_status: Optional[str] = Field(
        default=None,
        description="신청 상태 필터: PENDING|APPROVED|REJECTED"
    )
    start_dt: Optional[str] = Field(default=None, description="생성일 범위 시작 yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="생성일 범위 종료 yyyy-mm-dd")


class CounselorApplicationListItem(BaseModel):
    """상담사 신청 목록 아이템"""
    application_id: int
    name: str
    nickname: str
    email: str
    phone: str
    address: Optional[str] = None
    specialty_types: Optional[List[str]] = None
    keywords: Optional[str] = None
    introduction: Optional[str] = None
    selected_image_url: Optional[str] = None
    upload_image1: Optional[str] = None
    upload_image2: Optional[str] = None
    upload_image3: Optional[str] = None
    application_status: str
    admin_note: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CounselorApplicationDetailUpdate(BaseModel):
    """상담사 신청 상세 정보 수정용 스키마

    - 모든 필드는 선택적(partial update)
    - 이미지 파일은 API에서 UploadFile로 받음
    """
    name: Optional[str] = Field(default=None, description="실명")
    nickname: Optional[str] = Field(default=None, description="희망 활동명")
    email: Optional[str] = Field(default=None, description="이메일")
    phone: Optional[str] = Field(default=None, description="전화번호")
    address: Optional[str] = Field(default=None, description="주소")
    specialties: Optional[str] = Field(default=None, description="전문 분야 JSON 문자열")
    keywords: Optional[str] = Field(default=None, description="키워드")
    introduction: Optional[str] = Field(default=None, description="자기소개")
    application_status: Optional[Literal["PENDING", "APPROVED", "REJECTED"]] = Field(
        default=None,
        description="신청 상태"
    )
    admin_note: Optional[str] = Field(default=None, description="관리자 메모")
    reviewed_by: Optional[int] = Field(default=None, description="검토한 관리자 ID")


class CounselorApplicationDetailResponse(BaseModel):
    """상담사 신청 수정 결과 반환 스키마"""
    application_id: int
    name: str
    nickname: str
    email: str
    phone: str
    application_status: str
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CounselorApplicationStatusUpdate(BaseModel):
    """상담사 신청 상태 변경 요청 스키마"""
    application_status: Literal["PENDING", "APPROVED", "REJECTED"] = Field(
        ...,
        description="신청 상태: PENDING|APPROVED|REJECTED"
    )
    admin_note: Optional[str] = Field(default=None, description="관리자 메모")
    reviewed_by: Optional[int] = Field(default=None, description="검토한 관리자 ID")


class CounselorConversionRequest(BaseModel):
    """상담사 전환 요청 스키마 - 신청자 정보를 모두 파라미터로 받음"""
    counselor_code: str = Field(..., min_length=1, max_length=50, description="상담사 고유 코드")
    name: str = Field(..., min_length=1, max_length=50, description="실명")
    nickname: str = Field(..., min_length=1, max_length=100, description="활동명")
    email: str = Field(..., min_length=1, max_length=100, description="이메일")
    phone: str = Field(..., min_length=1, max_length=50, description="전화번호")
    address: Optional[str] = Field(default=None, max_length=500, description="주소")
    specialty_types: Optional[str] = Field(default=None, description="전문 분야 JSON 문자열")
    keywords: Optional[str] = Field(default=None, max_length=500, description="키워드")
    introduction: Optional[str] = Field(default=None, description="자기소개")
    selected_image_url: Optional[str] = Field(default=None, max_length=500, description="선택된 이미지 URL")
    upload_image1: Optional[str] = Field(default=None, max_length=500, description="업로드 이미지 1")
    upload_image2: Optional[str] = Field(default=None, max_length=500, description="업로드 이미지 2")
    upload_image3: Optional[str] = Field(default=None, max_length=500, description="업로드 이미지 3")
    application_status: Optional[str] = Field(default=None, max_length=20, description="신청 상태")
    admin_note: Optional[str] = Field(default=None, description="관리자 메모")

    model_config = ConfigDict(from_attributes=True)


class CounselorConversionResponse(BaseModel):
    """상담사 전환 응답 스키마"""
    counselor_id: str = Field(..., description="생성된 상담사 ID (이메일)")
    counselor_code: str = Field(..., description="상담사 고유 코드")
    name: str = Field(..., description="상담사 이름")
    nickname: str = Field(..., description="상담사 활동명")
    message: str = Field(default="상담사 전환 완료", description="응답 메시지")

    model_config = ConfigDict(from_attributes=True)
