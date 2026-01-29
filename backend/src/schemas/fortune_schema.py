"""
운세 관련 스키마

Story 2.3: 운세 캐시 서비스 스키마
Story 2.4 Task 5: 운세 스키마 확장 (LLM 응답 파싱용)
"""
from datetime import date as date_type, datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# 기본 스키마
# =============================================================================

class DayPillar(BaseModel):
    """일주 정보"""
    stem: str = Field(..., description="천간 (갑, 을, 병, ...)")
    branch: str = Field(..., description="지지 (자, 축, 인, ...)")


# =============================================================================
# 요청 스키마 (Story 2.4 Task 5)
# =============================================================================

class DailyFortuneRequest(BaseModel):
    """
    일일 운세 요청 스키마

    사용자의 생년월일시와 조회할 운세 카테고리를 포함합니다.
    """
    birth_datetime: datetime = Field(
        ...,
        description="사용자 생년월일시 (YYYY-MM-DD HH:MM:SS)"
    )
    category: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        default="daily",
        description="운세 카테고리"
    )
    target_date: Optional[date_type] = Field(
        default=None,
        description="조회할 운세 날짜 (기본: 오늘)"
    )

    @field_validator("birth_datetime", mode="before")
    @classmethod
    def parse_birth_datetime(cls, v: str | datetime) -> datetime:
        """생년월일시 파싱 (문자열 또는 datetime 허용)"""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # 다양한 형식 지원
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"지원하지 않는 날짜 형식입니다: {v}")
        raise ValueError(f"잘못된 타입입니다: {type(v)}")


# =============================================================================
# LLM 응답 스키마 (Story 2.4 Task 5)
# =============================================================================

class LLMFortuneOutput(BaseModel):
    """
    LLM 응답 파싱용 스키마

    GPT-4o-mini의 JSON 응답을 파싱합니다.
    각 섹션은 50~150자 이내로 제한됩니다.
    """
    overall: str = Field(..., description="총운 (50~150자)")
    love: str = Field(..., description="애정운 (50~150자)")
    career: str = Field(..., description="직장운 (50~150자)")
    health: str = Field(..., description="건강운 (50~150자)")
    wealth: str = Field(..., description="재물운 (50~150자)")
    lucky_color: Optional[str] = Field(None, description="행운의 색상")
    lucky_number: Optional[int] = Field(None, ge=1, le=99, description="행운의 숫자 (1~99)")

    @field_validator("overall", "love", "career", "health", "wealth", mode="after")
    @classmethod
    def validate_length(cls, v: str) -> str:
        """섹션 길이 검증 (50~150자, 유연하게 처리)"""
        # LLM 응답이 범위를 벗어나도 서비스 중단 방지
        if len(v) < 10:
            return v + " 오늘 하루도 좋은 일이 있을 것입니다."
        if len(v) > 200:
            return v[:197] + "..."
        return v


# =============================================================================
# 응답 스키마 (확장)
# =============================================================================

class FortuneResponse(BaseModel):
    """
    운세 응답 스키마

    LLM 생성 또는 캐시된 운세 데이터를 담습니다.
    Story 2.4에서 luck_score, keywords, sipsung 필드 추가.
    """
    target_date: date_type = Field(..., alias="date", description="운세 대상 날짜")
    fortune_type: str = Field(..., description="운세 유형 (daily, weekly, monthly, yearly)")
    day_pillar: DayPillar = Field(..., description="일주 정보")
    overall: str = Field(..., description="총운")
    love: str = Field(..., description="애정운")
    career: str = Field(..., description="사업/직장운")
    health: str = Field(..., description="건강운")
    wealth: str = Field(..., description="재물운")
    lucky_color: Optional[str] = Field(None, description="행운의 색상")
    lucky_number: Optional[int] = Field(None, description="행운의 숫자")
    source: str = Field(default="llm", description="운세 출처 (llm | fallback | cache)")

    # Story 2.4 확장 필드
    luck_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="운세 점수 (1~5)"
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="핵심 키워드 목록"
    )
    sipsung: Optional[str] = Field(
        default=None,
        description="오늘의 십성 (비견, 겁재, 식신, ...)"
    )

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,  # Allow both alias and field name
    }
