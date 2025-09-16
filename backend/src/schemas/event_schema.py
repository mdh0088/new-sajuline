"""
이벤트 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, validator

from src.models.event_model import EventType, RewardType


class EventBase(BaseModel):
    """이벤트 기본 스키마"""
    event_code: str = Field(..., min_length=1, max_length=50, description="이벤트 코드")
    event_name: str = Field(..., min_length=1, max_length=100, description="이벤트명")
    event_type: EventType = Field(..., description="이벤트 타입")
    description: Optional[str] = Field(None, description="설명")
    terms: Optional[str] = Field(None, description="약관")
    banner_image_url: Optional[str] = Field(None, max_length=500, description="배너 이미지 URL")
    reward_type: RewardType = Field(..., description="보상 타입")
    reward_value: int = Field(..., ge=0, description="보상 값")
    max_participants: Optional[int] = Field(None, ge=1, description="최대 참여자수")
    is_active: bool = Field(default=True, description="활성화 여부")
    valid_from: datetime = Field(..., description="시작일")
    valid_until: datetime = Field(..., description="종료일")
    event_metadata: Optional[Dict[str, Any]] = Field(None, description="추가 데이터 (JSON)")
    
    @validator('valid_until')
    def validate_date_range(cls, v, values):
        """종료일이 시작일보다 늦은지 검증"""
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('종료일은 시작일보다 늦어야 합니다')
        return v


class EventCreate(EventBase):
    """이벤트 생성 요청 스키마"""
    pass


class EventUpdate(BaseModel):
    """이벤트 수정 요청 스키마"""
    event_name: Optional[str] = Field(None, min_length=1, max_length=100, description="이벤트명")
    event_type: Optional[EventType] = Field(None, description="이벤트 타입")
    description: Optional[str] = Field(None, description="설명")
    terms: Optional[str] = Field(None, description="약관")
    banner_image_url: Optional[str] = Field(None, max_length=500, description="배너 이미지 URL")
    reward_type: Optional[RewardType] = Field(None, description="보상 타입")
    reward_value: Optional[int] = Field(None, ge=0, description="보상 값")
    max_participants: Optional[int] = Field(None, ge=1, description="최대 참여자수")
    is_active: Optional[bool] = Field(None, description="활성화 여부")
    valid_from: Optional[datetime] = Field(None, description="시작일")
    valid_until: Optional[datetime] = Field(None, description="종료일")
    event_metadata: Optional[Dict[str, Any]] = Field(None, description="추가 데이터 (JSON)")
    
    @validator('valid_until')
    def validate_date_range(cls, v, values):
        """종료일이 시작일보다 늦은지 검증"""
        if v is not None and 'valid_from' in values and values['valid_from'] is not None:
            if v <= values['valid_from']:
                raise ValueError('종료일은 시작일보다 늦어야 합니다')
        return v


class EventResponse(EventBase):
    """이벤트 정보 응답 스키마"""
    event_id: int = Field(..., description="이벤트 ID")
    current_participants: int = Field(..., description="현재 참여자수")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    
    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventResponse):
    """이벤트 상세 응답 (이전/다음 이동용 ID 포함)"""
    before_event_id: Optional[int] = Field(None, description="이전 이벤트 ID (없으면 null)")
    after_event_id: Optional[int] = Field(None, description="다음 이벤트 ID (없으면 null)")


class EventListResponse(BaseModel):
    """이벤트 목록 응답 스키마"""
    events: list[EventResponse] = Field(..., description="이벤트 목록")
    total: int = Field(..., description="전체 이벤트 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


# TODO: 추후 필요시 참고용 스키마들
# class EventParticipation(BaseModel):
#     """이벤트 참여 요청 스키마"""
#     event_id: int = Field(..., description="이벤트 ID")
#     user_id: str = Field(..., description="사용자 ID")
#
# class EventParticipationResponse(BaseModel):
#     """이벤트 참여 응답 스키마"""
#     event_id: int = Field(..., description="이벤트 ID")
#     user_id: str = Field(..., description="사용자 ID")
#     participated_at: datetime = Field(..., description="참여 일시")
#     reward_given: bool = Field(..., description="보상 지급 여부")
#
# class EventStatistics(BaseModel):
#     """이벤트 통계 스키마"""
#     event_id: int = Field(..., description="이벤트 ID")
#     total_participants: int = Field(..., description="총 참여자수")
#     participation_rate: float = Field(..., description="참여율")
#     total_reward_given: int = Field(..., description="총 지급된 보상")