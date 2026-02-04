"""
AI BI 어시스턴트 SLA 모니터링 서비스.

응답 시간, 에러율, LLM 비용 등의 SLA를 모니터링하고 위반 시 알림을 발송합니다.

Stories: STORY-6-3
FRs: FR32, NFR-O3, NFR-O4
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

import structlog

logger = structlog.get_logger()


class AlertSeverity(Enum):
    """알림 심각도"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SLAThreshold:
    """SLA 임계값 설정"""

    response_time_p95_ms: int = 3000  # p95 응답 시간 (3초)
    response_time_p99_ms: int = 5000  # p99 응답 시간 (5초)
    error_rate_warning: float = 0.05  # 에러율 경고 (5%)
    error_rate_critical: float = 0.10  # 에러율 위험 (10%)
    llm_cost_warning_pct: float = 0.80  # 비용 경고 (80%)
    llm_cost_critical_pct: float = 0.95  # 비용 위험 (95%)
    monthly_llm_budget: float = 1000.0  # 월 예산 ($)


@dataclass
class SLAViolation:
    """SLA 위반 이벤트"""

    metric_name: str
    current_value: float
    threshold_value: float
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SLAStatus:
    """현재 SLA 상태"""

    response_time_p95: float
    response_time_p99: float
    error_rate: float
    llm_cost_month: float
    llm_cost_pct: float
    violations: List[SLAViolation]
    healthy: bool


class SLAMonitor:
    """SLA 모니터링 서비스"""

    def __init__(
        self,
        metrics_collector: "MetricsCollector",
        alert_service: "AlertService",
        thresholds: SLAThreshold | None = None,
    ):
        self.metrics = metrics_collector
        self.alerts = alert_service
        self.thresholds = thresholds or SLAThreshold()
        self._monitoring = False

    async def check_sla(self) -> SLAStatus:
        """현재 SLA 상태 확인"""
        violations = []

        # 1. 응답 시간 확인
        response_times = await self.metrics.get_response_time_percentiles()
        p95 = response_times.get("p95", 0)
        p99 = response_times.get("p99", 0)

        if p95 > self.thresholds.response_time_p95_ms:
            violations.append(
                SLAViolation(
                    metric_name="response_time_p95",
                    current_value=p95,
                    threshold_value=self.thresholds.response_time_p95_ms,
                    severity=AlertSeverity.WARNING,
                    message=f"P95 응답 시간 SLA 위반: {p95}ms > {self.thresholds.response_time_p95_ms}ms",
                )
            )

        if p99 > self.thresholds.response_time_p99_ms:
            violations.append(
                SLAViolation(
                    metric_name="response_time_p99",
                    current_value=p99,
                    threshold_value=self.thresholds.response_time_p99_ms,
                    severity=AlertSeverity.CRITICAL,
                    message=f"P99 응답 시간 임계값 초과: {p99}ms > {self.thresholds.response_time_p99_ms}ms",
                )
            )

        # 2. 에러율 확인
        error_rate = await self.metrics.get_error_rate()

        if error_rate >= self.thresholds.error_rate_critical:
            violations.append(
                SLAViolation(
                    metric_name="error_rate",
                    current_value=error_rate,
                    threshold_value=self.thresholds.error_rate_critical,
                    severity=AlertSeverity.CRITICAL,
                    message=f"에러율 위험 수준: {error_rate*100:.1f}% >= {self.thresholds.error_rate_critical*100}%",
                )
            )
        elif error_rate >= self.thresholds.error_rate_warning:
            violations.append(
                SLAViolation(
                    metric_name="error_rate",
                    current_value=error_rate,
                    threshold_value=self.thresholds.error_rate_warning,
                    severity=AlertSeverity.WARNING,
                    message=f"에러율 경고: {error_rate*100:.1f}% >= {self.thresholds.error_rate_warning*100}%",
                )
            )

        # 3. LLM 비용 확인
        llm_cost = await self.metrics.get_monthly_llm_cost()

        # Division by zero 방지
        if self.thresholds.monthly_llm_budget <= 0:
            logger.warning("llm_budget_not_set", budget=self.thresholds.monthly_llm_budget)
            cost_pct = 0.0
        else:
            cost_pct = llm_cost / self.thresholds.monthly_llm_budget

        if cost_pct >= self.thresholds.llm_cost_critical_pct:
            violations.append(
                SLAViolation(
                    metric_name="llm_cost",
                    current_value=llm_cost,
                    threshold_value=self.thresholds.monthly_llm_budget
                    * self.thresholds.llm_cost_critical_pct,
                    severity=AlertSeverity.CRITICAL,
                    message=f"LLM 비용 위험: ${llm_cost:.2f} ({cost_pct*100:.0f}% of budget)",
                )
            )
        elif cost_pct >= self.thresholds.llm_cost_warning_pct:
            violations.append(
                SLAViolation(
                    metric_name="llm_cost",
                    current_value=llm_cost,
                    threshold_value=self.thresholds.monthly_llm_budget
                    * self.thresholds.llm_cost_warning_pct,
                    severity=AlertSeverity.WARNING,
                    message=f"LLM 비용 경고: ${llm_cost:.2f} ({cost_pct*100:.0f}% of budget)",
                )
            )

        # 위반 사항 알림 발송
        for violation in violations:
            await self.alerts.send_alert(violation)

        return SLAStatus(
            response_time_p95=p95,
            response_time_p99=p99,
            error_rate=error_rate,
            llm_cost_month=llm_cost,
            llm_cost_pct=cost_pct,
            violations=violations,
            healthy=len(violations) == 0,
        )

    async def start_monitoring(self, interval_seconds: int = 60):
        """주기적 모니터링 시작"""
        self._monitoring = True
        logger.info("sla_monitoring_started", interval=interval_seconds)

        while self._monitoring:
            try:
                status = await self.check_sla()
                if not status.healthy:
                    logger.warning(
                        "sla_violations_detected",
                        violations_count=len(status.violations),
                    )
            except Exception as e:
                logger.error("sla_check_error", error=str(e))

            await asyncio.sleep(interval_seconds)

    def stop_monitoring(self):
        """모니터링 중지"""
        self._monitoring = False
        logger.info("sla_monitoring_stopped")
