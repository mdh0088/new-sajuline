"""
도메인 이벤트 로깅 헬퍼

일관된 스키마와 로거 네임스페이스를 제공하여 주요 비즈니스 이벤트를 기록합니다.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .config import get_logger


MASK_KEYS = {"password", "token", "authorization", "cookie", "ssn", "email"}


def _mask(ctx: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return {k: ("****" if k.lower() in MASK_KEYS else v) for k, v in ctx.items()}
    except Exception:
        return ctx


def log_event(
    event: str,
    *,
    domain: str = "app",
    level: str = "INFO",
    **context: Any,
) -> None:
    """도메인 이벤트를 구조화 로그로 기록.

    - event: 이벤트 이름 (예: "auth.login.success")
    - domain: 로거 네임스페이스 (예: "app.auth", "app.user")
    - level: INFO|WARNING|ERROR
    - context: 표준 컨텍스트 필드(user.id, session.id, order.id, counselor.id, amount, currency, channel, referer 등)
    """
    logger_name = f"{domain}" if domain.startswith("app.") else f"app.{domain}"
    logger = logging.getLogger(logger_name)

    # 필드 네임 정규화: dot 표기 허용, 마스킹 적용
    ctx = _mask(context)
    ctx["event"] = event

    lvl = (level or "INFO").upper()
    if lvl == "ERROR":
        logger.error(event, extra=ctx)
    elif lvl == "WARNING":
        logger.warning(event, extra=ctx)
    else:
        logger.info(event, extra=ctx)


