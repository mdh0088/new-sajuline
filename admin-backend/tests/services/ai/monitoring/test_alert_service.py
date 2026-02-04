"""
AlertService 단위 테스트.

Stories: STORY-6-3
FRs: FR32
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.ai.monitoring.alert_service import AlertConfig, AlertService
from src.services.ai.monitoring.sla_monitor import AlertSeverity, SLAViolation


class TestAlertService:
    """AlertService 테스트"""

    @pytest.fixture
    def config(self):
        """Alert 설정"""
        return AlertConfig(
            slack_webhook_url="https://hooks.slack.com/test",
            sentry_dsn="https://test@sentry.io/123",
            cooldown_minutes=15,
        )

    @pytest.fixture
    def alert_service(self, config):
        """AlertService 인스턴스"""
        return AlertService(config)

    @pytest.fixture
    def sample_violation(self):
        """샘플 SLA 위반"""
        return SLAViolation(
            metric_name="response_time_p95",
            current_value=3500.0,
            threshold_value=3000.0,
            severity=AlertSeverity.WARNING,
            message="P95 응답 시간 SLA 위반: 3500ms > 3000ms",
        )

    @pytest.mark.asyncio
    async def test_send_alert_to_slack(self, alert_service, sample_violation):
        """Slack 알림 발송"""
        # Given
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock()
            mock_client_class.return_value = mock_client

            # When
            await alert_service.send_alert(sample_violation)

            # Then
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://hooks.slack.com/test"
            assert "json" in call_args[1]
            payload = call_args[1]["json"]
            assert "attachments" in payload

    @pytest.mark.asyncio
    async def test_send_alert_to_sentry(self, alert_service, sample_violation):
        """Sentry 알림 발송"""
        # Given
        with patch("sentry_sdk.capture_message") as mock_capture:
            with patch("sentry_sdk.push_scope") as mock_scope:
                # When
                await alert_service.send_alert(sample_violation)

                # Then
                mock_capture.assert_called_once()
                assert mock_capture.call_args[1]["level"] == "warning"

    @pytest.mark.asyncio
    async def test_send_alert_critical_to_sentry(self, alert_service):
        """Sentry CRITICAL 알림"""
        # Given
        critical_violation = SLAViolation(
            metric_name="error_rate",
            current_value=0.15,
            threshold_value=0.10,
            severity=AlertSeverity.CRITICAL,
            message="에러율 위험 수준: 15% >= 10%",
        )

        with patch("sentry_sdk.capture_message") as mock_capture:
            with patch("sentry_sdk.push_scope"):
                # When
                await alert_service.send_alert(critical_violation)

                # Then
                assert mock_capture.call_args[1]["level"] == "error"

    @pytest.mark.asyncio
    async def test_alert_cooldown(self, alert_service, sample_violation):
        """알림 쿨다운 (15분 이내 중복 알림 방지)"""
        # Given
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock()
            mock_client_class.return_value = mock_client

            # When - 첫 번째 알림
            await alert_service.send_alert(sample_violation)
            first_call_count = mock_client.post.call_count

            # When - 바로 다시 알림 (쿨다운 적용)
            await alert_service.send_alert(sample_violation)
            second_call_count = mock_client.post.call_count

            # Then
            assert first_call_count == 1
            assert second_call_count == 1  # 증가하지 않음 (쿨다운)

    @pytest.mark.asyncio
    async def test_alert_after_cooldown_expired(self, alert_service, sample_violation):
        """쿨다운 만료 후 알림 재발송"""
        # Given
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock()
            mock_client_class.return_value = mock_client

            # When - 첫 번째 알림
            await alert_service.send_alert(sample_violation)

            # Given - 쿨다운 시간 조작 (16분 전으로 설정)
            alert_key = (
                f"{sample_violation.metric_name}:{sample_violation.severity.value}"
            )
            alert_service._last_alerts[alert_key] = datetime.utcnow() - timedelta(
                minutes=16
            )

            # When - 쿨다운 만료 후 재발송
            await alert_service.send_alert(sample_violation)

            # Then
            assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_slack_alert_failure_handling(self, alert_service, sample_violation):
        """Slack 알림 실패 처리"""
        # Given
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(
                side_effect=httpx.RequestError("Network error")
            )
            mock_client_class.return_value = mock_client

            # When/Then - 예외 발생하지 않아야 함
            await alert_service.send_alert(sample_violation)

    def test_alert_config_defaults(self):
        """AlertConfig 기본값 확인"""
        # Given/When
        config = AlertConfig()

        # Then
        assert config.slack_webhook_url is None
        assert config.sentry_dsn is None
        assert config.email_recipients is None
        assert config.cooldown_minutes == 15

    def test_alert_config_custom(self):
        """AlertConfig 커스터마이징"""
        # Given/When
        config = AlertConfig(
            slack_webhook_url="https://custom.slack.com",
            cooldown_minutes=30,
            email_recipients=["admin@example.com"],
        )

        # Then
        assert config.slack_webhook_url == "https://custom.slack.com"
        assert config.cooldown_minutes == 30
        assert config.email_recipients == ["admin@example.com"]
