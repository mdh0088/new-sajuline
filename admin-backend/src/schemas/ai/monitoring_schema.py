"""
AI 모니터링 스키마.

Stories: STORY-6-3
FRs: FR32
"""

from pydantic import BaseModel


class ViolationItem(BaseModel):
    """SLA 위반 항목"""

    metric: str
    severity: str
    message: str


class SLAStatusResponse(BaseModel):
    """SLA 상태 응답"""

    healthy: bool
    response_time_p95: float
    response_time_p99: float
    error_rate: float  # Percentage (0-100)
    llm_cost_month: float
    llm_cost_pct: float  # Percentage (0-100)
    violations: list[ViolationItem]


class ResponseTimeMetrics(BaseModel):
    """응답 시간 메트릭"""

    p50: float
    p95: float
    p99: float
    avg: float
    count: int


class LLMCostMetrics(BaseModel):
    """LLM 비용 메트릭"""

    total: float
    by_model: dict[str, float]


class MetricsResponse(BaseModel):
    """메트릭 응답"""

    response_time: ResponseTimeMetrics
    error_rate: float
    llm_cost: LLMCostMetrics
