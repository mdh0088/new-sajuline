"""사용자 활동 로그 스키마"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class UserType(str, Enum):
    """사용자 타입"""
    USER = "USER"
    COUNSELOR = "COUNSELOR" 
    GUEST = "GUEST"


class DeviceType(str, Enum):
    """기기 타입"""
    DESKTOP = "DESKTOP"
    MOBILE = "MOBILE"
    TABLET = "TABLET"


class ActivityType(str, Enum):
    """활동 타입"""
    # 인증 관련
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    SIGNUP = "SIGNUP"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    
    # 페이지 접근
    PAGE_VIEW = "PAGE_VIEW"
    API_ACCESS = "API_ACCESS"
    
    # 상담 관련
    CONSULTATION_START = "CONSULTATION_START"
    CONSULTATION_END = "CONSULTATION_END"
    MESSAGE_SEND = "MESSAGE_SEND"
    
    # 결제 관련
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    
    # AI 서비스
    AI_FORTUNE_REQUEST = "AI_FORTUNE_REQUEST"
    AI_FORTUNE_COMPLETE = "AI_FORTUNE_COMPLETE"
    
    # 기타
    PROFILE_UPDATE = "PROFILE_UPDATE"
    SETTINGS_CHANGE = "SETTINGS_CHANGE"


class UserActivityLogBase(BaseModel):
    """사용자 활동 로그 기본 스키마"""
    user_id: Optional[str] = Field(None, description="사용자 ID", max_length=100)
    user_type: UserType = Field(UserType.USER, description="사용자 타입")
    activity_type: ActivityType = Field(..., description="활동 타입")
    activity_detail: Optional[Dict[str, Any]] = Field(None, description="활동 상세 정보")
    ip_address: Optional[str] = Field(None, description="IP 주소", max_length=45)
    user_agent: Optional[str] = Field(None, description="User Agent")
    device_type: Optional[DeviceType] = Field(None, description="기기 타입")


class UserActivityLogCreate(UserActivityLogBase):
    """사용자 활동 로그 생성 스키마"""
    pass


class UserActivityLogResponse(UserActivityLogBase):
    """사용자 활동 로그 응답 스키마"""
    log_id: int = Field(..., description="로그 ID")
    created_at: datetime = Field(..., description="생성일시")
    
    model_config = ConfigDict(from_attributes=True)


class UserActivityLogFilter(BaseModel):
    """사용자 활동 로그 필터 스키마"""
    user_id: Optional[str] = Field(None, description="사용자 ID")
    user_type: Optional[UserType] = Field(None, description="사용자 타입")
    activity_type: Optional[ActivityType] = Field(None, description="활동 타입")
    device_type: Optional[DeviceType] = Field(None, description="기기 타입")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    start_date: Optional[datetime] = Field(None, description="시작일시")
    end_date: Optional[datetime] = Field(None, description="종료일시")
    limit: int = Field(100, description="조회 개수", ge=1, le=1000)
    offset: int = Field(0, description="조회 시작점", ge=0)