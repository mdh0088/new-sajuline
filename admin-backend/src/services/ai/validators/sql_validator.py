"""
SQL 검증기

생성된 SQL의 안전성을 검증합니다.

Stories: AI-002, AI-003
FRs: FR-011, FR-013
"""

from dataclasses import dataclass
from typing import Optional, Set

import sqlparse

from src.common.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SQLValidationResult:
    """SQL 검증 결과"""

    is_valid: bool
    is_select_only: bool
    tables_used: Set[str]
    error: Optional[str]
    warnings: list[str]


class SQLValidator:
    """생성된 SQL 검증

    LLM이 생성한 SQL이 안전하고 허용된 범위 내에 있는지 검증합니다.

    Attributes:
        FORBIDDEN_KEYWORDS: SQL 실행이 금지된 키워드 목록
    """

    # SQL Injection 및 데이터 변경 방지를 위한 금지 키워드
    FORBIDDEN_KEYWORDS = {
        # DML (데이터 조작)
        "INSERT",
        "UPDATE",
        "DELETE",
        "REPLACE",
        "MERGE",
        # DDL (데이터 정의)
        "CREATE",
        "ALTER",
        "DROP",
        "TRUNCATE",
        "RENAME",
        # DCL (데이터 제어)
        "GRANT",
        "REVOKE",
        # TCL (트랜잭션 제어)
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        # 시스템 명령
        "EXEC",
        "EXECUTE",
        "XP_",
        "SP_",
        # 파일 조작
        "INTO OUTFILE",
        "INTO DUMPFILE",
        "LOAD DATA",
        # 위험한 함수
        "SLEEP",
        "BENCHMARK",
    }

    @classmethod
    async def validate(
        cls, sql: str, allowed_tables: Set[str], strict_limit: bool = False
    ) -> SQLValidationResult:
        """SQL 유효성 검증

        Args:
            sql: 검증할 SQL 문자열
            allowed_tables: 허용된 테이블 목록
            strict_limit: True시 LIMIT 절 필수 (없으면 실패)

        Returns:
            SQLValidationResult: 검증 결과

        Examples:
            >>> result = await SQLValidator.validate(
            ...     sql="SELECT * FROM users LIMIT 100",
            ...     allowed_tables={"users", "payments"}
            ... )
            >>> assert result.is_valid is True
            >>> assert result.is_select_only is True
        """
        warnings = []

        # 빈 SQL 체크
        if not sql or not sql.strip():
            return SQLValidationResult(
                is_valid=False,
                is_select_only=False,
                tables_used=set(),
                error="SQL이 비어있습니다",
                warnings=[],
            )

        # SQL 정규화 (대문자 변환 for 키워드 검사)
        sql_upper = sql.upper()

        # 금지 키워드 검사
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                logger.warning(
                    "sql_validation_forbidden_keyword",
                    extra={
                        "event": "sql_validation_forbidden_keyword",
                        "keyword": keyword,
                        "sql": sql[:100],  # 처음 100자만 로그
                    },
                )
                return SQLValidationResult(
                    is_valid=False,
                    is_select_only=False,
                    tables_used=set(),
                    error=f"금지된 키워드가 포함되어 있습니다: {keyword}",
                    warnings=[],
                )

        # sqlparse로 SQL 파싱
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return SQLValidationResult(
                    is_valid=False,
                    is_select_only=False,
                    tables_used=set(),
                    error="SQL 파싱 실패",
                    warnings=[],
                )

            # 첫 번째 statement만 검사
            statement = parsed[0]

            # SELECT 문인지 확인
            is_select = cls._is_select_statement(statement)
            if not is_select:
                return SQLValidationResult(
                    is_valid=False,
                    is_select_only=False,
                    tables_used=set(),
                    error="SELECT 문만 허용됩니다",
                    warnings=[],
                )

            # 사용된 테이블 추출
            tables_used = cls._extract_tables(statement)

            # 허용되지 않은 테이블 사용 확인
            unauthorized_tables = tables_used - allowed_tables
            if unauthorized_tables:
                return SQLValidationResult(
                    is_valid=False,
                    is_select_only=True,
                    tables_used=tables_used,
                    error=f"허용되지 않은 테이블 사용: {', '.join(unauthorized_tables)}",
                    warnings=[],
                )

            # LIMIT 절 확인
            if "LIMIT" not in sql_upper:
                if strict_limit:
                    # Strict 모드: LIMIT 없으면 실패
                    return SQLValidationResult(
                        is_valid=False,
                        is_select_only=True,
                        tables_used=tables_used,
                        error="LIMIT 절이 필수입니다 (strict mode)",
                        warnings=[],
                    )
                else:
                    # 일반 모드: 경고만
                    warnings.append(
                        "LIMIT 절이 없습니다. 성능을 위해 LIMIT 사용을 권장합니다."
                    )

            # 검증 성공
            logger.info(
                "sql_validation_success",
                extra={
                    "event": "sql_validation_success",
                    "tables_used": list(tables_used),
                    "has_limit": "LIMIT" in sql_upper,
                },
            )

            return SQLValidationResult(
                is_valid=True,
                is_select_only=True,
                tables_used=tables_used,
                error=None,
                warnings=warnings,
            )

        except Exception as e:
            logger.error(
                "sql_validation_error",
                extra={
                    "event": "sql_validation_error",
                    "error": str(e),
                    "sql": sql[:100],
                },
                exc_info=True,
            )
            return SQLValidationResult(
                is_valid=False,
                is_select_only=False,
                tables_used=set(),
                error=f"SQL 검증 중 오류 발생: {str(e)}",
                warnings=[],
            )

    @staticmethod
    def _is_select_statement(statement) -> bool:
        """SQL statement가 SELECT인지 확인

        Args:
            statement: sqlparse.sql.Statement 객체

        Returns:
            bool: SELECT 문이면 True
        """
        # statement의 첫 번째 토큰이 SELECT 키워드인지 확인
        for token in statement.tokens:
            if token.ttype is None:
                continue
            if token.ttype in (sqlparse.tokens.Keyword.DML,):
                return token.value.upper() == "SELECT"
        return False

    @staticmethod
    def _extract_tables(statement) -> Set[str]:
        """SQL statement에서 사용된 테이블 추출 (재귀적으로 서브쿼리 포함)

        Args:
            statement: sqlparse.sql.Statement 객체

        Returns:
            Set[str]: 추출된 테이블 이름 집합
        """
        tables = set()

        # FROM 절과 JOIN 절에서 테이블 추출
        from_seen = False
        for token in statement.tokens:
            # 서브쿼리 재귀 처리
            if isinstance(token, sqlparse.sql.Parenthesis):
                # 괄호 안에 서브쿼리가 있을 수 있음
                subquery_sql = token.value
                try:
                    parsed_subquery = sqlparse.parse(subquery_sql)
                    for sub_stmt in parsed_subquery:
                        tables.update(SQLValidator._extract_tables(sub_stmt))
                except Exception:
                    # 파싱 실패 시 무시 (안전하게)
                    pass

            if from_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        table_name = identifier.get_real_name()
                        if table_name:
                            tables.add(table_name.lower())
                elif isinstance(token, sqlparse.sql.Identifier):
                    table_name = token.get_real_name()
                    if table_name:
                        tables.add(table_name.lower())
                elif (
                    token.ttype is sqlparse.tokens.Keyword
                    and "JOIN" in token.value.upper()
                ):
                    continue  # JOIN 키워드 후에 테이블이 오므로 계속 진행
                elif token.ttype is sqlparse.tokens.Keyword:
                    # 다른 키워드를 만나면 FROM 절 종료
                    from_seen = False

            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == "FROM":
                from_seen = True

        return tables
