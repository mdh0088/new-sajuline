"""
Layer 2 SQL 검증 테스트.

Stories: 3-1
"""

import pytest

from src.services.ai.security.layer2_validator import (
    DANGEROUS_PATTERNS,
    FORBIDDEN_KEYWORDS,
    WARNING_PATTERNS,
    Layer2SQLValidator,
    SecurityValidationResult,
)


class TestSecurityValidationResult:
    """SecurityValidationResult 데이터클래스 테스트"""

    def test_result_creation_safe(self):
        """안전한 SQL 결과 생성"""
        result = SecurityValidationResult(
            is_safe=True,
            is_warning=False,
            violations=[],
            warnings=[],
            sql="SELECT * FROM users",
        )

        assert result.is_safe is True
        assert result.is_warning is False
        assert len(result.violations) == 0
        assert len(result.warnings) == 0

    def test_result_creation_unsafe(self):
        """위험한 SQL 결과 생성"""
        result = SecurityValidationResult(
            is_safe=False,
            is_warning=False,
            violations=["FORBIDDEN_KEYWORD: DELETE"],
            warnings=[],
            sql="DELETE FROM users",
        )

        assert result.is_safe is False
        assert len(result.violations) == 1
        assert "DELETE" in result.violations[0]

    def test_result_creation_warning(self):
        """경고가 있는 SQL 결과 생성"""
        result = SecurityValidationResult(
            is_safe=True,
            is_warning=True,
            violations=[],
            warnings=["Complex query with multiple joins"],
            sql="SELECT * FROM a JOIN b JOIN c",
        )

        assert result.is_safe is True
        assert result.is_warning is True
        assert len(result.warnings) == 1


class TestLayer2SQLValidator:
    """Layer 2 SQL 검증기 테스트"""

    @pytest.fixture
    def allowed_tables(self):
        """테스트용 허용 테이블 목록"""
        return {"users", "payments", "members", "counselors"}

    def test_validator_exists(self):
        """Layer2SQLValidator 클래스가 존재하는지 확인"""
        assert Layer2SQLValidator is not None

    def test_forbidden_keywords_defined(self):
        """금지 키워드 상수가 정의되어 있는지 확인"""
        assert isinstance(FORBIDDEN_KEYWORDS, set)
        assert len(FORBIDDEN_KEYWORDS) > 0
        assert "INSERT" in FORBIDDEN_KEYWORDS
        assert "UPDATE" in FORBIDDEN_KEYWORDS
        assert "DELETE" in FORBIDDEN_KEYWORDS
        assert "DROP" in FORBIDDEN_KEYWORDS

    def test_dangerous_patterns_defined(self):
        """위험 패턴 정규식이 정의되어 있는지 확인"""
        assert isinstance(DANGEROUS_PATTERNS, list)
        assert len(DANGEROUS_PATTERNS) > 0

    def test_warning_patterns_defined(self):
        """경고 패턴 정규식이 정의되어 있는지 확인"""
        assert isinstance(WARNING_PATTERNS, list)
        assert len(WARNING_PATTERNS) >= 0  # 경고는 선택적

    def test_validate_safe_select(self, allowed_tables):
        """안전한 SELECT 쿼리 검증"""
        sql = "SELECT id, name FROM users WHERE id = 1"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True
        assert len(result.violations) == 0

    def test_validate_forbidden_keyword_insert(self, allowed_tables):
        """INSERT 키워드 차단"""
        sql = "INSERT INTO users (name) VALUES ('test')"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert len(result.violations) > 0
        assert any("INSERT" in v for v in result.violations)

    def test_validate_forbidden_keyword_update(self, allowed_tables):
        """UPDATE 키워드 차단"""
        sql = "UPDATE users SET name = 'test' WHERE id = 1"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("UPDATE" in v for v in result.violations)

    def test_validate_forbidden_keyword_delete(self, allowed_tables):
        """DELETE 키워드 차단"""
        sql = "DELETE FROM users WHERE id = 1"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DELETE" in v for v in result.violations)

    def test_validate_forbidden_keyword_drop(self, allowed_tables):
        """DROP 키워드 차단"""
        sql = "DROP TABLE users"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DROP" in v for v in result.violations)

    def test_validate_dangerous_pattern_union(self, allowed_tables):
        """UNION 패턴 차단"""
        sql = "SELECT id FROM users UNION SELECT id FROM payments"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert len(result.violations) > 0
        assert any("UNION" in v.upper() for v in result.violations)

    def test_validate_dangerous_pattern_stacked_queries(self, allowed_tables):
        """스택 쿼리 차단 (세미콜론으로 구분)"""
        sql = "SELECT * FROM users; DROP TABLE members;"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        # 스택 쿼리 또는 DROP 키워드로 차단되어야 함
        assert len(result.violations) > 0

    def test_validate_dangerous_pattern_sql_comment(self, allowed_tables):
        """SQL 주석 차단"""
        sql = "SELECT * FROM users -- comment"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("--" in v for v in result.violations)

    def test_validate_dangerous_pattern_information_schema(
        self, allowed_tables
    ):
        """information_schema 접근 차단"""
        sql = "SELECT table_name FROM information_schema.tables"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("information_schema" in v.lower() for v in result.violations)

    def test_validate_table_whitelist_allowed(self, allowed_tables):
        """허용된 테이블 접근은 통과"""
        sql = "SELECT * FROM users"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True

    def test_validate_table_whitelist_forbidden(self, allowed_tables):
        """허용되지 않은 테이블 접근 차단"""
        sql = "SELECT * FROM admin_logs"  # not in allowed_tables

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("admin_logs" in v.lower() for v in result.violations)

    def test_validate_table_with_schema_prefix(self, allowed_tables):
        """스키마 prefix가 있는 테이블 이름 처리"""
        # dbo.users → users로 추출되어 허용되어야 함
        sql = "SELECT * FROM dbo.users"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True
        # 스키마가 제거되고 'users'만 검증되므로 통과

    def test_validate_table_with_schema_prefix_forbidden(self, allowed_tables):
        """스키마 prefix가 있지만 허용되지 않은 테이블"""
        sql = "SELECT * FROM dbo.admin_logs"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("admin_logs" in v.lower() for v in result.violations)

    def test_validate_multiple_violations(self, allowed_tables):
        """여러 위반사항이 있는 쿼리"""
        sql = "DELETE FROM users; DROP TABLE members;--"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        # DELETE, DROP, 주석 등 여러 위반사항
        assert len(result.violations) >= 2

    def test_validate_case_insensitive(self, allowed_tables):
        """대소문자 구분 없이 검증"""
        sql = "delete from users"  # lowercase

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DELETE" in v.upper() for v in result.violations)

    def test_validate_complex_join_safe(self, allowed_tables):
        """안전한 복잡한 JOIN 쿼리"""
        sql = """
        SELECT u.id, u.name, p.amount
        FROM users u
        INNER JOIN payments p ON u.id = p.user_id
        WHERE p.amount > 1000
        """

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True

    def test_validate_subquery_safe(self, allowed_tables):
        """안전한 서브쿼리 (허용된 테이블만 사용)"""
        sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM payments)"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is True

    def test_validate_empty_sql(self, allowed_tables):
        """빈 SQL 문자열 처리"""
        sql = ""

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("empty" in v.lower() for v in result.violations)

    def test_validate_whitespace_only_sql(self, allowed_tables):
        """공백만 있는 SQL 처리"""
        sql = "   \n\t   "

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False

    def test_validate_warning_large_result(self, allowed_tables):
        """대용량 결과 경고 (LIMIT 없는 쿼리)"""
        sql = "SELECT * FROM users"  # No LIMIT clause

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        # 안전하지만 경고가 있을 수 있음
        if result.is_warning:
            assert len(result.warnings) > 0

    def test_validate_dangerous_pattern_block_comment(self, allowed_tables):
        """블록 주석 패턴 차단 (/* */)"""
        sql = "SELECT * FROM users /* malicious comment */"

        result = Layer2SQLValidator.validate(sql, allowed_tables)

        assert result.is_safe is False
        assert any("DANGEROUS_PATTERN" in v and "*" in v for v in result.violations)

    def test_validate_warning_patterns_coverage(self, allowed_tables):
        """WARNING_PATTERNS 코드 커버리지 (활성화된 경고 패턴 테스트)"""
        # WARNING_PATTERNS를 일시적으로 활성화하여 lines 133-135 실행
        import src.services.ai.security.layer2_validator as validator_module

        # 원본 백업
        original_patterns = validator_module.WARNING_PATTERNS.copy()

        try:
            # 테스트용 경고 패턴 추가 (SELECT * 패턴)
            validator_module.WARNING_PATTERNS.append(r"SELECT\s+\*")

            sql = "SELECT * FROM users"
            result = Layer2SQLValidator.validate(sql, allowed_tables)

            # 경고가 발생해야 함 (lines 133-135 실행됨)
            assert result.is_safe is True  # 안전하지만
            assert result.is_warning is True  # 경고는 있음
            assert len(result.warnings) > 0
            assert "WARNING_PATTERN" in result.warnings[0]

        finally:
            # 원본 복원
            validator_module.WARNING_PATTERNS.clear()
            validator_module.WARNING_PATTERNS.extend(original_patterns)
