"""
상담사(Counselor) 모델 (관리자 백엔드 조회/인증 용 최소 필드)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Counselor(Base):
    """상담사 테이블 (t_counselor)"""
    __tablename__ = "t_counselor"

    counselor_id: Mapped[str] = mapped_column(String(100), primary_key=True, comment="상담사 ID(이메일)")
    counselor_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="상담사 코드")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="실명")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="비밀번호 해시")
    nickname: Mapped[str] = mapped_column(String(100), nullable=False, comment="닉네임")
    is_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="탈퇴 여부")
    is_show: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="노출 여부")
    specialty_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="전문 분야(JSON 문자열)")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="승인일시")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="마지막 로그인 일시")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, comment="생성 일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="수정 일시")

    def __repr__(self) -> str:
        return f"<Counselor(counselor_id={self.counselor_id}, nickname={self.nickname})>"


