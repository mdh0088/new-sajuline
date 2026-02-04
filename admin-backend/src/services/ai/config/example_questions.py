"""
예시 질문 설정.

도메인별 예시 질문 목록을 정의합니다.

Stories: 4-1
FRs: FR18
"""
from typing import TypedDict


class ExampleQuestion(TypedDict):
    """예시 질문 타입."""
    question: str
    description: str


# AC1: 도메인별 예시 질문 목록 (최소 10개) - Issue #4: 12개로 확장
EXAMPLE_QUESTIONS: dict[str, list[ExampleQuestion]] = {
    "매출": [
        {"question": "오늘 매출 얼마야?", "description": "당일 총 매출 조회"},
        {"question": "이번 주 결제 건수", "description": "주간 결제 현황"},
        {"question": "이번 달 매출 추이", "description": "월간 일별 매출"},
        {"question": "상담사별 매출 순위", "description": "상담사 실적 비교"},
        {"question": "결제 실패 건수", "description": "실패 원인별 집계"},
    ],
    "사용자": [
        {"question": "오늘 신규 가입자 수", "description": "당일 가입 현황"},
        {"question": "이번 달 활성 사용자", "description": "MAU 조회"},
        {"question": "최근 7일 가입 추이", "description": "일별 가입자 트렌드"},
        {"question": "탈퇴 사용자 수", "description": "탈퇴 현황 조회"},
    ],
    "상담": [
        {"question": "오늘 상담 건수", "description": "당일 상담 현황"},
        {"question": "상담사별 평균 상담 시간", "description": "효율성 분석"},
        {"question": "미완료 상담 목록", "description": "처리 필요 건"},
    ],
}


def get_total_question_count() -> int:
    """전체 예시 질문 개수 반환."""
    return sum(len(questions) for questions in EXAMPLE_QUESTIONS.values())
