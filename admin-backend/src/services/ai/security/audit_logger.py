"""
보안 감사 로깅

AI 어시스턴트 접근 시도 및 권한 위반 로깅
"""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.services.ai.security.rbac import AIRole

# 구조화 로깅 (JSON 형태)
logger = logging.getLogger("ai.security.audit")
KST = ZoneInfo("Asia/Seoul")


def log_access_denied(
    admin_id: int,
    role: AIRole,
    attempted_table: str | None = None,
    reason: str = "권한 없음",
) -> None:
    """
    접근 거부 로깅 (JSON 구조화)

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        attempted_table: 시도한 테이블명 (있는 경우)
        reason: 거부 이유
    """
    log_data = {
        "event_type": "access_denied",
        "admin_id": admin_id,
        "role": role.value,
        "attempted_table": attempted_table,
        "reason": reason,
        "timestamp": datetime.now(KST).isoformat(),
    }
    logger.warning(json.dumps(log_data))


def log_rate_limit_exceeded(admin_id: int, role: AIRole, retry_after: int) -> None:
    """
    Rate Limit 초과 로깅 (JSON 구조화)

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        retry_after: 재시도까지 남은 초
    """
    log_data = {
        "event_type": "rate_limit_exceeded",
        "admin_id": admin_id,
        "role": role.value,
        "retry_after": retry_after,
        "timestamp": datetime.now(KST).isoformat(),
    }
    logger.warning(json.dumps(log_data))


def log_access_granted(admin_id: int, role: AIRole, query: str | None = None) -> None:
    """
    접근 허용 로깅 (정보성, JSON 구조화)

    Args:
        admin_id: 관리자 ID
        role: AI 역할
        query: 사용자 질의 (있는 경우)
    """
    log_data = {
        "event_type": "access_granted",
        "admin_id": admin_id,
        "role": role.value,
        "query": query,
        "timestamp": datetime.now(KST).isoformat(),
    }
    logger.info(json.dumps(log_data))
