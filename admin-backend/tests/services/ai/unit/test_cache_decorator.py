"""
캐시 데코레이터 단위 테스트.

Stories: STORY-6-2
FRs: FR30, NFR-P6
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import time

from src.services.ai.utils.cache_decorator import cacheable
from src.services.ai.utils.cache_manager import AICacheManager, CacheEntry


@pytest.fixture
def mock_cache_manager():
    """Mock 캐시 매니저"""
    manager = AsyncMock(spec=AICacheManager)
    manager.get_cached_response = AsyncMock(return_value=None)
    manager.set_cached_response = AsyncMock(return_value=True)
    manager.record_response_time = AsyncMock()
    return manager


class TestCacheableDecorator:
    """cacheable 데코레이터 테스트"""

    @pytest.mark.asyncio
    async def test_cache_miss_executes_function(self, mock_cache_manager):
        """캐시 미스 시 함수 실행 테스트"""
        # 캐시 미스
        mock_cache_manager.get_cached_response.return_value = None

        @cacheable(mock_cache_manager)
        async def test_function(question, db_scope, admin_role):
            return {"answer": "실행됨", "from_cache": False}

        result = await test_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # 함수 실행 확인
        assert result["answer"] == "실행됨"
        assert result["from_cache"] is False

        # 캐시 조회 확인
        mock_cache_manager.get_cached_response.assert_called_once()

        # 캐시 저장 확인
        mock_cache_manager.set_cached_response.assert_called_once()

        # 응답 시간 기록 확인
        mock_cache_manager.record_response_time.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_data(self, mock_cache_manager):
        """캐시 히트 시 캐시 데이터 반환 테스트"""
        # 캐시 히트
        cached_entry = CacheEntry(
            data={"answer": "캐시된 데이터", "sql": "SELECT ..."},
            created_at="2024-01-01T00:00:00",
            hit_count=1,
            from_cache=True,
        )
        mock_cache_manager.get_cached_response.return_value = cached_entry

        function_executed = False

        @cacheable(mock_cache_manager)
        async def test_function(question, db_scope, admin_role):
            nonlocal function_executed
            function_executed = True
            return {"answer": "새 데이터"}

        result = await test_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # 캐시 데이터 반환 확인
        assert result["answer"] == "캐시된 데이터"
        assert result["from_cache"] is True
        assert result["cached_at"] == "2024-01-01T00:00:00"

        # 함수 실행 안 됨
        assert function_executed is False

        # 캐시 저장 안 됨
        mock_cache_manager.set_cached_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_miss_records_response_time(self, mock_cache_manager):
        """캐시 미스 시 응답 시간 기록 테스트"""
        mock_cache_manager.get_cached_response.return_value = None

        @cacheable(mock_cache_manager)
        async def slow_function(question, db_scope, admin_role):
            await asyncio.sleep(0.1)  # 100ms 지연
            return {"answer": "느린 응답"}

        import asyncio

        result = await slow_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # 응답 시간 기록 확인
        mock_cache_manager.record_response_time.assert_called_once()
        call_args = mock_cache_manager.record_response_time.call_args
        response_time = call_args.args[0]
        from_cache = call_args.kwargs["from_cache"]

        assert response_time >= 100  # 최소 100ms
        assert from_cache is False

    @pytest.mark.asyncio
    async def test_cache_hit_records_response_time(self, mock_cache_manager):
        """캐시 히트 시 응답 시간 기록 테스트"""
        cached_entry = CacheEntry(
            data={"answer": "캐시"},
            created_at="2024-01-01T00:00:00",
            hit_count=1,
            from_cache=True,
        )
        mock_cache_manager.get_cached_response.return_value = cached_entry

        @cacheable(mock_cache_manager)
        async def test_function(question, db_scope, admin_role):
            return {"answer": "새 데이터"}

        result = await test_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # 응답 시간 기록 확인
        mock_cache_manager.record_response_time.assert_called_once()
        call_args = mock_cache_manager.record_response_time.call_args
        from_cache = call_args.kwargs["from_cache"]

        assert from_cache is True

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(
        self, mock_cache_manager
    ):
        """데코레이터가 함수 메타데이터를 보존하는지 테스트"""

        @cacheable(mock_cache_manager)
        async def documented_function(question, db_scope, admin_role):
            """이것은 문서화된 함수입니다."""
            return {"answer": "test"}

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "이것은 문서화된 함수입니다."

    @pytest.mark.asyncio
    async def test_cache_with_different_roles(self, mock_cache_manager):
        """역할별로 다른 캐시 키 사용 테스트"""
        mock_cache_manager.get_cached_response.return_value = None

        @cacheable(mock_cache_manager)
        async def test_function(question, db_scope, admin_role):
            return {"answer": f"역할: {admin_role}"}

        # Admin 역할
        await test_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # Viewer 역할
        await test_function(
            question="테스트", db_scope="mariadb", admin_role="viewer"
        )

        # 두 번 호출 확인 (역할별로 다른 캐시 키)
        assert mock_cache_manager.get_cached_response.call_count == 2

        # 호출 인자 확인
        calls = mock_cache_manager.get_cached_response.call_args_list
        assert calls[0].kwargs["admin_role"] == "admin"
        assert calls[1].kwargs["admin_role"] == "viewer"

    @pytest.mark.asyncio
    async def test_cache_with_different_db_scopes(self, mock_cache_manager):
        """DB별로 다른 캐시 키 사용 테스트"""
        mock_cache_manager.get_cached_response.return_value = None

        @cacheable(mock_cache_manager)
        async def test_function(question, db_scope, admin_role):
            return {"answer": f"DB: {db_scope}"}

        # MariaDB
        await test_function(
            question="테스트", db_scope="mariadb", admin_role="admin"
        )

        # MSSQL
        await test_function(
            question="테스트", db_scope="mssql", admin_role="admin"
        )

        # 두 번 호출 확인 (DB별로 다른 캐시 키)
        assert mock_cache_manager.get_cached_response.call_count == 2

        # 호출 인자 확인
        calls = mock_cache_manager.get_cached_response.call_args_list
        assert calls[0].kwargs["db_scope"] == "mariadb"
        assert calls[1].kwargs["db_scope"] == "mssql"
