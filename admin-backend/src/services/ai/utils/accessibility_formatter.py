"""
접근성 모드 응답 포맷터.

스크린리더 친화적 텍스트 요약 생성 기능을 제공합니다.

Stories: AI-005 (Story 2-5)
FRs: FR-005, FR-006, NFR-A1, NFR-A3
"""

from typing import Any, List, Dict


class AccessibilityFormatter:
    """접근성 모드 응답 포맷터"""

    # 상세 표시할 최대 행 수 (대용량 데이터 대응)
    MAX_DETAIL_ROWS = 5

    # 순서 표현 (한국어)
    ORDINAL_NUMBERS = [
        "첫 번째",
        "두 번째",
        "세 번째",
        "네 번째",
        "다섯 번째",
        "여섯 번째",
        "일곱 번째",
        "여덟 번째",
        "아홉 번째",
        "열 번째",
    ]

    @staticmethod
    def format_for_screen_reader(
        answer: str,
        data: List[Dict[str, Any]],
        columns: List[str],
    ) -> str:
        """
        스크린리더 친화적 텍스트 요약 생성.

        Args:
            answer: LLM이 생성한 자연어 답변
            data: 쿼리 결과 데이터 (행 리스트)
            columns: 컬럼 이름 리스트

        Returns:
            스크린리더 친화적 텍스트 요약

        Examples:
            >>> data = [{"name": "홍길동", "amount": 10000}]
            >>> result = AccessibilityFormatter.format_for_screen_reader(
            ...     answer="매출 집계입니다.",
            ...     data=data,
            ...     columns=["name", "amount"]
            ... )
            >>> "첫 번째 결과" in result
            True
        """
        if not data:
            return answer

        parts = [answer, ""]

        # 전체 결과 수
        row_count = len(data)
        parts.append(f"총 {row_count}개의 결과가 있습니다.")
        parts.append("")

        # 상세 표시할 행 수 결정
        detail_count = min(row_count, AccessibilityFormatter.MAX_DETAIL_ROWS)

        # 각 행을 상세히 설명
        for idx, row in enumerate(data[:detail_count]):
            # 순서 표현
            if idx < len(AccessibilityFormatter.ORDINAL_NUMBERS):
                ordinal = AccessibilityFormatter.ORDINAL_NUMBERS[idx]
            else:
                ordinal = f"{idx + 1}번째"

            parts.append(f"{ordinal} 결과:")

            # 각 컬럼 값 설명
            for col in columns:
                value = row.get(col)
                formatted_value = AccessibilityFormatter._format_value_for_speech(
                    value
                )
                parts.append(f"  - {col}: {formatted_value}")

            parts.append("")

        # 나머지 행이 있으면 요약만
        if row_count > detail_count:
            remaining = row_count - detail_count
            parts.append(
                f"나머지 {remaining}개의 결과가 더 있습니다. "
                "전체 내용은 테이블 모드로 확인하실 수 있습니다."
            )

        return "\n".join(parts)

    @staticmethod
    def _format_value_for_speech(value: Any) -> str:
        """
        값을 음성 출력 친화적으로 포맷.

        Args:
            value: 포맷할 값

        Returns:
            음성 친화적으로 포맷된 문자열

        Examples:
            >>> AccessibilityFormatter._format_value_for_speech(120000000)
            '1억 2천만'
            >>> AccessibilityFormatter._format_value_for_speech(None)
            '값 없음'
        """
        if value is None:
            return "값 없음"

        # 숫자 타입 처리
        if isinstance(value, (int, float)):
            # 1억 이상
            if value >= 100_000_000:
                billions = value // 100_000_000
                remainder = (value % 100_000_000) // 10_000
                if remainder > 0:
                    # 천만 단위 처리 (예: 2000만 → 2천만)
                    if remainder >= 1000:
                        return f"{billions}억 {remainder // 1000}천만"
                    else:
                        return f"{billions}억 {remainder}만"
                return f"{billions}억"

            # 1만 이상
            elif value >= 10_000:
                ten_thousands = value // 10_000
                remainder = value % 10_000
                if remainder > 0:
                    return f"{ten_thousands}만 {remainder:,}"
                return f"{ten_thousands}만"

            # 천 단위 구분
            else:
                return f"{value:,}"

        # 문자열 그대로 반환
        return str(value)
