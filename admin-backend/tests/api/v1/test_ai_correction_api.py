"""
AI 답변 수정 API 테스트.

Stories: 5-2
FRs: FR25
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


class TestSubmitCorrectionAPI:
    """PUT /api/v1/ai/feedback/{query_id}/correction 테스트."""

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_submit_correction_success(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """수정 제출 성공 테스트 (AC1, AC2, AC3, AC5)."""
        # Given
        query_id = "query-123"
        request_data = {
            "corrected_answer": "수정된 정확한 답변입니다",
            "correction_reason": "숫자가 잘못되었습니다"
        }

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock correction service
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_correction = Mock()
            mock_correction.id = 1
            mock_correction.is_training_data = True

            mock_service = MockService.return_value
            mock_service.save_correction = AsyncMock(return_value=mock_correction)

            # When
            response = client.put(
                f"/api/v1/ai/feedback/{query_id}/correction",
                json=request_data
            )

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["correction_id"] == 1
            assert "검토 후 반영됩니다" in data["message"]

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_submit_correction_query_not_found(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """존재하지 않는 질의에 대한 수정 제출 실패 테스트 (AC3)."""
        # Given
        query_id = "nonexistent-query"
        request_data = {
            "corrected_answer": "수정된 답변입니다"
        }

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock correction service - query not found
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_service = MockService.return_value
            mock_service.save_correction = AsyncMock(
                side_effect=ValueError(f"Query not found: {query_id}")
            )

            # When
            response = client.put(
                f"/api/v1/ai/feedback/{query_id}/correction",
                json=request_data
            )

            # Then
            assert response.status_code == 404
            assert "Query not found" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_submit_correction_validation_error(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """잘못된 요청 데이터로 인한 검증 실패 테스트 (AC2)."""
        # Given
        query_id = "query-123"
        request_data = {
            "corrected_answer": "짧음"  # 10자 미만
        }

        # When
        response = client.put(
            f"/api/v1/ai/feedback/{query_id}/correction",
            json=request_data
        )

        # Then
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_submit_correction_boundary_10_chars(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """경계값 테스트: 정확히 10자 (AC2)."""
        # Given
        query_id = "550e8400-e29b-41d4-a716-446655440000"
        request_data = {
            "corrected_answer": "열글자답변입니다"  # 정확히 10자
        }

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock correction service
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_correction = Mock()
            mock_correction.id = 1
            mock_correction.is_training_data = True

            mock_service = MockService.return_value
            mock_service.save_correction = AsyncMock(return_value=mock_correction)

            # When
            response = client.put(
                f"/api/v1/ai/feedback/{query_id}/correction",
                json=request_data
            )

            # Then
            assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_submit_correction_invalid_query_id_format(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """UUID 형식 검증 테스트 (보안)."""
        # Given
        query_id = "invalid-query-id"
        request_data = {
            "corrected_answer": "수정된 답변입니다"
        }

        # When
        response = client.put(
            f"/api/v1/ai/feedback/{query_id}/correction",
            json=request_data
        )

        # Then
        assert response.status_code == 422  # Validation error


class TestGetCorrectionHistoryAPI:
    """GET /api/v1/ai/feedback/{query_id}/corrections 테스트."""

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_get_correction_history_success(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """수정 이력 조회 성공 테스트 (AC4)."""
        # Given
        query_id = "query-123"
        now = datetime.now(KST)

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock correction service
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_correction1 = Mock()
            mock_correction1.id = 1
            mock_correction1.admin_id = "admin1"
            mock_correction1.original_answer = "원본1"
            mock_correction1.corrected_answer = "수정1"
            mock_correction1.correction_reason = "사유1"
            mock_correction1.is_training_data = True
            mock_correction1.created_at = now

            mock_corrections = [mock_correction1]

            mock_service = MockService.return_value
            mock_service.get_corrections = AsyncMock(return_value=mock_corrections)

            # When
            response = client.get(f"/api/v1/ai/feedback/{query_id}/corrections")

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["query_id"] == query_id
            assert data["total_count"] == 1
            assert len(data["corrections"]) == 1
            assert data["corrections"][0]["id"] == 1

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_get_correction_history_empty(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """수정 이력이 없는 경우 테스트 (AC4)."""
        # Given
        query_id = "query-no-corrections"

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock correction service - empty result
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_service = MockService.return_value
            mock_service.get_corrections = AsyncMock(return_value=[])

            # When
            response = client.get(f"/api/v1/ai/feedback/{query_id}/corrections")

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["query_id"] == query_id
            assert data["total_count"] == 0
            assert len(data["corrections"]) == 0

    @pytest.mark.asyncio
    @patch("src.api.v1.ai_assistant_api.get_current_admin")
    @patch("src.api.v1.ai_assistant_api.check_ai_permission")
    @patch("src.api.v1.ai_assistant_api.rate_limit_dependency")
    @patch("src.api.v1.ai_assistant_api.get_db")
    @patch("src.api.v1.ai_assistant_api.log_ai_access")
    async def test_get_correction_history_multiple_corrections(
        self,
        mock_log,
        mock_get_db,
        mock_rate_limit,
        mock_permission,
        mock_get_admin,
        client,
    ):
        """동일 질의에 여러 수정 이력 누적 확인 (AC4)."""
        # Given
        query_id = "550e8400-e29b-41d4-a716-446655440000"
        now = datetime.now(KST)

        # Mock admin
        mock_admin = Mock()
        mock_admin.admin_id = "admin1"
        mock_get_admin.return_value = mock_admin

        # Mock permission
        mock_perm = Mock()
        mock_permission.return_value = mock_perm

        # Mock DB session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock log
        mock_log.return_value = None

        # Mock 3개의 수정 이력
        mock_corrections = []
        for i in range(3):
            mock_corr = Mock()
            mock_corr.id = i + 1
            mock_corr.admin_id = f"admin{i+1}"
            mock_corr.original_answer = f"원본{i+1}"
            mock_corr.corrected_answer = f"수정{i+1}"
            mock_corr.correction_reason = f"사유{i+1}"
            mock_corr.is_training_data = True
            mock_corr.created_at = now
            mock_corrections.append(mock_corr)

        # Mock correction service
        with patch("src.services.ai.services.correction_service.AICorrectionService") as MockService:
            mock_service = MockService.return_value
            mock_service.get_corrections = AsyncMock(return_value=mock_corrections)

            # When
            response = client.get(f"/api/v1/ai/feedback/{query_id}/corrections")

            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 3
            assert len(data["corrections"]) == 3
            # 최신순 정렬 확인
            assert data["corrections"][0]["id"] == 1
