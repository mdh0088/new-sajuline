"""
이벤트 참여 로그 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from src.models.event_model import RewardType


class EventParticipationBase(BaseModel):
    """이벤트 참여 기본 스키마"""
    event_id: int = Field(..., ge=1, description="이벤트 ID")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    participation_data: Optional[Dict[str, Any]] = Field(None, description="참여 데이터 (JSON)")
    reward_type: Optional[str] = Field(None, max_length=50, description="보상 타입")
    reward_value: Optional[int] = Field(None, ge=0, description="보상 값")


class EventParticipationCreate(BaseModel):
    """이벤트 참여 생성 요청 스키마"""
    event_id: int = Field(..., ge=1, description="이벤트 ID")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    participation_data: Optional[Dict[str, Any]] = Field(None, description="참여 데이터 (JSON)")


class EventParticipationUpdate(BaseModel):
    """이벤트 참여 수정 요청 스키마 (보상 지급용)"""
    reward_type: Optional[str] = Field(None, max_length=50, description="보상 타입")
    reward_value: Optional[int] = Field(None, ge=0, description="보상 값")
    participation_data: Optional[Dict[str, Any]] = Field(None, description="참여 데이터 (JSON)")


class EventParticipationResponse(EventParticipationBase):
    """이벤트 참여 정보 응답 스키마"""
    log_id: int = Field(..., description="참여 로그 ID")
    created_at: datetime = Field(..., description="참여 일시")
    
    model_config = ConfigDict(from_attributes=True)


class EventParticipationListResponse(BaseModel):
    """이벤트 참여 목록 응답 스키마"""
    participations: list[EventParticipationResponse] = Field(..., description="참여 목록")
    total: int = Field(..., description="전체 참여 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


class UserEventParticipationResponse(BaseModel):
    """사용자별 이벤트 참여 응답 스키마 (이벤트 정보 포함)"""
    log_id: int = Field(..., description="참여 로그 ID")
    event_id: int = Field(..., description="이벤트 ID")
    event_name: Optional[str] = Field(None, description="이벤트명")
    event_code: Optional[str] = Field(None, description="이벤트 코드")
    participation_data: Optional[Dict[str, Any]] = Field(None, description="참여 데이터")
    reward_type: Optional[str] = Field(None, description="보상 타입")
    reward_value: Optional[int] = Field(None, description="보상 값")
    created_at: datetime = Field(..., description="참여 일시")
    
    model_config = ConfigDict(from_attributes=True)


# TODO: 추후 필요시 참고용 스키마들
# class EventParticipationStatistics(BaseModel):
#     """이벤트 참여 통계 스키마"""
#     event_id: int = Field(..., description="이벤트 ID")
#     total_participants: int = Field(..., description="총 참여자 수")
#     unique_participants: int = Field(..., description="고유 참여자 수")
#     total_rewards_given: int = Field(..., description="총 지급된 보상")
#     participation_rate: float = Field(..., description="참여율")
#
# class BulkParticipationCreate(BaseModel):
#     """대량 참여 생성 요청 스키마"""
#     participations: list[EventParticipationCreate] = Field(..., description="참여 목록")
#
# class RewardProcessingRequest(BaseModel):
#     """보상 처리 요청 스키마"""
#     log_ids: list[int] = Field(..., description="처리할 로그 ID 목록")
#     reward_type: str = Field(..., description="보상 타입")
#     reward_value: int = Field(..., ge=0, description="보상 값")