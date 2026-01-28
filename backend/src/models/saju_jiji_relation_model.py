"""
지지 관계(SajuJijiRelation) 모델

Story 2.1 Task 4: 지지 관계 테이블 (AC: 1, 5)
- 30~50행: 합(6합), 충(6충), 형(삼형), 파(육파), 해(육해), 12운성
"""
from enum import Enum

from sqlalchemy import String, Integer, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class RelationType(str, Enum):
    """지지 관계 유형"""
    HAP = "합"  # 육합 (6종)
    CHUNG = "충"  # 육충 (6종)
    HYUNG = "형"  # 삼형 (3종)
    PA = "파"  # 육파 (6종)
    HAE = "해"  # 육해 (6종)
    TWELVE = "12운성"  # 12운성


class SajuJijiRelation(Base):
    """
    지지 관계 테이블

    지지(地支) 간의 합, 충, 형, 파, 해 등의 관계를 저장합니다.
    최소 12행 (6합 + 6충), 최대 50행 이상
    """

    __tablename__ = "saju_jiji_relation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="관계 ID (AUTO_INCREMENT)"
    )
    relation_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="관계 유형 (합, 충, 형, 파, 해, 12운성)"
    )
    jiji1: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="첫 번째 지지"
    )
    jiji2: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="두 번째 지지"
    )
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="관계 이름 (예: 자축합, 자오충)"
    )
    keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment="핵심 키워드 배열"
    )
    meaning: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="관계 의미 해석"
    )
    daily_impact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="일일 운세에 미치는 영향"
    )

    __table_args__ = (
        Index("idx_relation", "relation_type", "jiji1"),
        {"comment": "지지 관계 데이터 (합, 충, 형, 파, 해)"}
    )

    def __repr__(self) -> str:
        return f"<SajuJijiRelation(id={self.id}, name={self.name}, type={self.relation_type})>"
