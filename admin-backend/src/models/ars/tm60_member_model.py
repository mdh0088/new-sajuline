"""
ARS tm60_member 테이블 모델 (MSSQL 연동)
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, DateTime, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

ARSBase = declarative_base()


class MemberState(str, Enum):
    ACTIVE = "1"
    INACTIVE = "0"
    SUSPENDED = "2"


class ChatLevel(str, Enum):
    BASIC = "1"
    ADVANCED = "2"
    EXPERT = "3"


class MemberClass(str, Enum):
    NORMAL = "0"
    PREMIUM = "1"
    VIP = "2"


class TurnStatus(str, Enum):
    WAITING = "0"
    ACTIVE = "1"
    BREAK = "2"


class CounsellingStatus(str, Enum):
    AVAILABLE = "1"
    BUSY = "0"
    OFFLINE = "2"


class Tm60Member(ARSBase):
    __tablename__ = "tm60_member"

    idx: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)

    m_dnis: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    m_code: Mapped[str] = mapped_column(String(3), nullable=False, default="")
    m_name: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    m_nickname: Mapped[str] = mapped_column(String(20), nullable=False, default="")

    m_tel: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    m_tel1: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    m_tel2: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    m_mobile: Mapped[str] = mapped_column(String(20), nullable=False, default="")

    m_state: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")
    m_nextstate: Mapped[str] = mapped_column(String(5), nullable=False, default="")
    m_counselling: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")

    m_id: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    m_passwd: Mapped[str] = mapped_column(String(4), nullable=False, default="")
    m_memo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")

    last_chat: Mapped[str] = mapped_column(CHAR(14), nullable=False, default="")
    chat_level: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")

    class_: Mapped[str] = mapped_column("class", CHAR(1), nullable=False, default="0")
    turn: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="0")
    bang: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")
    holdoff: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="0")

    m_bunho: Mapped[str] = mapped_column(String(10), nullable=False, default="1")
    m_writer: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    m_prate: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    m_fdate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_bang', 'bang'),
        Index('idx_chat_level', 'chat_level'),
        Index('idx_dnis', 'm_dnis'),
        Index('idx_m_code', 'm_code'),
        Index('idx_m_counselling', 'm_counselling'),
        Index('idx_m_name', 'm_name'),
        Index('idx_m_nickname', 'm_nickname'),
        Index('idx_m_state', 'm_state'),
        Index('idx_turn', 'turn'),
        Index('idx_m_bunho', 'm_bunho'),
        {'schema': 'dbo'}
    )


