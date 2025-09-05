"""
등급 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class GradeBase(BaseModel):
    """등급 기본 스키마"""
    grade_name: str = Field(..., min_length=1, max_length=50, description="등급명")
    grade_level: int = Field(..., ge=1, description="등급 레벨")
    min_purchase_amount: int = Field(..., ge=0, description="최소 구매 금액")
    point_earn_rate: Decimal = Field(..., ge=0, le=100, description="포인트 적립률")
    discount_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100, description="할인율")
    benefits: Optional[Dict[str, Any]] = Field(None, description="추가 혜택 (JSON)")
    grade_image_url: Optional[str] = Field(None, max_length=500, description="등급 이미지 URL")
    description: Optional[str] = Field(None, description="등급 설명")
    is_active: bool = Field(default=True, description="활성화 여부")


class GradeCreate(GradeBase):
    """등급 생성 요청 스키마"""
    grade_code: str = Field(..., min_length=1, max_length=20, description="등급 코드")


class GradeUpdate(BaseModel):
    """등급 수정 요청 스키마"""
    grade_name: Optional[str] = Field(None, min_length=1, max_length=50, description="등급명")
    min_purchase_amount: Optional[int] = Field(None, ge=0, description="최소 구매 금액")
    point_earn_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="포인트 적립률")
    discount_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="할인율")
    benefits: Optional[Dict[str, Any]] = Field(None, description="추가 혜택 (JSON)")
    grade_image_url: Optional[str] = Field(None, max_length=500, description="등급 이미지 URL")
    description: Optional[str] = Field(None, description="등급 설명")
    is_active: Optional[bool] = Field(None, description="활성화 여부")


class GradeResponse(GradeBase):
    """등급 정보 응답 스키마"""
    grade_code: str = Field(..., description="등급 코드")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
    model_config = ConfigDict(from_attributes=True)


class NextGradeInfo(BaseModel):
    """다음 등급 정보 스키마"""
    current_grade: GradeResponse = Field(..., description="현재 등급 정보")
    next_grade: Optional[GradeResponse] = Field(None, description="다음 등급 정보 (최고 등급인 경우 None)")
    required_amount: Optional[int] = Field(None, description="다음 등급까지 필요한 구매 금액 (최고 등급인 경우 None)")


class GradeListResponse(BaseModel):
    """등급 목록 응답 스키마"""
    grades: list[GradeResponse] = Field(..., description="등급 목록")
    total: int = Field(..., description="전체 등급 수")


class UserGradeInfo(BaseModel):
    """사용자 등급 정보 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    current_grade: GradeResponse = Field(..., description="현재 등급")
    total_purchase_amount: int = Field(..., description="총 구매 금액")
    next_grade_info: Optional[NextGradeInfo] = Field(None, description="다음 등급 정보")