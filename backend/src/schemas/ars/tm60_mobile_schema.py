"""
ARS tm60_mobile 테이블 관련 Pydantic 스키마 (MSSQL 연동)

전화 상담 시작 시 모바일 플랫폼 정보 기록을 위한 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.ars.tm60_mobile_model import MobilePlatform


class Tm60MobileCreate(BaseModel):
    """tm60_mobile INSERT 요청 스키마"""
    mb_id: str = Field(..., min_length=1, max_length=50, description="유저 ID")
    mb_code: str = Field(..., min_length=1, max_length=3, description="상담사 코드")
    mb_platform: str = Field(
        default=MobilePlatform.MOBILE_WEB.value,
        description="플랫폼 타입: 1=Mobile web, 2=Android, 3=iOS"
    )


class Tm60MobileResponse(BaseModel):
    """tm60_mobile 응답 스키마"""
    idx: int = Field(..., description="고유 식별자")
    mb_id: str = Field(..., description="유저 ID")
    mb_code: str = Field(..., description="상담사 코드")
    mb_platform: str = Field(..., description="플랫폼 타입")
    platform_name: str = Field(..., description="플랫폼명")
    regdate: Optional[datetime] = Field(None, description="등록일시")

    model_config = ConfigDict(from_attributes=True)


class CallByPointRequest(BaseModel):
    """포인트 상담 전화 연결 요청 스키마 (프론트엔드 → 백엔드)"""
    counselor_code: str = Field(..., min_length=1, max_length=3, description="상담사 코드")
    platform: str = Field(
        default=MobilePlatform.MOBILE_WEB.value,
        description="플랫폼 타입: 1=Mobile web, 2=Android, 3=iOS"
    )


class CallByPointResponse(BaseModel):
    """포인트 상담 전화 연결 응답 스키마"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(default="", description="응답 메시지")
