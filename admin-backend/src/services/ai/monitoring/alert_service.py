"""
AI BI 어시스턴트 알림 서비스.

Slack, Sentry 등을 통해 SLA 위반 알림을 발송합니다.

Stories: STORY-6-3
FRs: FR32
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import httpx
import sentry_sdk
import structlog

from .sla_monitor import AlertSeverity, SLAViolation

logger = structlog.get_logger()


@dataclass
class AlertConfig:
    """알림 설정"""

    slack_webhook_url: Optional[str] = None
    email_recipients: list[str] = field(default_factory=list)
    sentry_dsn: Optional[str] = None
    cooldown_minutes: int = 15  # 동일 알림 쿨다운


class AlertService:
    """알림 서비스"""

    def __init__(self, config: AlertConfig):
        self.config = config
        self._last_alerts: dict[str, datetime] = {}

    async def send_alert(self, violation: SLAViolation):
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
                    ).seconds,
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
            message=violation.message,
        )

    async def _send_to_slack(self, violation: SLAViolation):
        """Slack 알림"""
        if not self.config.slack_webhook_url:
            return

        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨",
        }

        severity_color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9800",
            AlertSeverity.CRITICAL: "#f44336",
        }

        payload = {
            "attachments": [
                {
                    "color": severity_color[violation.severity],
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"{severity_emoji[violation.severity]} AI BI SLA Alert",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Metric:*\n{violation.metric_name}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Severity:*\n{violation.severity.value.upper()}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Current:*\n{violation.current_value}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Threshold:*\n{violation.threshold_value}",
                                },
                            ],
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Message:*\n{violation.message}",
                            },
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"Detected at: {violation.timestamp.isoformat()}",
                                }
                            ],
                        },
                    ],
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.config.slack_webhook_url, json=payload, timeout=10.0
                )
        except Exception as e:
            logger.error("slack_alert_failed", error=str(e))

    async def _send_to_sentry(self, violation: SLAViolation):
        """Sentry 이벤트 전송"""
        if not self.config.sentry_dsn:
            return

        with sentry_sdk.push_scope() as scope:
            scope.set_tag("sla_metric", violation.metric_name)
            scope.set_tag("severity", violation.severity.value)
            scope.set_extra("current_value", violation.current_value)
            scope.set_extra("threshold", violation.threshold_value)

            if violation.severity == AlertSeverity.CRITICAL:
                sentry_sdk.capture_message(violation.message, level="error")
            else:
                sentry_sdk.capture_message(violation.message, level="warning")
