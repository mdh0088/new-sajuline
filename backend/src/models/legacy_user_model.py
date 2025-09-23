"""
레거시 사용자 모델 (TBL_USER 테이블)
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, DateTime, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

LegacyBase = declarative_base()


class LegacyUser(LegacyBase):
    """레거시 사용자 정보 테이블 (TBL_USER)"""

    __tablename__ = "TBL_USER"

    IDX: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="사용자 고유 번호"
    )
    NICK_NAME: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="닉네임"
    )
    USER_ID: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="사용자 ID"
    )
    PASSWORD: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="비밀번호"
    )
    EMAIL: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="이메일"
    )
    PHONE: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        comment="전화번호"
    )
    USER_STATUS: Mapped[str] = mapped_column(
        CHAR(1),
        nullable=False,
        default="1",
        comment="사용자 상태"
    )
    JOIN_TYPE: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="가입 유형"
    )
    GRADE: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="WHITE",
        comment="등급"
    )
    MILEAGE: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="마일리지"
    )
    REGIST_DATE: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="등록일"
    )
    UPDATE_DATE: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="수정일"
    )
    LAST_LOGIN: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="마지막 로그인"
    )

    def __repr__(self) -> str:
        return f"<LegacyUser(IDX={self.IDX}, USER_ID='{self.USER_ID}', NICK_NAME='{self.NICK_NAME}')>"

    @property
    def is_active(self) -> bool:
        """사용자 활성 상태 확인"""
        return self.USER_STATUS == "1"

    # 새로운 User 모델과 호환되는 프로퍼티들
    @property
    def user_id(self) -> str:
        return self.USER_ID

    @property
    def nickname(self) -> str:
        return self.NICK_NAME or "사용자"  # 빈 닉네임 처리

    @property
    def email(self) -> str:
        return self.EMAIL

    @property
    def phone(self) -> str:
        return self.PHONE

    @property
    def password_hash(self) -> str:
        return self.PASSWORD

    @property
    def user_status(self) -> str:
        return "ACTIVE" if self.USER_STATUS == "1" else "INACTIVE"

    @property
    def grade_code(self) -> str:
        return self.GRADE or "WHITE"

    @property
    def mileage(self) -> int:
        return self.MILEAGE or 0

    @property
    def created_at(self) -> Optional[datetime]:
        return self.REGIST_DATE

    @property
    def updated_at(self) -> Optional[datetime]:
        return self.UPDATE_DATE

    @property
    def last_login_at(self) -> Optional[datetime]:
        return self.LAST_LOGIN