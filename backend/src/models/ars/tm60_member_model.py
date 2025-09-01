"""
ARS tm60_member 테이블 모델 (MSSQL 연동)

외부 상담사 시스템의 멤버(상담사) 정보를 읽기 전용으로 연동
레거시 시스템이므로 기존 컬럼명과 타입을 그대로 유지
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, DateTime, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

ARSBase = declarative_base()


class MemberState(str, Enum):
    """멤버 상태"""
    ACTIVE = "1"
    INACTIVE = "0"
    SUSPENDED = "2"


class ChatLevel(str, Enum):
    """채팅 레벨"""
    BASIC = "1"
    ADVANCED = "2"
    EXPERT = "3"


class MemberClass(str, Enum):
    """멤버 등급"""
    NORMAL = "0"
    PREMIUM = "1"
    VIP = "2"


class TurnStatus(str, Enum):
    """순번 상태"""
    WAITING = "0"
    ACTIVE = "1"
    BREAK = "2"


class CounsellingStatus(str, Enum):
    """상담 상태"""
    AVAILABLE = "1"
    BUSY = "0"
    OFFLINE = "2"


class Tm60Member(ARSBase):
    """
    ARS 멤버(상담사) 테이블 (tm60_member) 모델
    
    DDL 기반 (오타 수정):
    - idx: IDENTITY(1,1) 기본키
    - m_s: varchar(8) 
    - m_code: varchar(3) 멤버코드
    - m_name: varchar(20) 이름
    - m_nickname: varchar(20) 닉네임  
    - m_tel, m_tel1, m_tel2: varchar(20) 전화번호들
    - m_mobile: varchar(20) 모바일
    - m_state: char(1) 멤버 상태
    - m_nextstate: varchar(5) 다음 상태
    - m_counselling: char(1) 상담 상태
    - m_id: varchar(50) 멤버 ID
    - m_passwd: varchar(4) 패스워드
    - m_memo: varchar(50) 메모
    - last_chat: char(14) 마지막 채팅
    - chat_level: char(1) 채팅 레벨
    - class: char(1) 등급
    - turn: char(1) 순번
    - bang: char(1) 방번호
    - holdoff: char(1) 대기 상태
    - m_bunho: varchar(10) 번호
    - m_writer: int 작성자
    - m_prate: int 요금비율
    - m_fdate: datetime 가입일
    """
    __tablename__ = "tm60_member"
    
    # 기본 키
    idx: Mapped[int] = mapped_column(
        Integer, 
        Identity(start=1, increment=1), 
        primary_key=True,
        comment="멤버 고유 식별자"
    )
    
    # 기본 정보
    m_s: Mapped[str] = mapped_column(
        String(8), 
        nullable=False, 
        default="",
        comment="구분 코드"
    )
    m_code: Mapped[str] = mapped_column(
        String(3), 
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
    
    # 연락처 정보
    m_tel: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="전화번호"
    )
    m_tel1: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="전화번호1"
    )
    m_tel2: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="전화번호2"
    )
    m_mobile: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="",
        comment="모바일 번호"
    )
    
    # 상태 정보
    m_state: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="멤버 상태: 1=활성, 0=비활성, 2=정지"
    )
    m_nextstate: Mapped[str] = mapped_column(
        String(5), 
        nullable=False, 
        default="",
        comment="다음 상태"
    )
    m_counselling: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="상담 상태: 1=가능, 0=바쁨, 2=오프라인"
    )
    
    # 계정 정보
    m_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="",
        comment="멤버 ID"
    )
    m_passwd: Mapped[str] = mapped_column(
        String(4), 
        nullable=False, 
        default="",
        comment="패스워드"
    )
    m_memo: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="메모"
    )
    
    # 채팅 관련
    last_chat: Mapped[str] = mapped_column(
        CHAR(14), 
        nullable=False, 
        default="",
        comment="마지막 채팅 시간"
    )
    chat_level: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="채팅 레벨: 1=기본, 2=고급, 3=전문"
    )
    
    # 등급 및 상태
    class_: Mapped[str] = mapped_column(
        "class",  # SQL 예약어이므로 컬럼명 명시
        CHAR(1), 
        nullable=False, 
        default="0",
        comment="멤버 등급: 0=일반, 1=프리미엄, 2=VIP"
    )
    turn: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="0",
        comment="순번 상태: 0=대기, 1=활성, 2=휴식"
    )
    bang: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="방 번호"
    )
    holdoff: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="0",
        comment="대기 상태"
    )
    
    # 기타 정보
    m_bunho: Mapped[str] = mapped_column(
        String(10), 
        nullable=False, 
        default="1",
        comment="번호"
    )
    m_writer: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="작성자"
    )
    m_prate: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=100,
        comment="요금 비율"
    )
    
    # 날짜 정보
    m_fdate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="가입일"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_bang', 'bang'),
        Index('idx_chat_level', 'chat_level'),
        Index('idx_m_code', 'm_code'),
        Index('idx_m_counselling', 'm_counselling'),
        Index('idx_m_name', 'm_name'),
        Index('idx_m_nickname', 'm_nickname'),
        Index('idx_m_state', 'm_state'),
        Index('idx_turn', 'turn'),
        Index('idx_m_bunho', 'm_bunho'),
        {'schema': 'dbo', 'comment': 'ARS 멤버(상담사) 정보 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<Tm60Member(idx={self.idx}, m_code='{self.m_code}', m_name='{self.m_name}')>"
    
    @property
    def is_active(self) -> bool:
        """멤버 활성 상태 확인"""
        return self.m_state == MemberState.ACTIVE
    
    @property
    def is_counselling_available(self) -> bool:
        """상담 가능 상태 확인"""
        return self.m_counselling == CounsellingStatus.AVAILABLE
    
    @property
    def is_on_turn(self) -> bool:
        """순번 활성 상태 확인"""
        return self.turn == TurnStatus.ACTIVE
    
    @property
    def member_grade(self) -> str:
        """멤버 등급 반환"""
        grade_map = {
            MemberClass.NORMAL: "일반",
            MemberClass.PREMIUM: "프리미엄", 
            MemberClass.VIP: "VIP"
        }
        return grade_map.get(self.class_, "일반")
    
    @property
    def chat_level_name(self) -> str:
        """채팅 레벨명 반환"""
        level_map = {
            ChatLevel.BASIC: "기본",
            ChatLevel.ADVANCED: "고급",
            ChatLevel.EXPERT: "전문"
        }
        return level_map.get(self.chat_level, "기본")
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "idx": self.idx,
            "m_s": self.m_s,
            "m_code": self.m_code,
            "m_name": self.m_name,
            "m_nickname": self.m_nickname,
            "m_tel": self.m_tel,
            "m_tel1": self.m_tel1,
            "m_tel2": self.m_tel2,
            "m_mobile": self.m_mobile,
            "m_state": self.m_state,
            "m_nextstate": self.m_nextstate,
            "m_counselling": self.m_counselling,
            "m_id": self.m_id,
            "m_memo": self.m_memo,
            "last_chat": self.last_chat,
            "chat_level": self.chat_level,
            "class": self.class_,
            "turn": self.turn,
            "bang": self.bang,
            "holdoff": self.holdoff,
            "m_bunho": self.m_bunho,
            "m_writer": self.m_writer,
            "m_prate": self.m_prate,
            "m_fdate": self.m_fdate.isoformat() if self.m_fdate else None,
            "is_active": self.is_active,
            "is_counselling_available": self.is_counselling_available,
            "is_on_turn": self.is_on_turn,
            "member_grade": self.member_grade,
            "chat_level_name": self.chat_level_name
        }