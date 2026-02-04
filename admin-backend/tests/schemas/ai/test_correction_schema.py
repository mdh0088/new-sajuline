"""
답변 수정 스키마 테스트.

Stories: 5-2
FRs: FR25
"""
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import ValidationError

from src.schemas.ai.correction_schema import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionItem,
    CorrectionHistoryResponse,
)

KST = ZoneInfo("Asia/Seoul")


class TestCorrectionRequest:
    """CorrectionRequest 스키마 테스트."""

    def test_valid_correction_request(self):
        """유효한 수정 요청 테스트."""
        # Given
        data = {
            "corrected_answer": "수정된 정확한 답변입니다",
            "correction_reason": "숫자가 잘못되었습니다"
        }

        # When
        request = CorrectionRequest(**data)

        # Then
        assert request.corrected_answer == "수정된 정확한 답변입니다"
        assert request.correction_reason == "숫자가 잘못되었습니다"

    def test_correction_request_without_reason(self):
        """수정 사유 없이 요청 테스트."""
        # Given
        data = {
            "corrected_answer": "수정된 정확한 답변"  # 10자 이상
        }

        # When
        request = CorrectionRequest(**data)

        # Then
        assert request.corrected_answer == "수정된 정확한 답변"
        assert request.correction_reason is None

    def test_correction_request_min_length_validation(self):
        """최소 길이 검증 테스트."""
        # Given
        data = {
            "corrected_answer": "짧음"  # 10자 미만
        }

        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            CorrectionRequest(**data)

        assert "at least 10 characters" in str(exc_info.value)

    def test_correction_request_max_length_validation(self):
        """최대 길이 검증 테스트."""
        # Given
        data = {
            "corrected_answer": "a" * 5001  # 5000자 초과
        }

        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            CorrectionRequest(**data)

        assert "at most 5000 characters" in str(exc_info.value)

    def test_correction_reason_max_length(self):
        """수정 사유 최대 길이 검증 테스트."""
        # Given
        data = {
            "corrected_answer": "정확한 답변입니다",
            "correction_reason": "a" * 501  # 500자 초과
        }

        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            CorrectionRequest(**data)

        assert "at most 500 characters" in str(exc_info.value)


class TestCorrectionResponse:
    """CorrectionResponse 스키마 테스트."""

    def test_valid_correction_response(self):
        """유효한 수정 응답 테스트."""
        # Given
        data = {
            "success": True,
            "correction_id": 123,
            "message": "답변 수정이 제출되었습니다"
        }

        # When
        response = CorrectionResponse(**data)

        # Then
        assert response.success is True
        assert response.correction_id == 123
        assert response.message == "답변 수정이 제출되었습니다"


class TestCorrectionItem:
    """CorrectionItem 스키마 테스트."""

    def test_valid_correction_item(self):
        """유효한 수정 항목 테스트."""
        # Given
        now = datetime.now(KST)
        data = {
            "id": 1,
            "admin_id": "admin1",
            "original_answer": "원본 답변",
            "corrected_answer": "수정된 답변",
            "correction_reason": "수정 사유",
            "is_training_data": True,
            "created_at": now
        }

        # When
        item = CorrectionItem(**data)

        # Then
        assert item.id == 1
        assert item.admin_id == "admin1"
        assert item.original_answer == "원본 답변"
        assert item.corrected_answer == "수정된 답변"
        assert item.correction_reason == "수정 사유"
        assert item.is_training_data is True
        assert item.created_at == now

    def test_correction_item_without_reason(self):
        """수정 사유 없는 항목 테스트."""
        # Given
        now = datetime.now(KST)
        data = {
            "id": 1,
            "admin_id": "admin1",
            "original_answer": "원본",
            "corrected_answer": "수정",
            "is_training_data": False,
            "created_at": now
        }

        # When
        item = CorrectionItem(**data)

        # Then
        assert item.correction_reason is None
        assert item.is_training_data is False


class TestCorrectionHistoryResponse:
    """CorrectionHistoryResponse 스키마 테스트."""

    def test_valid_history_response(self):
        """유효한 이력 응답 테스트."""
        # Given
        now = datetime.now(KST)
        corrections = [
            {
                "id": 1,
                "admin_id": "admin1",
                "original_answer": "원본1",
                "corrected_answer": "수정1",
                "is_training_data": True,
                "created_at": now
            },
            {
                "id": 2,
                "admin_id": "admin2",
                "original_answer": "원본2",
                "corrected_answer": "수정2",
                "is_training_data": True,
                "created_at": now
            }
        ]
        data = {
            "query_id": "query-123",
            "corrections": corrections,
            "total_count": 2
        }

        # When
        response = CorrectionHistoryResponse(**data)

        # Then
        assert response.query_id == "query-123"
        assert len(response.corrections) == 2
        assert response.total_count == 2
        assert response.corrections[0].id == 1
        assert response.corrections[1].id == 2

    def test_empty_history_response(self):
        """빈 이력 응답 테스트."""
        # Given
        data = {
            "query_id": "query-456",
            "corrections": [],
            "total_count": 0
        }

        # When
        response = CorrectionHistoryResponse(**data)

        # Then
        assert response.query_id == "query-456"
        assert len(response.corrections) == 0
        assert response.total_count == 0
