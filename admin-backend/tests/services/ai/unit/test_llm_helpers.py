"""
LLM 헬퍼 함수 단위 테스트

Stories: 2-4
Reference: project-context.md#LLM-Call-Pattern
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from src.config.settings import Settings
from src.services.ai.utils.llm_helpers import call_llm_with_fallback


@pytest.fixture
def mock_settings():
    """Mock 설정 fixture"""
    settings = MagicMock(spec=Settings)
    settings.ai_llm_model = "gpt-4o-mini"
    settings.ai_llm_fallback_model = "gpt-3.5-turbo"
    settings.ai_llm_timeout = 30
    settings.openai_api_key = "test-api-key"
    return settings


@pytest.fixture
def mock_chain():
    """Mock LangChain Runnable fixture"""
    chain = MagicMock()
    chain.ainvoke = AsyncMock()
    return chain


class TestCallLLMWithFallback:
    """call_llm_with_fallback 함수 테스트"""

    @pytest.mark.asyncio
    async def test_primary_llm_success(self, mock_chain, mock_settings):
        """Primary LLM 첫 시도 성공"""
        # Given
        expected_result = AIMessage(content="Test response")
        mock_chain.ainvoke.return_value = expected_result
        input_data = {"question": "Test question"}

        # When
        result = await call_llm_with_fallback(
            chain=mock_chain,
            input_data=input_data,
            settings=mock_settings,
            agent_name="test_agent",
        )

        # Then
        assert result == expected_result
        mock_chain.ainvoke.assert_called_once_with(input_data)

    @pytest.mark.asyncio
    async def test_primary_llm_retry_then_success(self, mock_chain, mock_settings):
        """Primary LLM 재시도 후 성공"""
        # Given
        mock_chain.ainvoke.side_effect = [
            RateLimitError("Rate limit exceeded"),  # 첫 시도 실패
            AIMessage(content="Success after retry"),  # 재시도 성공
        ]
        input_data = {"question": "Test question"}

        # When
        result = await call_llm_with_fallback(
            chain=mock_chain,
            input_data=input_data,
            settings=mock_settings,
            agent_name="test_agent",
            max_retries=2,
        )

        # Then
        assert result.content == "Success after retry"
        assert mock_chain.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self, mock_chain, mock_settings):
        """Exponential backoff 타이밍 검증"""
        # Given
        mock_chain.ainvoke.side_effect = [
            RateLimitError("Rate limit"),
            RateLimitError("Rate limit again"),
            AIMessage(content="Finally success"),
        ]
        input_data = {"question": "Test"}

        # When
        start_time = asyncio.get_event_loop().time()
        result = await call_llm_with_fallback(
            chain=mock_chain,
            input_data=input_data,
            settings=mock_settings,
            max_retries=3,
        )
        end_time = asyncio.get_event_loop().time()

        # Then
        # 1초 + 2초 = 3초 이상 대기 (약간의 여유 포함)
        assert (end_time - start_time) >= 3.0
        assert result.content == "Finally success"

    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, mock_chain, mock_settings):
        """Primary 모든 재시도 실패 시 Fallback LLM 사용"""
        # Given
        mock_chain.ainvoke.side_effect = [
            APIConnectionError("Connection failed"),
            APIConnectionError("Connection failed again"),
        ]

        # Fallback chain mock
        with patch("src.services.ai.utils.llm_helpers.ChatOpenAI") as mock_openai:
            fallback_llm = MagicMock()
            mock_openai.return_value = fallback_llm

            # Fallback chain 구성 mock
            fallback_chain = MagicMock()
            fallback_chain.ainvoke = AsyncMock(
                return_value=AIMessage(content="Fallback response")
            )

            # chain.first 속성 mock (프롬프트 추출용)
            mock_chain.first = ChatPromptTemplate.from_messages(
                [("system", "Test prompt")]
            )

            # __or__ 연산자 mock (prompt | llm)
            mock_chain.first.__or__ = MagicMock(return_value=fallback_chain)

            input_data = {"question": "Test"}

            # When
            result = await call_llm_with_fallback(
                chain=mock_chain,
                input_data=input_data,
                settings=mock_settings,
                max_retries=2,
            )

            # Then
            assert result.content == "Fallback response"
            mock_openai.assert_called_once_with(
                model="gpt-3.5-turbo",
                temperature=0.3,
                timeout=30,
                api_key="test-api-key",
            )

    @pytest.mark.asyncio
    async def test_authentication_error_immediate_failure(
        self, mock_chain, mock_settings
    ):
        """인증 에러 발생 시 즉시 실패 (재시도 없음)"""
        # Given
        mock_chain.ainvoke.side_effect = AuthenticationError("Invalid API key")
        input_data = {"question": "Test"}

        # When & Then
        with pytest.raises(AuthenticationError):
            await call_llm_with_fallback(
                chain=mock_chain,
                input_data=input_data,
                settings=mock_settings,
            )

        # 재시도 없이 1회만 호출
        assert mock_chain.ainvoke.call_count == 1

    @pytest.mark.asyncio
    async def test_fallback_also_fails(self, mock_chain, mock_settings):
        """Primary와 Fallback 모두 실패 시 에러 발생"""
        # Given
        mock_chain.ainvoke.side_effect = APITimeoutError("Timeout")

        with patch("src.services.ai.utils.llm_helpers.ChatOpenAI") as mock_openai:
            fallback_llm = MagicMock()
            mock_openai.return_value = fallback_llm

            fallback_chain = MagicMock()
            fallback_chain.ainvoke = AsyncMock(
                side_effect=APITimeoutError("Fallback timeout")
            )

            mock_chain.first = ChatPromptTemplate.from_messages(
                [("system", "Test prompt")]
            )
            mock_chain.first.__or__ = MagicMock(return_value=fallback_chain)

            input_data = {"question": "Test"}

            # When & Then
            with pytest.raises(APITimeoutError):
                await call_llm_with_fallback(
                    chain=mock_chain,
                    input_data=input_data,
                    settings=mock_settings,
                    max_retries=1,
                )

    @pytest.mark.asyncio
    async def test_max_retries_parameter(self, mock_chain, mock_settings):
        """max_retries 파라미터 동작 검증"""
        # Given
        mock_chain.ainvoke.side_effect = [
            RateLimitError("Rate limit"),
            RateLimitError("Rate limit"),
            RateLimitError("Rate limit"),
            AIMessage(content="Success after 3 retries"),
        ]
        input_data = {"question": "Test"}

        # When
        result = await call_llm_with_fallback(
            chain=mock_chain,
            input_data=input_data,
            settings=mock_settings,
            max_retries=4,  # 4회까지 재시도 허용
        )

        # Then
        assert result.content == "Success after 3 retries"
        assert mock_chain.ainvoke.call_count == 4

    @pytest.mark.asyncio
    async def test_different_retryable_errors(self, mock_chain, mock_settings):
        """다양한 재시도 가능 에러 타입 처리"""
        # Given - 각기 다른 재시도 가능 에러
        mock_chain.ainvoke.side_effect = [
            RateLimitError("Rate limit"),
            APIConnectionError("Connection failed"),
            APITimeoutError("Request timeout"),
            AIMessage(content="Success"),
        ]
        input_data = {"question": "Test"}

        # When
        result = await call_llm_with_fallback(
            chain=mock_chain,
            input_data=input_data,
            settings=mock_settings,
            max_retries=4,
        )

        # Then
        assert result.content == "Success"
        assert mock_chain.ainvoke.call_count == 4
