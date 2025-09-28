"""
상담사 스키마 (관리자 백엔드)
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class CounselorResponse(BaseModel):
    counselor_id: str
    counselor_code: str
    password_hash: str
    name: str
    nickname: str
    phone: str
    profile_image_url: Optional[str] = None
    introduction_short: Optional[str] = None
    greeting_message: Optional[str] = None
    career_info: Optional[str] = None
    counselor_status: str
    grade: Optional[str] = None
    specialty_types: Optional[str] = None
    keywords: Optional[str] = None
    work_time: Optional[str] = None
    rating_avg: Optional[Decimal] = None
    rating_count: Optional[int] = None
    consultation_count: Optional[int] = None
    consultation_time_total: Optional[int] = None
    after_amount: Optional[int] = None
    before_amount: str
    is_best: Optional[bool] = None
    is_new: Optional[bool] = None
    is_out: bool
    is_show: bool
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CounselorFullDetailResponse(BaseModel):
    counselor: CounselorResponse
    member: Optional[dict] = Field(default=None, description="tm60_member 전체 필드")

"""
상담사 스키마 (관리자 백엔드)
"""
from typing import Literal, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class CounselorStateUpdateRequest(BaseModel):
    """상담사 상태 수정 요청 스키마

    - m_state: "1"(대기중), "2"(상담중), "3"(부재중)
    - counselor_code는 MSSQL tm60_member.m_code 매칭에 사용
    """
    counselor_id: str = Field(..., min_length=1, max_length=100, description="상담사 ID(이메일)")
    counselor_code: str = Field(..., min_length=1, max_length=50, description="상담사 코드")
    m_state: Literal["1", "2", "3"] = Field(..., description="상담사 상태: 1=대기중, 2=상담중, 3=부재중")


class CounselorStateUpdateResponse(BaseModel):
    """상담사 상태 수정 결과"""
    counselor_id: str = Field(..., description="상담사 ID")
    counselor_code: str = Field(..., description="상담사 코드")
    m_state: str = Field(..., description="변경된 상담사 상태")
    updated: bool = Field(..., description="업데이트 성공 여부")


class CounselorListParams(BaseModel):
    """상담사 목록 조회 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    search_type: str = Field(default="all", description="검색 타입: all|name|nickname|counselor_id")
    search_name: Optional[str] = Field(default=None, description="검색 키워드")
    specialties: Optional[List[str]] = Field(
        default=None,
        description="전문 분야 필터 (예: ['TARO','SAJU'])",
        validation_alias=AliasChoices("specialties", "specialyties"),
    )
    is_show: Optional[bool] = Field(default=None, description="노출 여부 필터")
    is_out: Optional[bool] = Field(default=None, description="탈퇴 여부 필터")
    start_dt: Optional[str] = Field(default=None, description="생성일 범위 시작 yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="생성일 범위 종료 yyyy-mm-dd")


class CounselorListItem(BaseModel):
    """상담사 목록 아이템 (m_state 포함)"""
    counselor_id: str
    counselor_code: str
    name: str
    nickname: str
    is_show: bool
    is_out: bool
    created_at: datetime
    specialty_types: Optional[List[str]] = None
    m_state: Optional[str] = Field(default=None, description="tm60_member.m_state")

    model_config = ConfigDict(from_attributes=True)


class CounselorDetailUpdate(BaseModel):
    """상담사 상세 정보 수정용 스키마 (multipart form + 파일 업로드)

    - 모든 필드는 선택적(partial update)
    - 파일은 API에서 UploadFile로 받고, 여기서는 값 검증만 담당
    """
    is_show: Optional[bool] = Field(default=None, description="노출 여부")
    name: Optional[str] = Field(default=None, description="실명")
    nickname: Optional[str] = Field(default=None, description="닉네임")
    phone: Optional[str] = Field(default=None, description="전화번호")
    password: Optional[str] = Field(default=None, description="비밀번호 원문 (있으면 해시 후 저장)")
    specialties: Optional[str] = Field(default=None, description="전문 분야 JSON 문자열 예: ['TARO','SAJU']")
    counselor_code: Optional[str] = Field(default=None, description="상담사 코드")
    grade: Optional[str] = Field(default=None, description="상담사 등급: BRONZE|SILVER|GOLD")
    after_amount: Optional[int] = Field(default=None, description="선불 금액")
    before_amount: Optional[int | str] = Field(default=None, description="후불 금액")
    work_time: Optional[str] = Field(default=None, description="업무 시간")
    is_new: Optional[bool] = Field(default=None, description="신규 여부")
    introduction_short: Optional[str] = Field(default=None, description="짧은 소개")
    greeting_message: Optional[str] = Field(default=None, description="인사말")
    career_info: Optional[str] = Field(default=None, description="경력사항")
    keywords: Optional[str] = Field(default=None, description="키워드 (쉼표 구분)")


class CounselorDetailResponse(BaseModel):
    """수정 결과 반환 스키마 (요약)"""
    counselor_id: str
    counselor_code: str
    name: str | None = None
    nickname: str
    phone: str | None = None
    profile_image_url: str | None = None
    is_show: bool
    is_new: bool | None = None

    model_config = ConfigDict(from_attributes=True)

