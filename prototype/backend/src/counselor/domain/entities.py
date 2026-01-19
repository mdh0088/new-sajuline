"""
Counselor 도메인 엔티티 정의 (MVP 버전)
상담사 로그인 및 기본 프로필 관련 엔티티만 포함
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr


@dataclass(slots=True)
class CounselorSpecialtyEntity:
    specialty_id: str
    specialty_code: str
    specialty_name: str
    description: Optional[str] = None


@dataclass(slots=True)
class CounselorEntity:
    counselor_id: str
    email: str
    password_hash: str
    counselor_nickname: str
    counselor_code: str
    name: str
    profile_image_url: Optional[str]
    introduction: str
    specialties: List[CounselorSpecialtyEntity]
    price_per_minute: int
    counselor_status: int | str
    counselor_status_text: str
    is_online: bool
    is_authorized: bool
    rating_avg: float
    rating_count: int
    created_at: datetime

class CounselorStatus(int, Enum):
    """상담사 상태"""
    WAITING = 1      # 대기중
    CONSULTING = 2   # 상담중
    AWAY = 3         # 부재중


# === 로그인 관련 엔티티 ===
class CounselorLoginRequest(BaseModel):
    """상담사 로그인 요청"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class CounselorTokenPair(BaseModel):
    """상담사 JWT 토큰 쌍"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class SpecialtyInfo(BaseModel):
    """전문분야 정보"""
    specialty_id: str  # UUID
    specialty_code: str
    specialty_name: str
    description: Optional[str] = None


class CounselorInfo(BaseModel):
    """상담사 정보 (로그인 후 공통 사용)"""
    counselor_id: str
    email: str
    counselor_nickname: str
    counselor_code: str
    name: str
    profile_image_url: Optional[str] = None
    introduction: str
    specialties: List[SpecialtyInfo] = []
    price_per_minute: int
    counselor_status: int
    counselor_status_text: str
    is_online: bool
    is_authorized: bool
    rating_avg: float
    rating_count: int
    created_at: datetime
    # 인증 관련 추가 필드
    roles: list[str] = ["counselor"]
    permissions: list[str] = []


class CounselorLoginResponse(BaseModel):
    """상담사 로그인 응답"""
    success: bool = True
    message: str = "상담사 로그인되었습니다."
    tokens: CounselorTokenPair
    counselor: CounselorInfo


# === 기본 프로필 엔티티 ===
class CounselorProfile(BaseModel):
    """상담사 프로필 (공개용)"""
    counselor_id: str
    counselor_nickname: str
    counselor_code: str
    name: str
    profile_image_url: Optional[str] = None
    introduction: str
    specialties: List[SpecialtyInfo]
    price_per_minute: int
    rating_avg: float
    rating_count: int
    is_online: bool
    counselor_status: int
    counselor_status_text: str


class CounselorListResponse(BaseModel):
    """상담사 목록 응답"""
    counselors: List[CounselorProfile]
    total_count: int
    has_more: bool


# === 상태 업데이트 엔티티 ===
class UpdateCounselorStatusRequest(BaseModel):
    """상담사 상태 업데이트 요청"""
    counselor_status: CounselorStatus


class UpdateOnlineStatusRequest(BaseModel):
    """온라인 상태 업데이트 요청"""
    is_online: bool


class SpecialtyListResponse(BaseModel):
    """전문분야 목록 응답"""
    specialties: List[SpecialtyInfo] 