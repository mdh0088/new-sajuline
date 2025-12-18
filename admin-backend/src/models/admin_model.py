"""
관리자(Admin) 모델 정의
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class Admin(Base):
    """관리자 테이블 (t_admin)"""
    __tablename__ = "t_admin"

    admin_id: Mapped[str] = mapped_column(String(100), primary_key=True, comment="관리자 ID")
    login_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="로그인 ID")
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, comment="이메일")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="비밀번호 해시")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="이름")
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="admin", comment="권한")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성 여부")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="마지막 로그인 일시")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(KST), comment="생성 일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(KST), comment="수정 일시")

    def __repr__(self) -> str:
        return f"<Admin(admin_id={self.admin_id}, role={self.role}, active={self.is_active})>"


