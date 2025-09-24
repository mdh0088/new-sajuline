"""
배너(Banner) 모델 정의
"""
from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Boolean, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class BannerType(str, Enum):
    """배너 타입"""
    MAIN = "MAIN"
    SUB = "SUB"
    POPUP = "POPUP"


class LinkTarget(str, Enum):
    """링크 타겟"""
    SELF = "SELF"
    BLANK = "BLANK"


class Banner(Base):
    """배너 테이블"""
    __tablename__ = "t_banner"

    # 기본키
    banner_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="배너 ID",
    )

    # 코드/이름
    banner_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="배너 코드",
    )
    banner_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="배너명",
    )

    # 타입/이미지/링크
    banner_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=BannerType.MAIN.value,
        comment="배너 타입: MAIN, SUB, POPUP",
    )
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="이미지 URL",
    )
    mobile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="모바일 이미지 URL",
    )
    link_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="링크 URL",
    )
    link_target: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=LinkTarget.SELF.value,
        comment="링크 타겟: SELF, BLANK",
    )

    # 노출/상태/기간/통계
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="노출 순서",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="활성화 여부",
    )
    valid_from: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="노출 시작일",
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="노출 종료일",
    )
    click_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="클릭수",
    )
    impression_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="노출수",
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="생성일시",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
        comment="수정일시",
    )

    # 인덱스/제약조건
    __table_args__ = (
        Index("uk_banner_code", "banner_code", unique=True),
        Index("idx_type_active", "banner_type", "is_active"),
        Index("idx_valid_date", "valid_from", "valid_until"),
        Index("idx_display_order", "display_order"),
        CheckConstraint(
            "banner_type IN ('MAIN','SUB','POPUP')",
            name="chk_banner_type",
        ),
        CheckConstraint(
            "link_target IN ('SELF','BLANK')",
            name="chk_link_target",
        ),
        CheckConstraint(
            "valid_from < valid_until",
            name="chk_banner_valid_date_range",
        ),
        {"comment": "배너"},
    )

    def __repr__(self) -> str:  # pragma: no cover - 디버깅 편의
        return f"<Banner(banner_id={self.banner_id}, banner_code={self.banner_code}, banner_type={self.banner_type})>"


