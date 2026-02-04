"""
AI 질의 히스토리 모델.

Stories: 4-1
FRs: FR19
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class AIQueryHistory(Base):
    """AI 질의 히스토리 테이블 (t_ai_query_history).

    AC3: 최근 질의 히스토리 표시 (최대 20개)
    - 질문, 실행 시간, 결과 요약
    """
    __tablename__ = "t_ai_query_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="히스토리 ID"
    )
    admin_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("t_admin.admin_id"),
        nullable=False,
        index=True,
        comment="관리자 ID"
    )
    query_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        comment="질의 고유 ID (UUID)"
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="사용자 질문"
    )
    answer_summary: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="응답 요약"
    )
    db_scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="mariadb",
        comment="DB 범위 (mariadb, mssql, cross-db)"
    )
    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="실행 시간 (밀리초)"
    )
    row_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="결과 행 수"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="실행 상태 (success, error)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        index=True,
        comment="생성 일시"
    )

    def __repr__(self) -> str:
        return (
            f"<AIQueryHistory(id={self.id}, "
            f"admin_id={self.admin_id}, "
            f"status={self.status})>"
        )
