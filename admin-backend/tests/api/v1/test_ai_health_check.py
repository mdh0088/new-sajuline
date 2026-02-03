"""
AI Assistant Health Check 엔드포인트 테스트.

Stories: 1-1, 2-1
FRs: FR-011
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestAIHealthCheck:
    """AI Assistant Health Check 엔드포인트 테스트"""

    def test_health_check_success_all_healthy(self):
        """모든 서비스가 정상일 때 healthy 응답"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis, patch(
            "openai.AsyncOpenAI"
        ) as mock_openai:
            # Redis 정상
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.close = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            # OpenAI 정상
            mock_openai_instance = AsyncMock()
            mock_openai_instance.models.list = AsyncMock()
            mock_openai.return_value = mock_openai_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["redis_connected"] is True
            assert data["openai_connected"] is True
            assert data["message"] is None

    def test_health_check_redis_failure(self):
        """Redis 연결 실패 시 unhealthy 응답"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis, patch(
            "openai.AsyncOpenAI"
        ) as mock_openai:
            # Redis 실패
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock(
                side_effect=Exception("Redis connection failed")
            )
            mock_redis.return_value = mock_redis_instance

            # OpenAI 정상
            mock_openai_instance = AsyncMock()
            mock_openai_instance.models.list = AsyncMock()
            mock_openai.return_value = mock_openai_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis_connected"] is False
            assert data["openai_connected"] is True
            assert "Redis" in data["message"]

    def test_health_check_openai_failure(self):
        """OpenAI API 연결 실패 시 unhealthy 응답"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis, patch(
            "openai.AsyncOpenAI"
        ) as mock_openai:
            # Redis 정상
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.close = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            # OpenAI 실패
            mock_openai_instance = AsyncMock()
            mock_openai_instance.models.list = AsyncMock(
                side_effect=Exception("OpenAI API failed")
            )
            mock_openai.return_value = mock_openai_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis_connected"] is True
            assert data["openai_connected"] is False
            assert "OpenAI" in data["message"]

    def test_health_check_all_failures(self):
        """모든 서비스 실패 시 unhealthy 응답"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis, patch(
            "openai.AsyncOpenAI"
        ) as mock_openai:
            # Redis 실패
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock(
                side_effect=Exception("Redis connection failed")
            )
            mock_redis.return_value = mock_redis_instance

            # OpenAI 실패
            mock_openai_instance = AsyncMock()
            mock_openai_instance.models.list = AsyncMock(
                side_effect=Exception("OpenAI API failed")
            )
            mock_openai.return_value = mock_openai_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis_connected"] is False
            assert data["openai_connected"] is False
            assert "Redis" in data["message"]
            assert "OpenAI" in data["message"]

    def test_health_check_no_openai_api_key(self):
        """OpenAI API 키가 설정되지 않았을 때"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis, patch(
            "src.config.settings.settings.openai_api_key", ""
        ):
            # Redis 정상
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.close = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis_connected"] is True
            assert data["openai_connected"] is False
            assert "API 키가 설정되지 않았습니다" in data["message"]

    def test_health_check_without_authentication(self):
        """인증 없이 health check 호출 (선택적 인증)"""
        response = client.get("/api/v1/ai/health")

        # 인증 없이도 접근 가능해야 함
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_redis_timeout(self):
        """Redis 타임아웃 처리"""
        with patch("redis.asyncio.Redis.from_url") as mock_redis:
            # Redis 타임아웃
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock(side_effect=TimeoutError("Timeout"))
            mock_redis.return_value = mock_redis_instance

            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis_connected"] is False
