"""
대안 제안 생성기 유닛 테스트.

Stories: STORY-4-2
FRs: FR21
"""

import pytest

from src.services.ai.utils.suggestion_generator import SuggestionGenerator


class TestSuggestionGenerator:
    """SuggestionGenerator 클래스 테스트."""

    def test_suggestion_templates_exist(self):
        """SUGGESTION_TEMPLATES 상수 존재 여부 테스트."""
        assert hasattr(SuggestionGenerator, "SUGGESTION_TEMPLATES")
        assert isinstance(SuggestionGenerator.SUGGESTION_TEMPLATES, dict)

    def test_suggestion_templates_structure(self):
        """SUGGESTION_TEMPLATES 구조 검증."""
        required_templates = [
            "rephrase",
            "broaden_scope",
            "narrow_scope",
            "alternative_data",
        ]

        for template in required_templates:
            assert template in SuggestionGenerator.SUGGESTION_TEMPLATES
            suggestions = SuggestionGenerator.SUGGESTION_TEMPLATES[template]
            assert isinstance(suggestions, list)
            assert len(suggestions) > 0

    def test_generate_rephrase_suggestions(self):
        """rephrase 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="rephrase",
            original_question="최근 매출",
        )

        assert isinstance(result, list)
        assert len(result) <= 3
        assert len(result) > 0

    def test_generate_broaden_scope_suggestions(self):
        """broaden_scope 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="broaden_scope",
            original_question="오늘 가입자",
        )

        assert isinstance(result, list)
        assert len(result) <= 3
        assert len(result) > 0

    def test_generate_narrow_scope_suggestions(self):
        """narrow_scope 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="narrow_scope",
            original_question="전체 사용자",
        )

        assert isinstance(result, list)
        assert len(result) <= 3
        assert len(result) > 0

    def test_generate_alternative_data_suggestions(self):
        """alternative_data 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="alternative_data",
            original_question="급여 정보",
        )

        assert isinstance(result, list)
        assert len(result) <= 3
        assert len(result) > 0

    def test_generate_general_suggestions(self):
        """general 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="general",
            original_question="어떤 질문",
        )

        assert isinstance(result, list)
        assert len(result) <= 3
        assert len(result) > 0

    def test_generate_retry_suggestions(self):
        """retry 템플릿 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="retry",
            original_question="복잡한 질문",
        )

        assert isinstance(result, list)
        assert len(result) <= 3

    def test_generate_max_suggestions_limit(self):
        """최대 제안 개수 제한 테스트."""
        result = SuggestionGenerator.generate(
            template="rephrase",
            original_question="테스트",
            max_suggestions=2,
        )

        assert len(result) <= 2

    def test_extract_keyword_with_known_keyword(self):
        """알려진 키워드 추출 테스트."""
        keywords = ["매출", "결제", "사용자", "상담", "가입"]

        for keyword in keywords:
            question = f"최근 {keyword} 정보"
            extracted = SuggestionGenerator._extract_keyword(question)
            assert keyword in extracted or extracted == keyword

    def test_extract_keyword_with_unknown_keyword(self):
        """알 수 없는 키워드 추출 테스트 (기본값 반환)."""
        question = "알 수 없는 정보"
        extracted = SuggestionGenerator._extract_keyword(question)
        assert extracted == "데이터"

    def test_generate_with_various_questions(self):
        """다양한 질문에 대한 제안 생성 테스트."""
        questions = [
            "최근 매출 얼마야",
            "사용자 통계 보여줘",
            "상담 건수 알려줘",
            "결제 현황은 어때",
        ]

        for question in questions:
            result = SuggestionGenerator.generate(
                template="rephrase",
                original_question=question,
            )

            assert isinstance(result, list)
            assert len(result) > 0
            assert len(result) <= 3

    def test_suggestion_contains_keyword(self):
        """제안에 키워드가 포함되는지 테스트."""
        question = "최근 매출 정보"
        result = SuggestionGenerator.generate(
            template="rephrase",
            original_question=question,
        )

        # 적어도 하나의 제안에는 키워드가 포함되어야 함
        has_keyword = any("매출" in suggestion for suggestion in result)
        assert has_keyword or any("데이터" in suggestion for suggestion in result)

    def test_generate_with_empty_question(self):
        """빈 질문에 대한 제안 생성 테스트."""
        result = SuggestionGenerator.generate(
            template="general",
            original_question="",
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_with_very_long_question(self):
        """매우 긴 질문에 대한 제안 생성 테스트."""
        long_question = "매출" + " 데이터" * 500  # ~3000자
        result = SuggestionGenerator.generate(
            template="rephrase",
            original_question=long_question,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) <= 3

    def test_generate_with_special_characters(self):
        """특수문자만 있는 질문 테스트."""
        result = SuggestionGenerator.generate(
            template="general",
            original_question="!@#$%^&*()",
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_with_unicode_emoji(self):
        """유니코드/이모지 질문 테스트."""
        result = SuggestionGenerator.generate(
            template="rephrase",
            original_question="최근 매출 😀📊",
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_extract_keyword_priority_order(self):
        """키워드 우선순위 테스트 (여러 키워드 포함 시 첫 번째 반환)."""
        question = "매출과 결제와 사용자"  # 3개 키워드 포함
        extracted = SuggestionGenerator._extract_keyword(question)
        # 리스트 순서대로 매출이 먼저 매칭되어야 함
        assert extracted == "매출"
