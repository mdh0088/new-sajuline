"""
AI 예시 질문 및 히스토리 API 통합 테스트.

Stories: 4-1
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.main import app


client = TestClient(app)


@pytest.fixture
def mock_admin():
    """Mock 관리자 객체."""
    admin = MagicMock()
    admin.admin_id = "test_admin"
    admin.role = "super_admin"
    return admin


@pytest.fixture
def mock_auth_dependency(mock_admin):
    """인증 의존성 Mock."""
    def override_get_current_admin():
        return mock_admin
    return override_get_current_admin


@pytest.fixture
def mock_permission():
    """권한 의존성 Mock."""
    permission = MagicMock()
    permission.can_query = True
    return permission


@pytest.fixture
def mock_permission_dependency(mock_permission):
    """권한 체크 의존성 Mock."""
    def override_check_ai_permission():
        return mock_permission
    return override_check_ai_permission


@pytest.fixture
def mock_rate_limit_dependency(mock_admin):
    """Rate Limit 의존성 Mock."""
    def override_rate_limit():
        return mock_admin
    return override_rate_limit


class TestExamplesAPI:
    """GET /api/v1/ai/examples 통합 테스트."""

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    def test_get_examples_success(
        self,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
        mock_permission_dependency,
    ):
        """AC1: 예시 질문 목록 조회 성공."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()

        # API 호출
        response = client.get("/api/v1/ai/examples")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

        # AC1: 최소 10개 질문
        total_questions = sum(
            len(cat["questions"]) for cat in data["categories"]
        )
        assert total_questions >= 10

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    def test_get_examples_with_category_filter(
        self,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
    ):
        """AC1: 카테고리 필터링."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()

        # API 호출
        response = client.get("/api/v1/ai/examples?category=매출")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "매출"

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    @patch("src.api.v1.ai_assistant_api.redis.from_url")
    def test_get_examples_redis_cache(
        self,
        mock_redis,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
    ):
        """AC6: Redis 캐시 적용."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()

        # Redis Mock
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None  # 캐시 미스
        mock_redis_client.setex = AsyncMock()
        mock_redis_client.close = AsyncMock()
        mock_redis.return_value = mock_redis_client

        # API 호출
        response = client.get("/api/v1/ai/examples")

        # 검증
        assert response.status_code == 200
        # Redis setex 호출 확인 (캐시 저장)
        assert mock_redis_client.setex.called


class TestHistoryAPI:
    """GET /api/v1/ai/history 통합 테스트."""

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.AIHistoryService")
    def test_get_history_success(
        self,
        mock_service_class,
        mock_get_db,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
    ):
        """AC3: 히스토리 조회 성공."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()
        mock_get_db.return_value = AsyncMock()

        # 히스토리 서비스 Mock
        mock_service = AsyncMock()
        mock_service.get_history.return_value = []
        mock_service_class.return_value = mock_service

        # API 호출
        response = client.get("/api/v1/ai/history")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "total_count" in data
        assert isinstance(data["history"], list)

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.AIHistoryService")
    def test_get_history_with_search(
        self,
        mock_service_class,
        mock_get_db,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
    ):
        """AC5: 히스토리 검색 기능."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()
        mock_get_db.return_value = AsyncMock()

        # 히스토리 서비스 Mock
        mock_service = AsyncMock()
        mock_service.get_history.return_value = []
        mock_service_class.return_value = mock_service

        # API 호출
        response = client.get("/api/v1/ai/history?search=매출")

        # 검증
        assert response.status_code == 200
        # 서비스 호출 시 search 파라미터 전달 확인
        mock_service.get_history.assert_called_once()
        call_args = mock_service.get_history.call_args
        assert call_args[1]["search"] == "매출"

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.AIHistoryService")
    def test_get_history_with_limit(
        self,
        mock_service_class,
        mock_get_db,
        mock_log,
        mock_rate_limit,
        mock_permission,
        mock_auth,
        mock_admin,
    ):
        """AC3: 히스토리 limit 파라미터 (최대 20개)."""
        # Mock 설정
        mock_auth.return_value = mock_admin
        mock_permission.return_value = MagicMock(can_query=True)
        mock_rate_limit.return_value = mock_admin
        mock_log.return_value = AsyncMock()
        mock_get_db.return_value = AsyncMock()

        # 히스토리 서비스 Mock
        mock_service = AsyncMock()
        mock_service.get_history.return_value = []
        mock_service_class.return_value = mock_service

        # API 호출
        response = client.get("/api/v1/ai/history?limit=10")

        # 검증
        assert response.status_code == 200
        # 서비스 호출 시 limit 파라미터 전달 확인
        call_args = mock_service.get_history.call_args
        assert call_args[1]["limit"] == 10
