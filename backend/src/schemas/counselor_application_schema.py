"""
상담사 지원 관련 스키마
DDL 기반 정확히 매핑
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CounselorApplicationCreate(BaseModel):
    """상담사 신청 생성 요청"""
    name: str = Field(..., min_length=1, max_length=50, description="실명")
    nickname: str = Field(..., min_length=1, max_length=100, description="희망 활동명")
    email: str = Field(..., min_length=1, max_length=100, description="이메일")
    phone: str = Field(..., min_length=1, max_length=50, description="전화번호")
    address: Optional[str] = Field(None, max_length=500, description="주소")
    specialty_types: List[str] = Field(..., description='신청 분야 예: ["TARO", "SAJU"]')
    keywords: Optional[str] = Field(None, max_length=500, description="키워드")
    introduction: Optional[str] = Field(None, description="자기소개")

    @field_validator('specialty_types')
    @classmethod
    def validate_specialty_types(cls, v):
        """specialty_types 유효성 검증"""
        allowed_types = {"TARO", "SAJU", "FORTUNE", "EASY"}
        if not v:
            raise ValueError("specialty_types는 최소 1개 이상 선택해야 합니다.")
        for item in v:
            if item not in allowed_types:
                raise ValueError(f"specialty_types는 TARO, SAJU, FORTUNE, EASY 중 하나여야 합니다.")
        return v


class CounselorApplicationResponse(BaseModel):
    """상담사 신청 응답"""
    application_id: int
    name: str
    nickname: str
    email: str
    phone: str
    address: Optional[str]
    specialty_types: Optional[List[str]]  # JSON 문자열을 파싱한 리스트
    keywords: Optional[str]
    introduction: Optional[str]
    upload_image1: Optional[str]
    upload_image2: Optional[str]
    upload_image3: Optional[str]
    application_status: str
    admin_note: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
