"""
ARS tm60_users 테이블 모델 (관리자 백엔드 / MSSQL 연동)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, CHAR, Identity, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column


ARSBase = declarative_base()


class Tm60Users(ARSBase):
    __tablename__ = "tm60_users"
    __table_args__ = (
        Index("idx_u_id", "u_id"),
        Index("idx_u_tel", "u_tel"),
        {"schema": "dbo", "comment": "ARS 사용자 정보"},
    )

    idx: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    u_id: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    u_tel: Mapped[str] = mapped_column(String(18), nullable=False, default="")
    u_passwd: Mapped[str] = mapped_column(CHAR(4), nullable=False, default="")
    u_kname: Mapped[str] = mapped_column(String(12), nullable=False, default="")
    u_memcd: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")
    u_login: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="1")
    u_state: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="0")
    u_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    u_fdate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    u_rdate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    regdate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    u_memo: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    def to_dict(self) -> dict:
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
        }










