"""
보안 이벤트 로거

SQL Injection 및 테이블 접근 거부 등 보안 이벤트를 로깅합니다.

Stories: 3-2
FRs: NFR-S7
"""

from datetime import datetime

import structlog

logger = structlog.get_logger()


class SecurityLogger:
    """
    보안 이벤트 로거

    보안 관련 이벤트를 구조화된 로그로 기록합니다.
    로그는 WARNING 레벨로 기록되며 JSON 형식으로 저장됩니다.

    Note:
        메서드들이 async로 정의된 이유는 미래 확장성을 위함입니다.
        (예: 비동기 로그 전송, 외부 SIEM 연동 등)
    """

    @staticmethod
    async def log_injection_attempt(
        admin_id: int,
        question: str,
        generated_sql: str,
        patterns_detected: list[str],
        risk_score: float,
    ) -> None:
        """
        SQL Injection 시도 로깅

        Args:
            admin_id: 관리자 ID
            question: 사용자 질문 (최대 200자)
            generated_sql: 생성된 SQL (최대 500자)
            patterns_detected: 탐지된 패턴 목록
            risk_score: 위험도 점수 (0.0 ~ 1.0)
        """
        logger.warning(
            "sql_injection_detected",
            event_type="SECURITY_INJECTION",
            admin_id=admin_id,
            question=question[:200],
            sql_preview=generated_sql[:500],
            patterns=patterns_detected,
            risk_score=risk_score,
            timestamp=datetime.utcnow().isoformat(),
            severity="HIGH",
        )

    @staticmethod
    async def log_table_access_denied(
        admin_id: int,
        question: str,
        blocked_tables: list[str],
    ) -> None:
        """
        테이블 접근 거부 로깅

        Args:
            admin_id: 관리자 ID
            question: 사용자 질문 (최대 200자)
            blocked_tables: 차단된 테이블 목록
        """
        logger.warning(
            "table_access_denied",
            event_type="SECURITY_ACCESS_DENIED",
            admin_id=admin_id,
            question=question[:200],
            blocked_tables=blocked_tables,
            timestamp=datetime.utcnow().isoformat(),
            severity="MEDIUM",
        )
