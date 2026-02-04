"""
에러 핸들러 유닛 테스트.

Stories: STORY-4-2
FRs: FR20, FR21
"""

import pytest

from src.services.ai.utils.error_handler import AIErrorHandler, UserFriendlyError


class TestUserFriendlyError:
    """UserFriendlyError 데이터클래스 테스트."""

    def test_user_friendly_error_creation(self):
        """UserFriendlyError 생성 테스트."""
        error = UserFriendlyError(
            user_message="질문을 이해하지 못했어요.",
            suggestions=["다시 질문해주세요", "더 구체적으로 질문해주세요"],
            error_code="AIBI_SQL_GEN_FAILED",
            technical_message="SQL generation failed: invalid query",
        )

        assert error.user_message == "질문을 이해하지 못했어요."
        assert len(error.suggestions) == 2
        assert error.error_code == "AIBI_SQL_GEN_FAILED"
        assert error.technical_message == "SQL generation failed: invalid query"

    def test_user_friendly_error_without_technical_message(self):
        """technical_message 없이 UserFriendlyError 생성 테스트."""
        error = UserFriendlyError(
            user_message="오류가 발생했습니다.",
            suggestions=["다시 시도해주세요"],
            error_code="UNKNOWN_ERROR",
        )

        assert error.user_message == "오류가 발생했습니다."
        assert error.technical_message is None


class TestAIErrorHandler:
    """AIErrorHandler 클래스 테스트."""

    def test_error_mappings_exist(self):
        """ERROR_MAPPINGS 상수 존재 여부 테스트."""
        assert hasattr(AIErrorHandler, "ERROR_MAPPINGS")
        assert isinstance(AIErrorHandler.ERROR_MAPPINGS, dict)

    def test_error_mappings_structure(self):
        """ERROR_MAPPINGS 구조 검증 (Story 4-2: message는 error_messages.py에서 관리)."""
        required_codes = [
            "AIBI_SQL_GEN_FAILED",
            "AIBI_TABLE_NOT_ALLOWED",
            "AIBI_LLM_TIMEOUT",
            "AIBI_EMPTY_RESULT",
            "AIBI_TOO_MANY_RESULTS",
        ]

        for code in required_codes:
            assert code in AIErrorHandler.ERROR_MAPPINGS
            mapping = AIErrorHandler.ERROR_MAPPINGS[code]
            # Story 4-2: message는 error_messages.py에서 관리 (Single Source of Truth)
            assert "suggestions_template" in mapping

    def test_handle_sql_gen_failed_error(self):
        """SQL 생성 실패 에러 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="최근 매출 얼마야",
        )

        assert isinstance(result, UserFriendlyError)
        assert result.error_code == "AIBI_SQL_GEN_FAILED"
        assert "질문을 이해하지 못했어요" in result.user_message
        assert len(result.suggestions) > 0
        assert len(result.suggestions) <= 3

    def test_handle_table_not_allowed_error(self):
        """테이블 접근 권한 없음 에러 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_TABLE_NOT_ALLOWED",
            original_question="급여 테이블 조회",
            technical_message="Table 'salary' is not whitelisted",
        )

        assert result.error_code == "AIBI_TABLE_NOT_ALLOWED"
        assert "권한이 없습니다" in result.user_message
        assert result.technical_message == "Table 'salary' is not whitelisted"
        assert len(result.suggestions) > 0

    def test_handle_llm_timeout_error(self):
        """LLM 타임아웃 에러 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_LLM_TIMEOUT",
            original_question="복잡한 질문",
        )

        assert result.error_code == "AIBI_LLM_TIMEOUT"
        assert "지연되고 있어요" in result.user_message or "다시 시도" in result.user_message
        assert len(result.suggestions) > 0

    def test_handle_empty_result_error(self):
        """빈 결과 에러 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_EMPTY_RESULT",
            original_question="오늘 가입자",
        )

        assert result.error_code == "AIBI_EMPTY_RESULT"
        assert "조회 결과가 없습니다" in result.user_message
        assert len(result.suggestions) > 0

    def test_handle_too_many_results_error(self):
        """너무 많은 결과 에러 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_TOO_MANY_RESULTS",
            original_question="전체 사용자",
        )

        assert result.error_code == "AIBI_TOO_MANY_RESULTS"
        assert "결과가 너무 많습니다" in result.user_message
        assert len(result.suggestions) > 0

    def test_handle_unknown_error_code(self):
        """알 수 없는 에러 코드 핸들링 테스트."""
        result = AIErrorHandler.handle_error(
            error_code="UNKNOWN_ERROR_CODE",
            original_question="어떤 질문",
            technical_message="Some technical error",
        )

        assert result.error_code == "UNKNOWN_ERROR_CODE"
        assert "문제가 발생했습니다" in result.user_message
        assert result.technical_message == "Some technical error"
        assert len(result.suggestions) > 0

    def test_suggestions_max_count(self):
        """제안의 최대 개수가 3개 이하인지 테스트."""
        error_codes = [
            "AIBI_SQL_GEN_FAILED",
            "AIBI_TABLE_NOT_ALLOWED",
            "AIBI_LLM_TIMEOUT",
            "AIBI_EMPTY_RESULT",
            "AIBI_TOO_MANY_RESULTS",
        ]

        for code in error_codes:
            result = AIErrorHandler.handle_error(
                error_code=code,
                original_question="테스트 질문",
            )
            assert len(result.suggestions) <= 3, f"{code} has more than 3 suggestions"

    def test_handle_error_with_various_questions(self):
        """다양한 질문에 대한 에러 핸들링 테스트."""
        questions = [
            "최근 매출",
            "사용자 통계",
            "상담 건수",
            "결제 현황",
        ]

        for question in questions:
            result = AIErrorHandler.handle_error(
                error_code="AIBI_SQL_GEN_FAILED",
                original_question=question,
            )

            assert isinstance(result, UserFriendlyError)
            assert result.user_message
            assert len(result.suggestions) > 0

    def test_error_guide_included_in_response(self):
        """에러 가이드가 응답에 포함되는지 테스트 (Story 4-2: AC5)."""
        result = AIErrorHandler.handle_error(
            error_code="AIBI_SQL_GEN_FAILED",
            original_question="테스트 질문",
        )

        assert result.error_guide is not None
        assert "title" in result.error_guide
        assert "description" in result.error_guide
        assert "tips" in result.error_guide
        assert isinstance(result.error_guide["tips"], list)

    def test_all_mapped_errors_have_guide(self):
        """매핑된 모든 에러 코드가 가이드를 가지는지 테스트."""
        error_codes = [
            "AIBI_SQL_GEN_FAILED",
            "AIBI_TABLE_NOT_ALLOWED",
            "AIBI_LLM_TIMEOUT",
            "AIBI_EMPTY_RESULT",
            "AIBI_TOO_MANY_RESULTS",
        ]

        for code in error_codes:
            result = AIErrorHandler.handle_error(
                error_code=code,
                original_question="테스트",
            )
            # 매핑된 에러는 모두 가이드가 있어야 함
            assert result.error_guide is not None, f"{code} has no error_guide"
