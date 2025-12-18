"""
관리자 백엔드 사용자 모델 (t_user)
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Boolean, Integer, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class User(Base):
    """사용자 정보 테이블 (t_user)

    backend의 사용자 모델 스키마와 정합성을 유지하기 위해 확장 필드 포함
    """

    __tablename__ = "t_user"

    # 기본키 및 로그인 정보
    user_id: Mapped[str] = mapped_column(String(100), primary_key=True, comment="사용자 ID (로그인 ID)")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="이메일")
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="비밀번호 해시 (소셜로그인은 NULL)")
    nickname: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="닉네임")
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="전화번호")

    # 가입 정보
    join_type: Mapped[str] = mapped_column(String(20), nullable=False, default="COMMON", comment="가입유형: COMMON|KAKAO|NAVER")
    social_provider: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="소셜 제공자: KAKAO, NAVER")
    social_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="소셜 고유 ID")

    # 사용자 상태
    user_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", comment="상태: ACTIVE, DORMANT, WITHDRAWN")
    grade_code: Mapped[str] = mapped_column(String(20), nullable=False, default="WHITE", comment="등급코드")

    # 프로필 정보
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="프로필 이미지 URL")
    birth_date: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, comment="생년월일시 (YYYY-MM-DD HH:MM 형식)")
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="성별: MALE, FEMALE")
    is_marketing_agreed: Mapped[bool] = mapped_column(Boolean, default=False, comment="마케팅 동의")

    # 보안 관련
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="비밀번호 변경일시")
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, comment="로그인 실패 횟수")
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="계정 잠금 해제 시간")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(KST), comment="생성일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(KST), comment="수정일시")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="마지막 로그인")
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="탈퇴일시")

    __table_args__ = (
        Index("idx_user_status", "user_status"),
        Index("idx_user_grade_code", "grade_code"),
        Index("idx_user_created_at", "created_at"),
        Index("idx_social_provider_id", "social_provider", "social_id"),
        CheckConstraint("user_status IN ('ACTIVE','DORMANT','WITHDRAWN')", name="chk_user_status"),
        CheckConstraint("join_type IN ('COMMON','KAKAO','NAVER')", name="chk_user_join_type"),
        {"comment": "사용자 정보"},
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"


