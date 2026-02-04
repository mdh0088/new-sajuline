"""
민감 데이터 마스킹 모듈.

역할별 민감 데이터 마스킹을 처리합니다.

Stories: 3-3-sensitive-data-masking
FRs: FR-016, NFR-S4
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from src.services.ai.config.masking_rules import (
    MASKING_RULES,
    TABLE_SPECIFIC_RULES,
    MaskingLevel,
    MaskingType,
)
from src.services.ai.security.rbac import AIRole

logger = logging.getLogger(__name__)


@dataclass
class MaskingResult:
    """마스킹 결과"""

    data: list[dict[str, Any]]
    masked_columns: list[str]
    mask_count: int


class DataMasker:
    """민감 데이터 마스킹"""

    # 역할별 마스킹 레벨 (AC 5: 역할별 마스킹 수준)
    MASKING_LEVELS = {
        AIRole.SUPER_ADMIN: MaskingLevel.NONE,  # 마스킹 안 함 (전체 표시)
        AIRole.ADMIN: MaskingLevel.PARTIAL,  # 부분 마스킹
        AIRole.VIEWER: MaskingLevel.FULL,  # 완전 마스킹
    }

    @classmethod
    def mask_data(
        cls,
        data: list[dict[str, Any]],
        columns: list[str],
        role: AIRole,
        table_name: str | None = None,
    ) -> MaskingResult:
        """
        데이터 마스킹 수행.

        Args:
            data: 쿼리 결과 데이터
            columns: 컬럼 이름 목록
            role: 사용자 역할
            table_name: 테이블명 (TABLE_SPECIFIC_RULES 적용 시)

        Returns:
            MaskingResult: 마스킹된 데이터 및 메타데이터
        """
        masking_level = cls.MASKING_LEVELS.get(role, MaskingLevel.FULL)
        masked_columns = []
        mask_count = 0

        # AC 5: Super Admin은 마스킹 안 함
        if masking_level == MaskingLevel.NONE:
            logger.info(f"Role {role.value}: No masking applied (SUPER_ADMIN)")
            return MaskingResult(
                data=data, masked_columns=[], mask_count=0
            )

        # 성능 최적화: 컬럼별 마스킹 타입 사전 계산 (O(n*m*k) → O(n*m))
        column_mask_types: dict[str, str] = {}
        for col in columns:
            # AC 2: 테이블별 규칙 우선 적용
            if table_name and table_name in TABLE_SPECIFIC_RULES:
                table_rules = TABLE_SPECIFIC_RULES[table_name]
                if col in table_rules:
                    column_mask_types[col] = table_rules[col]
                    continue

            # 일반 규칙 적용
            mask_type = MASKING_RULES.find_mask_type(col)
            if mask_type:
                column_mask_types[col] = mask_type

        # 데이터 마스킹 수행
        masked_data = []
        for row in data:
            masked_row = row.copy()
            for col, value in row.items():
                if value is None or col not in column_mask_types:
                    continue

                try:
                    original = str(value)
                    mask_type = column_mask_types[col]
                    masked = cls._apply_mask(
                        original, mask_type, masking_level.value
                    )

                    if masked != original:
                        masked_row[col] = masked
                        if col not in masked_columns:
                            masked_columns.append(col)
                        mask_count += 1
                except Exception as e:
                    # AC 3 + Error Handling: 마스킹 실패 시 완전 마스킹
                    logger.warning(
                        f"Masking failed for column '{col}': {e}. "
                        f"Applying full masking."
                    )
                    masked_row[col] = "***"
                    if col not in masked_columns:
                        masked_columns.append(col)
                    mask_count += 1

            masked_data.append(masked_row)

        # AC 3: 마스킹 결과 로깅
        if masked_columns:
            logger.info(
                f"Masked {mask_count} values in {len(masked_columns)} columns: "
                f"{masked_columns} (role: {role.value}, level: {masking_level.value})"
            )

        return MaskingResult(
            data=masked_data,
            masked_columns=masked_columns,
            mask_count=mask_count,
        )

    @classmethod
    def _apply_mask(cls, value: str, mask_type: str, level: str) -> str:
        """
        마스킹 타입에 따라 마스킹 적용.

        Args:
            value: 원본 값
            mask_type: 마스킹 타입 (MaskingType enum value)
            level: 마스킹 레벨 (MaskingLevel enum value)

        Returns:
            마스킹된 값

        Raises:
            ValueError: 알 수 없는 마스킹 타입
        """
        if mask_type == MaskingType.PHONE.value:
            return cls._mask_phone(value, level)
        elif mask_type == MaskingType.EMAIL.value:
            return cls._mask_email(value, level)
        elif mask_type == MaskingType.SSN.value:
            return cls._mask_ssn(value, level)
        elif mask_type == MaskingType.CARD.value:
            return cls._mask_card(value, level)
        elif mask_type == MaskingType.ACCOUNT.value:
            return cls._mask_account(value, level)
        elif mask_type == MaskingType.NAME.value:
            return cls._mask_name(value, level)
        else:
            # Fail-safe: 알 수 없는 타입은 완전 마스킹
            logger.error(f"Unknown mask_type: {mask_type}. Applying full mask.")
            return "***"

    @staticmethod
    def _mask_phone(value: str, level: str) -> str:
        """전화번호 마스킹: 010-****-1234"""
        if level == MaskingLevel.NONE.value:
            return value

        digits = re.sub(r"\D", "", value)
        if len(digits) < 10:
            return "***-****-****" if level == MaskingLevel.FULL.value else value

        if level == MaskingLevel.FULL.value:
            return "***-****-****"
        else:  # partial
            return f"{digits[:3]}-****-{digits[-4:]}"

    @staticmethod
    def _mask_email(value: str, level: str) -> str:
        """이메일 마스킹: ki***@example.com"""
        if level == MaskingLevel.NONE.value:
            return value

        if "@" not in value:
            return (
                "****@****.***" if level == MaskingLevel.FULL.value else value
            )

        local, domain = value.split("@", 1)

        if level == MaskingLevel.FULL.value:
            return "****@****.***"
        else:  # partial
            if len(local) <= 2:
                masked_local = local[0] + "***"
            else:
                masked_local = local[:2] + "***"
            return f"{masked_local}@{domain}"

    @staticmethod
    def _mask_ssn(value: str, level: str) -> str:
        """주민번호 마스킹: ******-******* (항상 완전 마스킹)"""
        if level == MaskingLevel.NONE.value:
            return value
        return "******-*******"

    @staticmethod
    def _mask_card(value: str, level: str) -> str:
        """카드번호 마스킹: ****-****-****-1234"""
        if level == MaskingLevel.NONE.value:
            return value

        digits = re.sub(r"\D", "", value)
        if len(digits) < 16:
            return "****-****-****-****"

        if level == MaskingLevel.FULL.value:
            return "****-****-****-****"
        else:  # partial
            return f"****-****-****-{digits[-4:]}"

    @staticmethod
    def _mask_account(value: str, level: str) -> str:
        """계좌번호 마스킹"""
        if level == MaskingLevel.NONE.value:
            return value

        if level == MaskingLevel.FULL.value:
            return "***-**-******"
        else:  # partial
            cleaned = re.sub(r"\D", "", value)
            if len(cleaned) > 4:
                return "***-**-***" + cleaned[-4:]
            return "***-**-******"

    @staticmethod
    def _mask_name(value: str, level: str) -> str:
        """이름 마스킹: 김*수"""
        if level == MaskingLevel.NONE.value:
            return value

        if not value or len(value) < 2:
            return "***"

        if level == MaskingLevel.FULL.value:
            return "***"
        else:  # partial
            if len(value) == 2:
                return value[0] + "*"
            else:
                return value[0] + "*" * (len(value) - 2) + value[-1]
