"""
상담사(Counselor) 모델 정의
"""
from enum import Enum
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, DateTime, Date, Boolean, Integer, Text, DECIMAL, CheckConstraint, Index, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CounselorStatus(str, Enum):
    """상담사 상태"""
    WAITING = "WAITING"      # 대기 중
    CONSULTING = "CONSULTING"  # 상담 중
    ABSENT = "ABSENT"        # 자리 비움


class CounselorGrade(str, Enum):
    """상담사 등급"""
    BRONZE = "BRONZE"  # 브론즈
    SILVER = "SILVER"  # 실버  
    GOLD = "GOLD"      # 골드


class Counselor(Base):
    """상담사 테이블"""
    __tablename__ = "t_counselor"
    
    # 기본키 및 로그인 정보
    counselor_id: Mapped[str] = mapped_column(
        String(100), 
        primary_key=True, 
        comment="상담사 ID (로그인 ID = 이메일)"
    )
    counselor_code: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        comment="상담사 고유 코드"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        comment="비밀번호 해시"
    )
    
    # 개인 정보
    name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        comment="실명"
    )
    nickname: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False, 
        comment="활동명"
    )
    phone: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        comment="전화번호"
    )
    profile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True, 
        comment="프로필 이미지"
    )
    introduction_short: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="짧은 소개"
    )
    greeting_message: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="인사말"
    )
    career_info: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="경력사항"
    )
    
    # 상담 관련 정보
    counselor_status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="WAITING", 
        comment="상태: WAITING, CONSULTING, ABSENT"
    )
    grade: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True, 
        default="BRONZE", 
        comment="등급: BRONZE, SILVER, GOLD"
    )
    
    # 전문 분야 
    specialty_types: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="전문 분야 (JSON 배열 형식 예: [\"TARO\",\"SAJU\"])"
    )
    # 키워드
    keywords: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="키워드"
    )
    # 업무 시간
    work_time: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="업무 시간"
    )
    
    # 평가 및 통계
    rating_avg: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(3, 2), 
        nullable=True, 
        default=Decimal('0.00'), 
        comment="평균 평점"
    )
    rating_count: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        default=0, 
        comment="평점 개수"
    )
    consultation_count: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        default=0, 
        comment="총 상담 횟수"
    )
    consultation_time_total: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        default=0, 
        comment="총 상담 시간(분)"
    )
    
    # 금액 관련
    after_amount: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True, 
        default=1000, 
        comment="선불 금액"
    )
    before_amount: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        default="1000", 
        comment="후분금액"
    )
    
    # 상태 플래그들 (tinyint(1) -> bool)
    is_new: Mapped[Optional[bool]] = mapped_column(
        Boolean, 
        nullable=True, 
        default=True, 
        comment="신규 상담사 여부"
    )
    is_out: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False, 
        comment="탈퇴 여부"
    )
    is_show: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False, 
        comment="노출여부"
    )
    
    # 승인 관련
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        comment="승인일시"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        comment="생성 일시"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        onupdate=datetime.utcnow, 
        comment="수정 일시"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        comment="마지막 로그인 일시"
    )
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        comment="탈퇴일시"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_counselor_status', 'counselor_status'),
        Index('idx_grade', 'grade'),
        Index('idx_rating', 'rating_avg', 'rating_count'),
        CheckConstraint(
            "counselor_status IN ('WAITING','CONSULTING','ABSENT')",
            name='chk_counselor_status'
        ),
        CheckConstraint(
            "grade IN ('BRONZE','SILVER','GOLD')",
            name='chk_grade'
        ),
        {'comment': '상담사 정보'}
    )
    
    def __repr__(self) -> str:
        return f"<Counselor(counselor_id={self.counselor_id}, nickname={self.nickname}, status={self.counselor_status})>"