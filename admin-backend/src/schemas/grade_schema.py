"""
등급(Grade) 스키마 (관리자 백엔드)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from typing import Any


class GradeItem(BaseModel):
    grade_code: str
    grade_name: str
    grade_level: int
    min_purchase_amount: int
    point_earn_rate: Decimal
    discount_rate: Decimal
    benefits: Optional[Dict[str, Any]] = None
    grade_image_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GradeListResponse(BaseModel):
    grades: List[GradeItem]
    total: int


class GradeDetailResponse(BaseModel):
    grade: GradeItem


class GradeCreateRequest(BaseModel):
    grade_code: str
    grade_name: str
    grade_level: int
    min_purchase_amount: int
    point_earn_rate: int | float
    discount_rate: int | float
    benefits: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: bool = True


class GradeUpdateRequest(BaseModel):
    grade_code: str = Field(..., description="PK: 수정 대상 코드")
    grade_name: Optional[str] = None
    grade_level: Optional[int] = None
    min_purchase_amount: Optional[int] = None
    point_earn_rate: Optional[int | float] = None
    discount_rate: Optional[int | float] = None
    benefits: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class GradeDeleteResponse(BaseModel):
    grade_code: str
    deleted: bool


class UsersByGradeItem(BaseModel):
    user_id: str
    email: str
    nickname: str
    phone: str
    join_type: str
    grade_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsersByGradeResponse(BaseModel):
    users: List[UsersByGradeItem]
    total: int


# =====================================================
# 월별 등급 업데이트 배치 관련 스키마
# =====================================================

class GradeChangeLogItem(BaseModel):
    """등급 변경 로그 항목"""
    log_id: int
    user_id: str
    grade_before: str
    grade_after: str
    purchase_amount: int
    change_reason: str
    admin_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GradeUpdateResultItem(BaseModel):
    """개별 사용자 등급 업데이트 결과"""
    user_id: str
    grade_before: str
    grade_after: str
    purchase_amount: int
    is_changed: bool = Field(..., description="등급 변경 여부")


class MonthlyGradeUpdateRequest(BaseModel):
    """월별 등급 업데이트 요청 스키마"""
    target_year: Optional[int] = Field(
        None,
        description="대상 연도 (미입력시 현재 기준 전월)"
    )
    target_month: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="대상 월 (미입력시 현재 기준 전월)"
    )
    dry_run: bool = Field(
        default=False,
        description="테스트 모드 (True: 실제 업데이트 없이 결과만 반환)"
    )


class MonthlyGradeUpdateResponse(BaseModel):
    """월별 등급 업데이트 응답 스키마"""
    target_year: int = Field(..., description="처리 대상 연도")
    target_month: int = Field(..., description="처리 대상 월")
    total_active_users: int = Field(..., description="전체 ACTIVE 사용자 수")
    total_processed: int = Field(..., description="처리된 사용자 수")
    total_upgraded: int = Field(..., description="등급 상승 사용자 수")
    total_downgraded: int = Field(..., description="등급 하락 사용자 수")
    total_unchanged: int = Field(..., description="등급 유지 사용자 수")
    dry_run: bool = Field(..., description="테스트 모드 여부")
    executed_at: datetime = Field(..., description="실행 시간")
    results: List[GradeUpdateResultItem] = Field(
        default=[],
        description="개별 처리 결과 (변경된 사용자만)"
    )


class GradeChangeLogListResponse(BaseModel):
    """등급 변경 로그 목록 응답"""
    logs: List[GradeChangeLogItem]
    total: int
    page: int = Field(default=1, description="현재 페이지")
    size: int = Field(default=20, description="페이지 당 개수")


