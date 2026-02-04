"""
대안 질문 생성기.

에러 상황에 맞는 대안 질문을 템플릿 기반으로 생성합니다.

Stories: STORY-4-2
FRs: FR21
"""

import logging

logger = logging.getLogger(__name__)


class SuggestionGenerator:
    """대안 질문 생성기."""

    SUGGESTION_TEMPLATES = {
        "rephrase": [
            "더 구체적으로: '{question}' → '이번 달 {keyword}'",
            "다른 표현: '총 {keyword}', '{keyword} 합계'",
            "기간 추가: '오늘 {keyword}', '이번 주 {keyword}'",
        ],
        "broaden_scope": [
            "기간을 넓혀보세요: '이번 달' → '최근 3개월'",
            "조건을 줄여보세요: 전체 데이터 조회",
            "다른 기준: '전체 {keyword}'",
        ],
        "narrow_scope": [
            "기간을 좁혀주세요: '이번 달만'",
            "특정 대상: '{keyword} 중 특정 항목만'",
            "요약으로 보기: '월별 요약'",
        ],
        "alternative_data": [
            "조회 가능: '매출 현황'",
            "조회 가능: '상담 건수'",
            "조회 가능: '사용자 통계'",
        ],
        "retry": [
            "잠시 후 다시 시도해주세요",
            "더 간단한 질문으로 시도해보세요",
        ],
        "general": [
            "다시 질문해주세요",
            "더 구체적으로 질문해주세요",
            "다른 표현으로 질문해주세요",
        ],
    }

    @classmethod
    def generate(
        cls,
        template: str,
        original_question: str,
        max_suggestions: int = 3,
    ) -> list[str]:
        """
        대안 제안 생성.

        Args:
            template: 템플릿 이름 (예: rephrase, broaden_scope)
            original_question: 사용자의 원래 질문
            max_suggestions: 최대 제안 개수 (기본값: 3)

        Returns:
            list[str]: 대안 질문 목록 (최대 max_suggestions개)
        """
        templates = cls.SUGGESTION_TEMPLATES.get(template, cls.SUGGESTION_TEMPLATES["general"])

        keyword = cls._extract_keyword(original_question)

        suggestions = []
        for tmpl in templates[:max_suggestions]:
            try:
                suggestion = tmpl.format(question=original_question, keyword=keyword)
                suggestions.append(suggestion)
            except KeyError as e:
                logger.warning(
                    f"Template format error: {e}, template: {tmpl}",
                    extra={"template": template, "question": original_question},
                )
                # 폴백: 간단한 대안 제안
                suggestions.append("다시 질문해주세요")

        return suggestions

    @staticmethod
    def _extract_keyword(question: str) -> str:
        """
        질문에서 핵심 키워드 추출.

        도메인별 키워드를 우선순위대로 검색하여 첫 번째 매칭되는 키워드를 반환합니다.
        매칭되는 키워드가 없으면 기본값 "데이터"를 반환합니다.

        Args:
            question: 사용자 질문

        Returns:
            str: 추출된 키워드 (기본값: "데이터")
        """
        # 도메인별 핵심 키워드 (우선순위 순)
        keywords = [
            "매출",
            "결제",
            "포인트",
            "환불",
            "사용자",
            "회원",
            "가입",
            "탈퇴",
            "상담",
            "상담사",
            "예약",
            "리뷰",
            "평가",
        ]
        for kw in keywords:
            if kw in question:
                return kw
        return "데이터"
