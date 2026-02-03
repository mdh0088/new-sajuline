"""
AI 질의 입력 유효성 검사.

Pydantic 스키마 검증 이후 추가 비즈니스 로직 검증을 수행합니다.

Stories: 2-1
FRs: FR-011 (자연어 질의 입력), FR-012 (입력 유효성 검사)
"""

import re
from dataclasses import dataclass, field
from typing import List

from src.schemas.ai.error_schema import AIErrorCode


@dataclass
class ValidationResult:
    """유효성 검사 결과"""

    is_valid: bool
    error_code: str | None = None
    message: str | None = None
    suggestions: List[str] = field(default_factory=list)


async def validate_query_input(question: str) -> ValidationResult:
    """
    질의 입력 추가 유효성 검사.

    Pydantic 스키마 검증 후 추가적인 비즈니스 로직 검증을 수행합니다.
    Defense in Depth: SQL Injection 패턴을 서비스 레벨에서도 검증합니다.

    NOTE: Pydantic 스키마는 이미 공백 제거(strip) 후 문자열을 전달하므로
    여기서는 이미 trim된 문자열로 검증합니다.
    하지만 직접 호출 시(테스트 등)를 위해 안전하게 strip 처리합니다.

    Args:
        question: 사용자 질문

    Returns:
        ValidationResult: 검증 결과
    """

    # 공백 제거 (Pydantic에서 이미 처리되지만 직접 호출 대비)
    trimmed = question.strip()

    # 길이 검사 (Pydantic min_length=5와 동일)
    if len(trimmed) < 5:
        return ValidationResult(
            is_valid=False,
            error_code=AIErrorCode.QUESTION_TOO_SHORT,
            message="질문이 너무 짧습니다. 더 구체적으로 질문해주세요.",
            suggestions=["예: '오늘 매출 얼마야?'", "예: '이번 달 신규 가입자 수'"],
        )

    # Defense in Depth: SQL Injection 패턴 체크 (Pydantic과 중복이지만 안전성 강화)
    sql_injection_patterns = [
        r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE)\b",
        r";\s*--",
        r"/\*.*?\*/",
        r"UNION\s+(ALL\s+)?SELECT",
        r"\bOR\s+\d+\s*=\s*\d+",
        r"\bAND\s+\d+\s*=\s*\d+",
        r"\b(sp_|xp_)\w+",
        r"0x[0-9a-fA-F]+",
    ]
    for pattern in sql_injection_patterns:
        if re.search(pattern, trimmed, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                error_code=AIErrorCode.SQL_KEYWORD_DETECTED,
                message="SQL 키워드를 직접 입력할 수 없습니다. 자연어로 질문해주세요.",
                suggestions=[
                    "자연어로 질문을 입력해주세요.",
                    "예: '오늘 매출 얼마야?'",
                ],
            )

    # 숫자/특수문자만 있는 경우
    if re.match(r"^[\d\s\W]+$", trimmed):
        return ValidationResult(
            is_valid=False,
            error_code=AIErrorCode.INVALID_INPUT,
            message="유효한 질문을 입력해주세요.",
            suggestions=["자연어로 질문을 입력해주세요."],
        )

    # 반복 문자 체크 (동일 문자 5번 이상 반복)
    if re.search(r"(.)\1{4,}", trimmed):
        return ValidationResult(
            is_valid=False,
            error_code=AIErrorCode.INVALID_INPUT,
            message="유효한 질문을 입력해주세요.",
            suggestions=["의미 있는 질문을 입력해주세요."],
        )

    return ValidationResult(is_valid=True)
