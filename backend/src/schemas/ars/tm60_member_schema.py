"""
ARS tm60_member 테이블 관련 Pydantic 스키마 (MSSQL 연동)

외부 상담사 시스템의 멤버(상담사) 정보 연동을 위한 읽기 전용 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.ars.tm60_member_model import (
    MemberState, 
    ChatLevel, 
    MemberClass, 
    TurnStatus, 
    CounsellingStatus
)


class Tm60MemberBase(BaseModel):
    """ARS 멤버 기본 스키마"""
    m_s: str = Field(default="", description="구분 코드")
    m_code: str = Field(..., description="멤버 코드")
    m_name: str = Field(..., description="멤버 이름")
    m_nickname: str = Field(..., description="멤버 닉네임")
    m_tel: str = Field(default="", description="전화번호")
    m_tel1: str = Field(default="", description="전화번호1")
    m_tel2: str = Field(default="", description="전화번호2")
    m_mobile: str = Field(default="", description="모바일 번호")
    m_state: str = Field(default="1", description="멤버 상태")
    m_nextstate: str = Field(default="", description="다음 상태")
    m_counselling: str = Field(default="1", description="상담 상태")
    m_id: str = Field(..., description="멤버 ID")
    m_memo: Optional[str] = Field(None, description="메모")
    last_chat: str = Field(default="", description="마지막 채팅 시간")
    chat_level: str = Field(default="1", description="채팅 레벨")
    class_: str = Field(default="0", description="멤버 등급", alias="class")
    turn: str = Field(default="0", description="순번 상태")
    bang: str = Field(default="1", description="방 번호")
    holdoff: str = Field(default="0", description="대기 상태")
    m_bunho: str = Field(default="1", description="번호")
    m_writer: int = Field(default=0, description="작성자")
    m_prate: int = Field(default=100, description="요금 비율")


class Tm60MemberResponse(Tm60MemberBase):
    """ARS 멤버 정보 응답 스키마"""
    idx: int = Field(..., description="멤버 고유 식별자")
    m_fdate: Optional[datetime] = Field(None, description="가입일")
    
    # 추가 속성 (계산된 필드)
    is_active: bool = Field(..., description="활성 상태")
    is_counselling_available: bool = Field(..., description="상담 가능 상태")
    is_on_turn: bool = Field(..., description="순번 활성 상태")
    member_grade: str = Field(..., description="멤버 등급명")
    chat_level_name: str = Field(..., description="채팅 레벨명")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Tm60MemberListResponse(BaseModel):
    """ARS 멤버 목록 응답 스키마"""
    members: list[Tm60MemberResponse] = Field(..., description="멤버 목록")
    total: int = Field(..., description="전체 멤버 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


class Tm60MemberSearch(BaseModel):
    """ARS 멤버 검색 스키마"""
    m_code: Optional[str] = Field(None, description="멤버 코드 검색")
    m_name: Optional[str] = Field(None, description="멤버 이름 검색")
    m_nickname: Optional[str] = Field(None, description="닉네임 검색")
    m_id: Optional[str] = Field(None, description="멤버 ID 검색")
    m_state: Optional[MemberState] = Field(None, description="멤버 상태 필터")
    m_counselling: Optional[CounsellingStatus] = Field(None, description="상담 상태 필터")
    chat_level: Optional[ChatLevel] = Field(None, description="채팅 레벨 필터")
    class_: Optional[MemberClass] = Field(None, description="멤버 등급 필터", alias="class")
    turn: Optional[TurnStatus] = Field(None, description="순번 상태 필터")
    bang: Optional[str] = Field(None, description="방 번호 필터")
    min_prate: Optional[int] = Field(None, description="최소 요금비율")
    max_prate: Optional[int] = Field(None, description="최대 요금비율")
    from_date: Optional[datetime] = Field(None, description="가입일 시작일")
    to_date: Optional[datetime] = Field(None, description="가입일 종료일")
    
    model_config = ConfigDict(populate_by_name=True)


class Tm60MemberStats(BaseModel):
    """ARS 멤버 통계 스키마"""
    total_members: int = Field(..., description="전체 멤버 수")
    active_members: int = Field(..., description="활성 멤버 수")
    counselling_available: int = Field(..., description="상담 가능 멤버 수")
    on_turn_members: int = Field(..., description="순번 활성 멤버 수")
    by_grade: dict[str, int] = Field(..., description="등급별 멤버 수")
    by_chat_level: dict[str, int] = Field(..., description="채팅 레벨별 멤버 수")


class Tm60MemberStateItem(BaseModel):
    """상담사 상태 동기화용 간소화 스키마"""
    m_code: str = Field(..., description="멤버 코드")
    m_state: str = Field(..., description="멤버 상태: 1=대기중, 2=상담중, 3=부재중")