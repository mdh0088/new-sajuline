"""
접근성 응답 프롬프트 단위 테스트.

Stories: AI-005 (Story 2-5)
FRs: FR-006, NFR-A3
"""

import pytest
from src.services.ai.prompts.accessibility_response import (
    ACCESSIBILITY_RESPONSE_PROMPT,
    PROMPT_VERSION,
    build_accessibility_response_prompt,
)


class TestAccessibilityResponsePrompt:
    """접근성 응답 프롬프트 테스트"""

    def test_prompt_version_exists(self):
        """프롬프트 버전이 정의되어 있음"""
        assert PROMPT_VERSION is not None
        assert isinstance(PROMPT_VERSION, str)
        assert "." in PROMPT_VERSION  # 시맨틱 버전 (x.y.z)

    def test_accessibility_response_prompt_exists(self):
        """접근성 응답 프롬프트가 정의되어 있음"""
        assert ACCESSIBILITY_RESPONSE_PROMPT is not None
        assert isinstance(ACCESSIBILITY_RESPONSE_PROMPT, str)
        assert len(ACCESSIBILITY_RESPONSE_PROMPT) > 0

    def test_prompt_contains_key_guidelines(self):
        """프롬프트에 핵심 가이드라인이 포함됨"""
        prompt = ACCESSIBILITY_RESPONSE_PROMPT

        # 핵심 규칙 포함 확인
        assert "시각 장애" in prompt or "스크린리더" in prompt
        assert "상세한 설명" in prompt or "상세" in prompt
        assert "숫자 읽기" in prompt or "읽기" in prompt
        assert "순서" in prompt
        assert "요약" in prompt

    def test_build_accessibility_response_prompt(self):
        """접근성 응답 프롬프트 빌더 테스트"""
        # Given
        user_query = "오늘 매출을 알려주세요"
        sql = "SELECT SUM(amount) FROM payments WHERE date = CURDATE()"
        result_data = [{"total": 1200000}]
        columns = ["total"]

        # When
        prompt = build_accessibility_response_prompt(
            user_query=user_query,
            sql=sql,
            result_data=result_data,
            columns=columns,
        )

        # Then
        assert user_query in prompt
        assert str(result_data) in prompt or "1200000" in prompt
        assert "상세한 설명" in prompt or "스크린리더" in prompt
