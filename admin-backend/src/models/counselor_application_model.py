"""
상담사 신청(Counselor Application) 모델 정의 (관리자 백엔드)
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Integer, Text, CheckConstraint, Index
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class ApplicationStatus(str, Enum):
    """신청 상태"""
    PENDING = "PENDING"    # 대기중
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거절됨


class CounselorApplication(Base):
    """상담사 신청 테이블 (t_counselor_application)"""
    __tablename__ = "t_counselor_application"

    # 기본키
    application_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="신청 ID")

    # 개인 정보
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="실명")
    nickname: Mapped[str] = mapped_column(String(100), nullable=False, comment="희망 활동명")
    email: Mapped[str] = mapped_column(String(100), nullable=False, comment="이메일")
    phone: Mapped[str] = mapped_column(String(50), nullable=False, comment="전화번호")
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="주소")

    # 전문 분야 및 소개
    specialty_types: Mapped[Optional[str]] = mapped_column(
        LONGTEXT,
        nullable=True,
        comment='신청 분야 (JSON 배열 형식 예: ["TARO","SAJU","FORTUNE","EASY"])'
    )
    keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="키워드")
    introduction: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="자기소개")

    # 이미지 관련
    selected_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="선택된 이미지")
    upload_image1: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="업로드 이미지 1")
    upload_image2: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="업로드 이미지 2")
    upload_image3: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="업로드 이미지 3")

    # 신청 상태 및 관리자 검토
    application_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        comment="상태: PENDING, APPROVED, REJECTED"
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="관리자 메모")
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="검토한 관리자 ID")
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="검토일시")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        comment="생성 일시"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=lambda: datetime.now(KST),
        comment="수정 일시"
    )

    __table_args__ = (
        Index("idx_application_status", "application_status"),
        Index("idx_created_at", "created_at"),
        CheckConstraint(
            "application_status IN ('PENDING','APPROVED','REJECTED')",
            name="chk_application_status"
        ),
        {"comment": "상담사 신청 정보"},
    )

    def __repr__(self) -> str:
        return (
            f"<CounselorApplication("
            f"application_id={self.application_id}, "
            f"name={self.name}, "
            f"email={self.email}, "
            f"status={self.application_status})>"
        )
