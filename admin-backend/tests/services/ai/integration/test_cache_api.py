"""
캐시 API 통합 테스트.

Stories: STORY-6-2
FRs: FR30
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from httpx import AsyncClient

from src.api.v1.ai_assistant_api import router
from src.models.admin_model import Admin
from src.services.ai.utils.cache_manager import CacheStats


@pytest.fixture
def app():
    """FastAPI 앱 생성"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_admin():
    """Mock admin user"""
    admin = Admin(
        id=1,
        login_id="test_admin",
        name="Test Admin",
        role="super_admin",
        is_active=True,
    )
    return admin


@pytest.mark.asyncio
async def test_get_cache_stats(app, mock_admin):
    """캐시 통계 조회 API 테스트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock dependencies
        with patch("src.api.v1.ai_assistant_api.get_current_admin", return_value=mock_admin):
            with patch("src.api.v1.ai_assistant_api.get_redis_client") as mock_redis:
                mock_redis_instance = AsyncMock()
                mock_redis.return_value = mock_redis_instance

                # Mock cache manager
                with patch("src.api.v1.ai_assistant_api.AICacheManager") as MockCacheManager:
                    mock_cache_manager = AsyncMock()
                    mock_cache_manager.get_stats.return_value = CacheStats(
                        total_requests=100,
                        cache_hits=30,
                        cache_misses=70,
                        hit_rate=30.0,
                        avg_response_time_cached=50.0,
                        avg_response_time_uncached=250.0,
                    )
                    MockCacheManager.return_value = mock_cache_manager

                    response = await client.get("/ai/cache/stats")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["total_requests"] == 100
                    assert data["cache_hits"] == 30
                    assert data["hit_rate"] == 30.0


@pytest.mark.asyncio
async def test_invalidate_cache_super_admin(app, mock_admin):
    """캐시 무효화 API 테스트 (Super Admin)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("src.api.v1.ai_assistant_api.get_current_admin", return_value=mock_admin):
            with patch("src.api.v1.ai_assistant_api.get_redis_client") as mock_redis:
                mock_redis_instance = AsyncMock()
                mock_redis.return_value = mock_redis_instance

                with patch("src.api.v1.ai_assistant_api.AICacheManager") as MockCacheManager:
                    mock_cache_manager = AsyncMock()
                    mock_cache_manager.invalidate_by_pattern.return_value = 5
                    MockCacheManager.return_value = mock_cache_manager

                    response = await client.post("/ai/cache/invalidate?pattern=query:")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["deleted_count"] == 5


@pytest.mark.asyncio
async def test_invalidate_cache_non_super_admin(app):
    """캐시 무효화 API 테스트 (Non Super Admin - 권한 거부)"""
    # Regular admin
    regular_admin = Admin(
        id=2,
        login_id="regular_admin",
        name="Regular Admin",
        role="admin",
        is_active=True,
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("src.api.v1.ai_assistant_api.get_current_admin", return_value=regular_admin):
            response = await client.post("/ai/cache/invalidate")

            assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalidate_all_cache(app, mock_admin):
    """전체 캐시 무효화 API 테스트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("src.api.v1.ai_assistant_api.get_current_admin", return_value=mock_admin):
            with patch("src.api.v1.ai_assistant_api.get_redis_client") as mock_redis:
                mock_redis_instance = AsyncMock()
                mock_redis.return_value = mock_redis_instance

                with patch("src.api.v1.ai_assistant_api.AICacheManager") as MockCacheManager:
                    mock_cache_manager = AsyncMock()
                    mock_cache_manager.invalidate_all.return_value = 10
                    MockCacheManager.return_value = mock_cache_manager

                    response = await client.post("/ai/cache/invalidate")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["deleted_count"] == 10
