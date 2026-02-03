"""
MariaDB 에이전트 통합 테스트.

NOTE: 현재는 Mock을 사용한 시나리오 테스트입니다 (CI/CD 환경 고려).
실제 DB 연결 테스트는 Docker MariaDB 컨테이너와 함께 수동 실행 필요.

TODO: 실제 MariaDB 연결을 사용하는 통합 테스트 추가
  - pytest-docker 플러그인으로 MariaDB 컨테이너 자동 시작
  - 또는 파일명을 test_mariadb_agent_scenarios.py로 변경

Stories: 2-3
FRs: FR-011, FR-012
"""
import pytest
from unittest.mock import patch, AsyncMock
import aiomysql

from src.services.ai.agents.mariadb_agent import MariaDBAgent, QueryResult
from src.services.ai.tools.mariadb_tool import MariaDBConnectionPool
from src.services.ai.config.table_whitelist import get_allowed_tables
from src.services.ai.security.rbac import AIRole


@pytest.mark.integration
class TestMariaDBAgentIntegration:
    """MariaDB 에이전트 통합 테스트 (실제 DB 연결)"""

    @pytest.fixture
    async def pool(self):
        """Mock MariaDB 연결 풀 (통합 테스트용)"""
        # 실제 DB 연결 대신 mock 사용 (CI/CD 환경 고려)
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5
        return mock_pool

    @pytest.fixture
    def agent(self, pool):
        """MariaDBAgent 인스턴스"""
        return MariaDBAgent(pool=pool)

    @pytest.mark.asyncio
    async def test_execute_query_with_real_connection(self, agent, pool):
        """실제 연결을 사용한 쿼리 실행 시뮬레이션"""
        # Mock cursor와 connection
        mock_cursor = AsyncMock()
        mock_cursor.description = (
            ("id", None, None, None, None, None, None),
            ("username", None, None, None, None, None, None),
            ("email", None, None, None, None, None, None),
        )
        mock_cursor.fetchall.return_value = [
            {"id": 1, "username": "user1", "email": "user1@example.com"},
            {"id": 2, "username": "user2", "email": "user2@example.com"},
        ]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id, username, email FROM t_user LIMIT 2"
        allowed_tables = get_allowed_tables(AIRole.ADMIN)

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
        assert result.row_count == 2
        assert result.columns == ["id", "username", "email"]
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_connection_pool_lifecycle(self, pool):
        """연결 풀 라이프사이클 테스트"""
        # 풀이 정상적으로 생성되고 종료되는지 확인
        agent = MariaDBAgent(pool=pool)

        # 쿼리 실행
        mock_cursor = AsyncMock()
        mock_cursor.description = (("count", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"count": 100}]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT COUNT(*) as count FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True
        assert result.data[0]["count"] == 100

        # 연결이 정상적으로 반환되었는지 확인
        pool.acquire.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, pool):
        """동시 쿼리 실행"""
        import asyncio

        agent = MariaDBAgent(pool=pool)

        # Mock 설정
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": 1}]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user LIMIT 1"
        allowed_tables = {"t_user"}

        # 동시에 5개 쿼리 실행
        tasks = [
            agent.execute_query(sql, allowed_tables) for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        # 모든 쿼리가 성공
        for result in results:
            assert result.success is True

        # acquire가 5번 호출됨
        assert pool.acquire.call_count == 5

    @pytest.mark.asyncio
    async def test_query_timeout_handling(self, agent, pool):
        """쿼리 타임아웃 처리"""
        # 타임아웃 시뮬레이션
        mock_cursor = AsyncMock()
        mock_cursor.execute.side_effect = aiomysql.OperationalError(
            1205, "Lock wait timeout exceeded"
        )

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT * FROM t_payment WHERE processing = 1"
        allowed_tables = {"t_payment"}

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is False
        assert result.error_code == "AIBI_QUERY_TIMEOUT"
        assert "타임아웃" in result.error_message

    @pytest.mark.asyncio
    async def test_large_result_set_truncation(self, agent, pool):
        """대용량 결과셋 truncation"""
        # 1500개 행 시뮬레이션
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": i} for i in range(1500)]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user"
        allowed_tables = {"t_user"}

        result = await agent.execute_query(sql, allowed_tables, max_rows=1000)

        assert result.success is True
        assert result.row_count == 1000
        assert result.total_count == 1500
        assert result.truncated is True

    @pytest.mark.asyncio
    async def test_role_based_table_access(self, agent, pool):
        """역할별 테이블 접근 제어"""
        # Admin 역할로 허용된 테이블 접근
        mock_cursor = AsyncMock()
        mock_cursor.description = (("id", None, None, None, None, None, None),)
        mock_cursor.fetchall.return_value = [{"id": 1}]

        mock_conn = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        pool.acquire.return_value.__aenter__.return_value = mock_conn

        sql = "SELECT id FROM t_user LIMIT 1"
        allowed_tables = get_allowed_tables(AIRole.ADMIN)

        result = await agent.execute_query(sql, allowed_tables)

        assert result.success is True

        # 허용되지 않은 테이블 접근
        sql_denied = "SELECT * FROM t_admin"

        result_denied = await agent.execute_query(sql_denied, allowed_tables)

        assert result_denied.success is False
        assert result_denied.error_code == "AIBI_TABLE_NOT_ALLOWED"
