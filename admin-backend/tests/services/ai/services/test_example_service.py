"""
예시 질문 서비스 테스트.

Stories: 4-1
"""
import pytest

from src.services.ai.config.example_questions import EXAMPLE_QUESTIONS
from src.services.ai.services.example_service import ExampleQuestionService


class TestExampleQuestionService:
    """ExampleQuestionService 단위 테스트."""

    def test_get_examples_returns_all_categories(self):
        """모든 카테고리의 예시 질문을 반환한다."""
        service = ExampleQuestionService()
        result = service.get_examples()

        assert "categories" in result
        assert len(result["categories"]) > 0

        # AC1: 도메인별 예시 질문 목록 표시
        categories = result["categories"]
        assert any(cat["name"] == "매출" for cat in categories)
        assert any(cat["name"] == "사용자" for cat in categories)
        assert any(cat["name"] == "상담" for cat in categories)

    def test_get_examples_has_minimum_10_questions(self):
        """AC1: 최소 10개 이상의 예시 질문이 있다."""
        service = ExampleQuestionService()
        result = service.get_examples()

        total_questions = sum(
            len(cat["questions"])
            for cat in result["categories"]
        )
        assert total_questions >= 10, f"Expected at least 10 questions, got {total_questions}"

    def test_get_examples_with_category_filter(self):
        """특정 카테고리 필터링이 작동한다."""
        service = ExampleQuestionService()
        result = service.get_examples(category="매출")

        assert "categories" in result
        categories = result["categories"]

        # 필터링된 결과에는 해당 카테고리만 포함
        assert len(categories) == 1
        assert categories[0]["name"] == "매출"
        assert len(categories[0]["questions"]) > 0

    def test_get_examples_with_invalid_category_returns_empty(self):
        """존재하지 않는 카테고리로 필터링 시 빈 결과 반환."""
        service = ExampleQuestionService()
        result = service.get_examples(category="존재하지않는카테고리")

        assert "categories" in result
        assert len(result["categories"]) == 0

    def test_example_questions_structure(self):
        """예시 질문이 올바른 구조를 가진다."""
        service = ExampleQuestionService()
        result = service.get_examples()

        for category in result["categories"]:
            assert "name" in category
            assert "questions" in category

            for question in category["questions"]:
                # AC1: 질문과 설명 포함
                assert "question" in question
                assert "description" in question
                assert isinstance(question["question"], str)
                assert isinstance(question["description"], str)
                assert len(question["question"]) > 0
                assert len(question["description"]) > 0

    def test_example_questions_constant_has_required_categories(self):
        """EXAMPLE_QUESTIONS 상수가 필수 카테고리를 포함한다."""
        # AC1: 매출, 사용자, 상담사 카테고리
        assert "매출" in EXAMPLE_QUESTIONS
        assert "사용자" in EXAMPLE_QUESTIONS
        assert "상담" in EXAMPLE_QUESTIONS

    def test_example_questions_constant_structure(self):
        """EXAMPLE_QUESTIONS가 올바른 데이터 구조를 가진다."""
        for category, questions in EXAMPLE_QUESTIONS.items():
            assert isinstance(questions, list)
            assert len(questions) > 0

            for q in questions:
                assert isinstance(q, dict)
                assert "question" in q
                assert "description" in q
