"""
MariaDB 연결 풀 관리자 테스트.

Stories: 2-3
FRs: FR-011, NFR-I1
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiomysql

from src.services.ai.tools.mariadb_tool import MariaDBConnectionPool


class TestMariaDBConnectionPool:
    """MariaDB 연결 풀 테스트"""

    @pytest.fixture(autouse=True)
    async def reset_pool(self):
        """각 테스트마다 풀 초기화"""
        if MariaDBConnectionPool._pool:
            await MariaDBConnectionPool.close_pool()
        MariaDBConnectionPool._pool = None
        MariaDBConnectionPool._initialized = False
        yield
        # 테스트 후 정리
        if MariaDBConnectionPool._pool:
            await MariaDBConnectionPool.close_pool()

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_get_pool_creates_singleton(self, mock_create_pool):
        """연결 풀이 싱글톤으로 생성됨"""
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5
        mock_create_pool.return_value = mock_pool

        # 첫 번째 호출
        pool1 = await MariaDBConnectionPool.get_pool()

        # 두 번째 호출
        pool2 = await MariaDBConnectionPool.get_pool()

        # 같은 인스턴스
        assert pool1 is pool2

        # create_pool은 한 번만 호출됨
        mock_create_pool.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_get_pool_configuration(self, mock_create_pool):
        """연결 풀 설정이 올바름"""
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5
        mock_create_pool.return_value = mock_pool

        await MariaDBConnectionPool.get_pool()

        # create_pool 호출 인자 확인
        call_kwargs = mock_create_pool.call_args.kwargs

        assert call_kwargs["minsize"] == 5
        assert call_kwargs["maxsize"] == 20
        assert call_kwargs["autocommit"] is True
        assert call_kwargs["charset"] == "utf8mb4"
        assert call_kwargs["connect_timeout"] == 10

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_close_pool(self, mock_create_pool):
        """연결 풀 종료"""
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5
        mock_create_pool.return_value = mock_pool

        # 풀 생성
        await MariaDBConnectionPool.get_pool()

        # 풀 종료
        await MariaDBConnectionPool.close_pool()

        # 종료 메서드 호출 확인
        mock_pool.close.assert_called_once()
        mock_pool.wait_closed.assert_called_once()

        # 싱글톤 초기화 확인
        assert MariaDBConnectionPool._pool is None
        assert MariaDBConnectionPool._initialized is False

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_connection_context_manager(self, mock_create_pool):
        """컨텍스트 매니저로 연결 가져오기"""
        mock_conn = AsyncMock(spec=aiomysql.Connection)
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_create_pool.return_value = mock_pool

        # 컨텍스트 매니저 사용
        async with MariaDBConnectionPool.connection() as conn:
            assert conn == mock_conn

        # acquire가 호출됨
        mock_pool.acquire.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_connection_error_handling(self, mock_create_pool):
        """연결 중 에러 발생 시 예외 전파"""
        mock_pool = AsyncMock(spec=aiomysql.Pool)
        mock_pool._closed = False
        mock_pool.size = 5
        mock_pool.freesize = 5

        # acquire에서 에러 발생
        mock_pool.acquire.return_value.__aenter__.side_effect = Exception(
            "Connection failed"
        )
        mock_create_pool.return_value = mock_pool

        # 에러가 전파되어야 함
        with pytest.raises(Exception, match="Connection failed"):
            async with MariaDBConnectionPool.connection() as conn:
                pass

    @pytest.mark.asyncio
    @patch("src.services.ai.tools.mariadb_tool.aiomysql.create_pool")
    async def test_pool_recreated_after_close(self, mock_create_pool):
        """종료 후 다시 get_pool 호출 시 재생성됨"""
        mock_pool1 = AsyncMock(spec=aiomysql.Pool)
        mock_pool1._closed = False
        mock_pool1.size = 5
        mock_pool1.freesize = 5

        mock_pool2 = AsyncMock(spec=aiomysql.Pool)
        mock_pool2._closed = False
        mock_pool2.size = 5
        mock_pool2.freesize = 5

        mock_create_pool.side_effect = [mock_pool1, mock_pool2]

        # 첫 번째 풀 생성
        pool1 = await MariaDBConnectionPool.get_pool()
        assert pool1 == mock_pool1

        # 풀 종료
        await MariaDBConnectionPool.close_pool()

        # 두 번째 풀 생성
        pool2 = await MariaDBConnectionPool.get_pool()
        assert pool2 == mock_pool2

        # create_pool이 두 번 호출됨
        assert mock_create_pool.call_count == 2
