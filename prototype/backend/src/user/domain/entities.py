"""
사용자 도메인 엔티티 정의
사용자 프로필, 설정, 포인트 관리 관련 엔티티
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from dataclasses import dataclass


class UserStatus(str, Enum):
    """사용자 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SubscriptionType(str, Enum):
    """구독 타입"""
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
@dataclass(slots=True)
class UserEntity:
    user_id: str
    email: str
    password_hash: str | None
    nickname: str
    phone: str
    join_type: str
    social_provider: str | None
    social_id: str | None
    user_status: str
    grade_code: str
    profile_image_url: Optional[str]
    birth_date: Optional[datetime]
    gender: Optional[str]
    is_marketing_agreed: bool
    failed_login_count: Optional[int]
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    withdrawn_at: Optional[datetime]

    @property
    def is_active(self) -> bool:
        return self.user_status == "ACTIVE"



class UserProfile(BaseModel):
    """사용자 프로필 정보"""
    id: str
    email: str
    name: str
    nickname: str
    status: UserStatus
    subscription_type: SubscriptionType = SubscriptionType.FREE
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    point_balance: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class UpdateProfileRequest(BaseModel):
    """프로필 업데이트 요청"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r'^01[0-9]{8,9}$')
    birth_date: Optional[datetime] = None
    gender: Optional[str] = Field(None, pattern=r'^[MF]$')


class UpdateProfileResponse(BaseModel):
    """프로필 업데이트 응답"""
    success: bool = True
    message: str = "프로필이 업데이트되었습니다."
    profile: UserProfile


class PointTransaction(BaseModel):
    """포인트 거래 내역"""
    id: str
    user_id: str
    amount: int
    transaction_type: str  # "charge", "use", "refund", "reward"
    description: str
    balance_after: int
    created_at: datetime


class AddPointsRequest(BaseModel):
    """포인트 추가 요청"""
    amount: int = Field(..., gt=0, description="추가할 포인트 (양수)")
    description: str = Field(..., max_length=200, description="거래 설명")


class UsePointsRequest(BaseModel):
    """포인트 사용 요청"""
    amount: int = Field(..., gt=0, description="사용할 포인트 (양수)")
    description: str = Field(..., max_length=200, description="거래 설명")


class PointTransactionResponse(BaseModel):
    """포인트 거래 응답"""
    success: bool = True
    message: str
    transaction: PointTransaction
    current_balance: int


class UserSettingsRequest(BaseModel):
    """사용자 설정 요청"""
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    notification_push: Optional[bool] = None
    marketing_consent: Optional[bool] = None


class UserSettings(BaseModel):
    """사용자 설정"""
    user_id: str
    notification_email: bool = True
    notification_sms: bool = False
    notification_push: bool = True
    marketing_consent: bool = False
    updated_at: Optional[datetime] = None


class UserStatsResponse(BaseModel):
    """사용자 통계 응답"""
    total_consultations: int = 0
    total_points_used: int = 0
    total_points_earned: int = 0
    favorite_consultants: list[str] = []
    member_since: datetime
    last_activity: Optional[datetime] = None


class DeleteAccountRequest(BaseModel):
    """계정 삭제 요청"""
    password: str = Field(..., description="현재 비밀번호 확인")
    reason: Optional[str] = Field(None, max_length=500, description="탈퇴 사유")


class DeleteAccountResponse(BaseModel):
    """계정 삭제 응답"""
    success: bool = True
    message: str = "계정이 삭제되었습니다."
    deleted_at: datetime 