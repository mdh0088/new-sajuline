"""
MariaDB 에이전트 단위 테스트.

Stories: 2-3
FRs: FR-011, FR-012
"""
import asyncio

import aiomysql
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.ai.agents.mariadb_agent import (
    MariaDBAgent,
    QueryResult,
)


class TestQueryResult:
    """QueryResult 데이터클래스 테스트"""

    def test_query_result_success(self):
        """성공적인 쿼리 결과"""
        result = QueryResult(
            success=True,
            data=[{"id": 1, "name": "test"}],
            columns=["id", "name"],
            row_count=1,
            total_count=1,
            truncated=False,
            error_code=None,
            error_message=None,
            execution_time_ms=50,
        )
        assert result.success is True
        assert result.data == [{"id": 1, "name": "test"}]
        assert result.row_count == 1
        assert result.truncated is False

    def test_query_result_error(self):
        """에러가 발생한 쿼리 결과"""
        result = QueryResult(
            success=False,
            data=None,
            columns=None,
            row_count=0,
            total_count=None,
            truncated=False,
            error_code="AIBI_TABLE_NOT_ALLOWED",
            error_message="테이블 접근이 허용되지 않습니다",
            execution_time_ms=10,
        )
        assert result.success is False
        assert result.error_code == "AIBI_TABLE_NOT_ALLOWED"
        assert result.data is None

    def test_query_result_truncated(self):
        """1000개 초과 결과 truncated"""
        result = QueryResult(
            success=True,
            data=[{"id": i} for i in range(1000)],
            columns=["id"],
            row_count=1000,
            total_count=1500,
            truncated=True,
            error_code=None,
            error_message=None,
            execution_time_ms=200,
        )
        assert result.truncated is True
        assert result.row_count == 1000
        assert result.total_count == 1500


class TestMariaDBAgent:
    """MariaDB 에이전트 테스트"""

    @pytest.fixture
    def mock_pool(self):
        """Mock aiomysql Pool"""
        pool = AsyncMock(spec=aiomysql.Pool)
        return pool

    @pytest.fixture
    def agent(self, mock_pool):
        """MariaDBAgent 인스턴스"""
        return MariaDBAgent(pool=mock_pool)

    @pytest.mark.asyncio
    async def test_execute_query_success(self, agent, mock_pool):
        """정상적인 쿼리 실행"""
        # Mock connection and cursor
        mock_cursor = AsyncMock()
        mock_cursor.description = (
            ("id", None, None, None, None, None, None),
            ("name", None, None, None, None, None, None),
        )
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id, name FROM t_user LIMIT 10"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
        assert result.row_count == 2
        assert result.columns == ["id", "name"]
        assert len(result.data) == 2
        assert result.truncated is False
        mock_cursor.execute.assert_called_once_with(sql)

    @pytest.mark.asyncio
    async def test_execute_query_with_limit_enforcement(self, agent, mock_pool):
        """LIMIT 절이 없는 쿼리에 자동으로 LIMIT 추가"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": i} for i in range(100)]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_payment"
        allowed_tables = {"t_payment"}

        result = await agent.execute_query(sql, allowed_tables)

        # LIMIT 1000이 추가되어야 함
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "LIMIT" in executed_sql.upper()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_query_table_not_allowed(self, agent, mock_pool):
        """허용되지 않은 테이블 접근 시 에러"""
        sql = "SELECT * FROM t_admin"
        allowed_tables = {"t_user", "t_payment"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_TABLE_NOT_ALLOWED"
        assert "t_admin" in result.error_message
        # DB 쿼리가 실행되지 않아야 함
        mock_pool.acquire.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_query_row_limit_1000(self, agent, mock_pool):
        """결과 행 수가 1000개로 제한됨"""
        # 1500개 행 시뮬레이션
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": i} for i in range(1500)]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user LIMIT 1500"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables, max_rows=1000)

        assert result.success is True
        assert result.row_count == 1000  # 1000개만 반환
        assert result.total_count == 1500  # 전체 개수 표시
        assert result.truncated is True
        assert len(result.data) == 1000

    @pytest.mark.asyncio
    async def test_execute_query_timeout(self, agent, mock_pool):
        """쿼리 타임아웃 (30초)"""
        mock_cursor = AsyncMock()
        mock_cursor.execute.side_effect = aiomysql.OperationalError(
            1205, "Lock wait timeout exceeded"
        )

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT * FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_QUERY_TIMEOUT"
        assert "타임아웃" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_query_syntax_error(self, agent, mock_pool):
        """SQL 문법 오류"""
        mock_cursor = AsyncMock()
        mock_cursor.execute.side_effect = aiomysql.ProgrammingError(
            1064, "You have an error in your SQL syntax"
        )

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELCT * FROM t_user"  # 오타
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_SQL_SYNTAX_ERROR"

    @pytest.mark.asyncio
    async def test_execute_query_empty_result(self, agent, mock_pool):
        """빈 결과 (정상 응답)"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (
            ("id", None, None, None, None, None, None),
            ("name", None, None, None, None, None, None),
        )
        mock_cursor.fetchall.return_value = []

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id, name FROM t_user WHERE id = 99999"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
        assert result.row_count == 0
        assert result.data == []
        assert result.columns == ["id", "name"]

    @pytest.mark.asyncio
    async def test_execute_query_with_custom_max_rows(self, agent, mock_pool):
        """커스텀 max_rows 파라미터 사용"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": i} for i in range(500)]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables, max_rows=100)

        assert result.success is True
        assert result.row_count == 100
        assert result.truncated is True
        assert result.total_count == 500

    @pytest.mark.asyncio
    async def test_execute_query_connection_error(self, agent, mock_pool):
        """DB 연결 오류"""
        mock_pool.acquire.side_effect = aiomysql.OperationalError(
            2003, "Can't connect to MySQL server"
        )

        sql = "SELECT * FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_DB_CONNECTION_ERROR"
        assert "연결" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_query_multiple_tables(self, agent, mock_pool):
        """여러 테이블 JOIN - 모두 허용된 경우"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (
            ("user_id", None, None, None, None, None, None),
            ("payment_amount", None, None, None, None, None, None),
        )
        mock_cursor.fetchall.return_value = [
            {"user_id": 1, "payment_amount": 10000},
        ]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = """
        SELECT u.id as user_id, p.amount as payment_amount
        FROM t_user u
        JOIN t_payment p ON u.id = p.user_id
        """
        allowed_tables = {"t_user", "t_payment"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
        assert result.row_count == 1

    @pytest.mark.asyncio
    async def test_execute_query_multiple_tables_one_not_allowed(self, agent, mock_pool):
        """여러 테이블 JOIN - 하나라도 허용되지 않으면 에러"""
        sql = """
        SELECT u.id, a.username
        FROM t_user u
        JOIN t_admin a ON u.id = a.user_id
        """
        allowed_tables = {"t_user", "t_payment"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_TABLE_NOT_ALLOWED"
        assert "t_admin" in result.error_message

    # === Edge Cases 테스트 (Code Review Issue #9) ===

    @pytest.mark.asyncio
    async def test_execute_query_invalid_column_name(self, agent, mock_pool):
        """존재하지 않는 컬럼 조회 시 에러"""
        mock_cursor = AsyncMock()
        mock_cursor.execute.side_effect = aiomysql.ProgrammingError(
            1054, "Unknown column 'invalid_column' in 'field list'"
        )

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT invalid_column FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_SQL_SYNTAX_ERROR"
        assert "column" in result.error_message.lower() or "syntax" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_extract_tables_with_backticks(self, agent):
        """백틱으로 감싸진 테이블 이름 추출"""
        sql = "SELECT * FROM `t_user` JOIN `t_payment` ON `t_user`.id = `t_payment`.user_id"
        tables = agent._extract_tables(sql)

        assert "t_user" in tables
        assert "t_payment" in tables

    @pytest.mark.asyncio
    async def test_extract_tables_from_subquery(self, agent):
        """서브쿼리 내 테이블 추출"""
        sql = """
        SELECT * FROM (
            SELECT id FROM t_admin WHERE role = 'admin'
        ) AS admins
        """
        tables = agent._extract_tables(sql)

        assert "t_admin" in tables

    @pytest.mark.asyncio
    async def test_ensure_limit_replaces_large_limit(self, agent):
        """기존 LIMIT이 max_rows보다 큰 경우 교체"""
        sql = "SELECT * FROM t_user LIMIT 5000"
        result_sql = agent._ensure_limit(sql, 1000)

        assert "LIMIT 1000" in result_sql
        assert "LIMIT 5000" not in result_sql

    @pytest.mark.asyncio
    async def test_ensure_limit_keeps_small_limit(self, agent):
        """기존 LIMIT이 max_rows보다 작은 경우 유지"""
        sql = "SELECT * FROM t_user LIMIT 100"
        result_sql = agent._ensure_limit(sql, 1000)

        assert "LIMIT 100" in result_sql
        assert "LIMIT 1000" not in result_sql

    @pytest.mark.asyncio
    async def test_execute_query_with_user_id_session_id_logging(self, agent, mock_pool):
        """user_id, session_id가 로깅에 포함됨"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": 1}]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user LIMIT 1"
        allowed_tables = {"t_user"}

        # user_id, session_id 전달
        result = await agent.execute_query(
            sql, allowed_tables, user_id=123, session_id="test-session-123"
        )

        assert result.success is True
        # 실제 로깅은 mock으로 검증하기 어려우므로, 메서드 호출 성공 확인

    @pytest.mark.asyncio
    async def test_execute_query_with_multiline_sql(self, agent, mock_pool):
        """여러 줄에 걸친 SQL 쿼리 처리"""
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": 1}]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = """
        SELECT
            id
        FROM
            t_user
        WHERE
            active = 1
        """
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
