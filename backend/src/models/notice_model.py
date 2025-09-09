"""
공지사항 모델 (t_notice 테이블)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import String, DateTime, Integer, Boolean, Text, JSON, Index, CheckConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class NoticeType(str, Enum):
    """공지 타입"""
    GENERAL = "GENERAL"
    EVENT = "EVENT"
    UPDATE = "UPDATE"


class TargetAudience(str, Enum):
    """대상 타입"""
    ALL = "ALL"
    USER = "USER"
    COUNSELOR = "COUNSELOR"


class Notice(Base):
    """공지사항 테이블"""
    
    __tablename__ = "t_notice"
    
    # 기본키
    notice_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="공지사항 ID"
    )
    
    # 공지 분류 및 기본 정보
    notice_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="GENERAL",
        comment="공지 타입: GENERAL, EVENT, UPDATE"
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="제목"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="내용"
    )
    
    # 대상 설정
    target_audience: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ALL",
        comment="대상: ALL, USER, COUNSELOR"
    )
    
    # 중요도 및 표시 설정
    is_important: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="중요 공지"
    )
    is_popup: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="팝업 표시"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="활성화 여부"
    )
    
    # 통계
    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="조회수"
    )
    
    # 첨부파일 (JSON 형태로 저장)
    attachments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
        comment="첨부파일"
    )
    
    # 작성자 정보
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_admin.admin_id"),
        nullable=False,
        comment="작성자"
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
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_type_active', 'notice_type', 'is_active'),
        Index('idx_target_audience', 'target_audience'),
        Index('idx_created_at', 'created_at', postgresql_using='btree', mysql_length={'created_at': None}),
        Index('fk_notice_admin', 'created_by'),
        CheckConstraint(
            "notice_type IN ('GENERAL','EVENT','UPDATE')",
            name='chk_notice_type'
        ),
        CheckConstraint(
            "target_audience IN ('ALL','USER','COUNSELOR')",
            name='chk_target_audience'
        ),
        {'comment': '공지사항'}
    )
    
    def __repr__(self) -> str:
        return f"<Notice(notice_id={self.notice_id}, title={self.title}, notice_type={self.notice_type})>"