"""
관리자 백엔드 결제 모델 (t_payment)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Payment(Base):
    """결제 내역 테이블 (t_payment)

    메인 백엔드의 `t_payment` 스키마와 정합성을 유지합니다.
    """

    __tablename__ = "t_payment"

    # 기본키
    payment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="결제 ID",
    )

    # 주문 정보
    order_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="주문번호",
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("t_user.user_id"),
        nullable=False,
        comment="사용자 ID",
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_point_product.product_id"),
        nullable=True,
        comment="상품 ID",
    )

    # 결제 정보
    payment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="결제 유형: POINT_CHARGE, SUBSCRIPTION",
    )
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="결제 금액",
    )
    point_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="충전 포인트",
    )
    mileage_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="사용 마일리지",
    )

    # 결제 수단 및 상태
    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="결제 수단",
    )
    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        comment="결제 상태",
    )

    # PG사 정보
    pg_tid: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="PG 거래번호",
    )
    cid: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="cid",
    )
    pay_info: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="결제정보",
    )
    tax_amount: Mapped[str] = mapped_column(
        String(100),
        default="0",
        comment="세금",
    )
    install_month: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="할부개월",
    )
    pay_hash: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="결제 해시",
    )
    taxfree_amount: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="비과세 금액",
    )
    nonsettle_amount: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="미결제 금액",
    )
    discount_amount: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="할인 금액",
    )
    point_use_flag: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="포인트 사용 여부",
    )
    disposable_cup_deposit: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="일회용컵 보증금",
    )
    domestic_flag: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="도메스틱 플래그",
    )

    # 결제 일시
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="결제 완료 시간",
    )

    # 응답 관련
    code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="성공코드",
    )
    result_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="결과 메시지",
    )

    # 취소 관련
    cancel_amount: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="환불 금액",
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="취소 시간",
    )

    # 계좌 정보
    account_no: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="계좌번호",
    )
    account_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="예금주명",
    )
    account_holder: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="계좌 소유자",
    )
    bank_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="은행 코드",
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="은행명",
    )

    # 가상계좌 정보
    expire_date: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="만료일",
    )
    expire_time: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="만료시간",
    )
    issue_tid: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="발급 거래번호",
    )

    # 현금영수증
    cash_receipt_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="현금영수증 종류",
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

    # 인덱스 정의
    __table_args__ = (
        Index("idx_payment_user_id_status", "user_id", "payment_status"),
        Index("idx_payment_paid_at", "paid_at"),
        Index("idx_payment_created_at", "created_at"),
        {"comment": "결제 내역"},
    )

    def __repr__(self) -> str:
        return f"<Payment(payment_id={self.payment_id}, order_no={self.order_no}, status={self.payment_status})>"



