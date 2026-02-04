"""
Layer 2 보안 통합 테스트

Stories: 3-2
FRs: FR-014, FR-015
"""
import pytest
from src.services.ai.security.layer2_validator import Layer2SQLValidator


class TestLayer2SecurityIntegration:
    """Layer 2 보안 통합 테스트"""

    def test_validate_sql_security_injection_detected(self):
        """SQL Injection 패턴 탐지 시 차단"""
        sql = "SELECT * FROM t_member UNION SELECT * FROM t_admin"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        # UNION injection과 t_admin 테이블 위반 모두 탐지
        assert any("UNION" in v or "DANGEROUS_PATTERN" in v for v in result.violations)

    def test_validate_sql_security_table_blocked(self):
        """블랙리스트 테이블 접근 시 차단"""
        sql = "SELECT * FROM t_admin"
        allowed_tables = {"t_member"}  # t_admin은 허용되지 않음

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("TABLE_NOT_ALLOWED" in v and "admin" in v for v in result.violations)

    def test_validate_sql_security_normal_query(self):
        """정상 쿼리는 통과"""
        sql = "SELECT id, name FROM t_member WHERE age > 18"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True
        assert len(result.violations) == 0

    def test_validate_sql_security_stacked_query(self):
        """Stacked Query 차단"""
        sql = "SELECT * FROM t_member; DROP TABLE t_member"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        # 세미콜론 패턴과 DROP 키워드 모두 탐지
        assert any("DROP" in v or "DANGEROUS_PATTERN" in v for v in result.violations)

    def test_validate_sql_security_comment_injection(self):
        """주석을 통한 우회 시도 차단"""
        sql = "SELECT * FROM t_member WHERE id=1-- AND active=1"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DANGEROUS_PATTERN" in v for v in result.violations)

    def test_validate_sql_security_time_based_injection(self):
        """Time-based Injection 차단"""
        sql = "SELECT * FROM t_member WHERE id=1 AND SLEEP(10)"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DANGEROUS_PATTERN" in v or "SLEEP" in v for v in result.violations)

    def test_validate_sql_security_system_table(self):
        """시스템 테이블 접근 차단"""
        sql = "SELECT * FROM information_schema.tables"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DANGEROUS_PATTERN" in v or "TABLE_NOT_ALLOWED" in v for v in result.violations)

    def test_validate_sql_security_join_with_whitelist(self):
        """화이트리스트 테이블 간 JOIN은 허용"""
        sql = "SELECT * FROM t_member m JOIN t_payment p ON m.id = p.user_id"
        allowed_tables = {"t_member", "t_payment"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True
        assert len(result.violations) == 0

    def test_validate_sql_security_multiple_violations(self):
        """여러 위반 사항 동시 탐지"""
        sql = "SELECT * FROM t_member UNION SELECT * FROM t_admin; DROP TABLE t_member--"
        allowed_tables = {"t_member"}

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        # UNION, t_admin, DROP, 세미콜론, 주석 모두 탐지
        assert len(result.violations) >= 3
