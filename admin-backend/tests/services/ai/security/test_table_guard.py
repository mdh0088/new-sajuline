"""
테이블 접근 제어 테스트

Stories: 3-2
FRs: FR-015, NFR-S3
"""
import pytest
from src.services.ai.security.table_guard import (
    TableAccessGuard,
    TableAccessResult,
)


class TestTableAccessGuard:
    """테이블 접근 제어 테스트"""

    def test_check_access_allowed_table(self):
        """화이트리스트 테이블은 접근 허용"""
        sql = "SELECT * FROM t_member WHERE active=1"
        allowed_tables = {"t_member", "t_payment"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is True
        assert len(result.blocked_tables) == 0
        assert result.reason is None

    def test_check_access_blocked_table(self):
        """블랙리스트 테이블은 접근 차단"""
        sql = "SELECT * FROM t_admin WHERE role='admin'"
        allowed_tables = {"t_member", "t_payment"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "t_admin" in result.blocked_tables
        assert "접근이 허용되지 않은 테이블" in result.reason

    def test_check_access_user_password_table(self):
        """t_user_password는 슈퍼 관리자도 접근 차단"""
        sql = "SELECT * FROM t_user_password"
        allowed_tables = {"t_member", "t_user_password"}

        # 일반 관리자
        result = TableAccessGuard.check_access(sql, allowed_tables, is_super_admin=False)
        assert result.allowed is False
        assert "t_user_password" in result.blocked_tables

        # 슈퍼 관리자도 차단
        result_super = TableAccessGuard.check_access(
            sql, allowed_tables, is_super_admin=True
        )
        assert result_super.allowed is False
        assert "t_user_password" in result_super.blocked_tables

    def test_check_access_payment_card_table(self):
        """t_payment_card는 슈퍼 관리자도 접근 차단"""
        sql = "SELECT * FROM t_payment_card"
        allowed_tables = {"t_member", "t_payment_card"}

        result = TableAccessGuard.check_access(sql, allowed_tables, is_super_admin=True)

        assert result.allowed is False
        assert "t_payment_card" in result.blocked_tables

    def test_check_access_system_table_information_schema(self):
        """information_schema 접근 차단"""
        sql = "SELECT * FROM information_schema.tables"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "information_schema.tables" in result.blocked_tables

    def test_check_access_system_table_mysql(self):
        """mysql.* 시스템 테이블 접근 차단"""
        sql = "SELECT * FROM mysql.user"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "mysql.user" in result.blocked_tables

    def test_check_access_not_in_whitelist(self):
        """화이트리스트에 없는 테이블 접근 차단"""
        sql = "SELECT * FROM t_unknown_table"
        allowed_tables = {"t_member", "t_payment"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "t_unknown_table" in result.blocked_tables

    def test_check_access_join_multiple_tables(self):
        """JOIN으로 여러 테이블 접근 시 모두 화이트리스트 확인"""
        sql = "SELECT * FROM t_member m JOIN t_payment p ON m.id = p.user_id"
        allowed_tables = {"t_member", "t_payment"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is True
        assert len(result.blocked_tables) == 0

    def test_check_access_join_with_blocked_table(self):
        """JOIN 중 하나라도 블랙리스트면 차단"""
        sql = "SELECT * FROM t_member m JOIN t_admin a ON m.id = a.user_id"
        allowed_tables = {"t_member", "t_admin"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "t_admin" in result.blocked_tables

    def test_extract_all_tables_from_clause(self):
        """FROM 절에서 테이블 추출"""
        sql = "SELECT * FROM t_member WHERE active=1"

        tables = TableAccessGuard._extract_all_tables(sql)

        assert "t_member" in tables

    def test_extract_all_tables_join_clause(self):
        """JOIN 절에서 테이블 추출"""
        sql = """
        SELECT * FROM t_member m
        JOIN t_payment p ON m.id = p.user_id
        LEFT JOIN t_counselor c ON m.id = c.member_id
        """

        tables = TableAccessGuard._extract_all_tables(sql)

        assert "t_member" in tables
        assert "t_payment" in tables
        assert "t_counselor" in tables

    def test_extract_all_tables_with_backticks(self):
        """백틱으로 감싼 테이블명 추출"""
        sql = "SELECT * FROM `t_member` WHERE active=1"

        tables = TableAccessGuard._extract_all_tables(sql)

        assert "t_member" in tables

    def test_extract_all_tables_with_schema(self):
        """스키마 포함 테이블명 추출"""
        sql = "SELECT * FROM mysql.user"

        tables = TableAccessGuard._extract_all_tables(sql)

        assert "mysql.user" in tables

    def test_case_insensitive_table_matching(self):
        """대소문자 구분 없이 테이블 매칭"""
        sql = "SELECT * FROM T_ADMIN WHERE id=1"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        # T_ADMIN (대문자)도 블랙리스트 매칭되어야 함
        assert result.allowed is False
        assert any("admin" in t.lower() for t in result.blocked_tables)

    def test_check_access_super_admin_allowed_tables(self):
        """슈퍼 관리자는 일부 민감 테이블 제외하고 접근 가능"""
        # t_sessions는 슈퍼 관리자는 접근 가능
        sql = "SELECT * FROM t_sessions"
        allowed_tables = {"t_sessions"}

        result = TableAccessGuard.check_access(sql, allowed_tables, is_super_admin=True)

        # t_sessions는 블랙리스트지만 슈퍼 관리자는 접근 가능
        # 단, t_user_password, t_payment_card, t_user_identity는 슈퍼 관리자도 차단
        assert result.allowed is True
        assert len(result.blocked_tables) == 0

    def test_check_access_performance_schema(self):
        """performance_schema 접근 차단"""
        sql = "SELECT * FROM performance_schema.events_statements_summary_by_digest"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False

    def test_check_access_sys_schema(self):
        """sys 스키마 접근 차단"""
        sql = "SELECT * FROM sys.schema_table_statistics"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False

    def test_check_access_multiple_blocked_tables(self):
        """여러 차단된 테이블이 있으면 모두 반환"""
        sql = "SELECT * FROM t_admin a JOIN t_user_password p ON a.id = p.admin_id"
        allowed_tables = {"t_member"}

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert len(result.blocked_tables) >= 2
        assert any("admin" in t.lower() for t in result.blocked_tables)
        assert any("password" in t.lower() for t in result.blocked_tables)

    def test_check_access_empty_allowed_tables(self):
        """빈 화이트리스트는 모든 테이블 차단"""
        sql = "SELECT * FROM t_member"
        allowed_tables = set()

        result = TableAccessGuard.check_access(sql, allowed_tables)

        assert result.allowed is False
        assert "t_member" in result.blocked_tables
