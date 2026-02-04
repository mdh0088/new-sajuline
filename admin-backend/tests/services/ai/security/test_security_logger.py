"""
보안 로거 테스트

Stories: 3-2
FRs: NFR-S7
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.services.ai.security.security_logger import SecurityLogger


class TestSecurityLogger:
    """보안 로거 테스트"""

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_log_injection_attempt(self, mock_logger):
        """SQL Injection 시도 로깅"""
        admin_id = 123
        question = "사용자 정보 조회" + "A" * 200  # 긴 질문
        generated_sql = "SELECT * FROM users UNION SELECT * FROM admin" + "X" * 500
        patterns_detected = ["union_injection", "stacked_query"]
        risk_score = 0.8

        await SecurityLogger.log_injection_attempt(
            admin_id=admin_id,
            question=question,
            generated_sql=generated_sql,
            patterns_detected=patterns_detected,
            risk_score=risk_score,
        )

        # logger.warning 호출 확인
        mock_logger.warning.assert_called_once()

        # 호출 인자 확인
        call_args = mock_logger.warning.call_args

        # 첫 번째 인자는 event type
        assert call_args[0][0] == "sql_injection_detected"

        # 키워드 인자 확인
        kwargs = call_args[1]
        assert kwargs["event_type"] == "SECURITY_INJECTION"
        assert kwargs["admin_id"] == admin_id
        assert len(kwargs["question"]) <= 200  # 잘림
        assert len(kwargs["sql_preview"]) <= 500  # 잘림
        assert kwargs["patterns"] == patterns_detected
        assert kwargs["risk_score"] == risk_score
        assert kwargs["severity"] == "HIGH"
        assert "timestamp" in kwargs

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_log_table_access_denied(self, mock_logger):
        """테이블 접근 거부 로깅"""
        admin_id = 456
        question = "관리자 정보 조회"
        blocked_tables = ["t_admin", "t_user_password"]

        await SecurityLogger.log_table_access_denied(
            admin_id=admin_id,
            question=question,
            blocked_tables=blocked_tables,
        )

        # logger.warning 호출 확인
        mock_logger.warning.assert_called_once()

        # 호출 인자 확인
        call_args = mock_logger.warning.call_args

        # 첫 번째 인자는 event type
        assert call_args[0][0] == "table_access_denied"

        # 키워드 인자 확인
        kwargs = call_args[1]
        assert kwargs["event_type"] == "SECURITY_ACCESS_DENIED"
        assert kwargs["admin_id"] == admin_id
        assert kwargs["question"] == question
        assert kwargs["blocked_tables"] == blocked_tables
        assert kwargs["severity"] == "MEDIUM"
        assert "timestamp" in kwargs

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_log_injection_question_truncation(self, mock_logger):
        """질문이 200자를 초과하면 잘림"""
        long_question = "A" * 300

        await SecurityLogger.log_injection_attempt(
            admin_id=1,
            question=long_question,
            generated_sql="SELECT 1",
            patterns_detected=["test"],
            risk_score=0.5,
        )

        call_args = mock_logger.warning.call_args
        kwargs = call_args[1]

        # 200자로 잘렸는지 확인
        assert len(kwargs["question"]) == 200

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_log_injection_sql_truncation(self, mock_logger):
        """SQL이 500자를 초과하면 잘림"""
        long_sql = "SELECT " + "X" * 600

        await SecurityLogger.log_injection_attempt(
            admin_id=1,
            question="test",
            generated_sql=long_sql,
            patterns_detected=["test"],
            risk_score=0.5,
        )

        call_args = mock_logger.warning.call_args
        kwargs = call_args[1]

        # 500자로 잘렸는지 확인
        assert len(kwargs["sql_preview"]) == 500

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_log_table_access_question_truncation(self, mock_logger):
        """테이블 접근 거부 시 질문이 200자를 초과하면 잘림"""
        long_question = "B" * 300

        await SecurityLogger.log_table_access_denied(
            admin_id=1,
            question=long_question,
            blocked_tables=["t_admin"],
        )

        call_args = mock_logger.warning.call_args
        kwargs = call_args[1]

        # 200자로 잘렸는지 확인
        assert len(kwargs["question"]) == 200

    @pytest.mark.asyncio
    @patch("src.services.ai.security.security_logger.logger")
    async def test_timestamp_format(self, mock_logger):
        """타임스탬프가 ISO 8601 형식"""
        await SecurityLogger.log_injection_attempt(
            admin_id=1,
            question="test",
            generated_sql="SELECT 1",
            patterns_detected=["test"],
            risk_score=0.5,
        )

        call_args = mock_logger.warning.call_args
        kwargs = call_args[1]

        # ISO 8601 형식 확인 (YYYY-MM-DDTHH:MM:SS.mmmmmm)
        timestamp = kwargs["timestamp"]
        # 파싱 가능한지 확인
        datetime.fromisoformat(timestamp)
