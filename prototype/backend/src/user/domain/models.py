"""
User 도메인 모델

사용자, 관리자, 시스템 설정 관련 테이블 정의
"""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Integer, 
    String, Text, func
)

from src.common.database.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """사용자 정보 테이블"""
    
    __tablename__ = "t_user"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    user_id = Column(String(100), primary_key=True, index=True, comment="사용자 ID")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="이메일 주소")
    password_hash = Column(String(255), nullable=True, comment="비밀번호 해시 (소셜로그인시 NULL)")
    nickname = Column(String(100), unique=True, nullable=False, comment="닉네임")
    phone = Column(String(15), unique=True, nullable=False, comment="전화번호")
    join_type = Column(String(20), nullable=False, default="COMMON", comment="가입 유형 (COMMON/SOCIAL)")
    social_provider = Column(String(20), nullable=True, comment="소셜 로그인 제공자 (kakao/naver)")
    social_id = Column(String(255), nullable=True, comment="소셜 로그인 고유 ID")
    user_status = Column(String(20), nullable=False, default="ACTIVE", comment="사용자 상태 (ACTIVE/INACTIVE/WITHDRAWN)")
    grade_code = Column(String(20), nullable=False, default="WHITE", comment="회원 등급 (WHITE/BRONZE/SILVER/GOLD/PLATINUM)")
    profile_image_url = Column(String(500), nullable=True, comment="프로필 이미지 URL")
    birth_date = Column(Date, nullable=True, comment="생년월일")
    gender = Column(String(10), nullable=True, comment="성별 (M/F)")
    is_marketing_agreed = Column(Boolean, nullable=True, default=False, comment="마케팅 동의 여부")
    password_changed_at = Column(DateTime, nullable=True, comment="비밀번호 변경 일시")
    failed_login_count = Column(Integer, nullable=True, default=0, comment="로그인 실패 횟수")
    locked_until = Column(DateTime, nullable=True, comment="계정 잠금 해제 시간")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="가입 일시")
    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), comment="수정 일시")
    last_login_at = Column(DateTime, nullable=True, comment="마지막 로그인 일시")
    withdrawn_at = Column(DateTime, nullable=True, comment="탈퇴 일시")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, nickname={self.nickname})>"
    
    @property
    def is_active(self) -> bool:
        """활성 사용자 여부"""
        return self.user_status == "ACTIVE"
    
    @property
    def is_premium(self) -> bool:
        """프리미엄 회원 여부 (grade_code 기반)"""
        return self.grade_code not in ["WHITE", "BRONZE"]
    
    @is_premium.setter
    def is_premium(self, value: bool) -> None:
        """프리미엄 설정 (grade_code로 변환)"""
        if value:
            self.grade_code = "GOLD"  # 프리미엄으로 설정
        else:
            self.grade_code = "WHITE"  # 일반으로 설정
    
    # point_balance는 t_user_point_balance 테이블과 연동 (임시 속성으로 유지)
    @property
    def point_balance(self) -> int:
        """포인트 잔액 (t_user_point_balance 테이블에서 조회해야 함)"""
        return getattr(self, '_point_balance', 0)
    
    @point_balance.setter 
    def point_balance(self, value: int) -> None:
        """포인트 잔액 설정 (실제로는 t_user_point_balance 업데이트)"""
        self._point_balance = value
    
    # fcm_token 임시 속성
    @property
    def fcm_token(self) -> Optional[str]:
        """FCM 토큰 (임시 구현)"""
        return getattr(self, '_fcm_token', None)
    
    @fcm_token.setter
    def fcm_token(self, value: Optional[str]) -> None:
        """FCM 토큰 설정 (임시 구현)"""
        self._fcm_token = value


class Admin(Base, TimestampMixin):
    """관리자 정보 테이블"""
    
    __tablename__ = "t_admin"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    admin_id = Column(String(100), primary_key=True, comment="관리자 ID")
    email = Column(String(254), nullable=False, unique=True, comment="이메일")
    password_hash = Column(String(255), nullable=False, comment="비밀번호 해시")
    name = Column(String(50), nullable=False, comment="이름")
    role = Column(String(20), nullable=False, default="CS", comment="역할")
    is_active = Column(Boolean, default=True, comment="활성 여부")
    last_login_at = Column(DateTime, nullable=True, comment="마지막 로그인 시간")
    
    def __repr__(self):
        return f"<Admin(admin_id={self.admin_id}, email={self.email}, role={self.role})>"
    
    @property
    def is_super_admin(self) -> bool:
        """슈퍼 관리자 여부"""
        return self.role == "SUPER"


class SystemConfig(Base):
    """시스템 설정 테이블"""
    
    __tablename__ = "t_system_config"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    config_key = Column(String(100), primary_key=True, comment="설정 키")
    config_value = Column(Text, nullable=False, comment="설정 값")
    description = Column(Text, nullable=True, comment="설명")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시간"
    )
    
    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, value={self.config_value})>"
    
    @classmethod
    def get_value(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """설정값 조회 (캐시 고려 필요)"""
        # 실제 구현은 서비스 레이어에서
        pass


class Notice(Base, TimestampMixin):
    """공지사항 테이블"""
    
    __tablename__ = "t_notice"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    notice_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="공지사항 ID"
    )
    title = Column(String(200), nullable=False, comment="제목")
    content = Column(Text, nullable=False, comment="내용")
    is_important = Column(Boolean, default=False, comment="중요 공지 여부")
    is_active = Column(Boolean, default=True, comment="활성 여부")
    admin_id = Column(String(100), nullable=False, comment="작성자 ID")
    
    def __repr__(self):
        return f"<Notice(notice_id={self.notice_id}, title={self.title})>"


class FAQ(Base, TimestampMixin):
    """자주 묻는 질문 테이블"""
    
    __tablename__ = "t_faq"
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    faq_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="FAQ ID"
    )
    category = Column(String(30), nullable=False, comment="카테고리")
    question = Column(Text, nullable=False, comment="질문")
    answer = Column(Text, nullable=False, comment="답변")
    display_order = Column(Integer, default=0, comment="표시 순서")
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    def __repr__(self):
        return f"<FAQ(faq_id={self.faq_id}, category={self.category}, question={self.question[:30]}...)>" 