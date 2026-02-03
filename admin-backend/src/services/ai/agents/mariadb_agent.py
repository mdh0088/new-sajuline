"""
MariaDB 질의 실행 에이전트.

Schema RAG로 테이블 구조를 로드하고 생성된 SQL을 실행합니다.
화이트리스트 테이블만 접근을 허용하고, 결과 행 수를 제한합니다.

Stories: 2-3
FRs: FR-011, FR-012
"""

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any

import aiomysql

from src.common.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """MariaDB 쿼리 실행 결과"""

    success: bool
    data: list[dict[str, str | int | float | None]] | None = None
    columns: list[str] | None = None
    row_count: int = 0
    total_count: int | None = None
    truncated: bool = False
    error_code: str | None = None
    error_message: str | None = None
    execution_time_ms: int = 0


class MariaDBAgent:
    """MariaDB 질의 실행 에이전트

    생성된 SQL을 MariaDB에서 실행하고 결과를 반환합니다.
    화이트리스트 테이블만 접근을 허용하고, 결과 행 수를 제한합니다.
    """

    MAX_ROWS = 1000
    QUERY_TIMEOUT = 30  # 초
    POOL_ACQUIRE_TIMEOUT = 10  # 연결 풀에서 연결 획득 타임아웃 (초)

    def __init__(self, pool: aiomysql.Pool):
        """
        Args:
            pool: aiomysql 연결 풀
        """
        self.pool = pool

    async def execute_query(
        self,
        sql: str,
        allowed_tables: set[str],
        max_rows: int | None = None,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> QueryResult:
        """SQL 실행 및 결과 반환

        Args:
            sql: 실행할 SQL 쿼리
            allowed_tables: 허용된 테이블 목록
            max_rows: 최대 반환 행 수 (기본값: 1000)
            user_id: 사용자 ID (Audit Trail용, 선택)
            session_id: 세션 ID (Audit Trail용, 선택)

        Returns:
            QueryResult: 쿼리 실행 결과
        """
        start_time = time.time()
        max_rows = max_rows or self.MAX_ROWS

        try:
            # 1. 테이블 접근 권한 검증
            tables_in_query = self._extract_tables(sql)
            unauthorized_tables = tables_in_query - allowed_tables

            if unauthorized_tables:
                error_msg = (
                    f"허용되지 않은 테이블 접근: {', '.join(unauthorized_tables)}"
                )
                logger.warning(
                    "unauthorized_table_access",
                    extra={
                        "event": "unauthorized_table_access",
                        "user_id": user_id,
                        "session_id": session_id,
                        "tables": list(unauthorized_tables),
                        "sql": sql,
                    },
                )
                return QueryResult(
                    success=False,
                    error_code="AIBI_TABLE_NOT_ALLOWED",
                    error_message=error_msg,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # 2. LIMIT 절 확인/추가
            sql_with_limit = self._ensure_limit(sql, max_rows)

            # 3. 쿼리 실행 (타임아웃 적용)
            try:
                # Pool에서 연결 획득 (타임아웃)
                async with asyncio.timeout(self.POOL_ACQUIRE_TIMEOUT):
                    async with self.pool.acquire() as conn:
                        # 쿼리 실행 (타임아웃)
                        async with asyncio.timeout(self.QUERY_TIMEOUT):
                            async with conn.cursor(aiomysql.DictCursor) as cursor:
                                await cursor.execute(sql_with_limit)

                                # 컬럼 이름 추출
                                columns = (
                                    [desc[0] for desc in cursor.description]
                                    if cursor.description
                                    else []
                                )

                                # 모든 결과 fetch
                                rows = await cursor.fetchall()
                                total_count = len(rows)

                                # 행 수 제한
                                truncated = total_count > max_rows
                                data = rows[:max_rows]
                                row_count = len(data)

                                execution_time_ms = int(
                                    (time.time() - start_time) * 1000
                                )

                                logger.info(
                                    "mariadb_query_executed",
                                    extra={
                                        "event": "mariadb_query_executed",
                                        "user_id": user_id,
                                        "session_id": session_id,
                                        "sql": sql,
                                        "row_count": row_count,
                                        "total_count": total_count,
                                        "truncated": truncated,
                                        "execution_time_ms": execution_time_ms,
                                        "tables": list(tables_in_query),
                                    },
                                )

                                return QueryResult(
                                    success=True,
                                    data=data,
                                    columns=columns,
                                    row_count=row_count,
                                    total_count=total_count if truncated else row_count,
                                    truncated=truncated,
                                    execution_time_ms=execution_time_ms,
                                )

            except asyncio.TimeoutError:
                execution_time_ms = int((time.time() - start_time) * 1000)
                # Pool 고갈인지 쿼리 타임아웃인지 구분
                if execution_time_ms < self.POOL_ACQUIRE_TIMEOUT * 1000:
                    # Pool 고갈
                    logger.warning(
                        "mariadb_pool_exhausted",
                        extra={
                            "event": "mariadb_pool_exhausted",
                            "user_id": user_id,
                            "session_id": session_id,
                            "sql": sql,
                        },
                    )
                    return QueryResult(
                        success=False,
                        error_code="AIBI_POOL_EXHAUSTED",
                        error_message="데이터베이스 연결이 일시적으로 혼잡합니다. 잠시 후 다시 시도해 주세요.",
                        execution_time_ms=execution_time_ms,
                    )
                else:
                    # 쿼리 타임아웃
                    logger.warning(
                        "mariadb_query_timeout",
                        extra={
                            "event": "mariadb_query_timeout",
                            "user_id": user_id,
                            "session_id": session_id,
                            "sql": sql,
                            "execution_time_ms": execution_time_ms,
                        },
                    )
                    return QueryResult(
                        success=False,
                        error_code="AIBI_QUERY_TIMEOUT",
                        error_message=f"쿼리 실행 시간이 {self.QUERY_TIMEOUT}초를 초과했습니다. 쿼리를 간단하게 수정하거나 잠시 후 다시 시도해 주세요.",
                        execution_time_ms=execution_time_ms,
                    )

        except aiomysql.OperationalError as e:
            error_code = e.args[0] if e.args else 0
            error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)

            # 타임아웃 에러 (1205)
            if error_code == 1205 or "timeout" in error_msg.lower():
                return QueryResult(
                    success=False,
                    error_code="AIBI_QUERY_TIMEOUT",
                    error_message="쿼리 실행 타임아웃이 발생했습니다. 쿼리를 간단하게 수정하거나 잠시 후 다시 시도해 주세요.",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )
            # 연결 오류 (2003)
            elif error_code == 2003 or "connect" in error_msg.lower():
                logger.error(
                    "mariadb_connection_error",
                    extra={
                        "event": "mariadb_connection_error",
                        "error": error_msg,
                    },
                )
                return QueryResult(
                    success=False,
                    error_code="AIBI_DB_CONNECTION_ERROR",
                    error_message="데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )
            else:
                logger.error(
                    "mariadb_operational_error",
                    extra={
                        "event": "mariadb_operational_error",
                        "error": error_msg,
                    },
                )
                return QueryResult(
                    success=False,
                    error_code="AIBI_DB_ERROR",
                    error_message=f"데이터베이스 오류가 발생했습니다: {error_msg}",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

        except aiomysql.ProgrammingError as e:
            error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
            logger.warning(
                "mariadb_syntax_error",
                extra={
                    "event": "mariadb_syntax_error",
                    "sql": sql,
                    "error": error_msg,
                },
            )
            return QueryResult(
                success=False,
                error_code="AIBI_SQL_SYNTAX_ERROR",
                error_message=f"SQL 문법 오류가 발생했습니다: {error_msg}",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        except Exception as e:
            logger.exception(
                "mariadb_unexpected_error",
                extra={
                    "event": "mariadb_unexpected_error",
                    "sql": sql,
                    "error": str(e),
                },
            )
            return QueryResult(
                success=False,
                error_code="AIBI_INTERNAL_ERROR",
                error_message=f"예기치 않은 오류가 발생했습니다: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    def _extract_tables(self, sql: str) -> set[str]:
        """SQL에서 테이블 이름 추출

        Args:
            sql: SQL 쿼리

        Returns:
            set[str]: 추출된 테이블 이름 목록

        Note:
            개선된 정규식으로 다음을 지원:
            - 백틱으로 감싸진 테이블: `table_name`
            - 여러 공백/줄바꿈
            - 서브쿼리 내 테이블 (재귀적 추출)
        """
        # 서브쿼리를 재귀적으로 처리
        tables = set()

        # 1. FROM, JOIN 절에서 테이블 추출 (개선된 패턴)
        # 백틱(`)과 여러 공백 지원
        pattern = r"(?:FROM|JOIN)\s+(?:`([a-zA-Z0-9_]+)`|([a-zA-Z0-9_]+))"
        matches = re.findall(pattern, sql, re.IGNORECASE | re.DOTALL)

        for match in matches:
            # match는 튜플 (백틱 그룹, 일반 그룹)
            table_name = match[0] if match[0] else match[1]
            if table_name:
                tables.add(table_name.lower())

        # 2. 서브쿼리 내 테이블 추출 (재귀)
        subquery_pattern = r"\(([^()]*SELECT[^()]*)\)"
        subqueries = re.findall(subquery_pattern, sql, re.IGNORECASE | re.DOTALL)
        for subquery in subqueries:
            # 재귀 호출
            tables.update(self._extract_tables(subquery))

        return tables

    def _ensure_limit(self, sql: str, max_rows: int) -> str:
        """SQL에 LIMIT 절이 없으면 추가, 있으면 max_rows와 비교하여 더 작은 값 사용

        Args:
            sql: SQL 쿼리
            max_rows: 최대 행 수

        Returns:
            str: LIMIT이 포함된 SQL (max_rows 이하로 제한됨)
        """
        # LIMIT 절 추출
        limit_match = re.search(r"\bLIMIT\s+(\d+)", sql, re.IGNORECASE)

        if limit_match:
            existing_limit = int(limit_match.group(1))
            # 기존 LIMIT이 max_rows보다 크면 교체
            if existing_limit > max_rows:
                return re.sub(
                    r"\bLIMIT\s+\d+",
                    f"LIMIT {max_rows}",
                    sql,
                    flags=re.IGNORECASE,
                )
            # 기존 LIMIT이 max_rows 이하면 그대로 사용
            return sql

        # LIMIT 없으면 추가 (세미콜론과 공백 제거)
        trimmed_sql = sql.rstrip("; \t\n")
        return f"{trimmed_sql} LIMIT {max_rows}"
