"""
Counselor 도메인 모델

상담사 정보 테이블 정의
"""

from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Integer, Numeric, String, Text, func, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship

from src.common.database.base import Base, TimestampMixin


# Specialty는 별도 테이블이 아니라 코드로만 관리됨 (MariaDB 실제 구조)
SPECIALTY_MAPPING = {
    "SAJU": "사주",
    "TAROT": "타로",
    "LOVE": "연애",
    "CAREER": "취업",
    "BUSINESS": "사업",
    "NAME": "작명",
    "DREAM": "해몽",
    "FORTUNE": "운세",
    "COMPATIBILITY": "궁합"
}

class CounselorSpecialty(Base):
    """상담사-전문분야 매핑 테이블 (MariaDB 실제 구조)"""
    
    __tablename__ = "t_counselor_specialty"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    counselor_id = Column(
        String(100),
        ForeignKey("t_counselor.counselor_id", ondelete="CASCADE"),
        primary_key=True
    )
    specialty_code = Column(
        String(20),
        primary_key=True,
        comment="전문분야 코드"
    )
    is_main = Column(String(1), nullable=True, default="Y", comment="주전공 여부")
    experience_years = Column(Integer, nullable=True, default=0, comment="경력년수")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성 시간")
    
    def __repr__(self):
        return f"<CounselorSpecialty(counselor_id={self.counselor_id}, specialty={self.specialty_code})>"
    
    @property
    def specialty_name(self) -> str:
        """전문분야명 조회"""
        return SPECIALTY_MAPPING.get(self.specialty_code, self.specialty_code)


class Counselor(Base, TimestampMixin):
    """상담사 정보 테이블"""
    
    __tablename__ = "t_counselor"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    counselor_id = Column(String(100), primary_key=True, comment="상담사 ID")
    counselor_code = Column(String(50), nullable=False, unique=True, comment="상담사 코드")
    password_hash = Column(String(255), nullable=False, comment="비밀번호 해시")
    name = Column(String(50), nullable=False, comment="실명")
    nickname = Column(String(100), nullable=False, unique=True, comment="상담사 닉네임")
    phone = Column(String(50), nullable=False, unique=True, comment="전화번호")
    profile_image_url = Column(String(500), nullable=True, comment="프로필 이미지 URL")
    introduction_short = Column(Text, nullable=True, comment="짧은 소개")
    greeting_message = Column(Text, nullable=True, comment="인사말")
    career_info = Column(Text, nullable=True, comment="경력 정보")
    counselor_status = Column(String(20), nullable=False, default="WAITING", comment="상담사 상태")
    grade = Column(String(20), nullable=True, default="BRONZE", comment="상담사 등급")
    rating_avg = Column(Numeric(3, 2), nullable=True, default=0.00, comment="평균 평점")
    rating_count = Column(Integer, nullable=True, default=0, comment="평점 수")
    consultation_count = Column(Integer, nullable=True, default=0, comment="상담 횟수")
    consultation_time_total = Column(Integer, nullable=True, default=0, comment="총 상담 시간")
    after_amount = Column(Integer, nullable=True, default=1000, comment="상담료 (후불)")
    before_amount = Column(String(100), nullable=False, default="1000", comment="상담료 (선불)")
    is_new = Column(String(1), nullable=True, default="Y", comment="신규 여부")
    is_out = Column(String(1), nullable=False, default="N", comment="탈퇴 여부")
    is_show = Column(String(1), nullable=False, default="N", comment="노출 여부")
    approved_at = Column(DateTime, nullable=True, comment="승인 시간")
    last_login_at = Column(DateTime, nullable=True, comment="마지막 로그인")
    withdrawn_at = Column(DateTime, nullable=True, comment="탈퇴 시간")
    
    # 관계 정의 (MariaDB 실제 구조에 맞춤)
    specialties = relationship(
        "CounselorSpecialty",
        back_populates=None,
        lazy="select",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Counselor(counselor_id={self.counselor_id}, nickname={self.nickname})>"
    
    @property
    def is_active(self) -> bool:
        """활성 상담사 여부"""
        return self.is_show == "Y" and self.is_out == "N" and self.approved_at is not None
    
    @property
    def is_available(self) -> bool:
        """상담 가능 여부"""
        return self.is_active and self.counselor_status == "WAITING"
    
    @property
    def counselor_status_text(self) -> str:
        """상담사 상태 텍스트"""
        status_map = {
            "WAITING": "대기중", 
            "CONSULTING": "상담중", 
            "ABSENT": "부재중",
            "OFFLINE": "오프라인"
        }
        return status_map.get(self.counselor_status, "알 수 없음")
    
    @property 
    def is_authorized(self) -> bool:
        """관리자 승인 여부 (MariaDB 스키마 호환)"""
        return self.approved_at is not None
    
    @property
    def is_online(self) -> bool:
        """온라인 여부 (MariaDB 스키마 호환)"""
        return self.counselor_status in ["WAITING", "CONSULTING"]
    
    @property
    def counselor_nickname(self) -> str:
        """닉네임 (기존 코드 호환성)"""
        return self.nickname
    
    @property
    def price_per_minute(self) -> int:
        """분당 상담료 (기존 코드 호환성)"""
        return int(self.after_amount) if self.after_amount else 1000
    
    @property
    def introduction(self) -> str:
        """소개글 (기존 코드 호환성)"""
        return self.introduction_short or ""
    
    def update_rating(self, new_rating: int) -> None:
        """평점 업데이트"""
        if self.rating_avg and self.rating_count:
            total_score = float(self.rating_avg) * self.rating_count
            self.rating_count += 1
            self.rating_avg = round((total_score + new_rating) / self.rating_count, 2)
        else:
            self.rating_count = 1
            self.rating_avg = float(new_rating) 