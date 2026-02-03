"""
AI 보안 모듈.

4-Layer Security Framework 제공:
- Layer 1: Prompt Engineering (프롬프트 보안)
- Layer 2: SQL Validation (SQL 검증)
- Layer 3: Result Sanitization (결과 정제)
- Layer 4: User Confirmation (사용자 확인)

Stories: 3-1
"""

from dataclasses import dataclass
from typing import Any, Set

from .layer1_prompt import SECURITY_SYSTEM_PROMPT, build_secure_prompt
from .layer2_validator import (
    DANGEROUS_PATTERNS,
    FORBIDDEN_KEYWORDS,
    WARNING_PATTERNS,
    Layer2SQLValidator,
    SecurityValidationResult,
)
from .layer3_result import (
    MAX_ROWS,
    SENSITIVE_COLUMNS,
    Layer3ResultValidator,
    ResultValidationResult,
)
from .layer4_user import (
    COMPLEX_JOIN_THRESHOLD,
    LARGE_RESULT_THRESHOLD,
    Layer4UserConfirmation,
    UserConfirmationRequired,
)


@dataclass
class SecurityPipelineResult:
    """
    보안 파이프라인 전체 결과.

    Attributes:
        layer1_prompt: Layer 1에서 생성된 보안 프롬프트
        layer2_validation: Layer 2 SQL 검증 결과
        layer3_validation: Layer 3 결과 검증 결과
        layer4_confirmation: Layer 4 사용자 확인 결과
        is_safe: 전체 파이프라인이 안전한지 여부
    """

    layer1_prompt: str
    layer2_validation: SecurityValidationResult | None
    layer3_validation: ResultValidationResult | None
    layer4_confirmation: UserConfirmationRequired | None
    is_safe: bool


class SecurityPipeline:
    """
    4-Layer Security Framework 파이프라인.

    모든 보안 레이어를 순차적으로 적용하여 AI BI 어시스턴트의 보안을 보장합니다.
    """

    @classmethod
    def build_secure_prompt(cls, user_query: str, allowed_tables: Set[str]) -> str:
        """
        Layer 1: 보안 프롬프트 생성.

        Args:
            user_query: 사용자 자연어 질의
            allowed_tables: 허용된 테이블 목록

        Returns:
            str: 보안 지침이 포함된 프롬프트
        """
        return build_secure_prompt(user_query, allowed_tables)

    @classmethod
    def validate_sql(
        cls, sql: str, allowed_tables: Set[str]
    ) -> SecurityValidationResult:
        """
        Layer 2: SQL 보안 검증.

        Args:
            sql: 검증할 SQL 문자열
            allowed_tables: 허용된 테이블 목록

        Returns:
            SecurityValidationResult: 검증 결과
        """
        return Layer2SQLValidator.validate(sql, allowed_tables)

    @classmethod
    def sanitize_result(
        cls, data: list[dict[str, Any]], columns: list[str]
    ) -> tuple[list[dict[str, Any]], ResultValidationResult]:
        """
        Layer 3: 결과 정제 (마스킹 및 자르기).

        Args:
            data: 쿼리 결과 데이터
            columns: 컬럼 이름 목록

        Returns:
            tuple: (정제된 데이터, 검증 결과)
        """
        return Layer3ResultValidator.validate_and_sanitize(data, columns)

    @classmethod
    def check_user_confirmation(
        cls, sql: str, estimated_rows: int | None = None
    ) -> UserConfirmationRequired:
        """
        Layer 4: 사용자 확인 필요 여부 판단.

        Args:
            sql: 실행할 SQL
            estimated_rows: 예상 결과 행 수

        Returns:
            UserConfirmationRequired: 확인 필요 여부 및 이유
        """
        return Layer4UserConfirmation.check_confirmation_needed(sql, estimated_rows)

    @classmethod
    def full_pipeline(
        cls,
        user_query: str,
        sql: str,
        allowed_tables: Set[str],
        data: list[dict[str, Any]] | None = None,
        columns: list[str] | None = None,
        estimated_rows: int | None = None,
    ) -> SecurityPipelineResult:
        """
        전체 보안 파이프라인 실행.

        Args:
            user_query: 사용자 자연어 질의
            sql: 생성된 SQL
            allowed_tables: 허용된 테이블 목록
            data: 쿼리 결과 데이터 (선택적, Layer 3용)
            columns: 컬럼 목록 (선택적, Layer 3용)
            estimated_rows: 예상 결과 행 수 (선택적, Layer 4용)

        Returns:
            SecurityPipelineResult: 전체 파이프라인 결과
        """
        # Layer 1: 프롬프트 생성
        prompt = cls.build_secure_prompt(user_query, allowed_tables)

        # Layer 2: SQL 검증
        validation = cls.validate_sql(sql, allowed_tables)

        # Layer 3: 결과 정제 (데이터가 있는 경우)
        result3 = None
        if data is not None and columns is not None:
            _, result3 = cls.sanitize_result(data, columns)

        # Layer 4: 사용자 확인
        confirmation = cls.check_user_confirmation(sql, estimated_rows)

        # 전체 안전성 판단
        is_safe = validation.is_safe and not confirmation.required

        return SecurityPipelineResult(
            layer1_prompt=prompt,
            layer2_validation=validation,
            layer3_validation=result3,
            layer4_confirmation=confirmation,
            is_safe=is_safe,
        )


__all__ = [
    # Layer 1
    "SECURITY_SYSTEM_PROMPT",
    "build_secure_prompt",
    # Layer 2
    "FORBIDDEN_KEYWORDS",
    "DANGEROUS_PATTERNS",
    "WARNING_PATTERNS",
    "Layer2SQLValidator",
    "SecurityValidationResult",
    # Layer 3
    "MAX_ROWS",
    "SENSITIVE_COLUMNS",
    "Layer3ResultValidator",
    "ResultValidationResult",
    # Layer 4
    "LARGE_RESULT_THRESHOLD",
    "COMPLEX_JOIN_THRESHOLD",
    "Layer4UserConfirmation",
    "UserConfirmationRequired",
    # Pipeline
    "SecurityPipeline",
    "SecurityPipelineResult",
]
