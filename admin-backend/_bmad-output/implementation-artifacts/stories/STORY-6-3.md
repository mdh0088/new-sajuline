# STORY-6-3: SLA 모니터링 및 알림

**Epic:** Epic 6 - 시스템 안정성 및 운영 (System Reliability & Operations)
**Priority:** P1 - Phase 1.5
**Story Points:** 5
**Status:** Ready for Dev
**Assigned To:** Unassigned
**Created:** 2026-02-02
**Sprint:** 2 (Phase 1.5)

---

## User Story

As a 시스템 관리자
I want SLA 위반 시 알림을 받기를
So that 서비스 문제를 빠르게 인지하고 대응할 수 있다

---

## Description

### Background

AI BI 어시스턴트의 서비스 품질을 보장하기 위해 SLA(Service Level Agreement) 모니터링이 필요합니다. 응답 시간, 에러율, LLM 비용 등 핵심 지표를 추적하고 임계값 초과 시 즉시 알림을 발송합니다.

### Scope

**In scope:**
- 응답 시간 SLA (p95 3초) 모니터링
- 에러율 임계값 모니터링
- LLM 비용 월 상한 알림
- Slack/이메일 알림 지원
- Sentry 연동

**Out of scope:**
- 메트릭 대시보드 UI (Phase 2)
- 자동 스케일링 트리거

---

## Acceptance Criteria

- [ ] 응답 시간 SLA (p95 3초) 위반이 감지된다
- [ ] 에러율 임계값 초과가 감지된다
- [ ] LLM 비용 월 상한 도달 시 알림이 발송된다
- [ ] Slack/이메일 알림이 지원된다
- [ ] 메트릭 대시보드가 제공된다 (Phase 1.5)

---

## Technical Notes

### Components

- **Backend:**
  - `src/services/ai/monitoring/sla_monitor.py` - SLA 모니터링
  - `src/services/ai/monitoring/metrics_collector.py` - 메트릭 수집
  - `src/services/ai/monitoring/alert_service.py` - 알림 서비스
  - Sentry 연동

### SLA Monitor Implementation

```python
# src/services/ai/monitoring/sla_monitor.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class SLAThreshold:
    """SLA 임계값 설정"""
    response_time_p95_ms: int = 3000     # p95 응답 시간 (3초)
    response_time_p99_ms: int = 5000     # p99 응답 시간 (5초)
    error_rate_warning: float = 0.05     # 에러율 경고 (5%)
    error_rate_critical: float = 0.10    # 에러율 위험 (10%)
    llm_cost_warning_pct: float = 0.80   # 비용 경고 (80%)
    llm_cost_critical_pct: float = 0.95  # 비용 위험 (95%)
    monthly_llm_budget: float = 1000.0   # 월 예산 ($)

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
        thresholds: SLAThreshold | None = None
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
            violations.append(SLAViolation(
                metric_name="response_time_p95",
                current_value=p95,
                threshold_value=self.thresholds.response_time_p95_ms,
                severity=AlertSeverity.WARNING,
                message=f"P95 응답 시간 SLA 위반: {p95}ms > {self.thresholds.response_time_p95_ms}ms"
            ))

        if p99 > self.thresholds.response_time_p99_ms:
            violations.append(SLAViolation(
                metric_name="response_time_p99",
                current_value=p99,
                threshold_value=self.thresholds.response_time_p99_ms,
                severity=AlertSeverity.CRITICAL,
                message=f"P99 응답 시간 임계값 초과: {p99}ms > {self.thresholds.response_time_p99_ms}ms"
            ))

        # 2. 에러율 확인
        error_rate = await self.metrics.get_error_rate()

        if error_rate >= self.thresholds.error_rate_critical:
            violations.append(SLAViolation(
                metric_name="error_rate",
                current_value=error_rate,
                threshold_value=self.thresholds.error_rate_critical,
                severity=AlertSeverity.CRITICAL,
                message=f"에러율 위험 수준: {error_rate*100:.1f}% >= {self.thresholds.error_rate_critical*100}%"
            ))
        elif error_rate >= self.thresholds.error_rate_warning:
            violations.append(SLAViolation(
                metric_name="error_rate",
                current_value=error_rate,
                threshold_value=self.thresholds.error_rate_warning,
                severity=AlertSeverity.WARNING,
                message=f"에러율 경고: {error_rate*100:.1f}% >= {self.thresholds.error_rate_warning*100}%"
            ))

        # 3. LLM 비용 확인
        llm_cost = await self.metrics.get_monthly_llm_cost()
        cost_pct = llm_cost / self.thresholds.monthly_llm_budget

        if cost_pct >= self.thresholds.llm_cost_critical_pct:
            violations.append(SLAViolation(
                metric_name="llm_cost",
                current_value=llm_cost,
                threshold_value=self.thresholds.monthly_llm_budget * self.thresholds.llm_cost_critical_pct,
                severity=AlertSeverity.CRITICAL,
                message=f"LLM 비용 위험: ${llm_cost:.2f} ({cost_pct*100:.0f}% of budget)"
            ))
        elif cost_pct >= self.thresholds.llm_cost_warning_pct:
            violations.append(SLAViolation(
                metric_name="llm_cost",
                current_value=llm_cost,
                threshold_value=self.thresholds.monthly_llm_budget * self.thresholds.llm_cost_warning_pct,
                severity=AlertSeverity.WARNING,
                message=f"LLM 비용 경고: ${llm_cost:.2f} ({cost_pct*100:.0f}% of budget)"
            ))

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
            healthy=len(violations) == 0
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
                        violations_count=len(status.violations)
                    )
            except Exception as e:
                logger.error("sla_check_error", error=str(e))

            await asyncio.sleep(interval_seconds)

    def stop_monitoring(self):
        """모니터링 중지"""
        self._monitoring = False
        logger.info("sla_monitoring_stopped")
```

### Metrics Collector

```python
# src/services/ai/monitoring/metrics_collector.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
import redis.asyncio as redis
import statistics

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: Dict[str, str] = None

class MetricsCollector:
    """메트릭 수집기"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "ai_metrics"

    async def record_response_time(
        self,
        response_time_ms: float,
        success: bool,
        model: str
    ):
        """응답 시간 기록"""
        now = datetime.utcnow()
        minute_key = now.strftime("%Y%m%d%H%M")

        # 응답 시간 리스트에 추가 (1시간 보관)
        key = f"{self.prefix}:response_time:{minute_key}"
        await self.redis.lpush(key, response_time_ms)
        await self.redis.expire(key, 3600)

        # 성공/실패 카운트
        status = "success" if success else "error"
        await self.redis.hincrby(
            f"{self.prefix}:counts:{minute_key}",
            status, 1
        )
        await self.redis.expire(f"{self.prefix}:counts:{minute_key}", 3600)

    async def record_llm_cost(self, cost: float, model: str):
        """LLM 비용 기록"""
        month_key = datetime.utcnow().strftime("%Y%m")
        await self.redis.hincrbyfloat(
            f"{self.prefix}:llm_cost:{month_key}",
            "total", cost
        )
        await self.redis.hincrbyfloat(
            f"{self.prefix}:llm_cost:{month_key}",
            model, cost
        )

    async def get_response_time_percentiles(
        self,
        window_minutes: int = 60
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
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}

        sorted_times = sorted(all_times)
        n = len(sorted_times)

        return {
            "p50": sorted_times[int(n * 0.50)] if n > 0 else 0,
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_times[int(n * 0.99)] if n > 0 else 0,
            "avg": statistics.mean(all_times),
            "count": n
        }

    async def get_error_rate(
        self,
        window_minutes: int = 60
    ) -> float:
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
        cost = await self.redis.hget(
            f"{self.prefix}:llm_cost:{month_key}",
            "total"
        )
        return float(cost) if cost else 0.0

    async def get_llm_cost_by_model(self) -> Dict[str, float]:
        """모델별 LLM 비용 조회"""
        month_key = datetime.utcnow().strftime("%Y%m")
        costs = await self.redis.hgetall(f"{self.prefix}:llm_cost:{month_key}")
        return {
            k.decode(): float(v)
            for k, v in costs.items()
            if k != b"total"
        }
```

### Alert Service

```python
# src/services/ai/monitoring/alert_service.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import httpx
import structlog
import sentry_sdk

logger = structlog.get_logger()

@dataclass
class AlertConfig:
    slack_webhook_url: Optional[str] = None
    email_recipients: list[str] = None
    sentry_dsn: Optional[str] = None
    cooldown_minutes: int = 15  # 동일 알림 쿨다운

class AlertService:
    """알림 서비스"""

    def __init__(self, config: AlertConfig):
        self.config = config
        self._last_alerts: dict[str, datetime] = {}

    async def send_alert(self, violation: "SLAViolation"):
        """알림 발송"""
        # 쿨다운 확인
        alert_key = f"{violation.metric_name}:{violation.severity.value}"
        if alert_key in self._last_alerts:
            elapsed = datetime.utcnow() - self._last_alerts[alert_key]
            if elapsed < timedelta(minutes=self.config.cooldown_minutes):
                logger.debug(
                    "alert_cooldown",
                    key=alert_key,
                    remaining_seconds=(
                        timedelta(minutes=self.config.cooldown_minutes) - elapsed
                    ).seconds
                )
                return

        self._last_alerts[alert_key] = datetime.utcnow()

        # 다중 채널 알림
        await self._send_to_slack(violation)
        await self._send_to_sentry(violation)
        # await self._send_email(violation)  # Phase 2

        logger.info(
            "alert_sent",
            metric=violation.metric_name,
            severity=violation.severity.value,
            message=violation.message
        )

    async def _send_to_slack(self, violation: "SLAViolation"):
        """Slack 알림"""
        if not self.config.slack_webhook_url:
            return

        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨"
        }

        severity_color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9800",
            AlertSeverity.CRITICAL: "#f44336"
        }

        payload = {
            "attachments": [{
                "color": severity_color[violation.severity],
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{severity_emoji[violation.severity]} AI BI SLA Alert"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Metric:*\n{violation.metric_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:*\n{violation.severity.value.upper()}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Current:*\n{violation.current_value}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Threshold:*\n{violation.threshold_value}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:*\n{violation.message}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"Detected at: {violation.timestamp.isoformat()}"
                        }]
                    }
                ]
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.config.slack_webhook_url,
                    json=payload,
                    timeout=10.0
                )
        except Exception as e:
            logger.error("slack_alert_failed", error=str(e))

    async def _send_to_sentry(self, violation: "SLAViolation"):
        """Sentry 이벤트 전송"""
        if not self.config.sentry_dsn:
            return

        with sentry_sdk.push_scope() as scope:
            scope.set_tag("sla_metric", violation.metric_name)
            scope.set_tag("severity", violation.severity.value)
            scope.set_extra("current_value", violation.current_value)
            scope.set_extra("threshold", violation.threshold_value)

            if violation.severity == AlertSeverity.CRITICAL:
                sentry_sdk.capture_message(
                    violation.message,
                    level="error"
                )
            else:
                sentry_sdk.capture_message(
                    violation.message,
                    level="warning"
                )
```

### API Endpoints

```python
# src/api/v1/ai_assistant_api.py 확장
@router.get("/monitoring/sla", response_model=SLAStatusResponse)
async def get_sla_status(
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis = Depends(get_redis),
):
    """현재 SLA 상태 조회"""
    metrics = MetricsCollector(redis_client)
    alerts = AlertService(AlertConfig())
    monitor = SLAMonitor(metrics, alerts)

    status = await monitor.check_sla()
    return SLAStatusResponse(
        healthy=status.healthy,
        response_time_p95=status.response_time_p95,
        response_time_p99=status.response_time_p99,
        error_rate=status.error_rate * 100,
        llm_cost_month=status.llm_cost_month,
        llm_cost_pct=status.llm_cost_pct * 100,
        violations=[
            ViolationItem(
                metric=v.metric_name,
                severity=v.severity.value,
                message=v.message
            )
            for v in status.violations
        ]
    )

@router.get("/monitoring/metrics")
async def get_metrics(
    window_minutes: int = Query(default=60, le=1440),
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis = Depends(get_redis),
):
    """상세 메트릭 조회"""
    metrics = MetricsCollector(redis_client)

    return {
        "response_time": await metrics.get_response_time_percentiles(window_minutes),
        "error_rate": await metrics.get_error_rate(window_minutes),
        "llm_cost": {
            "total": await metrics.get_monthly_llm_cost(),
            "by_model": await metrics.get_llm_cost_by_model()
        }
    }
```

---

## Dependencies

**Prerequisite Stories:**
- Story 6-1: LLM Fallback 및 Circuit Breaker

**Blocked Stories:**
- 없음

**External Dependencies:**
- Redis (메트릭 저장)
- Slack (알림)
- Sentry (에러 추적)

---

## Definition of Done

- [ ] 코드 구현 완료
  - [ ] SLA Monitor (`sla_monitor.py`)
  - [ ] Metrics Collector (`metrics_collector.py`)
  - [ ] Alert Service (`alert_service.py`)
  - [ ] API 엔드포인트
- [ ] 단위 테스트 작성 및 통과 (≥80% 커버리지)
  - [ ] SLA 위반 감지 테스트
  - [ ] 메트릭 수집 테스트
  - [ ] 알림 발송 테스트
- [ ] 통합 테스트 통과
- [ ] Slack 알림 테스트 완료
- [ ] 코드 리뷰 완료
- [ ] 스테이징 환경 배포 완료

---

## Story Points Breakdown

- **SLA Monitor:** 1.5 points
- **Metrics Collector:** 1.5 points
- **Alert Service:** 1 point
- **테스트:** 1 point
- **Total:** 5 points

---

## Additional Notes

### NFR 관련

- **FR32**: SLA 알림 ✓
- **NFR-O3**: SLA 위반 시 즉시 알림 ✓
- **NFR-O4**: LLM 비용 월 상한 알림 ✓
- **AR21-AR23**: 테스트 패턴, Golden Dataset ✓

### SLA 지표

| 지표 | 목표 | 경고 임계값 | 위험 임계값 |
|------|------|------------|------------|
| P95 응답 시간 | ≤ 3초 | 3초 | 5초 |
| 에러율 | < 1% | 5% | 10% |
| LLM 비용 | 월 $1,000 | 80% | 95% |

### 모니터링 간격

- **실시간**: 응답 시간, 에러율 (1분 단위)
- **배치**: LLM 비용 (1시간 단위)
- **알림 쿨다운**: 동일 알림 15분

---

## Progress Tracking

**Status History:**
- 2026-02-02: Created by SM

**Actual Effort:** TBD

---

**This story was created using BMAD Method v6 - Phase 4 (Implementation Planning)**
