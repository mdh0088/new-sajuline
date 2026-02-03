"""
Layer 3: 결과 보안 검증 및 처리.

쿼리 결과를 검증하고 민감 데이터를 마스킹합니다.

Stories: 3-1
FRs: FR-021 (4-Layer Security)
"""

from dataclasses import dataclass, field
from typing import Any

# 최대 반환 행 수 (NFR-003 "첫 토큰 <1초" 준수)
MAX_ROWS = 500

# 민감 컬럼 목록 (대소문자 무시)
SENSITIVE_COLUMNS = {
    "password",
    "passwd",
    "pwd",
    "resident_number",
    "ssn",
    "jumin",
    "card_number",
    "credit_card",
    "bank_account",
    "account_number",
    "secret",
    "api_key",
    "token",
}


@dataclass
class ResultValidationResult:
    """
    결과 검증 결과.

    Attributes:
        row_count: 원본 행 수 (자르기 전)
        was_truncated: 결과가 잘렸는지 여부
        masked_columns: 마스킹된 컬럼 목록
        warnings: 경고 사항 목록
    """

    row_count: int
    was_truncated: bool
    masked_columns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Layer3ResultValidator:
    """Layer 3: 결과 보안 검증 및 처리"""

    @classmethod
    def validate_and_sanitize(
        cls, data: list[dict[str, Any]], columns: list[str]
    ) -> tuple[list[dict[str, Any]], ResultValidationResult]:
        """
        결과 검증 및 정제.

        Args:
            data: 쿼리 결과 데이터 (row의 리스트)
            columns: 컬럼 이름 목록

        Returns:
            tuple[list[dict[str, Any]], ResultValidationResult]:
                - 정제된 데이터 (마스킹 및 자르기 적용)
                - 검증 결과
        """
        original_row_count = len(data)
        masked_columns = []
        warnings = []

        # 빈 결과 처리
        if original_row_count == 0:
            return data, ResultValidationResult(
                row_count=0,
                was_truncated=False,
                masked_columns=[],
                warnings=[],
            )

        # 1. 민감 컬럼 식별 (대소문자 무시)
        sensitive_cols_in_result = []
        columns_lower_map = {col.lower(): col for col in columns}

        for sensitive in SENSITIVE_COLUMNS:
            if sensitive in columns_lower_map:
                original_col_name = columns_lower_map[sensitive]
                sensitive_cols_in_result.append(original_col_name)
                masked_columns.append(original_col_name)

        # 2. 데이터 복사 (원본 불변성 보장)
        sanitized_data = []
        for row in data:
            row_copy = row.copy()
            sanitized_data.append(row_copy)

        # 3. 민감 데이터 마스킹
        for row in sanitized_data:
            for col in sensitive_cols_in_result:
                if col in row:
                    # NULL/None 값도 마스킹 (일관성)
                    row[col] = "***"

        # 4. 행 수 제한 (MAX_ROWS 초과 시 자르기)
        was_truncated = False
        if original_row_count > MAX_ROWS:
            sanitized_data = sanitized_data[:MAX_ROWS]
            was_truncated = True
            warnings.append(
                f"Result truncated: {original_row_count} rows → {MAX_ROWS} rows"
            )

        # 5. 대용량 결과 경고 (선택적, MAX_ROWS에 가까운 경우)
        if original_row_count >= MAX_ROWS * 0.9 and not was_truncated:
            warnings.append(
                f"Large result set: {original_row_count} rows (close to limit)"
            )

        # 결과 생성
        result = ResultValidationResult(
            row_count=original_row_count,
            was_truncated=was_truncated,
            masked_columns=masked_columns,
            warnings=warnings,
        )

        return sanitized_data, result
