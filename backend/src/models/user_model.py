"""
사용자 모델 (t_user 테이블)
"""
from datetime import datetime, date
from typing import Optional
from enum import Enum

from sqlalchemy import String, DateTime, Date, Boolean, Integer, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class JoinType(str, Enum):
    """가입 유형"""
    COMMON = "COMMON"
    KAKAO = "KAKAO"
    NAVER = "NAVER"


class UserStatus(str, Enum):
    """사용자 상태"""
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"
    WITHDRAWN = "WITHDRAWN"


class Gender(str, Enum):
    """성별"""
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(Base):
    """사용자 정보 테이블"""
    
    __tablename__ = "t_user"
    
    # 기본키 및 로그인 정보
    user_id: Mapped[str] = mapped_column(
        String(100), 
        primary_key=True, 
        comment="사용자 ID (로그인 ID)"
    )
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="이메일"
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        comment="비밀번호 해시 (소셜로그인은 NULL)"
    )
    nickname: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="닉네임"
    )
    phone: Mapped[str] = mapped_column(
        String(15), 
        unique=True, 
        nullable=False,
        comment="전화번호"
    )
    
    # 가입 정보
    join_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="COMMON",
        comment="가입유형: COMMON, KAKAO, NAVER"
    )
    social_provider: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="소셜 제공자: KAKAO, NAVER"
    )
    social_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        comment="소셜 고유 ID"
    )
    
    # 사용자 상태
    user_status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="ACTIVE",
        comment="상태: ACTIVE, DORMANT, WITHDRAWN"
    )
    grade_code: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="WHITE",
        comment="등급코드"
    )
    
    # 프로필 정보
    profile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True,
        comment="프로필 이미지 URL"
    )
    birth_date: Mapped[Optional[str]] = mapped_column(
        String(30), 
        nullable=True,
        comment="생년월일시 (YYYY-MM-DD HH:MM 형식)"
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="성별: MALE, FEMALE"
    )
    mileage_point: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="마일리지 포인트"
    )
    is_marketing_agreed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="마케팅 동의"
    )
    
    # 보안 관련
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="비밀번호 변경일시"
    )
    failed_login_count: Mapped[int] = mapped_column(
        Integer, 
        default=0,
        comment="로그인 실패 횟수"
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="계정 잠금 해제 시간"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        default=datetime.utcnow,
        comment="생성일시"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        onupdate=datetime.utcnow,
        comment="수정일시"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="마지막 로그인"
    )
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        comment="탈퇴일시"
    )
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_user_status', 'user_status'),
        Index('idx_grade_code', 'grade_code'),
        Index('idx_created_at', 'created_at'),
        Index('idx_social_provider_id', 'social_provider', 'social_id'),
        CheckConstraint(
            "user_status IN ('ACTIVE','DORMANT','WITHDRAWN')",
            name='chk_user_status'
        ),
        CheckConstraint(
            "join_type IN ('COMMON','KAKAO','NAVER')",
            name='chk_join_type'
        ),
        {'comment': '사용자 정보'}
    )
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"


class UserOut(Base):
    """회원 탈퇴 유저 테이블"""

    __tablename__ = "t_user_out"

    # 기본키
    out_idx: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="탈퇴 고유 식별자"
    )

    # 탈퇴 유저 정보
    user_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="탈퇴한 사용자 ID"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="탈퇴한 사용자 닉네임"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(15),
        nullable=True,
        comment="탈퇴한 사용자 전화번호"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="탈퇴한 사용자 이메일"
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="탈퇴 일시"
    )

    # 인덱스 정의
    __table_args__ = (
        Index('idx_user_out_user_id', 'user_id'),
        Index('idx_user_out_phone', 'phone'),
        Index('idx_user_out_created_at', 'created_at'),
        {'comment': '회원 탈퇴 유저'}
    )

    def __repr__(self) -> str:
        return f"<UserOut(out_idx={self.out_idx}, user_id={self.user_id})>"