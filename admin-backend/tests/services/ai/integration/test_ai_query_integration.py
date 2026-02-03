"""
AI 질의 통합 테스트 - 인증/RBAC/Rate Limit 통합.

Stories: 2-1
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.main import app

client = TestClient(app)


class TestAIQueryIntegration:
    """AI 질의 API 통합 테스트"""

    @pytest.fixture
    def mock_super_admin(self):
        """슈퍼 관리자 모의 객체"""
        return {
            "id": 1,
            "username": "superadmin",
            "role": "super_admin",
        }

    @pytest.fixture
    def mock_admin(self):
        """일반 관리자 모의 객체"""
        return {
            "id": 2,
            "username": "admin",
            "role": "admin",
        }

    @pytest.fixture
    def mock_viewer(self):
        """뷰어 모의 객체"""
        return {
            "id": 3,
            "username": "viewer",
            "role": "viewer",
        }

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.services.ai.utils.auth_logger.log_ai_access")
    def test_full_integration_super_admin_success(
        self,
        mock_log_ai_access,
        mock_rate_limit,
        mock_check_permission,
        mock_get_admin,
        mock_super_admin,
    ):
        """슈퍼 관리자 - 인증/RBAC/Rate Limit 통과 후 성공"""
        mock_get_admin.return_value = MagicMock(admin_id=1)
        mock_check_permission.return_value = {
            "admin_id": 1,
            "role": "super_admin",
        }
        mock_rate_limit.return_value = None
        mock_log_ai_access.return_value = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/ai/query",
            json={
                "question": "오늘 매출 얼마야?",
                "db_scope": "mariadb",
                "max_rows": 100,
            },
            headers={"Authorization": "Bearer fake-super-admin-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "query_id" in data
        assert len(data["query_id"]) == 36  # UUID 길이
        assert "answer" in data
        assert data["execution_time_ms"] > 0

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    def test_authentication_failure(self, mock_get_admin):
        """인증 실패 - 401 Unauthorized"""
        mock_get_admin.side_effect = Exception("Unauthorized")

        response = client.post(
            "/api/v1/ai/query",
            json={"question": "오늘 매출 얼마야?"},
        )

        assert response.status_code == 401

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    def test_rbac_permission_denied(
        self,
        mock_check_permission,
        mock_get_admin,
        mock_viewer,
    ):
        """RBAC 권한 거부 - 403 Forbidden"""
        mock_get_admin.return_value = MagicMock(admin_id=3)
        mock_check_permission.side_effect = Exception("Permission denied")

        response = client.post(
            "/api/v1/ai/query",
            json={"question": "오늘 매출 얼마야?"},
            headers={"Authorization": "Bearer fake-viewer-token"},
        )

        assert response.status_code == 500  # Exception handling

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.services.ai.utils.auth_logger.log_ai_access")
    def test_validation_failure_after_auth(
        self,
        mock_log_ai_access,
        mock_rate_limit,
        mock_check_permission,
        mock_get_admin,
        mock_admin,
    ):
        """인증 통과 후 유효성 검사 실패 - 400 Bad Request"""
        mock_get_admin.return_value = MagicMock(admin_id=2)
        mock_check_permission.return_value = {
            "admin_id": 2,
            "role": "admin",
        }
        mock_rate_limit.return_value = None
        mock_log_ai_access.return_value = AsyncMock(return_value=None)

        # 숫자만 입력 - 유효성 검사 실패
        response = client.post(
            "/api/v1/ai/query",
            json={"question": "12345"},
            headers={"Authorization": "Bearer fake-admin-token"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error_code"] == "AIBI_INVALID_INPUT"
        assert "유효한 질문" in data["detail"]["message"]

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.services.ai.utils.auth_logger.log_ai_access")
    def test_sql_injection_blocked_after_auth(
        self,
        mock_log_ai_access,
        mock_rate_limit,
        mock_check_permission,
        mock_get_admin,
        mock_super_admin,
    ):
        """인증 통과 후 SQL Injection 차단 - 422 Unprocessable Entity"""
        mock_get_admin.return_value = MagicMock(admin_id=1)
        mock_check_permission.return_value = {
            "admin_id": 1,
            "role": "super_admin",
        }
        mock_rate_limit.return_value = None
        mock_log_ai_access.return_value = AsyncMock(return_value=None)

        # SQL 키워드 포함 - Pydantic 스키마 검증 실패
        response = client.post(
            "/api/v1/ai/query",
            json={"question": "SELECT * FROM users WHERE 1=1"},
            headers={"Authorization": "Bearer fake-super-admin-token"},
        )

        assert response.status_code == 422
        data = response.json()
        assert any("SQL 키워드" in str(e) for e in data.get("detail", []))

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.services.ai.utils.auth_logger.log_ai_access")
    def test_include_sql_flag_respected(
        self,
        mock_log_ai_access,
        mock_rate_limit,
        mock_check_permission,
        mock_get_admin,
        mock_super_admin,
    ):
        """include_sql=True 플래그 동작 확인"""
        mock_get_admin.return_value = MagicMock(admin_id=1)
        mock_check_permission.return_value = {
            "admin_id": 1,
            "role": "super_admin",
        }
        mock_rate_limit.return_value = None
        mock_log_ai_access.return_value = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/ai/query",
            json={
                "question": "오늘 매출 얼마야?",
                "include_sql": True,
            },
            headers={"Authorization": "Bearer fake-super-admin-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["generated_sql"] is not None

    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.services.ai.utils.auth_logger.log_ai_access")
    def test_db_scope_parameter(
        self,
        mock_log_ai_access,
        mock_rate_limit,
        mock_check_permission,
        mock_get_admin,
        mock_super_admin,
    ):
        """db_scope 파라미터 동작 확인"""
        mock_get_admin.return_value = MagicMock(admin_id=1)
        mock_check_permission.return_value = {
            "admin_id": 1,
            "role": "super_admin",
        }
        mock_rate_limit.return_value = None
        mock_log_ai_access.return_value = AsyncMock(return_value=None)

        # MSSQL 스코프 테스트
        response = client.post(
            "/api/v1/ai/query",
            json={
                "question": "상담사별 상담 건수 알려줘",
                "db_scope": "mssql",
            },
            headers={"Authorization": "Bearer fake-super-admin-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
