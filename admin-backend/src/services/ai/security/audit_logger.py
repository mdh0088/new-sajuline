"""
보안 감사 로깅

AI 어시스턴트 접근 시도 및 권한 위반 로깅
"""

import logging
from datetime import datetime

from src.services.ai.security.rbac import AIRole

# 구조화 로깅 (향후 structlog 적용 가능)
logger = logging.getLogger("ai.security.audit")


def log_access_denied(
    admin_id: int,
    role: AIRole,
    attempted_table: str | None = None,
    reason: str = "권한 없음",
) -> None:
    """
    접근 거부 로깅

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        attempted_table: 시도한 테이블명 (있는 경우)
        reason: 거부 이유
    """
    logger.warning(
        "AI access denied",
        extra={
            "admin_id": admin_id,
            "role": role.value,
            "attempted_table": attempted_table,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "access_denied",
        },
    )


def log_rate_limit_exceeded(admin_id: int, role: AIRole, retry_after: int) -> None:
    """
    Rate Limit 초과 로깅

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        retry_after: 재시도까지 남은 초
    """
    logger.warning(
        "AI rate limit exceeded",
        extra={
            "admin_id": admin_id,
            "role": role.value,
            "retry_after": retry_after,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rate_limit_exceeded",
        },
    )


def log_access_granted(admin_id: int, role: AIRole, query: str | None = None) -> None:
    """
    접근 허용 로깅 (정보성)

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        query: 사용자 질의 (있는 경우)
    """
    logger.info(
        "AI access granted",
        extra={
            "admin_id": admin_id,
            "role": role.value,
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "access_granted",
        },
    )
