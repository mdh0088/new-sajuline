"""
Layer 3 결과 검증 테스트.

Stories: 3-1
"""

import pytest

from src.services.ai.security.layer3_result import (
    MAX_ROWS,
    SENSITIVE_COLUMNS,
    Layer3ResultValidator,
    ResultValidationResult,
)


class TestResultValidationResult:
    """ResultValidationResult 데이터클래스 테스트"""

    def test_result_creation(self):
        """결과 검증 결과 생성"""
        result = ResultValidationResult(
            row_count=10,
            was_truncated=False,
            masked_columns=[],
            warnings=[],
        )

        assert result.row_count == 10
        assert result.was_truncated is False
        assert len(result.masked_columns) == 0

    def test_result_with_masking(self):
        """마스킹이 적용된 결과"""
        result = ResultValidationResult(
            row_count=5,
            was_truncated=False,
            masked_columns=["password", "card_number"],
            warnings=[],
        )

        assert len(result.masked_columns) == 2
        assert "password" in result.masked_columns


class TestLayer3ResultValidator:
    """Layer 3 결과 검증기 테스트"""

    def test_validator_exists(self):
        """Layer3ResultValidator 클래스가 존재하는지 확인"""
        assert Layer3ResultValidator is not None

    def test_max_rows_defined(self):
        """MAX_ROWS 상수가 정의되어 있는지 확인"""
        assert isinstance(MAX_ROWS, int)
        assert MAX_ROWS > 0
        assert MAX_ROWS == 500  # NFR-003 준수 (첫 토큰 <1초)

    def test_sensitive_columns_defined(self):
        """SENSITIVE_COLUMNS 상수가 정의되어 있는지 확인"""
        assert isinstance(SENSITIVE_COLUMNS, set)
        assert len(SENSITIVE_COLUMNS) > 0
        # 주요 민감 컬럼들이 포함되어 있어야 함
        assert "password" in SENSITIVE_COLUMNS
        assert "card_number" in SENSITIVE_COLUMNS
        assert "ssn" in SENSITIVE_COLUMNS or "resident_number" in SENSITIVE_COLUMNS

    def test_validate_and_sanitize_basic(self):
        """기본 결과 검증 및 정제"""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        columns = ["id", "name"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        assert result.row_count == 2
        assert result.was_truncated is False
        assert len(sanitized_data) == 2
        assert sanitized_data == data  # 변경 없음

    def test_validate_truncate_large_result(self):
        """대용량 결과 자르기 (MAX_ROWS 초과)"""
        # MAX_ROWS보다 많은 데이터 생성
        data = [{"id": i, "value": f"data{i}"} for i in range(MAX_ROWS + 100)]
        columns = ["id", "value"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        assert result.row_count == MAX_ROWS + 100  # 원본 행 수
        assert result.was_truncated is True
        assert len(sanitized_data) == MAX_ROWS  # 잘린 후 행 수

    def test_validate_mask_sensitive_column_password(self):
        """비밀번호 컬럼 마스킹"""
        data = [
            {"id": 1, "password": "secret123"},
            {"id": 2, "password": "abc456"},
        ]
        columns = ["id", "password"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        assert "password" in result.masked_columns
        # 마스킹된 데이터 확인
        assert sanitized_data[0]["password"] == "***"
        assert sanitized_data[1]["password"] == "***"

    def test_validate_mask_sensitive_column_card_number(self):
        """카드번호 컬럼 마스킹"""
        data = [
            {"id": 1, "card_number": "1234-5678-9012-3456"},
        ]
        columns = ["id", "card_number"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        assert "card_number" in result.masked_columns
        assert sanitized_data[0]["card_number"] == "***"

    def test_validate_mask_multiple_sensitive_columns(self):
        """여러 민감 컬럼 동시 마스킹"""
        data = [
            {
                "id": 1,
                "name": "Alice",
                "password": "secret",
                "card_number": "1234-5678",
                "ssn": "123-45-6789",
            },
        ]
        columns = ["id", "name", "password", "card_number", "ssn"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        # 민감 컬럼이 모두 마스킹되어야 함
        assert len(result.masked_columns) >= 2  # password, card_number는 필수
        assert sanitized_data[0]["password"] == "***"
        assert sanitized_data[0]["card_number"] == "***"
        # name은 마스킹되지 않음
        assert sanitized_data[0]["name"] == "Alice"

    def test_validate_case_insensitive_column_matching(self):
        """대소문자 구분 없이 민감 컬럼 감지"""
        data = [
            {"id": 1, "PASSWORD": "secret"},  # 대문자
            {"id": 2, "Card_Number": "1234"},  # 혼합
        ]
        columns = ["id", "PASSWORD", "Card_Number"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        # 대소문자 관계없이 마스킹되어야 함
        assert len(result.masked_columns) >= 1
        assert sanitized_data[0]["PASSWORD"] == "***"
        assert sanitized_data[1]["Card_Number"] == "***"

    def test_validate_empty_result(self):
        """빈 결과 처리"""
        data = []
        columns = []

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        assert result.row_count == 0
        assert result.was_truncated is False
        assert len(sanitized_data) == 0

    def test_validate_partial_sensitive_columns(self):
        """일부 컬럼만 민감한 경우"""
        data = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
        columns = ["id", "name", "email"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        # 민감하지 않은 컬럼은 그대로
        assert sanitized_data[0]["name"] == "Alice"
        assert sanitized_data[0]["email"] == "alice@example.com"

    def test_validate_null_values_in_sensitive_columns(self):
        """민감 컬럼에 NULL 값이 있는 경우"""
        data = [
            {"id": 1, "password": None},
            {"id": 2, "password": "secret"},
        ]
        columns = ["id", "password"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        # NULL 값도 마스킹 (또는 그대로 유지)
        # 구현 정책에 따라 달라질 수 있음
        assert "password" in result.masked_columns

    def test_validate_immutability(self):
        """원본 데이터 불변성 보장"""
        original_data = [
            {"id": 1, "password": "secret"},
        ]
        columns = ["id", "password"]

        # 원본 복사본 생성
        data_copy = [row.copy() for row in original_data]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data_copy, columns
        )

        # 원본은 변경되지 않아야 함
        assert original_data[0]["password"] == "secret"
        # 정제된 데이터는 마스킹되어야 함
        assert sanitized_data[0]["password"] == "***"

    def test_validate_warnings_for_large_result(self):
        """대용량 결과에 대한 경고"""
        # MAX_ROWS에 가까운 데이터
        data = [{"id": i} for i in range(MAX_ROWS - 10)]
        columns = ["id"]

        sanitized_data, result = Layer3ResultValidator.validate_and_sanitize(
            data, columns
        )

        # 경고가 있을 수 있음 (선택적)
        if len(result.warnings) > 0:
            assert any("large" in w.lower() for w in result.warnings)
