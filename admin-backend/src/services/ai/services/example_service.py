"""
예시 질문 서비스.

Stories: 4-1
FRs: FR18
"""
from typing import TypedDict

from src.services.ai.config.example_questions import EXAMPLE_QUESTIONS


class CategoryOutput(TypedDict):
    """카테고리 출력 타입."""
    name: str
    questions: list[dict[str, str]]


class ExampleQuestionsOutput(TypedDict):
    """예시 질문 출력 타입."""
    categories: list[CategoryOutput]


class ExampleQuestionService:
    """예시 질문 서비스.

    AC1: 도메인별 예시 질문 목록 제공
    AC2: 예시 질문 클릭 시 입력 필드 자동 입력 (프론트엔드에서 처리)
    """

    def get_examples(self, category: str | None = None) -> ExampleQuestionsOutput:
        """예시 질문 목록 조회.

        Args:
            category: 카테고리 필터 (None이면 전체)

        Returns:
            ExampleQuestionsOutput: 카테고리별 예시 질문 목록
        """
        # 카테고리 필터링
        if category:
            # 특정 카테고리만 반환
            if category in EXAMPLE_QUESTIONS:
                categories = [
                    CategoryOutput(
                        name=category,
                        questions=EXAMPLE_QUESTIONS[category]
                    )
                ]
            else:
                # 존재하지 않는 카테고리
                categories = []
        else:
            # 전체 카테고리 반환
            categories = [
                CategoryOutput(name=name, questions=questions)
                for name, questions in EXAMPLE_QUESTIONS.items()
            ]

        return ExampleQuestionsOutput(categories=categories)
