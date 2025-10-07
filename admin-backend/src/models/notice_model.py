"""
공지사항(Notice) 모델 정의 - t_notice 테이블
"""
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, DateTime, Boolean, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from src.core.database import Base


class Notice(Base):
    """공지사항 테이블 (t_notice)

    프로젝트 스키마(improved-schema.sql)를 기준으로 하되,
    관리자 ID 타입은 현재 관리자 모델(`t_admin.admin_id`)과 정합성을 위해 문자열로 맞춥니다.
    """

    __tablename__ = "t_notice"

    # 기본키
    notice_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="공지 PK")

    # 분류/대상
    notice_type: Mapped[str] = mapped_column(String(20), nullable=False, default="GENERAL", comment="공지 타입")
    target_audience: Mapped[str] = mapped_column(String(20), nullable=False, default="ALL", comment="대상: ALL|USER|COUNSELOR")

    # 내용
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="제목")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="내용")

    # 상태/표시
    is_important: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="중요 공지")
    is_popup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="팝업 표시")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="활성화 여부")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="조회수")

    # 첨부/작성자
    attachments: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True, comment="첨부파일(JSON)")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="작성자 관리자 ID")

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, comment="등록일시")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="수정일시")

    __table_args__ = (
        Index("idx_type_active", "notice_type", "is_active"),
        Index("idx_target_audience", "target_audience"),
        Index("idx_created_at", "created_at"),
        {"comment": "공지사항"},
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notice(id={self.notice_id}, type={self.notice_type}, title={self.title})>"



