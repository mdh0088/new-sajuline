"""
AI 피드백 스키마 테스트.

Stories: 5-1
FRs: FR-024, FR-026
"""
import pytest
from pydantic import ValidationError

from src.schemas.ai.feedback_schema import AIFeedbackRequest, AIFeedbackResponse


class TestAIFeedbackRequest:
    """AIFeedbackRequest 스키마 테스트"""

    def test_valid_feedback_with_comment(self):
        """코멘트가 있는 유효한 피드백 요청 테스트"""
        # Given & When
        request = AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440000",
            rating=4,
            comment="결과는 정확했지만 응답이 조금 느렸어요"
        )

        # Then
        assert request.query_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.rating == 4
        assert request.comment == "결과는 정확했지만 응답이 조금 느렸어요"

    def test_valid_feedback_without_comment(self):
        """코멘트가 없는 유효한 피드백 요청 테스트"""
        # Given & When
        request = AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440001",
            rating=5
        )

        # Then
        assert request.query_id == "550e8400-e29b-41d4-a716-446655440001"
        assert request.rating == 5
        assert request.comment is None

    def test_rating_minimum_value(self):
        """별점 최소값(1) 테스트"""
        # Given & When
        request = AIFeedbackRequest(
            query_id="test-query-id",
            rating=1
        )

        # Then
        assert request.rating == 1

    def test_rating_maximum_value(self):
        """별점 최대값(5) 테스트"""
        # Given & When
        request = AIFeedbackRequest(
            query_id="test-query-id",
            rating=5
        )

        # Then
        assert request.rating == 5

    def test_rating_below_minimum_fails(self):
        """별점 최소값(1) 미만일 때 검증 실패 테스트"""
        # Given & When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(
                query_id="test-query-id",
                rating=0
            )

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "rating" in str(errors[0]["loc"])

    def test_rating_above_maximum_fails(self):
        """별점 최대값(5) 초과일 때 검증 실패 테스트"""
        # Given & When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(
                query_id="test-query-id",
                rating=6
            )

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "rating" in str(errors[0]["loc"])

    def test_comment_max_length(self):
        """코멘트 최대 길이(1000자) 테스트"""
        # Given
        long_comment = "a" * 1000

        # When
        request = AIFeedbackRequest(
            query_id="test-query-id",
            rating=3,
            comment=long_comment
        )

        # Then
        assert len(request.comment) == 1000

    def test_comment_exceeds_max_length_fails(self):
        """코멘트가 최대 길이(1000자)를 초과할 때 검증 실패 테스트"""
        # Given
        too_long_comment = "a" * 1001

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(
                query_id="test-query-id",
                rating=3,
                comment=too_long_comment
            )

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "comment" in str(errors[0]["loc"])

    def test_missing_query_id_fails(self):
        """query_id 필수 필드 누락 시 검증 실패 테스트"""
        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(rating=4)  # type: ignore

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "query_id" in str(errors[0]["loc"])

    def test_missing_rating_fails(self):
        """rating 필수 필드 누락 시 검증 실패 테스트"""
        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(query_id="test-query-id")  # type: ignore

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "rating" in str(errors[0]["loc"])

    def test_example_schema_included(self):
        """스키마 예시가 포함되어 있는지 테스트"""
        # When
        schema = AIFeedbackRequest.model_json_schema()

        # Then
        assert "examples" in schema or "example" in schema.get("properties", {}).get("query_id", {})


class TestAIFeedbackResponse:
    """AIFeedbackResponse 스키마 테스트"""

    def test_success_response(self):
        """성공 응답 테스트"""
        # Given & When
        response = AIFeedbackResponse(
            success=True,
            message="피드백이 제출되었습니다. 감사합니다!"
        )

        # Then
        assert response.success is True
        assert response.message == "피드백이 제출되었습니다. 감사합니다!"

    def test_failure_response(self):
        """실패 응답 테스트"""
        # Given & When
        response = AIFeedbackResponse(
            success=False,
            message="피드백 제출에 실패했습니다."
        )

        # Then
        assert response.success is False
        assert response.message == "피드백 제출에 실패했습니다."

    def test_missing_success_fails(self):
        """success 필수 필드 누락 시 검증 실패 테스트"""
        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackResponse(message="Test")  # type: ignore

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "success" in str(errors[0]["loc"])

    def test_missing_message_fails(self):
        """message 필수 필드 누락 시 검증 실패 테스트"""
        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackResponse(success=True)  # type: ignore

        # Then
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "message" in str(errors[0]["loc"])
