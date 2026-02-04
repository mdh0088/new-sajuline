"""
감사 로거 단위 테스트.

Stories: 3-4
"""
import pytest
from unittest.mock import Mock, patch, call
from datetime import datetime
from src.services.ai.audit.audit_logger import (
    AIQueryAuditLog,
    AIAuditLogger,
)


class TestAIQueryAuditLog:
    """AIQueryAuditLog 데이터클래스 테스트"""

    def test_create_audit_log_with_all_fields(self):
        """모든 필드를 포함한 감사 로그 생성"""
        log = AIQueryAuditLog(
            request_id="550e8400-e29b-41d4-a716-446655440000",
            admin_id=123,
            admin_role="admin",
            question="오늘 매출 얼마야?",
            db_scope="mariadb",
            generated_sql="SELECT SUM(amount) FROM t_payment",
            execution_time_ms=1523,
            row_count=1,
            status="success",
            tables_accessed=["t_payment"],
            masked_columns=[],
        )

        assert log.request_id == "550e8400-e29b-41d4-a716-446655440000"
        assert log.admin_id == 123
        assert log.admin_role == "admin"
        assert log.question == "오늘 매출 얼마야?"
        assert log.status == "success"
        assert log.tables_accessed == ["t_payment"]

    def test_auto_generate_timestamp(self):
        """타임스탬프 자동 생성 확인"""
        log = AIQueryAuditLog(
            request_id="test-123",
            admin_id=1,
            admin_role="viewer",
            question="test",
            db_scope="mariadb",
            generated_sql=None,
            execution_time_ms=100,
            row_count=0,
            status="blocked",
        )

        assert log.timestamp is not None
        assert isinstance(log.timestamp, str)
        # ISO 8601 형식 검증
        datetime.fromisoformat(log.timestamp.replace("Z", "+00:00"))

    def test_optional_fields_can_be_none(self):
        """선택적 필드가 None일 수 있음"""
        log = AIQueryAuditLog(
            request_id="test-456",
            admin_id=2,
            admin_role="admin",
            question="query",
            db_scope="mariadb",
            generated_sql=None,
            execution_time_ms=200,
            row_count=0,
            status="error",
            error_code="AI_ERR_001",
            error_message="LLM timeout",
        )

        assert log.generated_sql is None
        assert log.tables_accessed is None
        assert log.masked_columns is None
        assert log.error_code == "AI_ERR_001"


class TestAIAuditLogger:
    """AIAuditLogger 클래스 테스트"""

    @pytest.mark.asyncio
    async def test_log_query_success_status(self):
        """성공 상태 질의 로깅 - INFO 레벨"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            log = AIQueryAuditLog(
                request_id="req-001",
                admin_id=10,
                admin_role="super_admin",
                question="매출 데이터 조회",
                db_scope="mariadb",
                generated_sql="SELECT * FROM payments",
                execution_time_ms=500,
                row_count=100,
                status="success",
            )

            await AIAuditLogger.log_query(log)

            # INFO 레벨로 로깅되었는지 확인
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            # JSON 메시지 확인
            log_message = call_args[0][0]
            assert "req-001" in log_message
            assert "success" in log_message
            assert "ai_query_audit" in log_message

    @pytest.mark.asyncio
    async def test_log_query_blocked_status(self):
        """차단 상태 질의 로깅 - WARNING 레벨"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            log = AIQueryAuditLog(
                request_id="req-002",
                admin_id=20,
                admin_role="viewer",
                question="시스템 테이블 조회",
                db_scope="mariadb",
                generated_sql="SELECT * FROM mysql.user",
                execution_time_ms=0,
                row_count=0,
                status="blocked",
                error_code="SECURITY_VIOLATION",
            )

            await AIAuditLogger.log_query(log)

            # WARNING 레벨로 로깅되었는지 확인
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            log_message = call_args[0][0]
            assert "blocked" in log_message
            assert "ai_query_audit" in log_message

    @pytest.mark.asyncio
    async def test_log_query_error_status(self):
        """에러 상태 질의 로깅 - ERROR 레벨"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            log = AIQueryAuditLog(
                request_id="req-003",
                admin_id=30,
                admin_role="admin",
                question="잘못된 질의",
                db_scope="mariadb",
                generated_sql=None,
                execution_time_ms=0,
                row_count=0,
                status="error",
                error_code="AI_ERR_001",
                error_message="LLM timeout",
            )

            await AIAuditLogger.log_query(log)

            # ERROR 레벨로 로깅되었는지 확인
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            log_message = call_args[0][0]
            assert "error" in log_message
            assert "AI_ERR_001" in log_message

    @pytest.mark.asyncio
    async def test_sql_masking_over_500_chars(self):
        """500자 이상 SQL은 잘라서 로깅"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            long_sql = "SELECT * FROM table WHERE " + "x=1 AND " * 100
            log = AIQueryAuditLog(
                request_id="req-004",
                admin_id=40,
                admin_role="admin",
                question="복잡한 쿼리",
                db_scope="mariadb",
                generated_sql=long_sql,
                execution_time_ms=1000,
                row_count=50,
                status="success",
            )

            await AIAuditLogger.log_query(log)

            # JSON 메시지에서 SQL 확인
            call_args = mock_logger.info.call_args
            json_message = call_args[0][0]
            import json
            logged_data = json.loads(json_message)
            assert len(logged_data["generated_sql"]) == 500

    @pytest.mark.asyncio
    async def test_log_rate_limit_exceeded(self):
        """Rate limit 초과 로깅 - WARNING 레벨"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            await AIAuditLogger.log_rate_limit_exceeded(
                admin_id=50,
                admin_role="viewer",
                current_count=11,
                limit=10,
            )

            # WARNING 레벨 확인
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args

            # JSON 메시지 확인
            json_message = call_args[0][0]
            import json
            log_data = json.loads(json_message)
            assert log_data["admin_id"] == 50
            assert log_data["current_count"] == 11
            assert log_data["limit"] == 10
            assert log_data["event"] == "ai_rate_limit_exceeded"

    @pytest.mark.asyncio
    async def test_log_security_event(self):
        """보안 이벤트 로깅"""
        with patch("src.services.ai.audit.audit_logger.logger") as mock_logger:
            await AIAuditLogger.log_security_event(
                event_type="sql_injection_attempt",
                admin_id=60,
                admin_role="admin",
                details={
                    "detected_pattern": "DROP TABLE",
                    "blocked_sql": "DROP TABLE users;",
                },
            )

            # WARNING 레벨 확인
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args

            # JSON 메시지 확인
            json_message = call_args[0][0]
            import json
            log_data = json.loads(json_message)
            assert log_data["event"] == "ai_security_event"
            assert log_data["event_type"] == "sql_injection_attempt"
            assert log_data["admin_id"] == 60
            assert log_data["detected_pattern"] == "DROP TABLE"
