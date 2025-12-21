"""
등급 변경 로그 모델 (t_grade_change_log 테이블)
"""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class GradeChangeLog(Base):
    """등급 변경 로그 테이블 (t_grade_change_log)

    사용자의 등급 변경 이력을 기록합니다.
    - 자동 배치에 의한 월별 등급 갱신
    - 관리자에 의한 수동 등급 변경
    """

    __tablename__ = "t_grade_change_log"

    # 기본키
    log_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="로그 ID"
    )

    # 사용자 정보
    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="사용자 ID"
    )

    # 등급 변경 정보
    grade_before: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="이전 등급"
    )
    grade_after: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="변경 후 등급"
    )

    # 결제 금액
    purchase_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="구매 금액"
    )

    # 변경 사유
    change_reason: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="변경 사유 (AUTO_BATCH, MANUAL 등)"
    )

    # 관리자 정보
    admin_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="처리 관리자 ID"
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        comment="생성일시"
    )

    # 인덱스 정의
    __table_args__ = (
        Index('idx_grade_change_log_user_id', 'user_id'),
        Index('idx_grade_change_log_created_at', 'created_at'),
        {'comment': '등급 변경 로그'}
    )

    def __repr__(self) -> str:
        return f"<GradeChangeLog(log_id={self.log_id}, user_id={self.user_id}, {self.grade_before}->{self.grade_after})>"
