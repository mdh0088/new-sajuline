"""
Layer 2: SQL 보안 검증.

생성된 SQL을 화이트리스트 기반으로 검증하여 위험한 패턴을 차단합니다.

Stories: 3-1
FRs: FR-021 (4-Layer Security)
"""

import re
from dataclasses import dataclass, field
from typing import Set

# 금지 키워드 (대문자로 정의, 검증 시 대소문자 무시)
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

# 위험 패턴 (정규식)
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
    def validate(cls, sql: str, allowed_tables: Set[str]) -> SecurityValidationResult:
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
            violations.append("EMPTY_SQL: SQL query is empty or whitespace-only")
            return SecurityValidationResult(
                is_safe=False,
                is_warning=False,
                violations=violations,
                warnings=warnings,
                sql=sql,
            )

        # 대소문자 무시를 위해 대문자 변환 (원본은 유지)
        sql_upper = sql.upper()

        # 2. 금지 키워드 검증
        for keyword in FORBIDDEN_KEYWORDS:
            # 단어 경계를 고려하여 검사 (예: "INSERTED" != "INSERT")
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, sql_upper):
                violations.append(f"FORBIDDEN_KEYWORD: {keyword}")

        # 3. 위험 패턴 검증 (정규식)
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE | re.DOTALL):
                pattern_name = pattern[:30]  # 패턴 이름 축약
                violations.append(f"DANGEROUS_PATTERN: {pattern_name}")

        # 4. 테이블 화이트리스트 검증
        # FROM/JOIN 절에서 테이블 이름 추출 (스키마.테이블 형식 포함)
        table_pattern = r"\b(?:FROM|JOIN)\s+(?:([a-zA-Z_][a-zA-Z0-9_]*)\.)?([a-zA-Z_][a-zA-Z0-9_]*)"
        found_tables_raw = re.findall(table_pattern, sql, re.IGNORECASE)

        # (schema, table) 튜플에서 table만 추출 (스키마 prefix 제거)
        found_tables = [table for schema, table in found_tables_raw]

        for table in found_tables:
            if table.lower() not in {t.lower() for t in allowed_tables}:
                violations.append(
                    f"TABLE_NOT_ALLOWED: '{table}' is not in allowed tables"
                )

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
