"""
십성 해석(SajuSipsungInterpretation) 모델

Story 2.1 Task 3: 십성 해석 테이블 (AC: 1, 4)
- 100행: 일간(10) × 십성(10) 조합
- 십성: 비견, 겁재, 식신, 상관, 정재, 편재, 정관, 편관, 정인, 편인
"""
from sqlalchemy import String, Integer, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SajuSipsungInterpretation(Base):
    """
    십성 해석 테이블

    일간(日干)과 십성(十星)의 조합에 따른 해석 데이터를 저장합니다.
    총 100개 조합 (10개 일간 × 10개 십성)
    """

    __tablename__ = "saju_sipsung_interpretation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="해석 ID (AUTO_INCREMENT)"
    )
    ilgan: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="일간 (갑~계)"
    )
    sipsung: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="십성 (비견, 겁재, 식신, 상관, 정재, 편재, 정관, 편관, 정인, 편인)"
    )
    keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment="핵심 키워드 배열"
    )
    positive_meaning: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="긍정적 의미 해석"
    )
    negative_meaning: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="부정적 의미 해석"
    )
    daily_advice: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="일일 운세 조언"
    )

    __table_args__ = (
        Index("idx_ilgan_sipsung", "ilgan", "sipsung"),
        {"comment": "십성 해석 데이터 (일간×십성 100조합)"}
    )

    def __repr__(self) -> str:
        return f"<SajuSipsungInterpretation(id={self.id}, ilgan={self.ilgan}, sipsung={self.sipsung})>"
