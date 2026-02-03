"""
응답 데이터 포맷터.

테이블 데이터의 숫자, 날짜, 금액을 사용자 친화적으로 포맷팅.

Stories: 2-4
FRs: FR-011, FR-013
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any


class ResponseFormatter:
    """응답 데이터 포맷터

    테이블 데이터의 숫자, 날짜, 금액을 사용자 친화적인 형식으로 변환합니다.
    """

    @staticmethod
    def format_table_data(
        data: list[dict[str, Any]],
        columns: list[str],
        column_mappings: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """테이블 데이터 포맷팅

        Args:
            data: 원본 데이터
            columns: 컬럼 목록
            column_mappings: 컬럼 한글 매핑 (옵션)

        Returns:
            list[dict[str, Any]]: 포맷팅된 데이터
        """
        if not data:
            return []

        formatted_data = []

        for row in data:
            formatted_row = {}

            for col in columns:
                value = row.get(col)

                # 컬럼명 한글화
                display_col = column_mappings.get(col, col) if column_mappings else col

                # 값 포맷팅
                formatted_value = ResponseFormatter._format_value(value, col)

                formatted_row[display_col] = formatted_value

            formatted_data.append(formatted_row)

        return formatted_data

    @staticmethod
    def _format_value(value: Any, column_name: str) -> Any:
        """개별 값 포맷팅

        컬럼명과 값 타입을 기반으로 적절한 포맷을 적용합니다.

        타입 추론 순서:
        1. NULL 값 → "-"
        2. 컬럼명에 금액 키워드 포함 → 금액 포맷 (억/만/원)
        3. 컬럼명에 날짜 키워드 포함 → 날짜 포맷 (YYYY-MM-DD)
        4. datetime/date 타입 → 날짜 포맷
        5. 숫자 타입 (금액 컬럼) → 금액 포맷
        6. 숫자 타입 (일반) → 천 단위 구분
        7. 기타 → 문자열 변환

        Args:
            value: 원본 값
            column_name: 컬럼명 (타입 추론용 - 금액/날짜 키워드 감지)

        Returns:
            Any: 포맷팅된 값 (문자열 또는 원본)
        """
        if value is None:
            return "-"

        # 금액 컬럼 감지 (amount, price, sales, revenue, cost 등)
        # 영문 및 한글 키워드 모두 지원
        is_money_column = any(
            keyword in column_name.lower()
            for keyword in [
                # 영문 키워드
                "amount",
                "price",
                "sales",
                "revenue",
                "cost",
                "total",
                "fee",
                "charge",
                "deposit",
                "refund",
                "discount",
                "tax",
                "commission",
                # 한글 키워드
                "금액",
                "가격",
                "매출",
                "수익",
                "비용",
                "합계",
                "수수료",
                "요금",
                "입금",
                "환불",
                "할인",
                "세금",
                "수수료",
            ]
        )

        # 날짜 컬럼 감지 (date, time, created, updated 등)
        is_date_column = any(
            keyword in column_name.lower()
            for keyword in [
                "date",
                "time",
                "created",
                "updated",
                "deleted",
                "at",
                "started",
                "finished",
                "expired",
                "birth",
                "joined",
                "registered",
                "modified",
                "confirmed",
                "completed",
                "canceled",
                "scheduled",
            ]
        )

        # 날짜 타입
        if isinstance(value, (date, datetime)):
            return ResponseFormatter.format_date(value)

        # 날짜 컬럼인데 문자열인 경우 (예: "2024-01-15") - 그대로 반환
        if is_date_column and isinstance(value, str):
            return value

        # 숫자 타입
        if isinstance(value, (int, float, Decimal)):
            if is_money_column:
                return ResponseFormatter.format_money(value)
            else:
                return ResponseFormatter.format_number(value)

        # 그 외는 문자열로 변환
        return str(value)

    @staticmethod
    def format_money(amount: int | float | Decimal) -> str:
        """금액 포맷팅

        Args:
            amount: 금액

        Returns:
            str: 포맷팅된 금액 (예: "1억 2천만원", "500만원", "15,000원")
        """
        amount = float(amount)

        # 음수 처리
        is_negative = amount < 0
        amount = abs(amount)

        if amount >= 100_000_000:
            # 1억 이상: "X억 Y천만원"
            billion = int(amount // 100_000_000)
            remainder = amount % 100_000_000
            if remainder >= 10_000_000:
                million = int(remainder // 10_000_000)
                result = f"{billion}억 {million}천만원"
            else:
                result = f"{billion}억원"
        elif amount >= 10_000:
            # 1만 이상: "X만원" 또는 "X천만원"
            if amount >= 10_000_000:
                million = int(amount // 10_000_000)
                result = f"{million}천만원"
            else:
                ten_thousand = int(amount // 10_000)
                result = f"{ten_thousand}만원"
        else:
            # 1만 미만: "X,XXX원"
            result = f"{amount:,.0f}원"

        return f"-{result}" if is_negative else result

    @staticmethod
    def format_number(number: int | float | Decimal) -> str:
        """숫자 포맷팅 (천 단위 구분)

        Args:
            number: 숫자

        Returns:
            str: 포맷팅된 숫자 (예: "1,234", "1,234.56")
        """
        number = float(number)

        # 정수인 경우
        if number == int(number):
            return f"{int(number):,}"

        # 소수점이 있는 경우 (소수점 2자리까지)
        return f"{number:,.2f}"

    @staticmethod
    def format_date(date_value: date | datetime) -> str:
        """날짜 포맷팅

        Args:
            date_value: 날짜 또는 날짜시간

        Returns:
            str: 포맷팅된 날짜 (예: "2024-01-15", "2024-01-15 14:30")
        """
        if isinstance(date_value, datetime):
            # 시간 정보가 있는 경우
            if date_value.hour != 0 or date_value.minute != 0 or date_value.second != 0:
                return date_value.strftime("%Y-%m-%d %H:%M")
            else:
                # 시간이 00:00:00인 경우 날짜만 표시
                return date_value.strftime("%Y-%m-%d")
        else:
            # date 타입
            return date_value.strftime("%Y-%m-%d")

    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """퍼센트 포맷팅

        Args:
            value: 퍼센트 값 (0-100 범위)
            decimal_places: 소수점 자리수 (기본값: 1)

        Returns:
            str: 포맷팅된 퍼센트 (예: "12.5%", "99.9%")
        """
        return f"{value:.{decimal_places}f}%"
