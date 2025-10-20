"""
상담사 지원(Counselor Application) 모델 정의
사용자 제공 DDL 기반 정확히 매핑
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class CounselorApplication(Base):
    """상담사 신청 정보 테이블"""
    __tablename__ = "t_counselor_application"

    application_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="실명"
    )
    nickname: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="희망 활동명"
    )
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="이메일"
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="전화번호"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="주소"
    )

    specialty_types: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='신청 분야 JSON'
    )
    keywords: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="키워드"
    )
    introduction: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="자기소개"
    )

    upload_image1: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    upload_image2: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    upload_image3: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    application_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        comment="상태"
    )
    admin_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="관리자 메모"
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="검토한 관리자"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="검토일시"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=func.current_timestamp()
    )

    __table_args__ = (
        {'comment': '상담사 신청 정보'}
    )
