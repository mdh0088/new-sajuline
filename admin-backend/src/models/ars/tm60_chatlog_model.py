"""
ARS tm60_chatlog 테이블 모델 (MSSQL 연동)
"""
from typing import Optional

from sqlalchemy import String, Integer, Float, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

ARSBase = declarative_base()


class Tm60Chatlog(ARSBase):
    """채팅 로그 테이블"""
    __tablename__ = "tm60_chatlog"

    idx: Mapped[int] = mapped_column(
        Integer, Identity(start=1, increment=1), primary_key=True
    )

    # 상담사 정보
    fdnis: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    m_code: Mapped[str] = mapped_column(String(3), nullable=False, default="")
    m_name: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    m_nickname: Mapped[str] = mapped_column(String(20), nullable=False, default="")

    # 시간 정보
    starttm: Mapped[Optional[str]] = mapped_column(
        String(19), nullable=True, default=""
    )
    endtm: Mapped[Optional[str]] = mapped_column(
        String(19), nullable=True, default=""
    )
    chatstart: Mapped[Optional[str]] = mapped_column(
        String(19), nullable=True, default=""
    )
    chatend: Mapped[Optional[str]] = mapped_column(
        String(19), nullable=True, default=""
    )

    # 전화번호
    u_tel: Mapped[str] = mapped_column(String(15), nullable=False, default="")
    t_tel: Mapped[str] = mapped_column(String(15), nullable=False, default="")

    # 날짜/시간 분리 필드
    yyyy: Mapped[str] = mapped_column(CHAR(4), nullable=False, default="")
    mm: Mapped[str] = mapped_column(CHAR(2), nullable=False, default="")
    dd: Mapped[str] = mapped_column(CHAR(2), nullable=False, default="")
    hh: Mapped[str] = mapped_column(CHAR(2), nullable=False, default="")

    # 파일 및 상태
    fname: Mapped[str] = mapped_column(String(17), nullable=False, default="")
    scode: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")
    platform: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="0")

    # 사용자 정보
    u_id: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    u_name: Mapped[str] = mapped_column(String(70), nullable=False, default="")

    # 채팅 시간
    chattm: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    realchattm: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 요금 정보
    usepoint: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    t_money: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    t2_money: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # 상태 플래그
    success: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    call_chk: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    menu: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 통화 정보
    call_span: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calltm: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 단위 요금
    unit_use: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    prate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_dd", "dd"),
        Index("idx_endtm", "endtm"),
        Index("idx_fdnis", "fdnis"),
        Index("idx_hh", "hh"),
        Index("idx_m_code", "m_code"),
        Index("idx_m_nickname", "m_nickname"),
        Index("idx_mm", "mm"),
        Index("idx_platform", "platform"),
        Index("idx_scode", "scode"),
        Index("idx_starttm", "starttm"),
        Index("idx_success", "success"),
        Index("idx_u_id", "u_id"),
        Index("idx_yyyy", "yyyy"),
        {"schema": "dbo", "comment": "채팅 로그"},
    )
