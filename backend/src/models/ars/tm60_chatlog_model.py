"""
ARS tm60_chatlog 테이블 모델 (MSSQL 연동)

외부 상담사 시스템의 채팅 로그 정보를 읽기 전용으로 연동
레거시 시스템이므로 기존 컬럼명과 타입을 그대로 유지
"""
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, Float, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

ARSBase = declarative_base()


class PlatformType(str, Enum):
    """플랫폼 타입"""
    WEB = "0"
    MOBILE = "1"
    APP = "2"


class SuccessStatus(int, Enum):
    """성공 상태"""
    FAILED = 0
    SUCCESS = 1
    PARTIAL = 2


class ServiceCode(str, Enum):
    """서비스 코드"""
    NORMAL = "1"
    PREMIUM = "2"
    EVENT = "3"


class Tm60Chatlog(ARSBase):
    """
    ARS 채팅 로그 테이블 (tm60_chatlog) 모델
    
    DDL 기반 (오타 수정):
    - idx: IDENTITY(1,1) 기본키
    - fdnis: varchar(8) DNIS 정보
    - m_code: char(3) 멤버 코드
    - m_name: varchar(20) 멤버 이름
    - m_nickname: varchar(20) 멤버 닉네임
    - starttm: varchar(19) 시작 시간
    - endtm: varchar(19) 종료 시간  
    - chatstart: varchar(19) 채팅 시작
    - chatend: varchar(19) 채팅 종료
    - u_tel: varchar(15) 사용자 전화번호
    - t_tel: varchar(15) 상담사 전화번호
    - yyyy: char(4) 연도
    - mm: char(2) 월
    - dd: char(2) 일
    - hh: char(2) 시간
    - fname: varchar(17) 파일명
    - scode: char(1) 서비스 코드
    - platform: char(1) 플랫폼
    - u_id: varchar(50) 사용자 ID
    - chattm: int 채팅 시간
    - realchattm: int 실제 채팅 시간
    - usepoint: int 사용 포인트
    - fee: int 수수료
    - money: int 금액
    - t2_money: real T2 금액
    - success: int 성공 여부
    - u_chk: int 사용자 체크
    - menu: int 메뉴
    - call_span: int 통화 간격
    - calltm: int 통화 시간
    - unit_use: int 단위 사용
    - unit_sec: int 단위 초
    - unit_fee: real 단위 수수료
    - prate: int 요율
    - call_name: varchar(70) 통화자명
    """
    __tablename__ = "tm60_chatlog"
    
    # 기본 키
    idx: Mapped[int] = mapped_column(
        Integer, 
        Identity(start=1, increment=1), 
        primary_key=True,
        comment="채팅로그 고유 식별자"
    )
    
    # DNIS 및 멤버 정보
    fdnis: Mapped[str] = mapped_column(
        String(8), 
        nullable=False, 
        default="",
        comment="DNIS 정보"
    )
    m_code: Mapped[str] = mapped_column(
        CHAR(3), 
        nullable=False, 
        default="",
        comment="멤버 코드"
    )
    m_name: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="멤버 이름"
    )
    m_nickname: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="멤버 닉네임"
    )
    
    # 시간 정보
    starttm: Mapped[Optional[str]] = mapped_column(
        String(19), 
        nullable=True,
        default="",
        comment="시작 시간"
    )
    endtm: Mapped[Optional[str]] = mapped_column(
        String(19), 
        nullable=True,
        default="",
        comment="종료 시간"
    )
    chatstart: Mapped[Optional[str]] = mapped_column(
        String(19), 
        nullable=True,
        default="",
        comment="채팅 시작 시간"
    )
    chatend: Mapped[Optional[str]] = mapped_column(
        String(19), 
        nullable=True,
        default="",
        comment="채팅 종료 시간"
    )
    
    # 연락처 정보
    u_tel: Mapped[str] = mapped_column(
        String(15), 
        nullable=False, 
        default="",
        comment="사용자 전화번호"
    )
    t_tel: Mapped[str] = mapped_column(
        String(15), 
        nullable=False, 
        default="",
        comment="상담사 전화번호"
    )
    
    # 날짜 분리 필드
    yyyy: Mapped[str] = mapped_column(
        CHAR(4), 
        nullable=False, 
        default="",
        comment="연도"
    )
    mm: Mapped[str] = mapped_column(
        CHAR(2), 
        nullable=False, 
        default="",
        comment="월"
    )
    dd: Mapped[str] = mapped_column(
        CHAR(2), 
        nullable=False, 
        default="",
        comment="일"
    )
    hh: Mapped[str] = mapped_column(
        CHAR(2), 
        nullable=False, 
        default="",
        comment="시간"
    )
    
    # 파일 및 서비스 정보
    fname: Mapped[str] = mapped_column(
        String(17), 
        nullable=False, 
        default="",
        comment="파일명"
    )
    scode: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="서비스 코드: 1=일반, 2=프리미엄, 3=이벤트"
    )
    platform: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="0",
        comment="플랫폼: 0=웹, 1=모바일, 2=앱"
    )
    
    # 사용자 정보
    u_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="",
        comment="사용자 ID"
    )
    
    # 시간 및 포인트 정보
    chattm: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="채팅 시간(초)"
    )
    realchattm: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="실제 채팅 시간(초)"
    )
    usepoint: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="사용 포인트"
    )
    
    # 금액 정보
    fee: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="수수료"
    )
    t_money: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="상담사 수익"
    )
    t2_money: Mapped[float] = mapped_column(
        Float, 
        nullable=False, 
        default=0.0,
        comment="추가 수익"
    )
    
    # 상태 정보
    success: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="성공 여부: 0=실패, 1=성공, 2=부분성공"
    )
    u_chk: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="사용자 체크"
    )
    menu: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="메뉴 번호"
    )
    
    # 통화 관련 정보
    call_span: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="통화 간격"
    )
    calltm: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="통화 시간(초)"
    )
    
    # 단위 정보
    unit_use: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="단위 사용량"
    )
    unit_sec: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="단위 초"
    )
    unit_fee: Mapped[float] = mapped_column(
        Float, 
        nullable=False, 
        default=0.0,
        comment="단위 수수료"
    )
    prate: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="요율"
    )
    
    # 통화자 정보
    call_name: Mapped[str] = mapped_column(
        String(70), 
        nullable=False, 
        default="",
        comment="통화자명"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_dd', 'dd'),
        Index('idx_endtm', 'endtm'),
        Index('idx_fdnis', 'fdnis'),
        Index('idx_hh', 'hh'),
        Index('idx_m_code', 'm_code'),
        Index('idx_m_nickname', 'm_nickname'),
        Index('idx_mm', 'mm'),
        Index('idx_platform', 'platform'),
        Index('idx_scode', 'scode'),
        Index('idx_starttm', 'starttm'),
        Index('idx_success', 'success'),
        Index('idx_u_id', 'u_id'),
        Index('idx_yyyy', 'yyyy'),
        {'schema': 'dbo', 'comment': 'ARS 채팅 로그 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<Tm60Chatlog(idx={self.idx}, m_code='{self.m_code}', u_id='{self.u_id}')>"
    
    @property
    def is_successful(self) -> bool:
        """성공 상태 확인"""
        return self.success == SuccessStatus.SUCCESS
    
    @property
    def platform_name(self) -> str:
        """플랫폼명 반환"""
        platform_map = {
            PlatformType.WEB: "웹",
            PlatformType.MOBILE: "모바일",
            PlatformType.APP: "앱"
        }
        return platform_map.get(self.platform, "알 수 없음")
    
    @property
    def service_name(self) -> str:
        """서비스명 반환"""
        service_map = {
            ServiceCode.NORMAL: "일반",
            ServiceCode.PREMIUM: "프리미엄",
            ServiceCode.EVENT: "이벤트"
        }
        return service_map.get(self.scode, "일반")
    
    @property
    def date_string(self) -> str:
        """날짜 문자열 반환"""
        return f"{self.yyyy}-{self.mm}-{self.dd}"
    
    @property
    def datetime_string(self) -> str:
        """날짜시간 문자열 반환"""
        return f"{self.yyyy}-{self.mm}-{self.dd} {self.hh}:00:00"
    
    @property
    def chat_duration_minutes(self) -> float:
        """채팅 시간(분) 반환"""
        return round(self.chattm / 60, 2) if self.chattm > 0 else 0.0
    
    @property
    def real_chat_duration_minutes(self) -> float:
        """실제 채팅 시간(분) 반환"""
        return round(self.realchattm / 60, 2) if self.realchattm > 0 else 0.0
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "idx": self.idx,
            "fdnis": self.fdnis,
            "m_code": self.m_code,
            "m_name": self.m_name,
            "m_nickname": self.m_nickname,
            "starttm": self.starttm,
            "endtm": self.endtm,
            "chatstart": self.chatstart,
            "chatend": self.chatend,
            "u_tel": self.u_tel,
            "t_tel": self.t_tel,
            "yyyy": self.yyyy,
            "mm": self.mm,
            "dd": self.dd,
            "hh": self.hh,
            "fname": self.fname,
            "scode": self.scode,
            "platform": self.platform,
            "u_id": self.u_id,
            "chattm": self.chattm,
            "realchattm": self.realchattm,
            "usepoint": self.usepoint,
            "fee": self.fee,
            "t_money": self.t_money,
            "t2_money": self.t2_money,
            "success": self.success,
            "u_chk": self.u_chk,
            "menu": self.menu,
            "call_span": self.call_span,
            "calltm": self.calltm,
            "unit_use": self.unit_use,
            "unit_sec": self.unit_sec,
            "unit_fee": self.unit_fee,
            "prate": self.prate,
            "call_name": self.call_name,
            "is_successful": self.is_successful,
            "platform_name": self.platform_name,
            "service_name": self.service_name,
            "date_string": self.date_string,
            "datetime_string": self.datetime_string,
            "chat_duration_minutes": self.chat_duration_minutes,
            "real_chat_duration_minutes": self.real_chat_duration_minutes
        }