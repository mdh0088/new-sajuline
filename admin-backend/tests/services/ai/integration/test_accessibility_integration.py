"""
접근성 모드 통합 테스트.

Stories: AI-005 (Story 2-5)
FRs: FR-005, FR-006, NFR-A1, NFR-A3
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.schemas.ai.query_schema import AccessibilityHints


class TestAccessibilityIntegration:
    """접근성 모드 통합 테스트"""

    @pytest.fixture
    def mock_admin_auth(self):
        """관리자 인증 Mock"""
        with patch(
            "src.api.v1.ai_assistant_api.get_current_admin"
        ) as mock_get_admin:
            mock_admin = MagicMock()
            mock_admin.admin_id = 1
            mock_admin.username = "test_admin"
            mock_get_admin.return_value = mock_admin
            yield mock_get_admin

    @pytest.fixture
    def mock_permission_check(self):
        """권한 체크 Mock"""
        with patch(
            "src.api.v1.ai_assistant_api.check_ai_permission"
        ) as mock_permission:
            mock_permission.return_value = {
                "admin_id": 1,
                "role": "super_admin",
                "allowed_tables": {"users", "payments"},
            }
            yield mock_permission

    @pytest.fixture
    def mock_rate_limiter(self):
        """Rate Limiter Mock"""
        with patch(
            "src.api.v1.ai_assistant_api.rate_limit_dependency"
        ) as mock_limiter:
            mock_limiter.return_value = None
            yield mock_limiter

    def test_include_sql_parameter(
        self, mock_admin_auth, mock_permission_check, mock_rate_limiter
    ):
        """include_sql=true 파라미터 테스트"""
        # Given
        client = TestClient(app)

        with patch(
            "src.api.v1.ai_assistant_api.SQLGenerationAgent"
        ) as mock_sql_agent, patch(
            "src.api.v1.ai_assistant_api.MariaDBAgent"
        ) as mock_mariadb_agent, patch(
            "src.api.v1.ai_assistant_api.ResponseGenerationAgent"
        ) as mock_response_agent, patch(
            "src.api.v1.ai_assistant_api.get_aiomysql_pool"
        ) as mock_pool, patch(
            "src.api.v1.ai_assistant_api.SchemaLoader"
        ) as mock_schema, patch(
            "src.api.v1.ai_assistant_api.get_role_allowed_tables"
        ) as mock_allowed_tables, patch(
            "src.api.v1.ai_assistant_api.log_ai_access"
        ) as mock_log:

            # Mock 설정
            mock_sql_agent_instance = AsyncMock()
            mock_sql_agent_instance.generate_sql.return_value = MagicMock(
                success=True, sql="SELECT * FROM users LIMIT 10"
            )
            mock_sql_agent.return_value = mock_sql_agent_instance

            mock_mariadb_agent_instance = AsyncMock()
            mock_mariadb_agent_instance.execute_query.return_value = MagicMock(
                success=True,
                data=[{"user_id": 1, "name": "홍길동"}],
                columns=["user_id", "name"],
                row_count=1,
            )
            mock_mariadb_agent.return_value = mock_mariadb_agent_instance

            mock_response_agent_instance = AsyncMock()
            mock_response_agent_instance.generate_response.return_value = (
                MagicMock(
                    success=True, natural_language_response="사용자 1명을 찾았습니다."
                )
            )
            mock_response_agent.return_value = mock_response_agent_instance

            mock_allowed_tables.return_value = {"users"}
            mock_log.return_value = AsyncMock()

            # When: include_sql=true
            response = client.post(
                "/api/v1/ai/query",
                json={"question": "사용자 목록을 보여주세요", "include_sql": True},
            )

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["generated_sql"] is not None
            assert "SELECT" in data["generated_sql"]

    def test_accessibility_mode_text_summary_only(
        self, mock_admin_auth, mock_permission_check, mock_rate_limiter
    ):
        """accessibility_mode=true 시 텍스트 요약만 제공"""
        # Given
        client = TestClient(app)

        with patch(
            "src.api.v1.ai_assistant_api.SQLGenerationAgent"
        ) as mock_sql_agent, patch(
            "src.api.v1.ai_assistant_api.MariaDBAgent"
        ) as mock_mariadb_agent, patch(
            "src.api.v1.ai_assistant_api.ResponseGenerationAgent"
        ) as mock_response_agent, patch(
            "src.api.v1.ai_assistant_api.get_aiomysql_pool"
        ) as mock_pool, patch(
            "src.api.v1.ai_assistant_api.SchemaLoader"
        ) as mock_schema, patch(
            "src.api.v1.ai_assistant_api.get_role_allowed_tables"
        ) as mock_allowed_tables, patch(
            "src.api.v1.ai_assistant_api.log_ai_access"
        ) as mock_log:

            # Mock 설정
            mock_sql_agent_instance = AsyncMock()
            mock_sql_agent_instance.generate_sql.return_value = MagicMock(
                success=True, sql="SELECT COUNT(*) FROM users"
            )
            mock_sql_agent.return_value = mock_sql_agent_instance

            mock_mariadb_agent_instance = AsyncMock()
            mock_mariadb_agent_instance.execute_query.return_value = MagicMock(
                success=True,
                data=[{"count": 100}],
                columns=["count"],
                row_count=1,
            )
            mock_mariadb_agent.return_value = mock_mariadb_agent_instance

            mock_response_agent_instance = AsyncMock()
            mock_response_agent_instance.generate_response.return_value = (
                MagicMock(success=True, natural_language_response="총 100명입니다.")
            )
            mock_response_agent.return_value = mock_response_agent_instance

            mock_allowed_tables.return_value = {"users"}
            mock_log.return_value = AsyncMock()

            # When: accessibility_mode=true
            response = client.post(
                "/api/v1/ai/query",
                json={
                    "question": "사용자 수를 알려주세요",
                    "accessibility_mode": True,
                },
            )

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["answer_summary"] is not None
            assert "총 1개의 결과가 있습니다" in data["answer_summary"]
            assert data["data"] == []  # 빈 배열 반환 (AC 4 준수)
            assert data["accessibility_hints"] is not None
            assert data["accessibility_hints"]["row_count"] == 1

    def test_accessibility_hints_structure(
        self, mock_admin_auth, mock_permission_check, mock_rate_limiter
    ):
        """접근성 힌트 구조 검증"""
        # Given
        client = TestClient(app)

        with patch(
            "src.api.v1.ai_assistant_api.SQLGenerationAgent"
        ) as mock_sql_agent, patch(
            "src.api.v1.ai_assistant_api.MariaDBAgent"
        ) as mock_mariadb_agent, patch(
            "src.api.v1.ai_assistant_api.ResponseGenerationAgent"
        ) as mock_response_agent, patch(
            "src.api.v1.ai_assistant_api.get_aiomysql_pool"
        ) as mock_pool, patch(
            "src.api.v1.ai_assistant_api.SchemaLoader"
        ) as mock_schema, patch(
            "src.api.v1.ai_assistant_api.get_role_allowed_tables"
        ) as mock_allowed_tables, patch(
            "src.api.v1.ai_assistant_api.log_ai_access"
        ) as mock_log:

            # Mock 설정 (간소화)
            mock_sql_agent_instance = AsyncMock()
            mock_sql_agent_instance.generate_sql.return_value = MagicMock(
                success=True, sql="SELECT * FROM users"
            )
            mock_sql_agent.return_value = mock_sql_agent_instance

            mock_mariadb_agent_instance = AsyncMock()
            mock_mariadb_agent_instance.execute_query.return_value = MagicMock(
                success=True,
                data=[{"id": 1}],
                columns=["id"],
                row_count=1,
            )
            mock_mariadb_agent.return_value = mock_mariadb_agent_instance

            mock_response_agent_instance = AsyncMock()
            mock_response_agent_instance.generate_response.return_value = (
                MagicMock(success=True, natural_language_response="결과")
            )
            mock_response_agent.return_value = mock_response_agent_instance

            mock_allowed_tables.return_value = {"users"}
            mock_log.return_value = AsyncMock()

            # When
            response = client.post(
                "/api/v1/ai/query",
                json={"question": "테스트", "accessibility_mode": True},
            )

            # Then
            assert response.status_code == 200
            data = response.json()
            hints = data["accessibility_hints"]
            assert "aria_label" in hints
            assert "aria_live" in hints
            assert hints["aria_live"] == "polite"
            assert "row_count" in hints
            assert "column_count" in hints

    def test_normal_mode_no_accessibility_hints(
        self, mock_admin_auth, mock_permission_check, mock_rate_limiter
    ):
        """일반 모드에서는 접근성 힌트가 없음"""
        # Given
        client = TestClient(app)

        with patch(
            "src.api.v1.ai_assistant_api.SQLGenerationAgent"
        ) as mock_sql_agent, patch(
            "src.api.v1.ai_assistant_api.MariaDBAgent"
        ) as mock_mariadb_agent, patch(
            "src.api.v1.ai_assistant_api.ResponseGenerationAgent"
        ) as mock_response_agent, patch(
            "src.api.v1.ai_assistant_api.get_aiomysql_pool"
        ) as mock_pool, patch(
            "src.api.v1.ai_assistant_api.SchemaLoader"
        ) as mock_schema, patch(
            "src.api.v1.ai_assistant_api.get_role_allowed_tables"
        ) as mock_allowed_tables, patch(
            "src.api.v1.ai_assistant_api.log_ai_access"
        ) as mock_log:

            # Mock 설정
            mock_sql_agent_instance = AsyncMock()
            mock_sql_agent_instance.generate_sql.return_value = MagicMock(
                success=True, sql="SELECT 1"
            )
            mock_sql_agent.return_value = mock_sql_agent_instance

            mock_mariadb_agent_instance = AsyncMock()
            mock_mariadb_agent_instance.execute_query.return_value = MagicMock(
                success=True,
                data=[{"col": 1}],
                columns=["col"],
                row_count=1,
            )
            mock_mariadb_agent.return_value = mock_mariadb_agent_instance

            mock_response_agent_instance = AsyncMock()
            mock_response_agent_instance.generate_response.return_value = (
                MagicMock(success=True, natural_language_response="결과")
            )
            mock_response_agent.return_value = mock_response_agent_instance

            mock_allowed_tables.return_value = {"users"}
            mock_log.return_value = AsyncMock()

            # When: accessibility_mode=false (기본값)
            response = client.post(
                "/api/v1/ai/query",
                json={"question": "테스트", "accessibility_mode": False},
            )

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["answer_summary"] is None
            assert data["accessibility_hints"] is None
            assert data["data"] is not None  # 테이블 데이터 제공
