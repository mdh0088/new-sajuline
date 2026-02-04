"""
에러 핸들러 API 통합 테스트.

Stories: STORY-4-2
FRs: FR20, FR21
"""

import pytest

from src.schemas.ai.error_schema import AIErrorResponse
from src.services.ai.utils.error_handler import AIErrorHandler


class TestErrorHandlerAPIIntegration:
    """API와 에러 핸들러 통합 테스트."""

    def test_error_handler_integration_with_response_model(self):
        """에러 핸들러와 응답 모델 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="최근 매출",
        )

        # AIErrorResponse 모델로 변환
        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert response.error_code == "AIBI_SQL_GEN_FAILED"
        assert isinstance(response.message, str)
        assert len(response.message) > 0
        assert isinstance(response.suggestions, list)
        assert len(response.suggestions) > 0
        assert len(response.suggestions) <= 3

    def test_sql_gen_failed_integration(self):
        """SQL 생성 실패 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="최근 매출 얼마야",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "질문을 이해하지 못했어요" in response.message
        assert len(response.suggestions) > 0

    def test_llm_timeout_integration(self):
        """LLM 타임아웃 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_LLM_TIMEOUT",
            original_question="복잡한 분석 질문",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "지연되고 있어요" in response.message or "다시 시도" in response.message
        assert len(response.suggestions) > 0

    def test_table_not_allowed_integration(self):
        """테이블 접근 권한 없음 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_TABLE_NOT_ALLOWED",
            original_question="급여 테이블 조회",
            technical_message="Table 'salary' is not whitelisted",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "권한이 없습니다" in response.message
        assert len(response.suggestions) > 0
        assert friendly_error.technical_message == "Table 'salary' is not whitelisted"

    def test_empty_result_integration(self):
        """빈 결과 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_EMPTY_RESULT",
            original_question="오늘 가입자",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "조회 결과가 없습니다" in response.message
        assert len(response.suggestions) > 0

    def test_too_many_results_integration(self):
        """너무 많은 결과 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_TOO_MANY_RESULTS",
            original_question="전체 사용자",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "결과가 너무 많습니다" in response.message
        assert len(response.suggestions) > 0

    def test_error_guide_integration(self):
        """에러 가이드 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="테스트 질문",
        )

        assert friendly_error.error_guide is not None
        assert "title" in friendly_error.error_guide
        assert "description" in friendly_error.error_guide
        assert "tips" in friendly_error.error_guide

    def test_unknown_error_code_integration(self):
        """알 수 없는 에러 코드 통합 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="UNKNOWN_ERROR",
            original_question="테스트 질문",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
        )

        assert "문제가 발생했습니다" in response.message
        assert len(response.suggestions) > 0

    def test_error_response_serialization(self):
        """에러 응답 직렬화 테스트."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="테스트",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
            error_guide=friendly_error.error_guide,
        )

        # 딕셔너리로 변환 가능한지 확인
        response_dict = response.model_dump()

        assert "error_code" in response_dict
        assert "message" in response_dict
        assert "suggestions" in response_dict
        assert "error_guide" in response_dict

    def test_error_guide_in_api_response(self):
        """API 응답에 error_guide가 포함되는지 테스트 (Story 4-2: AC5)."""
        friendly_error = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="매출 조회",
        )

        response = AIErrorResponse(
            error_code=friendly_error.error_code,
            message=friendly_error.user_message,
            suggestions=friendly_error.suggestions,
            error_guide=friendly_error.error_guide,
        )

        assert response.error_guide is not None
        assert "title" in response.error_guide
        assert response.error_guide["title"] == "질문 이해 오류"
