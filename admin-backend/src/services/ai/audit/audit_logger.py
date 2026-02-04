"""
AI 질의 감사 로거.

모든 AI 질의와 보안 이벤트를 구조화된 JSON 로그로 기록합니다.

Stories: 3-4
FRs: FR17, FR28
"""
from datetime import datetime, UTC
from dataclasses import dataclass, asdict
from typing import Any
import json
import logging

# AI 감사 전용 로거
logger = logging.getLogger("ai.audit")


@dataclass
class AIQueryAuditLog:
    """AI 질의 감사 로그 데이터클래스"""

    request_id: str
    admin_id: int
    admin_role: str
    question: str
    db_scope: str
    generated_sql: str | None
    execution_time_ms: int
    row_count: int
    status: str  # success, blocked, error
    error_code: str | None = None
    error_message: str | None = None
    tables_accessed: list[str] | None = None
    masked_columns: list[str] | None = None
    timestamp: str | None = None

    def __post_init__(self):
        """타임스탬프 자동 생성"""
        if self.timestamp is None:
            # datetime.now(UTC).isoformat()은 이미 +00:00을 포함
            self.timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")


class AIAuditLogger:
    """AI 서비스 감사 로거"""

    @staticmethod
    async def log_query(audit_log: AIQueryAuditLog):
        """
        질의 감사 로그 기록.

        Args:
            audit_log: 감사 로그 데이터

        Log Levels:
            - INFO: success 상태
            - WARNING: blocked 상태
            - ERROR: error 상태
        """
        log_data = asdict(audit_log)

        # SQL 민감 정보 마스킹 (500자 제한)
        if audit_log.generated_sql and len(audit_log.generated_sql) > 500:
            log_data["generated_sql"] = audit_log.generated_sql[:500]

        # 이벤트 타입 추가
        log_data["event"] = "ai_query_audit"

        # JSON 형식으로 직렬화 (구조화된 로깅)
        json_log = json.dumps(log_data, ensure_ascii=False)

        # 상태에 따라 로그 레벨 결정 (JSON 문자열만 로깅)
        if audit_log.status == "success":
            logger.info(json_log)
        elif audit_log.status == "blocked":
            logger.warning(json_log)
        else:
            logger.error(json_log)

    @staticmethod
    async def log_rate_limit_exceeded(
        admin_id: int,
        admin_role: str,
        current_count: int,
        limit: int,
    ):
        """
        Rate Limit 초과 로그 기록.

        Args:
            admin_id: 관리자 ID
            admin_role: 관리자 역할
            current_count: 현재 요청 수
            limit: 허용 제한
        """
        log_data = {
            "event": "ai_rate_limit_exceeded",
            "admin_id": admin_id,
            "admin_role": admin_role,
            "current_count": current_count,
            "limit": limit,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        json_log = json.dumps(log_data, ensure_ascii=False)
        logger.warning(json_log)

    @staticmethod
    async def log_security_event(
        event_type: str,
        admin_id: int,
        admin_role: str,
        details: dict[str, Any],
    ):
        """
        보안 이벤트 로그 기록.

        Args:
            event_type: 이벤트 타입 (예: sql_injection_attempt)
            admin_id: 관리자 ID
            admin_role: 관리자 역할
            details: 이벤트 세부사항
        """
        log_data = {
            "event": "ai_security_event",
            "event_type": event_type,
            "admin_id": admin_id,
            "admin_role": admin_role,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            **details,
        }
        json_log = json.dumps(log_data, ensure_ascii=False)
        logger.warning(json_log)
