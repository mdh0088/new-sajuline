"""
배너(Banner) 모델 정의 - t_banner 테이블
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Banner(Base):
    """배너 테이블 (t_banner)

    improved-schema.sql의 정의를 준수합니다.
    """

    __tablename__ = "t_banner"

    # 기본키 및 코드
    banner_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="배너 PK")
    banner_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="배너 코드")

    # 기본 정보
    banner_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="배너명")
    banner_type: Mapped[str] = mapped_column(String(20), nullable=False, default="MAIN", comment="배너 타입: MAIN, SUB, POPUP")

    # 이미지/링크
    image_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="이미지 URL(파일명 저장)")
    mobile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="모바일 이미지 URL")
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="링크 URL")
    link_target: Mapped[str] = mapped_column(String(10), nullable=False, default="SELF", comment="링크 타겟: SELF, BLANK")

    # 전시/상태/기간
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="노출 순서")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="노출 시작일")
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="노출 종료일")

    # 지표
    click_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="클릭수")
    impression_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="노출수")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)


