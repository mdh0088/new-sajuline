"""
SecurityPipeline 통합 테스트.

Stories: 3-1
"""

import pytest

from src.services.ai.security import SecurityPipeline


class TestSecurityPipeline:
    """SecurityPipeline 통합 테스트"""

    @pytest.fixture
    def allowed_tables(self):
        """테스트용 허용 테이블"""
        return {"users", "payments", "members"}

    def test_pipeline_exists(self):
        """SecurityPipeline 클래스가 존재하는지 확인"""
        assert SecurityPipeline is not None

    def test_pipeline_safe_query_full_flow(self, allowed_tables):
        """안전한 쿼리의 전체 플로우"""
        user_query = "회원 수를 조회해줘"
        generated_sql = "SELECT COUNT(*) as count FROM users"
        result_data = [{"count": 150}]
        result_columns = ["count"]

        # Layer 1: 프롬프트 생성
        prompt = SecurityPipeline.build_secure_prompt(user_query, allowed_tables)
        assert user_query in prompt
        assert "users" in prompt

        # Layer 2: SQL 검증
        validation = SecurityPipeline.validate_sql(generated_sql, allowed_tables)
        assert validation.is_safe is True

        # Layer 3: 결과 정제
        sanitized, result_validation = SecurityPipeline.sanitize_result(
            result_data, result_columns
        )
        assert sanitized == result_data
        assert result_validation.row_count == 1

        # Layer 4: 사용자 확인 필요 여부
        confirmation = SecurityPipeline.check_user_confirmation(generated_sql)
        assert confirmation.required is False

    def test_pipeline_dangerous_sql_blocked(self, allowed_tables):
        """위험한 SQL 차단"""
        dangerous_sql = "DELETE FROM users WHERE id = 1"

        validation = SecurityPipeline.validate_sql(dangerous_sql, allowed_tables)

        assert validation.is_safe is False
        assert len(validation.violations) > 0
        assert any("DELETE" in v for v in validation.violations)

    def test_pipeline_unauthorized_table_blocked(self, allowed_tables):
        """허용되지 않은 테이블 접근 차단"""
        sql = "SELECT * FROM admin_logs"  # not in allowed_tables

        validation = SecurityPipeline.validate_sql(sql, allowed_tables)

        assert validation.is_safe is False
        assert any("admin_logs" in v.lower() for v in validation.violations)

    def test_pipeline_sensitive_data_masked(self, allowed_tables):
        """민감 데이터 마스킹"""
        sql = "SELECT id, password FROM users"
        result_data = [
            {"id": 1, "password": "secret123"},
            {"id": 2, "password": "pass456"},
        ]
        result_columns = ["id", "password"]

        sanitized, result_validation = SecurityPipeline.sanitize_result(
            result_data, result_columns
        )

        # 비밀번호가 마스킹되어야 함
        assert sanitized[0]["password"] == "***"
        assert sanitized[1]["password"] == "***"
        assert "password" in result_validation.masked_columns

    def test_pipeline_large_result_truncated(self, allowed_tables):
        """대용량 결과 자르기"""
        sql = "SELECT * FROM payments"
        result_data = [{"id": i, "amount": 1000} for i in range(1500)]
        result_columns = ["id", "amount"]

        sanitized, result_validation = SecurityPipeline.sanitize_result(
            result_data, result_columns
        )

        assert result_validation.was_truncated is True
        assert len(sanitized) == 500  # MAX_ROWS (NFR-003 준수)
        assert result_validation.row_count == 1500  # 원본 행 수

    def test_pipeline_complex_join_needs_confirmation(self, allowed_tables):
        """복잡한 조인은 사용자 확인 필요"""
        sql = """
        SELECT * FROM users u
        JOIN payments p ON u.id = p.user_id
        JOIN members m ON u.id = m.member_id
        JOIN sessions s ON u.id = s.user_id
        """

        confirmation = SecurityPipeline.check_user_confirmation(sql)

        assert confirmation.required is True
        assert "join" in confirmation.reason.lower()

    def test_pipeline_end_to_end_safe_scenario(self, allowed_tables):
        """안전한 시나리오의 전체 플로우"""
        user_query = "최근 결제 10건을 조회해줘"
        generated_sql = """
        SELECT id, user_id, amount, created_at
        FROM payments
        ORDER BY created_at DESC
        LIMIT 10
        """
        result_data = [
            {"id": i, "user_id": i % 10, "amount": 50000, "created_at": "2026-02-03"}
            for i in range(10)
        ]
        result_columns = ["id", "user_id", "amount", "created_at"]

        # 1. 프롬프트 생성
        prompt = SecurityPipeline.build_secure_prompt(user_query, allowed_tables)
        assert "payments" in prompt

        # 2. SQL 검증
        validation = SecurityPipeline.validate_sql(generated_sql, allowed_tables)
        assert validation.is_safe is True

        # 3. 결과 정제
        sanitized, result_validation = SecurityPipeline.sanitize_result(
            result_data, result_columns
        )
        assert len(sanitized) == 10
        assert result_validation.row_count == 10

        # 4. 사용자 확인 (LIMIT이 있으므로 불필요)
        confirmation = SecurityPipeline.check_user_confirmation(generated_sql)
        assert confirmation.required is False

    def test_pipeline_end_to_end_blocked_scenario(self, allowed_tables):
        """차단되는 시나리오의 전체 플로우"""
        user_query = "모든 회원 삭제"
        malicious_sql = "DELETE FROM users"

        # 프롬프트 생성 (Layer 1은 LLM이 안전한 SQL 생성하도록 유도)
        prompt = SecurityPipeline.build_secure_prompt(user_query, allowed_tables)
        assert "SELECT" in prompt.upper()

        # SQL 검증 (Layer 2에서 차단)
        validation = SecurityPipeline.validate_sql(malicious_sql, allowed_tables)
        assert validation.is_safe is False
        assert any("DELETE" in v for v in validation.violations)

    def test_pipeline_layer_independence(self, allowed_tables):
        """각 레이어가 독립적으로 동작하는지 확인"""
        # Layer 1만 사용
        prompt = SecurityPipeline.build_secure_prompt("테스트", allowed_tables)
        assert isinstance(prompt, str)

        # Layer 2만 사용
        validation = SecurityPipeline.validate_sql(
            "SELECT * FROM users", allowed_tables
        )
        assert validation.is_safe is True

        # Layer 3만 사용
        sanitized, _ = SecurityPipeline.sanitize_result([{"id": 1}], ["id"])
        assert len(sanitized) == 1

        # Layer 4만 사용
        confirmation = SecurityPipeline.check_user_confirmation("SELECT * FROM users")
        assert isinstance(confirmation.required, bool)

    def test_pipeline_all_layers_imported(self):
        """모든 레이어 클래스가 import 가능한지 확인"""
        from src.services.ai.security import (
            Layer2SQLValidator,
            Layer3ResultValidator,
            Layer4UserConfirmation,
            build_secure_prompt,
        )

        assert Layer2SQLValidator is not None
        assert Layer3ResultValidator is not None
        assert Layer4UserConfirmation is not None
        assert build_secure_prompt is not None
