"""
ARS tm60_mobile 테이블 모델 (MSSQL 연동)

전화 상담 시작 시 모바일 플랫폼 정보를 기록하는 테이블
레거시 시스템과의 호환성을 위해 기존 컬럼명과 타입을 유지
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, DateTime, Index, Identity
from sqlalchemy.orm import Mapped, mapped_column

from src.models.ars.tm60_member_model import ARSBase


class MobilePlatform(str, Enum):
    """모바일 플랫폼 타입"""
    MOBILE_WEB = "1"  # Mobile web
    ANDROID = "2"     # Android
    IOS = "3"         # Apple (iPhone, iPad, iPod)


class Tm60Mobile(ARSBase):
    """
    ARS 모바일 통화 기록 테이블 (tm60_mobile) 모델

    DDL:
    CREATE TABLE ars.dbo.tm60_mobile (
        idx int NOT NULL IDENTITY(1,1),
        mb_id varchar(50) DEFAULT ('') NOT NULL,
        mb_code varchar(3) DEFAULT ('') NOT NULL,
        mb_platform varchar(1) DEFAULT ('') NOT NULL,
        regdate datetime NULL,
        CONSTRAINT PK__tm60_mobile__40106F4B PRIMARY KEY (idx)
    );

    필드 설명:
    - idx: 기본키 (IDENTITY)
    - mb_id: 유저 ID (user_id)
    - mb_code: 상담사 코드 (counselor_code)
    - mb_platform: 플랫폼 타입 (1=Mobile web, 2=Android, 3=iOS)
    - regdate: 등록일시
    """
    __tablename__ = "tm60_mobile"

    # 기본 키
    idx: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
        comment="고유 식별자"
    )

    # 유저 정보
    mb_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="",
        comment="유저 ID"
    )

    # 상담사 정보
    mb_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="",
        comment="상담사 코드"
    )

    # 플랫폼 정보
    mb_platform: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default="",
        comment="플랫폼 타입: 1=Mobile web, 2=Android, 3=iOS"
    )

    # 등록일시
    regdate: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="등록일시"
    )

    # 인덱스 정의
    __table_args__ = (
        Index('idx_mb_code', 'mb_code'),
        Index('idx_mb_id', 'mb_id'),
        Index('idx_regdate', 'regdate'),
        {'schema': 'dbo', 'comment': 'ARS 모바일 통화 기록 테이블'}
    )

    def __repr__(self) -> str:
        return f"<Tm60Mobile(idx={self.idx}, mb_id='{self.mb_id}', mb_code='{self.mb_code}')>"

    @property
    def platform_name(self) -> str:
        """플랫폼명 반환"""
        platform_map = {
            MobilePlatform.MOBILE_WEB: "Mobile Web",
            MobilePlatform.ANDROID: "Android",
            MobilePlatform.IOS: "iOS"
        }
        return platform_map.get(self.mb_platform, "Unknown")

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "idx": self.idx,
            "mb_id": self.mb_id,
            "mb_code": self.mb_code,
            "mb_platform": self.mb_platform,
            "platform_name": self.platform_name,
            "regdate": self.regdate.isoformat() if self.regdate else None
        }
