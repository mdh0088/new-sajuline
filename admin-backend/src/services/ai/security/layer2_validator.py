"""
Layer 2: SQL 보안 검증.

생성된 SQL을 화이트리스트 기반으로 검증하여 위험한 패턴을 차단합니다.

Stories: 3-1, 3-2
FRs: FR-021 (4-Layer Security), FR-014, FR-015
"""

import re
from dataclasses import dataclass, field
from typing import Set

from src.services.ai.security.injection_detector import SQLInjectionDetector
from src.services.ai.security.table_guard import TableAccessGuard

# 금지 키워드 (대문자로 정의, 검증 시 대소문자 무시)
# 추가 보안 레이어: SQLInjectionDetector와 함께 사용하여 다층 방어
FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "CREATE",
    "ALTER",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "XP_",
    "SP_",
    "LOAD_FILE",
    "INTO OUTFILE",
    "INTO DUMPFILE",
}

# DEPRECATED: 이제 SQLInjectionDetector를 사용합니다 (Story 3-2)
# 하위 호환성을 위해 유지하지만 사용하지 않습니다
DANGEROUS_PATTERNS = [
    r"UNION\s+(?:ALL\s+)?SELECT",  # UNION Injection
    r";\s*SELECT",  # Stacked queries (semicolon)
    r";\s*\w+",  # Stacked queries (any statement after semicolon)
    r"--",  # SQL line comments
    r"/\*.*?\*/",  # Block comments
    r"BENCHMARK\s*\(",  # Time-based injection
    r"SLEEP\s*\(",  # Time-based injection
    r"information_schema",  # Schema enumeration (case insensitive)
    r"mysql\.",  # MySQL system database
    r"pg_catalog\.",  # PostgreSQL system catalog
]

# 경고 패턴 (안전하지만 주의 필요)
WARNING_PATTERNS: list[str] = [
    # r"SELECT\s+\*",  # SELECT * (컬럼 명시 권장, but too strict)
    # r"(?:JOIN\s+){3,}",  # 3개 이상 JOIN (복잡도 경고, optional)
]


@dataclass
class SecurityValidationResult:
    """
    SQL 보안 검증 결과.

    Attributes:
        is_safe: 쿼리가 안전한지 여부
        is_warning: 경고가 있는지 여부 (안전하지만 주의 필요)
        violations: 보안 위반 사항 목록
        warnings: 경고 사항 목록
        sql: 검증된 SQL 문자열
    """

    is_safe: bool
    is_warning: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sql: str = ""


class Layer2SQLValidator:
    """Layer 2: SQL 보안 검증기"""

    @classmethod
    def validate(
        cls, sql: str, allowed_tables: Set[str]
    ) -> SecurityValidationResult:
        """
        SQL 보안 검증 수행.

        Args:
            sql: 검증할 SQL 문자열
            allowed_tables: 허용된 테이블 목록

        Returns:
            SecurityValidationResult: 검증 결과
        """
        violations: list[str] = []
        warnings: list[str] = []

        # 1. 빈 SQL 체크
        if not sql or not sql.strip():
            violations.append(
                "EMPTY_SQL: SQL query is empty or whitespace-only"
            )
            return SecurityValidationResult(
                is_safe=False,
                is_warning=False,
                violations=violations,
                warnings=warnings,
                sql=sql,
            )

        # 대소문자 무시를 위해 대문자 변환 (원본은 유지)
        sql_upper = sql.upper()

        # 2. 금지 키워드 검증 (추가 보안 레이어)
        for keyword in FORBIDDEN_KEYWORDS:
            # 단어 경계를 고려하여 검사 (예: "INSERTED" != "INSERT")
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, sql_upper):
                violations.append(f"FORBIDDEN_KEYWORD: {keyword}")

        # 3. SQL Injection 패턴 검증 (Story 3-2)
        injection_result = SQLInjectionDetector.detect(sql)
        if injection_result.is_injection:
            for pattern_name in injection_result.patterns_detected:
                violations.append(f"SQL_INJECTION: {pattern_name}")

        # 4. 테이블 접근 제어 검증 (Story 3-2)
        table_access_result = TableAccessGuard.check_access(
            sql=sql, allowed_tables=allowed_tables, is_super_admin=False
        )
        if not table_access_result.allowed:
            for blocked_table in table_access_result.blocked_tables:
                violations.append(f"TABLE_ACCESS_DENIED: {blocked_table}")

        # 5. 경고 패턴 검증 (선택적)
        for pattern in WARNING_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                pattern_name = pattern[:30]
                warnings.append(f"WARNING_PATTERN: {pattern_name}")

        # 결과 생성
        is_safe = len(violations) == 0
        is_warning = len(warnings) > 0

        return SecurityValidationResult(
            is_safe=is_safe,
            is_warning=is_warning,
            violations=violations,
            warnings=warnings,
            sql=sql,
        )
