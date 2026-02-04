"""
자동완성 스키마.

Stories: 4-3
FRs: FR22
"""
from pydantic import BaseModel, Field


class AutocompleteResponse(BaseModel):
    """자동완성 응답.

    AC1: 실시간 자동완성 제안
    AC2: 자주 사용된 질문 우선 제안
    AC3: 테이블/컬럼 이름 포함
    """

    suggestions: list[str] = Field(
        description="자동완성 제안 목록",
        examples=[["오늘 가입자 수는?", "이번 달 매출"]],
    )
    query: str = Field(description="검색 쿼리")
    count: int = Field(description="제안 개수")


class CacheHitRateResponse(BaseModel):
    """캐시 히트율 응답.

    AC5: 캐시 히트율이 30% 이상이다
    """

    hit_rate: float = Field(description="캐시 히트율 (0.0 ~ 1.0)")
    threshold_met: bool = Field(description="30% 임계값 충족 여부")
    total_requests: int = Field(description="총 요청 수")
    cache_hits: int = Field(description="캐시 히트 수")
