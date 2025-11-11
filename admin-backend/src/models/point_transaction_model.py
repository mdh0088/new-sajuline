"""
포인트 거래 내역 모델 (t_point_transaction)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class PointTransaction(Base):
    __tablename__ = "t_point_transaction"

    transaction_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # 요구사항: transaction_type=ADMIN, currency_type=POINT 사용
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    currency_type: Mapped[str] = mapped_column(String(20), nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)

    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pt_user_created", "user_id", "created_at"),
        {"comment": "포인트 거래 내역"},
    )






























