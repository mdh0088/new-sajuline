"""
접근성 포맷터 단위 테스트.

스크린리더 친화적 텍스트 요약 생성 기능을 검증합니다.

Stories: AI-005 (Story 2-5)
FRs: FR-005, FR-006, NFR-A1, NFR-A3
"""

import pytest
from src.services.ai.utils.accessibility_formatter import AccessibilityFormatter


class TestAccessibilityFormatter:
    """AccessibilityFormatter 단위 테스트"""

    def test_format_for_screen_reader_with_data(self):
        """데이터가 있을 때 스크린리더 친화적 텍스트 생성"""
        # Given
        answer = "오늘 총 매출은 1억 2천만원입니다."
        data = [
            {"date": "2024-01-01", "amount": 120000000},
            {"date": "2024-01-02", "amount": 95000000},
        ]
        columns = ["date", "amount"]

        # When
        result = AccessibilityFormatter.format_for_screen_reader(
            answer=answer, data=data, columns=columns
        )

        # Then
        assert "오늘 총 매출은 1억 2천만원입니다." in result
        assert "총 2개의 결과가 있습니다." in result
        assert "첫 번째 결과" in result
        assert "두 번째 결과" in result

    def test_format_for_screen_reader_empty_data(self):
        """빈 데이터일 때 원래 답변만 반환"""
        # Given
        answer = "조회 결과가 없습니다."
        data = []
        columns = []

        # When
        result = AccessibilityFormatter.format_for_screen_reader(
            answer=answer, data=data, columns=columns
        )

        # Then
        assert result == answer
        assert "결과가 있습니다" not in result

    def test_format_value_for_speech_large_amount(self):
        """큰 금액을 음성 친화적으로 포맷"""
        # Given
        value = 120000000  # 1억 2천만

        # When
        result = AccessibilityFormatter._format_value_for_speech(value)

        # Then
        assert "억" in result
        assert "1억" in result or "1억 2천만" in result

    def test_format_value_for_speech_medium_amount(self):
        """만 단위 금액을 음성 친화적으로 포맷"""
        # Given
        value = 12000  # 1만 2천

        # When
        result = AccessibilityFormatter._format_value_for_speech(value)

        # Then
        assert "만" in result

    def test_format_value_for_speech_small_amount(self):
        """작은 금액을 천 단위 구분으로 포맷"""
        # Given
        value = 1234

        # When
        result = AccessibilityFormatter._format_value_for_speech(value)

        # Then
        assert "1,234" in result

    def test_format_value_for_speech_none(self):
        """None 값을 '값 없음'으로 포맷"""
        # Given
        value = None

        # When
        result = AccessibilityFormatter._format_value_for_speech(value)

        # Then
        assert result == "값 없음"

    def test_format_value_for_speech_string(self):
        """문자열 값을 그대로 반환"""
        # Given
        value = "테스트"

        # When
        result = AccessibilityFormatter._format_value_for_speech(value)

        # Then
        assert result == "테스트"

    def test_format_for_screen_reader_with_ordinal_numbers(self):
        """순서 표시 (첫 번째, 두 번째, ...) 검증"""
        # Given
        answer = "상위 3개 매출 지점입니다."
        data = [
            {"name": "강남점", "sales": 50000000},
            {"name": "홍대점", "sales": 40000000},
            {"name": "신촌점", "sales": 30000000},
        ]
        columns = ["name", "sales"]

        # When
        result = AccessibilityFormatter.format_for_screen_reader(
            answer=answer, data=data, columns=columns
        )

        # Then
        assert "첫 번째" in result
        assert "두 번째" in result
        assert "세 번째" in result

    def test_format_for_screen_reader_with_column_names(self):
        """컬럼 이름을 포함한 설명 검증"""
        # Given
        answer = "사용자 목록입니다."
        data = [
            {"user_id": 1, "name": "홍길동"},
        ]
        columns = ["user_id", "name"]

        # When
        result = AccessibilityFormatter.format_for_screen_reader(
            answer=answer, data=data, columns=columns
        )

        # Then
        # 컬럼 이름이 포함되어야 함
        assert "user_id" in result or "사용자 ID" in result
        assert "name" in result or "이름" in result

    def test_format_for_screen_reader_max_detail_rows(self):
        """대용량 데이터는 처음 5개만 상세 표시"""
        # Given
        answer = "전체 매출 내역입니다."
        data = [{"row": i} for i in range(20)]  # 20개 데이터
        columns = ["row"]

        # When
        result = AccessibilityFormatter.format_for_screen_reader(
            answer=answer, data=data, columns=columns
        )

        # Then
        assert "총 20개의 결과가 있습니다." in result
        # 처음 5개만 상세 표시
        assert "첫 번째" in result
        assert "다섯 번째" in result or "5번째" in result
        # 나머지는 요약만
        assert "나머지" in result or "이하" in result or "등" in result
