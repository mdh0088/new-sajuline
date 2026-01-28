"""
지지(SajuJiji) 모델

Story 2.1 Task 2: 지지 테이블 (AC: 1, 3)
- 12행: 자(子), 축(丑), 인(寅), 묘(卯), 진(辰), 사(巳), 오(午), 미(未), 신(申), 유(酉), 술(戌), 해(亥)
"""
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SajuJiji(Base):
    """
    지지 테이블

    사주명리학의 지지(地支) 12개를 저장합니다.
    자(子)~해(亥)까지의 기초 데이터를 포함합니다.
    """

    __tablename__ = "saju_jiji"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="지지 ID (1~12)"
    )
    name: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="지지 이름 (자~해)"
    )
    hanja: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="한자 (子~亥)"
    )
    oheng: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="오행 (목, 화, 토, 금, 수)"
    )
    yin_yang: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="음양 (양, 음)"
    )
    animal: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="12지신 동물 (쥐, 소, 호랑이, ...)"
    )
    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="대응 음력월 (1~12, 자=11월)"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="지지 설명 및 특성"
    )

    __table_args__ = (
        {"comment": "지지 (地支) 기초 데이터"}
    )

    def __repr__(self) -> str:
        return f"<SajuJiji(id={self.id}, name={self.name}, animal={self.animal})>"
