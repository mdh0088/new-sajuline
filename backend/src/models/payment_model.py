"""
결제 내역 모델 (t_payment 테이블)
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, DateTime, Integer, Numeric, Text, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class Payment(Base):
    """결제 내역 테이블"""
    
    __tablename__ = "t_payment"
    
    # 기본키
    payment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="결제 ID"
    )
    
    # 주문 정보
    order_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="주문번호"
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("t_user.user_id"),
        nullable=False,
        comment="사용자 ID"
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_point_product.product_id"),
        nullable=True,
        comment="상품 ID"
    )
    
    # 결제 정보
    payment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="결제 유형: POINT_CHARGE, SUBSCRIPTION"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="결제 금액"
    )
    point_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="충전 포인트"
    )
    bonus_point: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="보너스 포인트"
    )
    mileage_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="사용 마일리지"
    )
    
    # 결제 수단 및 상태
    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="결제 수단"
    )
    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        comment="결제 상태"
    )
    
    # PG사 정보
    pg_provider: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="PG사"
    )
    pg_tid: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="PG 거래번호"
    )
    cid: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="cid"
    )
    pay_info: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="결제정보"
    )
    tax_amount: Mapped[str] = mapped_column(
        String(100),
        default="0",
        comment="세금"
    )
    domestic_flag: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="도메스틱 플래그"
    )
    
    # 결제 일시
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="결제 완료 시간"
    )
    
    # 취소 관련
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="취소 시간"
    )
    cancel_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="취소 사유"
    )
    refund_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="환불 금액"
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
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_user_id_status', 'user_id', 'payment_status'),
        Index('idx_paid_at', 'paid_at'),
        Index('idx_created_at', 'created_at'),
        {'comment': '결제 내역'}
    )
    
    def __repr__(self) -> str:
        return f"<Payment(payment_id={self.payment_id}, order_no={self.order_no}, status={self.payment_status})>"