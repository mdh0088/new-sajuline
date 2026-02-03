"""
SQL Validator 단위 테스트

SQL 검증 로직을 테스트합니다.

Stories: AI-002, AI-003
FRs: FR-011, FR-013
"""
import pytest

from src.services.ai.validators.sql_validator import SQLValidator, SQLValidationResult


@pytest.mark.asyncio
class TestSQLValidator:
    """SQL Validator 테스트"""

    async def test_valid_select_query(self):
        """유효한 SELECT 쿼리 테스트"""
        sql = "SELECT * FROM users WHERE id = 1 LIMIT 100"
        allowed_tables = {"users", "payments"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is True
        assert result.is_select_only is True
        assert "users" in result.tables_used
        assert result.error is None

    async def test_forbidden_insert_keyword(self):
        """INSERT 키워드 차단 테스트"""
        sql = "INSERT INTO users (name) VALUES ('test')"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert result.is_select_only is False
        assert result.error is not None
        assert "INSERT" in result.error

    async def test_forbidden_update_keyword(self):
        """UPDATE 키워드 차단 테스트"""
        sql = "UPDATE users SET name = 'hacker' WHERE id = 1"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert "UPDATE" in result.error

    async def test_forbidden_delete_keyword(self):
        """DELETE 키워드 차단 테스트"""
        sql = "DELETE FROM users WHERE id = 1"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert "DELETE" in result.error

    async def test_forbidden_drop_keyword(self):
        """DROP 키워드 차단 테스트"""
        sql = "DROP TABLE users"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert "DROP" in result.error

    async def test_forbidden_exec_keyword(self):
        """EXEC 키워드 차단 테스트 (SQL Injection 방지)"""
        sql = "SELECT * FROM users; EXEC xp_cmdshell 'dir'"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert "EXEC" in result.error or "XP_" in result.error

    async def test_unauthorized_table(self):
        """허용되지 않은 테이블 사용 테스트"""
        sql = "SELECT * FROM admin_secrets LIMIT 10"
        allowed_tables = {"users", "payments"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert result.error is not None
        assert "admin_secrets" in result.error.lower()

    async def test_join_query_with_allowed_tables(self):
        """허용된 테이블 간 JOIN 쿼리 테스트"""
        sql = """
        SELECT u.id, u.name, p.amount
        FROM users u
        INNER JOIN payments p ON u.id = p.user_id
        LIMIT 100
        """
        allowed_tables = {"users", "payments"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is True
        assert result.is_select_only is True
        assert "users" in result.tables_used
        assert "payments" in result.tables_used

    async def test_join_query_with_unauthorized_table(self):
        """허용되지 않은 테이블과의 JOIN 테스트"""
        sql = """
        SELECT u.id, s.secret_data
        FROM users u
        INNER JOIN secrets s ON u.id = s.user_id
        """
        allowed_tables = {"users", "payments"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert "secrets" in result.error.lower()

    async def test_empty_sql(self):
        """빈 SQL 테스트"""
        sql = ""
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False
        assert result.error is not None

    async def test_whitespace_only_sql(self):
        """공백만 있는 SQL 테스트"""
        sql = "   \n\t  "
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is False

    async def test_limit_warning(self):
        """LIMIT 없는 쿼리 경고 테스트"""
        sql = "SELECT * FROM users"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        # 검증은 통과하지만 경고가 있어야 함
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("LIMIT" in warning for warning in result.warnings)

    async def test_date_functions_allowed(self):
        """날짜 함수가 포함된 쿼리 테스트"""
        sql = """
        SELECT * FROM users
        WHERE DATE(created_at) = CURDATE()
        LIMIT 100
        """
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is True
        assert result.is_select_only is True

    async def test_aggregate_functions_allowed(self):
        """집계 함수가 포함된 쿼리 테스트"""
        sql = """
        SELECT COUNT(*) as user_count, SUM(amount) as total_amount
        FROM users
        GROUP BY status
        """
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is True

    async def test_subquery_with_allowed_tables(self):
        """서브쿼리 테스트 (허용된 테이블만 사용)"""
        sql = """
        SELECT u.id, u.name
        FROM users u
        WHERE u.id IN (SELECT DISTINCT user_id FROM payments WHERE amount > 1000)
        LIMIT 50
        """
        allowed_tables = {"users", "payments"}

        result = await SQLValidator.validate(sql, allowed_tables)

        assert result.is_valid is True
        assert "users" in result.tables_used
        assert "payments" in result.tables_used

    async def test_case_insensitive_keyword_detection(self):
        """대소문자 무관 키워드 감지 테스트"""
        sqls = [
            "insert into users values (1)",
            "INSERT INTO users VALUES (1)",
            "Insert Into users Values (1)",
        ]
        allowed_tables = {"users"}

        for sql in sqls:
            result = await SQLValidator.validate(sql, allowed_tables)
            assert result.is_valid is False, f"Failed for SQL: {sql}"
            assert "INSERT" in result.error.upper()

    async def test_validation_result_structure(self):
        """SQLValidationResult 데이터 구조 테스트"""
        result = SQLValidationResult(
            is_valid=True,
            is_select_only=True,
            tables_used={"users", "payments"},
            error=None,
            warnings=["No LIMIT clause"],
        )

        assert result.is_valid is True
        assert result.is_select_only is True
        assert len(result.tables_used) == 2
        assert "users" in result.tables_used
        assert result.error is None
        assert len(result.warnings) == 1

    async def test_subquery_table_extraction(self):
        """서브쿼리 내 테이블 추출 테스트 (보안 중요)"""
        sql = """
        SELECT u.id, u.name
        FROM users u
        WHERE u.id IN (SELECT user_id FROM payments WHERE amount > 1000)
        LIMIT 50
        """
        allowed_tables = {"users"}  # payments는 허용 안 됨

        result = await SQLValidator.validate(sql, allowed_tables)

        # 서브쿼리의 payments 테이블이 감지되어야 함
        assert result.is_valid is False, "서브쿼리 테이블이 감지되지 않았습니다!"
        assert "payments" in result.error.lower()

    async def test_nested_subquery_table_extraction(self):
        """중첩 서브쿼리 테이블 추출 테스트"""
        sql = """
        SELECT *
        FROM users
        WHERE id IN (
            SELECT user_id FROM payments WHERE amount IN (
                SELECT threshold FROM admin_settings
            )
        )
        """
        allowed_tables = {"users", "payments"}  # admin_settings 허용 안 됨

        result = await SQLValidator.validate(sql, allowed_tables)

        # 중첩 서브쿼리의 admin_settings가 감지되어야 함
        assert result.is_valid is False
        assert "admin_settings" in result.error.lower()

    async def test_strict_limit_mode_enabled(self):
        """Strict LIMIT 모드 테스트 (LIMIT 필수)"""
        sql = "SELECT * FROM users"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables, strict_limit=True)

        # Strict 모드에서는 LIMIT 없으면 실패
        assert result.is_valid is False
        assert "LIMIT" in result.error

    async def test_strict_limit_mode_with_limit(self):
        """Strict LIMIT 모드에서 LIMIT 있으면 통과"""
        sql = "SELECT * FROM users LIMIT 100"
        allowed_tables = {"users"}

        result = await SQLValidator.validate(sql, allowed_tables, strict_limit=True)

        assert result.is_valid is True
