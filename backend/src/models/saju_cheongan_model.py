"""
천간(SajuCheongan) 모델

Story 2.1 Task 1: 천간 테이블 (AC: 1, 2)
- 10행: 갑(甲), 을(乙), 병(丙), 정(丁), 무(戊), 기(己), 경(庚), 신(辛), 임(壬), 계(癸)
"""
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SajuCheongan(Base):
    """
    천간 테이블

    사주명리학의 천간(天干) 10개를 저장합니다.
    갑(甲)~계(癸)까지의 기초 데이터를 포함합니다.
    """

    __tablename__ = "saju_cheongan"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="천간 ID (1~10)"
    )
    name: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="천간 이름 (갑~계)"
    )
    hanja: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="한자 (甲~癸)"
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
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="천간 설명 및 특성"
    )

    __table_args__ = (
        {"comment": "천간 (天干) 기초 데이터"}
    )

    def __repr__(self) -> str:
        return f"<SajuCheongan(id={self.id}, name={self.name}, hanja={self.hanja})>"
