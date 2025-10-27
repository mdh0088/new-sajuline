"""
포인트/마일리지 거래 내역 모델
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, DateTime, Integer, Text, DECIMAL, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class TransactionType(str, Enum):
    """거래 유형"""
    CHARGE = "CHARGE"    # 충전
    USE = "USE"          # 사용
    EARN = "EARN"        # 적립
    EXPIRE = "EXPIRE"    # 만료
    CANCEL = "CANCEL"    # 취소


class CurrencyType(str, Enum):
    """통화 유형"""
    POINT = "POINT"      # 포인트
    MILEAGE = "MILEAGE"  # 마일리지


class ReferenceType(str, Enum):
    """참조 유형"""
    PAYMENT = "PAYMENT"        # 결제
    CONSULTATION = "CONSULTATION"  # 상담
    EVENT = "EVENT"            # 이벤트
    MANUAL = "MANUAL"          # 수동 처리
    REVIEW = "REVIEW"          # 후기 작성
    MILEAGE_PRODUCT = "MILEAGE_PRODUCT"  # 마일리지 상품 구매


class PointTransaction(Base):
    """포인트/마일리지 거래 내역 테이블"""
    __tablename__ = "t_point_transaction"
    
    # 기본키
    transaction_id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True, 
        comment="거래 ID"
    )
    
    # 사용자 ID (외래키 제약조건 제거)
    user_id: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="사용자 ID"
    )
    
    # 거래 정보
    transaction_type: Mapped[str] = mapped_column(
        String(30), 
        nullable=False, 
        comment="거래 유형: CHARGE, USE, EARN, EXPIRE, CANCEL"
    )
    currency_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        comment="통화 유형: POINT, MILEAGE"
    )
    amount: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        comment="거래 금액 (양수: 증가, 음수: 감소)"
    )
    balance_after: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        comment="거래 후 잔액"
    )
    
    # 참조 정보
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True, 
        comment="참조 유형: PAYMENT, CONSULTATION, EVENT, MANUAL"
    )
    reference_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        comment="참조 ID"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="거래 설명"
    )
    
    # 추가 정보
    earn_rate: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), 
        nullable=True, 
        comment="적립률"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        comment="만료일시"
    )
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        comment="거래 일시"
    )
    
    # 인덱스 및 제약조건 정의
    __table_args__ = (
        Index('idx_user_currency_created', 'user_id', 'currency_type', 'created_at'),
        Index('idx_reference', 'reference_type', 'reference_id'),
        Index('idx_expires_at', 'expires_at'),
        {'comment': '포인트/마일리지 거래 내역'}
    )
    
    def __repr__(self) -> str:
        return f"<PointTransaction(transaction_id={self.transaction_id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"