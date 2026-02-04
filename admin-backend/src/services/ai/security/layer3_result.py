"""
Layer 3: 결과 보안 검증 및 처리.

쿼리 결과를 검증하고 민감 데이터를 마스킹합니다.

Stories: 3-1, 3-3-sensitive-data-masking
FRs: FR-021 (4-Layer Security), FR-016 (Data Masking)
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from src.services.ai.security.data_masking import DataMasker
from src.services.ai.security.rbac import AIRole

logger = logging.getLogger(__name__)

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
        cls,
        data: list[dict[str, Any]],
        columns: list[str],
        role: AIRole = AIRole.VIEWER,
        table_name: str | None = None,
    ) -> tuple[list[dict[str, Any]], ResultValidationResult]:
        """
        결과 검증 및 정제.

        Args:
            data: 쿼리 결과 데이터 (row의 리스트)
            columns: 컬럼 이름 목록
            role: 사용자 역할 (마스킹 레벨 결정)
            table_name: 테이블명 (테이블별 마스킹 규칙 적용)

        Returns:
            tuple[list[dict[str, Any]], ResultValidationResult]:
                - 정제된 데이터 (마스킹 및 자르기 적용)
                - 검증 결과
        """
        original_row_count = len(data)
        warnings = []

        # 빈 결과 처리
        if original_row_count == 0:
            logger.info("Empty result set - no validation needed")
            return data, ResultValidationResult(
                row_count=0,
                was_truncated=False,
                masked_columns=[],
                warnings=[],
            )

        # 1. 행 수 제한 (MAX_ROWS 초과 시 자르기)
        was_truncated = False
        sanitized_data = data
        if original_row_count > MAX_ROWS:
            sanitized_data = data[:MAX_ROWS]
            was_truncated = True
            warning_msg = (
                f"Result truncated: {original_row_count} rows → {MAX_ROWS} rows"
            )
            warnings.append(warning_msg)
            logger.warning(warning_msg)

        # 2. 민감 데이터 마스킹 (역할별, AC 2: 테이블별 규칙 적용)
        masking_result = DataMasker.mask_data(
            sanitized_data, columns, role, table_name=table_name
        )

        # 3. 민감 컬럼 로깅 추가 (기존 방식과 통합)
        sensitive_cols_in_result = []
        columns_lower_map = {col.lower(): col for col in columns}

        for sensitive in SENSITIVE_COLUMNS:
            if sensitive in columns_lower_map:
                original_col_name = columns_lower_map[sensitive]
                if original_col_name not in masking_result.masked_columns:
                    sensitive_cols_in_result.append(original_col_name)

        # 4. 완전 마스킹이 필요한 민감 컬럼 처리 (password, token 등)
        for row in masking_result.data:
            for col in sensitive_cols_in_result:
                if col in row:
                    row[col] = "***"

        # 모든 마스킹된 컬럼 병합
        all_masked_columns = list(
            set(masking_result.masked_columns + sensitive_cols_in_result)
        )

        # 5. 대용량 결과 경고 (선택적, MAX_ROWS에 가까운 경우)
        if original_row_count >= MAX_ROWS * 0.9 and not was_truncated:
            warning_msg = (
                f"Large result set: {original_row_count} rows (close to limit)"
            )
            warnings.append(warning_msg)
            logger.warning(warning_msg)

        # AC 3: 민감 컬럼 로깅 (마스킹 결과 포함)
        if all_masked_columns:
            logger.info(
                f"Layer3 validation complete: "
                f"masked_columns={all_masked_columns}, "
                f"row_count={original_row_count}, "
                f"truncated={was_truncated}, "
                f"role={role.value}, "
                f"table={table_name or 'N/A'}"
            )
        elif sensitive_cols_in_result:
            logger.info(
                f"Sensitive columns detected (fully masked): "
                f"{sensitive_cols_in_result}"
            )

        # 결과 생성
        result = ResultValidationResult(
            row_count=original_row_count,
            was_truncated=was_truncated,
            masked_columns=all_masked_columns,
            warnings=warnings,
        )

        return masking_result.data, result
