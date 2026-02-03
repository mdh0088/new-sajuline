"""
Layer 1 프롬프트 보안 테스트.

Stories: 3-1
"""

import pytest

from src.services.ai.security.layer1_prompt import (
    SECURITY_SYSTEM_PROMPT,
    build_secure_prompt,
)


class TestLayer1PromptSecurity:
    """Layer 1: 프롬프트 엔지니어링 보안 테스트"""

    def test_security_system_prompt_exists(self):
        """시스템 프롬프트 상수가 정의되어 있는지 확인"""
        assert isinstance(SECURITY_SYSTEM_PROMPT, str)
        assert len(SECURITY_SYSTEM_PROMPT) > 0

    def test_security_prompt_contains_select_only(self):
        """SELECT only 제약이 명시되어 있는지 확인"""
        prompt = SECURITY_SYSTEM_PROMPT.lower()
        assert "select" in prompt
        assert any(
            keyword in prompt
            for keyword in ["only", "만", "오직", "제한", "허용"]
        )

    def test_security_prompt_contains_allowed_tables(self):
        """허용 테이블 목록이 명시되어 있는지 확인"""
        prompt = SECURITY_SYSTEM_PROMPT.lower()
        assert any(
            keyword in prompt
            for keyword in ["allowed", "허용", "table", "테이블"]
        )

    def test_security_prompt_contains_forbidden_patterns(self):
        """금지 패턴 설명이 포함되어 있는지 확인"""
        prompt = SECURITY_SYSTEM_PROMPT.lower()
        assert any(
            keyword in prompt
            for keyword in [
                "forbidden",
                "금지",
                "prohibited",
                "not allowed",
                "허용되지 않",
            ]
        )

    def test_build_secure_prompt_basic(self):
        """기본 보안 프롬프트 생성 테스트"""
        user_query = "오늘 결제 금액 얼마야?"
        allowed_tables = {"payments", "members"}

        prompt = build_secure_prompt(
            user_query=user_query, allowed_tables=allowed_tables
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert user_query in prompt

    def test_build_secure_prompt_includes_system_prompt(self):
        """생성된 프롬프트에 시스템 보안 지침이 포함되는지 확인"""
        user_query = "회원 정보 조회"
        allowed_tables = {"members"}

        prompt = build_secure_prompt(
            user_query=user_query, allowed_tables=allowed_tables
        )

        # 시스템 프롬프트의 핵심 요소가 포함되어야 함
        prompt_lower = prompt.lower()
        assert "select" in prompt_lower or SECURITY_SYSTEM_PROMPT in prompt

    def test_build_secure_prompt_includes_allowed_tables(self):
        """생성된 프롬프트에 허용 테이블 목록이 포함되는지 확인"""
        user_query = "결제 통계"
        allowed_tables = {"payments", "members", "counselors"}

        prompt = build_secure_prompt(
            user_query=user_query, allowed_tables=allowed_tables
        )

        # 모든 허용 테이블이 프롬프트에 포함되어야 함
        for table in allowed_tables:
            assert table in prompt

    def test_build_secure_prompt_with_empty_allowed_tables(self):
        """허용 테이블이 비어있을 때 에러 발생 확인"""
        user_query = "데이터 조회"

        with pytest.raises(ValueError, match="allowed_tables.*empty"):
            build_secure_prompt(user_query=user_query, allowed_tables=set())

    def test_build_secure_prompt_with_special_characters(self):
        """특수 문자가 포함된 쿼리도 안전하게 처리"""
        user_query = "SELECT * FROM users; DROP TABLE members;--"
        allowed_tables = {"users"}

        prompt = build_secure_prompt(
            user_query=user_query, allowed_tables=allowed_tables
        )

        # 프롬프트가 생성되어야 함 (검증은 Layer 2에서)
        assert isinstance(prompt, str)
        assert user_query in prompt

    def test_build_secure_prompt_immutability(self):
        """동일한 입력에 대해 일관된 프롬프트 생성"""
        user_query = "회원 수 조회"
        allowed_tables = {"members"}

        prompt1 = build_secure_prompt(user_query, allowed_tables)
        prompt2 = build_secure_prompt(user_query, allowed_tables)

        assert prompt1 == prompt2
