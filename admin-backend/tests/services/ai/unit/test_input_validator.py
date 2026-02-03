"""
AI 입력 유효성 검사 단위 테스트.

Stories: 2-1
"""

import pytest
from src.services.ai.validators.input_validator import (
    validate_query_input,
    ValidationResult,
)
from src.schemas.ai.error_schema import AIErrorCode


class TestValidateQueryInput:
    """validate_query_input 함수 테스트"""

    @pytest.mark.asyncio
    async def test_valid_question(self):
        """유효한 질문 - 성공"""
        result = await validate_query_input("오늘 매출 얼마야?")
        assert result.is_valid is True
        assert result.error_code is None
        assert result.message is None

    @pytest.mark.asyncio
    async def test_valid_question_long(self):
        """유효한 긴 질문 - 성공"""
        result = await validate_query_input(
            "이번 달 신규 가입자 중에서 유료 결제를 한 사람은 몇 명이야?"
        )
        assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_question_too_short_after_strip(self):
        """공백 제거 후 5자 미만 - 실패"""
        result = await validate_query_input("   안녕   ")
        assert result.is_valid is False
        assert result.error_code == AIErrorCode.QUESTION_TOO_SHORT
        assert "짧습니다" in result.message
        assert len(result.suggestions) > 0

    @pytest.mark.asyncio
    async def test_only_numbers(self):
        """숫자만 입력 - 실패"""
        result = await validate_query_input("12345")
        assert result.is_valid is False
        assert result.error_code == AIErrorCode.INVALID_INPUT
        assert "유효한 질문" in result.message

    @pytest.mark.asyncio
    async def test_only_special_characters(self):
        """특수문자만 입력 - 실패"""
        result = await validate_query_input("!@#$%^&*()")
        assert result.is_valid is False
        assert result.error_code == AIErrorCode.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_repeated_characters(self):
        """반복 문자 (5회 이상) - 실패"""
        result = await validate_query_input("aaaaa")
        assert result.is_valid is False
        assert result.error_code == AIErrorCode.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_mixed_valid_input(self):
        """숫자 포함 유효 질문 - 성공"""
        result = await validate_query_input("2024년 1월 매출은?")
        assert result.is_valid is True
