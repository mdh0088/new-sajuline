"""
ARS tm60_users 테이블 모델 (MSSQL 연동)

외부 상담사 시스템의 사용자 정보를 읽기 전용으로 연동
레거시 시스템이므로 기존 컬럼명과 타입을 그대로 유지
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, DateTime, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

ARSBase = declarative_base()


class UserMemCode(str, Enum):
    """회원 구분 코드"""
    NORMAL = "1"
    SPECIAL = "2"


class UserLoginStatus(str, Enum):
    """로그인 상태"""
    ACTIVE = "1"
    INACTIVE = "0"


class UserState(str, Enum):
    """사용자 상태"""
    NORMAL = "0"
    BLOCKED = "1"
    WITHDRAWN = "2"


class Tm60Users(ARSBase):
    """
    ARS 사용자 테이블 (tm60_users) 모델
    
    DDL 기반:
    - idx: IDENTITY(1,1) 기본키
    - u_id: varchar(50) 사용자 ID
    - u_tel: varchar(18) 전화번호 (인덱스)
    - u_passwd: char(4) 패스워드
    - u_kname: varchar(12) 한글이름
    - u_memcd: char(1) 회원구분 (기본값: '1')
    - u_login: char(1) 로그인상태 (기본값: '1') 
    - u_state: char(1) 사용자상태 (기본값: '0')
    - u_point: int 포인트 (기본값: 0)
    - u_fdate, u_rdate, regdate: datetime
    - u_memo: varchar(255) 메모
    """
    __tablename__ = "tm60_users"
    
    # 기본 키
    idx: Mapped[int] = mapped_column(
        Integer, 
        Identity(start=1, increment=1), 
        primary_key=True,
        comment="사용자 고유 식별자"
    )
    
    # 사용자 기본 정보
    u_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="",
        comment="사용자 ID"
    )
    u_tel: Mapped[str] = mapped_column(
        String(18), 
        nullable=False, 
        default="",
        comment="사용자 전화번호"
    )
    u_passwd: Mapped[str] = mapped_column(
        CHAR(4), 
        nullable=False, 
        default="",
        comment="사용자 패스워드 (4자리)"
    )
    u_kname: Mapped[str] = mapped_column(
        String(12), 
        nullable=False, 
        default="",
        comment="사용자 한글 이름"
    )
    
    # 사용자 상태 정보
    u_memcd: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="회원 구분 코드: 1=일반, 2=특별"
    )
    u_login: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="1",
        comment="로그인 상태: 1=활성, 0=비활성"
    )
    u_state: Mapped[str] = mapped_column(
        CHAR(1), 
        nullable=False, 
        default="0",
        comment="사용자 상태: 0=정상, 1=차단, 2=탈퇴"
    )
    
    # 포인트 정보
    u_point: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="사용자 포인트"
    )
    
    # 날짜 정보
    u_fdate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="최초 가입일"
    )
    u_rdate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="최근 수정일"
    )
    regdate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="등록일"
    )
    
    # 메모
    u_memo: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        default="",
        comment="사용자 메모"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_id', 'u_id'),
        Index('idx_tel', 'u_tel'),
        {'schema': 'dbo', 'comment': 'ARS 사용자 정보 테이블'}
    )
    
    def __repr__(self) -> str:
        return f"<Tm60Users(idx={self.idx}, u_id='{self.u_id}', u_tel='{self.u_tel}')>"
    
    @property
    def is_active(self) -> bool:
        """사용자 활성 상태 확인"""
        return self.u_state == UserState.NORMAL
    
    @property
    def is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        return self.u_login == UserLoginStatus.ACTIVE
    
    @property
    def member_type(self) -> str:
        """회원 유형 반환"""
        return "특별회원" if self.u_memcd == UserMemCode.SPECIAL else "일반회원"
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "idx": self.idx,
            "u_id": self.u_id,
            "u_tel": self.u_tel,
            "u_kname": self.u_kname,
            "u_memcd": self.u_memcd,
            "u_login": self.u_login,
            "u_state": self.u_state,
            "u_point": self.u_point,
            "u_fdate": self.u_fdate.isoformat() if self.u_fdate else None,
            "u_rdate": self.u_rdate.isoformat() if self.u_rdate else None,
            "regdate": self.regdate.isoformat() if self.regdate else None,
            "u_memo": self.u_memo,
            "is_active": self.is_active,
            "is_logged_in": self.is_logged_in,
            "member_type": self.member_type
        }