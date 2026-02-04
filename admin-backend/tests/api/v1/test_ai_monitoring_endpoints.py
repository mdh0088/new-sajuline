"""
AI Monitoring API 엔드포인트 통합 테스트.

Stories: STORY-6-3
FRs: FR32
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.ai.monitoring.alert_service import AlertConfig, AlertService
from src.services.ai.monitoring.metrics_collector import MetricsCollector
from src.services.ai.monitoring.sla_monitor import (
    AlertSeverity,
    SLAMonitor,
    SLAStatus,
    SLAViolation,
)


class TestAIMonitoringLogic:
    """AI Monitoring 로직 테스트 (API 통합 없이)"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis 클라이언트"""
        mock = AsyncMock()
        mock.lpush = AsyncMock(return_value=1)
        mock.expire = AsyncMock(return_value=True)
        mock.hincrby = AsyncMock(return_value=1)
        mock.hincrbyfloat = AsyncMock(return_value=1.0)
        mock.lrange = AsyncMock(return_value=[])
        mock.hgetall = AsyncMock(return_value={})
        mock.hget = AsyncMock(return_value=None)
        return mock

    @pytest.mark.asyncio
    async def test_monitoring_integration(self, mock_redis):
        """모니터링 컴포넌트 통합 테스트"""
        # Given - 메트릭 수집기 준비 (정상 범위 데이터)
        mock_redis.lrange.return_value = [
            str(1500 + i * 10).encode() for i in range(100)
        ]  # 1500~2490ms
        mock_redis.hgetall.return_value = {b"success": b"98", b"error": b"2"}
        mock_redis.hget.return_value = b"500.0"

        # Given - 모니터링 서비스 초기화
        metrics = MetricsCollector(mock_redis)
        alerts = AlertService(AlertConfig())
        monitor = SLAMonitor(metrics, alerts)

        # When - SLA 확인
        status = await monitor.check_sla()

        # Then - 상태 검증
        assert status is not None
        assert status.healthy is True
        assert status.response_time_p95 > 0
        assert status.error_rate == 0.02  # 2/100
        assert status.llm_cost_month == 500.0

    @pytest.mark.asyncio
    async def test_sla_violation_detection(self, mock_redis):
        """SLA 위반 감지 테스트"""
        # Given - 높은 응답 시간 설정
        mock_redis.lrange.return_value = [str(4000).encode() for _ in range(100)]
        mock_redis.hgetall.return_value = {b"success": b"100"}
        mock_redis.hget.return_value = b"100.0"

        # Given - 모니터링 서비스
        metrics = MetricsCollector(mock_redis)
        alerts = AlertService(AlertConfig())
        monitor = SLAMonitor(metrics, alerts)

        # When
        status = await monitor.check_sla()

        # Then - 위반 감지
        assert status.healthy is False
        assert len(status.violations) > 0
        assert any(v.metric_name == "response_time_p95" for v in status.violations)

    @pytest.mark.asyncio
    async def test_metric_collection(self, mock_redis):
        """메트릭 수집 통합 테스트"""
        # Given
        collector = MetricsCollector(mock_redis)

        # When - 메트릭 기록
        await collector.record_response_time(
            response_time_ms=2000.0, success=True, model="gpt-4o-mini"
        )
        await collector.record_llm_cost(0.05, "gpt-4o-mini")

        # Then - Redis 호출 검증
        assert mock_redis.lpush.called
        assert mock_redis.hincrbyfloat.called
