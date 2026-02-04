"""
SLAMonitor 단위 테스트.

Stories: STORY-6-3
FRs: FR32, NFR-O3, NFR-O4
"""

from dataclasses import asdict
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.ai.monitoring.sla_monitor import (
    AlertSeverity,
    SLAMonitor,
    SLAStatus,
    SLAThreshold,
    SLAViolation,
)


class TestSLAMonitor:
    """SLAMonitor 테스트"""

    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock MetricsCollector"""
        mock = AsyncMock()
        mock.get_response_time_percentiles = AsyncMock(
            return_value={"p95": 2000, "p99": 3000}
        )
        mock.get_error_rate = AsyncMock(return_value=0.01)
        mock.get_monthly_llm_cost = AsyncMock(return_value=500.0)
        return mock

    @pytest.fixture
    def mock_alert_service(self):
        """Mock AlertService"""
        mock = AsyncMock()
        mock.send_alert = AsyncMock()
        return mock

    @pytest.fixture
    def default_thresholds(self):
        """기본 임계값"""
        return SLAThreshold()

    @pytest.fixture
    def monitor(self, mock_metrics_collector, mock_alert_service, default_thresholds):
        """SLAMonitor 인스턴스"""
        return SLAMonitor(
            mock_metrics_collector, mock_alert_service, default_thresholds
        )

    @pytest.mark.asyncio
    async def test_check_sla_all_healthy(self, monitor, mock_alert_service):
        """SLA 확인 (모든 지표 정상)"""
        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is True
        assert len(status.violations) == 0
        mock_alert_service.send_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_sla_response_time_p95_violation(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """P95 응답 시간 SLA 위반"""
        # Given
        mock_metrics_collector.get_response_time_percentiles.return_value = {
            "p95": 3500,  # > 3000ms 임계값
            "p99": 4000,
        }

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        assert len(status.violations) >= 1
        assert any(v.metric_name == "response_time_p95" for v in status.violations)

        p95_violation = next(
            v for v in status.violations if v.metric_name == "response_time_p95"
        )
        assert p95_violation.severity == AlertSeverity.WARNING
        assert p95_violation.current_value == 3500
        mock_alert_service.send_alert.assert_called()

    @pytest.mark.asyncio
    async def test_check_sla_response_time_p99_violation(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """P99 응답 시간 임계값 초과"""
        # Given
        mock_metrics_collector.get_response_time_percentiles.return_value = {
            "p95": 2500,
            "p99": 6000,  # > 5000ms 임계값
        }

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        p99_violation = next(
            v for v in status.violations if v.metric_name == "response_time_p99"
        )
        assert p99_violation.severity == AlertSeverity.CRITICAL
        assert p99_violation.current_value == 6000

    @pytest.mark.asyncio
    async def test_check_sla_error_rate_warning(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """에러율 경고 임계값 초과"""
        # Given
        mock_metrics_collector.get_error_rate.return_value = 0.07  # 7% > 5% 경고

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        error_violation = next(
            v for v in status.violations if v.metric_name == "error_rate"
        )
        assert error_violation.severity == AlertSeverity.WARNING
        assert error_violation.current_value == 0.07

    @pytest.mark.asyncio
    async def test_check_sla_error_rate_critical(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """에러율 위험 임계값 초과"""
        # Given
        mock_metrics_collector.get_error_rate.return_value = 0.12  # 12% > 10% 위험

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        error_violation = next(
            v for v in status.violations if v.metric_name == "error_rate"
        )
        assert error_violation.severity == AlertSeverity.CRITICAL
        assert error_violation.current_value == 0.12

    @pytest.mark.asyncio
    async def test_check_sla_llm_cost_warning(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """LLM 비용 경고 (80% 초과)"""
        # Given
        mock_metrics_collector.get_monthly_llm_cost.return_value = 850.0  # 85% of $1000

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        cost_violation = next(
            v for v in status.violations if v.metric_name == "llm_cost"
        )
        assert cost_violation.severity == AlertSeverity.WARNING
        assert cost_violation.current_value == 850.0
        assert status.llm_cost_pct == 0.85

    @pytest.mark.asyncio
    async def test_check_sla_llm_cost_critical(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """LLM 비용 위험 (95% 초과)"""
        # Given
        mock_metrics_collector.get_monthly_llm_cost.return_value = 980.0  # 98% of $1000

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        cost_violation = next(
            v for v in status.violations if v.metric_name == "llm_cost"
        )
        assert cost_violation.severity == AlertSeverity.CRITICAL
        assert cost_violation.current_value == 980.0

    @pytest.mark.asyncio
    async def test_check_sla_multiple_violations(
        self, monitor, mock_metrics_collector, mock_alert_service
    ):
        """다중 SLA 위반"""
        # Given
        mock_metrics_collector.get_response_time_percentiles.return_value = {
            "p95": 3500,  # 위반
            "p99": 4000,
        }
        mock_metrics_collector.get_error_rate.return_value = 0.08  # 위반
        mock_metrics_collector.get_monthly_llm_cost.return_value = 850.0  # 위반

        # When
        status = await monitor.check_sla()

        # Then
        assert status.healthy is False
        assert len(status.violations) == 3
        assert mock_alert_service.send_alert.call_count == 3

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, monitor):
        """모니터링 시작/중지"""
        # Given
        monitor._monitoring = False

        # When
        import asyncio

        task = asyncio.create_task(monitor.start_monitoring(interval_seconds=1))
        await asyncio.sleep(0.1)  # 모니터링 시작 대기
        monitor.stop_monitoring()
        await asyncio.sleep(0.1)  # 종료 대기

        # Then
        assert monitor._monitoring is False
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def test_sla_threshold_defaults(self):
        """SLA 임계값 기본값 확인"""
        # Given/When
        threshold = SLAThreshold()

        # Then
        assert threshold.response_time_p95_ms == 3000
        assert threshold.response_time_p99_ms == 5000
        assert threshold.error_rate_warning == 0.05
        assert threshold.error_rate_critical == 0.10
        assert threshold.llm_cost_warning_pct == 0.80
        assert threshold.llm_cost_critical_pct == 0.95
        assert threshold.monthly_llm_budget == 1000.0

    def test_sla_threshold_custom(self):
        """SLA 임계값 커스터마이징"""
        # Given/When
        threshold = SLAThreshold(response_time_p95_ms=2000, monthly_llm_budget=5000.0)

        # Then
        assert threshold.response_time_p95_ms == 2000
        assert threshold.monthly_llm_budget == 5000.0
