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


