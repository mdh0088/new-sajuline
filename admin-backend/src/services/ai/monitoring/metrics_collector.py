"""
AI BI 어시스턴트 메트릭 수집기.

Redis를 사용하여 응답 시간, 에러율, LLM 비용 등을 추적합니다.

Stories: STORY-6-3
FRs: FR32
"""

import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict

import redis.asyncio as redis


@dataclass
class MetricPoint:
    """메트릭 데이터 포인트"""

    timestamp: datetime
    value: float
    labels: Dict[str, str] | None = None


class MetricsCollector:
    """메트릭 수집기"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "ai_metrics"

    async def record_response_time(
        self, response_time_ms: float, success: bool, model: str
    ):
        """응답 시간 기록"""
        now = datetime.utcnow()
        minute_key = now.strftime("%Y%m%d%H%M")

        # 응답 시간 리스트에 추가 (90분 보관 - 조회 범위 60분 + 여유)
        key = f"{self.prefix}:response_time:{minute_key}"
        await self.redis.lpush(key, response_time_ms)
        await self.redis.expire(key, 5400)  # 90분 = 5400초

        # 성공/실패 카운트
        status = "success" if success else "error"
        await self.redis.hincrby(f"{self.prefix}:counts:{minute_key}", status, 1)
        await self.redis.expire(f"{self.prefix}:counts:{minute_key}", 5400)  # 90분

    async def record_llm_cost(self, cost: float, model: str):
        """LLM 비용 기록"""
        month_key = datetime.utcnow().strftime("%Y%m")
        await self.redis.hincrbyfloat(
            f"{self.prefix}:llm_cost:{month_key}", "total", cost
        )
        await self.redis.hincrbyfloat(
            f"{self.prefix}:llm_cost:{month_key}", model, cost
        )

    async def get_response_time_percentiles(
        self, window_minutes: int = 60
    ) -> Dict[str, float]:
        """응답 시간 백분위수 계산"""
        now = datetime.utcnow()
        all_times = []

        for i in range(window_minutes):
            minute = now - timedelta(minutes=i)
            key = f"{self.prefix}:response_time:{minute.strftime('%Y%m%d%H%M')}"
            times = await self.redis.lrange(key, 0, -1)
            all_times.extend([float(t) for t in times])

        if not all_times:
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0}

        sorted_times = sorted(all_times)
        n = len(sorted_times)

        # 정확한 백분위수 계산 (index는 0부터 시작하므로 -1 필요)
        def percentile_index(pct: float) -> int:
            """백분위수에 해당하는 인덱스 계산"""
            return max(0, min(n - 1, math.ceil(n * pct) - 1))

        return {
            "p50": sorted_times[percentile_index(0.50)] if n > 0 else 0,
            "p95": sorted_times[percentile_index(0.95)] if n > 0 else 0,
            "p99": sorted_times[percentile_index(0.99)] if n > 0 else 0,
            "avg": statistics.mean(all_times),
            "count": n,
        }

    async def get_error_rate(self, window_minutes: int = 60) -> float:
        """에러율 계산"""
        now = datetime.utcnow()
        total_success = 0
        total_error = 0

        for i in range(window_minutes):
            minute = now - timedelta(minutes=i)
            key = f"{self.prefix}:counts:{minute.strftime('%Y%m%d%H%M')}"
            counts = await self.redis.hgetall(key)
            total_success += int(counts.get(b"success", 0))
            total_error += int(counts.get(b"error", 0))

        total = total_success + total_error
        if total == 0:
            return 0.0

        return total_error / total

    async def get_monthly_llm_cost(self) -> float:
        """월간 LLM 비용 조회"""
        month_key = datetime.utcnow().strftime("%Y%m")
        cost = await self.redis.hget(f"{self.prefix}:llm_cost:{month_key}", "total")
        return float(cost) if cost else 0.0

    async def get_llm_cost_by_model(self) -> Dict[str, float]:
        """모델별 LLM 비용 조회"""
        month_key = datetime.utcnow().strftime("%Y%m")
        costs = await self.redis.hgetall(f"{self.prefix}:llm_cost:{month_key}")
        return {k.decode(): float(v) for k, v in costs.items() if k != b"total"}
