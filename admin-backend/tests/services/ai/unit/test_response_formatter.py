"""
응답 포맷터 단위 테스트

Stories: 2-4
FRs: FR-011, FR-013
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from src.services.ai.utils.response_formatter import ResponseFormatter


class TestResponseFormatter:
    """ResponseFormatter 테스트"""

    def test_format_money_large_amount(self):
        """큰 금액 포맷팅 테스트 (억 단위)"""
        # 1억 2천만원
        result = ResponseFormatter.format_money(120000000)
        assert result == "1억 2천만원"

        # 3억원
        result = ResponseFormatter.format_money(300000000)
        assert result == "3억원"

        # 5억 5천만원
        result = ResponseFormatter.format_money(550000000)
        assert result == "5억 5천만원"

    def test_format_money_medium_amount(self):
        """중간 금액 포맷팅 테스트 (만원 단위)"""
        # 500만원
        result = ResponseFormatter.format_money(5000000)
        assert result == "500만원"

        # 1천만원
        result = ResponseFormatter.format_money(10000000)
        assert result == "1천만원"

        # 150만원
        result = ResponseFormatter.format_money(1500000)
        assert result == "150만원"

    def test_format_money_small_amount(self):
        """작은 금액 포맷팅 테스트 (원 단위)"""
        # 5,000원
        result = ResponseFormatter.format_money(5000)
        assert result == "5,000원"

        # 1,250원
        result = ResponseFormatter.format_money(1250)
        assert result == "1,250원"

    def test_format_money_negative(self):
        """음수 금액 포맷팅 테스트"""
        result = ResponseFormatter.format_money(-120000000)
        assert result == "-1억 2천만원"

        result = ResponseFormatter.format_money(-5000000)
        assert result == "-500만원"

    def test_format_money_decimal(self):
        """Decimal 타입 금액 포맷팅 테스트"""
        result = ResponseFormatter.format_money(Decimal("120000000.50"))
        assert result == "1억 2천만원"

    def test_format_number_integer(self):
        """정수 포맷팅 테스트"""
        result = ResponseFormatter.format_number(1234)
        assert result == "1,234"

        result = ResponseFormatter.format_number(1234567)
        assert result == "1,234,567"

    def test_format_number_float(self):
        """부동소수점 포맷팅 테스트"""
        result = ResponseFormatter.format_number(1234.56)
        assert result == "1,234.56"

        result = ResponseFormatter.format_number(9999.99)
        assert result == "9,999.99"

    def test_format_date_date_only(self):
        """날짜 포맷팅 테스트 (date 타입)"""
        test_date = date(2024, 1, 15)
        result = ResponseFormatter.format_date(test_date)
        assert result == "2024-01-15"

    def test_format_date_datetime_with_time(self):
        """날짜시간 포맷팅 테스트 (시간 포함)"""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)
        result = ResponseFormatter.format_date(test_datetime)
        assert result == "2024-01-15 14:30"

    def test_format_date_datetime_without_time(self):
        """날짜시간 포맷팅 테스트 (시간 00:00:00)"""
        test_datetime = datetime(2024, 1, 15, 0, 0, 0)
        result = ResponseFormatter.format_date(test_datetime)
        assert result == "2024-01-15"

    def test_format_percentage(self):
        """퍼센트 포맷팅 테스트"""
        result = ResponseFormatter.format_percentage(12.5)
        assert result == "12.5%"

        result = ResponseFormatter.format_percentage(99.9)
        assert result == "99.9%"

        result = ResponseFormatter.format_percentage(50.0, decimal_places=0)
        assert result == "50%"

    def test_format_table_data_empty(self):
        """빈 데이터 포맷팅 테스트"""
        result = ResponseFormatter.format_table_data(
            data=[],
            columns=["id", "name"],
        )
        assert result == []

    def test_format_table_data_with_mappings(self):
        """컬럼 매핑 포함 테이블 데이터 포맷팅 테스트"""
        data = [
            {"user_id": 1, "total_sales": 5000000, "created_at": date(2024, 1, 15)},
            {"user_id": 2, "total_sales": 3000000, "created_at": date(2024, 1, 16)},
        ]
        columns = ["user_id", "total_sales", "created_at"]
        column_mappings = {
            "user_id": "사용자 ID",
            "total_sales": "총 매출",
            "created_at": "생성일시",
        }

        result = ResponseFormatter.format_table_data(
            data=data,
            columns=columns,
            column_mappings=column_mappings,
        )

        assert len(result) == 2
        assert "사용자 ID" in result[0]
        assert "총 매출" in result[0]
        assert "생성일시" in result[0]

        # 금액 포맷팅 확인 (total_sales는 금액 컬럼으로 감지)
        assert result[0]["총 매출"] == "500만원"
        assert result[1]["총 매출"] == "300만원"

        # 날짜 포맷팅 확인
        assert result[0]["생성일시"] == "2024-01-15"

    def test_format_table_data_null_values(self):
        """NULL 값 처리 테스트"""
        data = [
            {"id": 1, "name": "Alice", "memo": None},
            {"id": 2, "name": None, "memo": "Test"},
        ]
        columns = ["id", "name", "memo"]

        result = ResponseFormatter.format_table_data(
            data=data,
            columns=columns,
        )

        assert result[0]["memo"] == "-"
        assert result[1]["name"] == "-"

    def test_format_value_detection(self):
        """값 타입 자동 감지 및 포맷팅 테스트"""
        # 금액 컬럼명 감지
        assert ResponseFormatter._format_value(5000000, "amount") == "500만원"
        assert ResponseFormatter._format_value(5000000, "price") == "500만원"
        assert ResponseFormatter._format_value(5000000, "sales") == "500만원"
        assert ResponseFormatter._format_value(5000000, "total_amount") == "500만원"

        # 일반 숫자 컬럼
        assert ResponseFormatter._format_value(1234, "count") == "1,234"
        assert ResponseFormatter._format_value(1234.56, "average") == "1,234.56"

        # 날짜 타입
        test_date = date(2024, 1, 15)
        assert ResponseFormatter._format_value(test_date, "created_at") == "2024-01-15"

        # 문자열
        assert ResponseFormatter._format_value("Test", "name") == "Test"

        # NULL
        assert ResponseFormatter._format_value(None, "memo") == "-"
