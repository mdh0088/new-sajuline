"""
ARS tm60_chatlog 테이블 관련 Pydantic 스키마 (MSSQL 연동)

외부 상담사 시스템의 채팅 로그 정보 연동을 위한 읽기 전용 스키마
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime

from src.models.ars.tm60_chatlog_model import (
    PlatformType, 
    SuccessStatus, 
    ServiceCode
)


class Tm60ChatlogBase(BaseModel):
    """ARS 채팅로그 기본 스키마"""
    fdnis: str = Field(default="", description="DNIS 정보")
    m_code: str = Field(..., description="멤버 코드")
    m_name: str = Field(..., description="멤버 이름")
    m_nickname: str = Field(..., description="멤버 닉네임")
    starttm: Optional[str] = Field(None, description="시작 시간")
    endtm: Optional[str] = Field(None, description="종료 시간")
    chatstart: Optional[str] = Field(None, description="채팅 시작 시간")
    chatend: Optional[str] = Field(None, description="채팅 종료 시간")
    u_tel: str = Field(default="", description="사용자 전화번호")
    t_tel: str = Field(default="", description="상담사 전화번호")
    yyyy: str = Field(..., description="연도")
    mm: str = Field(..., description="월")
    dd: str = Field(..., description="일")
    hh: str = Field(..., description="시간")
    fname: str = Field(default="", description="파일명")
    scode: str = Field(default="1", description="서비스 코드")
    platform: str = Field(default="0", description="플랫폼")
    u_id: str = Field(..., description="사용자 ID")
    chattm: int = Field(default=0, description="채팅 시간(초)")
    realchattm: int = Field(default=0, description="실제 채팅 시간(초)")
    usepoint: int = Field(default=0, description="사용 포인트")
    fee: int = Field(default=0, description="수수료")
    t_money: int = Field(default=0, description="상담사 수익")
    t2_money: float = Field(default=0.0, description="추가 수익")
    success: int = Field(default=0, description="성공 여부")
    u_chk: Optional[int] = Field(None, description="사용자 체크")
    menu: int = Field(default=0, description="메뉴 번호")
    call_span: int = Field(default=0, description="통화 간격")
    calltm: int = Field(default=0, description="통화 시간(초)")
    unit_use: int = Field(default=0, description="단위 사용량")
    unit_sec: int = Field(default=0, description="단위 초")
    unit_fee: float = Field(default=0.0, description="단위 수수료")
    prate: int = Field(default=0, description="요율")
    call_name: str = Field(default="", description="통화자명")


class Tm60ChatlogResponse(Tm60ChatlogBase):
    """ARS 채팅로그 정보 응답 스키마"""
    idx: int = Field(..., description="채팅로그 고유 식별자")
    
    # 추가 속성 (계산된 필드)
    is_successful: bool = Field(..., description="성공 상태")
    platform_name: str = Field(..., description="플랫폼명")
    service_name: str = Field(..., description="서비스명")
    date_string: str = Field(..., description="날짜 문자열 (YYYY-MM-DD)")
    datetime_string: str = Field(..., description="날짜시간 문자열")
    chat_duration_minutes: float = Field(..., description="채팅 시간(분)")
    real_chat_duration_minutes: float = Field(..., description="실제 채팅 시간(분)")
    
    model_config = ConfigDict(from_attributes=True)


class Tm60ChatlogListResponse(BaseModel):
    """ARS 채팅로그 목록 응답 스키마"""
    chatlogs: list[Tm60ChatlogResponse] = Field(..., description="채팅로그 목록")
    total: int = Field(..., description="전체 채팅로그 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


class Tm60ChatlogSearch(BaseModel):
    """ARS 채팅로그 검색 스키마"""
    m_code: Optional[str] = Field(None, description="멤버 코드 검색")
    m_name: Optional[str] = Field(None, description="멤버 이름 검색")
    m_nickname: Optional[str] = Field(None, description="멤버 닉네임 검색")
    u_id: Optional[str] = Field(None, description="사용자 ID 검색")
    u_tel: Optional[str] = Field(None, description="사용자 전화번호 검색")
    platform: Optional[PlatformType] = Field(None, description="플랫폼 필터")
    scode: Optional[ServiceCode] = Field(None, description="서비스 코드 필터")
    success: Optional[SuccessStatus] = Field(None, description="성공 상태 필터")
    yyyy: Optional[str] = Field(None, description="연도 필터")
    mm: Optional[str] = Field(None, description="월 필터")
    dd: Optional[str] = Field(None, description="일 필터")
    hh: Optional[str] = Field(None, description="시간 필터")
    from_date: Optional[date] = Field(None, description="검색 시작일")
    to_date: Optional[date] = Field(None, description="검색 종료일")
    min_usepoint: Optional[int] = Field(None, description="최소 사용 포인트")
    max_usepoint: Optional[int] = Field(None, description="최대 사용 포인트")
    min_chattm: Optional[int] = Field(None, description="최소 채팅 시간(초)")
    max_chattm: Optional[int] = Field(None, description="최대 채팅 시간(초)")


class Tm60ChatlogStats(BaseModel):
    """ARS 채팅로그 통계 스키마"""
    total_chatlogs: int = Field(..., description="전체 채팅로그 수")
    successful_chatlogs: int = Field(..., description="성공한 채팅로그 수")
    success_rate: float = Field(..., description="성공률(%)")
    total_chat_time: int = Field(..., description="총 채팅 시간(초)")
    total_points_used: int = Field(..., description="총 사용 포인트")
    total_revenue: int = Field(..., description="총 수익")
    avg_chat_duration: float = Field(..., description="평균 채팅 시간(분)")
    by_platform: dict[str, int] = Field(..., description="플랫폼별 채팅 수")
    by_service: dict[str, int] = Field(..., description="서비스별 채팅 수")
    by_hour: dict[str, int] = Field(..., description="시간대별 채팅 수")
    by_date: dict[str, int] = Field(..., description="날짜별 채팅 수")


class Tm60ChatlogDaily(BaseModel):
    """ARS 일별 채팅로그 통계 스키마"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    total_count: int = Field(..., description="총 채팅 수")
    success_count: int = Field(..., description="성공 채팅 수")
    success_rate: float = Field(..., description="성공률(%)")
    total_chat_time: int = Field(..., description="총 채팅 시간(초)")
    total_points: int = Field(..., description="총 사용 포인트")
    total_revenue: int = Field(..., description="총 수익")
    avg_duration: float = Field(..., description="평균 채팅 시간(분)")
    unique_users: int = Field(..., description="고유 사용자 수")
    unique_counselors: int = Field(..., description="고유 상담사 수")


class Tm60ChatlogSummary(BaseModel):
    """ARS 채팅로그 요약 스키마"""
    period: str = Field(..., description="조회 기간")
    total_sessions: int = Field(..., description="총 세션 수")
    successful_sessions: int = Field(..., description="성공 세션 수")
    success_rate: float = Field(..., description="성공률(%)")
    total_duration_hours: float = Field(..., description="총 채팅 시간(시간)")
    avg_session_duration: float = Field(..., description="평균 세션 시간(분)")
    total_points_consumed: int = Field(..., description="총 포인트 소비")
    total_revenue: int = Field(..., description="총 수익")
    peak_hour: str = Field(..., description="최대 이용 시간대")
    top_platform: str = Field(..., description="최다 이용 플랫폼")
    most_active_counselor: str = Field(..., description="최다 상담 상담사")
    daily_average: float = Field(..., description="일평균 세션 수")