"""
관리자 백엔드용 ARS tm60_member 최소 모델 (MSSQL)
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


ARSBase = declarative_base()


class Tm60Member(ARSBase):
    __tablename__ = "tm60_member"
    __table_args__ = {"schema": "dbo"}

    m_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    m_state: Mapped[str] = mapped_column(String(1))


