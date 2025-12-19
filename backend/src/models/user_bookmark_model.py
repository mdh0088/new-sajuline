"""
사용자 북마크 모델 (t_user_bookmark 테이블)
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")


class UserBookmark(Base):
    """사용자 북마크 테이블"""
    
    __tablename__ = "t_user_bookmark"
    
    # 기본키
    bookmark_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True, 
        comment="북마크 ID"
    )
    
    # 사용자 ID
    user_id: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="유저 id"
    )
    
    # 상담사 ID
    counselor_id: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="상담사 id"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        comment="등록일"
    )
    
    # 인덱스 정의
    __table_args__ = (
        Index('t_user_bookmark_user_id_IDX', 'user_id'),
        Index('t_user_bookmark_counselor_id_IDX', 'counselor_id'),
        {'comment': '사용자 북마크'}
    )
    
    def __repr__(self) -> str:
        return f"<UserBookmark(bookmark_id={self.bookmark_id}, user_id={self.user_id}, counselor_id={self.counselor_id})>"