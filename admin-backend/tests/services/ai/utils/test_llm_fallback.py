"""
LLM Fallback Manager 테스트.

Stories: STORY-6-1
FRs: FR29, NFR-R2, AR10
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from src.services.ai.utils.llm_fallback import (
    LLMFallbackManager,
    LLMConfig,
    LLMAllModelsFailedError,
)
from src.services.ai.utils.circuit_breaker import CircuitBreakerOpenError


@pytest.fixture
def llm_configs():
    """테스트용 LLM 설정"""
    primary = LLMConfig(
        model="gpt-4o-mini",
        api_key="test-key",
        temperature=0,
        timeout=10,
        max_retries=2
    )
    fallback = LLMConfig(
        model="gpt-3.5-turbo",
        api_key="test-key",
        temperature=0,
        timeout=10,
        max_retries=2
    )
    return primary, fallback


@pytest.fixture
def mock_llm():
    """Mock LLM 인스턴스"""
    with patch("src.services.ai.utils.llm_fallback.ChatOpenAI") as mock:
        yield mock


class TestLLMFallbackManagerInitialization:
    """LLM Fallback Manager 초기화 테스트"""

    def test_initialization_with_configs(self, llm_configs, mock_llm):
        """설정으로 초기화 성공"""
        primary, fallback = llm_configs
        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        assert manager.primary == primary
        assert manager.fallbacks == [fallback]
        assert len(manager._circuit_breakers) == 2
        assert len(manager._llms) == 2

    def test_creates_circuit_breakers_for_each_model(self, llm_configs, mock_llm):
        """각 모델마다 Circuit Breaker 생성"""
        primary, fallback = llm_configs
        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        assert "gpt-4o-mini" in manager._circuit_breakers
        assert "gpt-3.5-turbo" in manager._circuit_breakers


class TestLLMFallbackManagerPrimarySuccess:
    """Primary LLM 성공 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_primary_success_returns_result(self, llm_configs, mock_llm):
        """Primary 모델 성공 시 결과 반환"""
        primary, fallback = llm_configs

        # Mock LLM 응답
        mock_instance = MagicMock()
        mock_instance.ainvoke = AsyncMock(return_value=AIMessage(content="test response"))
        mock_llm.return_value = mock_instance

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        messages = [{"role": "user", "content": "test"}]
        result = await manager.invoke(messages)

        assert result.content == "test response"
        assert mock_instance.ainvoke.call_count == 1

    @pytest.mark.asyncio
    async def test_primary_success_does_not_call_fallback(self, llm_configs, mock_llm):
        """Primary 성공 시 Fallback 호출 안 함"""
        primary, fallback = llm_configs

        call_count = {"primary": 0, "fallback": 0}

        def create_mock_llm(model):
            instance = MagicMock()
            async def mock_invoke(*args, **kwargs):
                if model == "gpt-4o-mini":
                    call_count["primary"] += 1
                else:
                    call_count["fallback"] += 1
                return AIMessage(content=f"response from {model}")
            instance.ainvoke = mock_invoke
            return instance

        mock_llm.side_effect = lambda model, **kwargs: create_mock_llm(model)

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        messages = [{"role": "user", "content": "test"}]
        result = await manager.invoke(messages)

        assert call_count["primary"] == 1
        assert call_count["fallback"] == 0


class TestLLMFallbackManagerFallbackScenarios:
    """Fallback 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_primary_failure_triggers_fallback(self, llm_configs, mock_llm):
        """Primary 실패 시 Fallback 시도"""
        primary, fallback = llm_configs

        call_sequence = []

        def create_mock_llm(model):
            instance = MagicMock()
            async def mock_invoke(*args, **kwargs):
                call_sequence.append(model)
                if model == "gpt-4o-mini":
                    raise Exception("Primary failed")
                return AIMessage(content="fallback response")
            instance.ainvoke = mock_invoke
            return instance

        mock_llm.side_effect = lambda model, **kwargs: create_mock_llm(model)

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        messages = [{"role": "user", "content": "test"}]

        # Circuit Breaker threshold 미만으로 실패
        with patch.object(manager._circuit_breakers["gpt-4o-mini"], "call") as mock_cb:
            mock_cb.side_effect = Exception("Primary failed")

            with patch.object(manager._circuit_breakers["gpt-3.5-turbo"], "call") as mock_fallback_cb:
                mock_fallback_cb.return_value = AIMessage(content="fallback response")

                result = await manager.invoke(messages)

        assert result.content == "fallback response"

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_skips_to_fallback(self, llm_configs, mock_llm):
        """Circuit Breaker OPEN 시 Fallback으로 즉시 전환"""
        primary, fallback = llm_configs

        def create_mock_llm(model):
            instance = MagicMock()
            async def mock_invoke(*args, **kwargs):
                return AIMessage(content=f"response from {model}")
            instance.ainvoke = mock_invoke
            return instance

        mock_llm.side_effect = lambda model, **kwargs: create_mock_llm(model)

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        messages = [{"role": "user", "content": "test"}]

        # Primary Circuit Breaker를 OPEN 상태로 설정
        with patch.object(manager._circuit_breakers["gpt-4o-mini"], "call") as mock_primary_cb:
            mock_primary_cb.side_effect = CircuitBreakerOpenError("Circuit is open")

            with patch.object(manager._circuit_breakers["gpt-3.5-turbo"], "call") as mock_fallback_cb:
                mock_fallback_cb.return_value = AIMessage(content="fallback response")

                result = await manager.invoke(messages)

        assert result.content == "fallback response"

    @pytest.mark.asyncio
    async def test_all_models_fail_raises_error(self, llm_configs, mock_llm):
        """모든 모델 실패 시 에러 발생"""
        primary, fallback = llm_configs

        def create_mock_llm(model):
            instance = MagicMock()
            async def mock_invoke(*args, **kwargs):
                raise Exception(f"{model} failed")
            instance.ainvoke = mock_invoke
            return instance

        mock_llm.side_effect = lambda model, **kwargs: create_mock_llm(model)

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        messages = [{"role": "user", "content": "test"}]

        with patch.object(manager._circuit_breakers["gpt-4o-mini"], "call") as mock_primary:
            mock_primary.side_effect = Exception("Primary failed")

            with patch.object(manager._circuit_breakers["gpt-3.5-turbo"], "call") as mock_fallback:
                mock_fallback.side_effect = Exception("Fallback failed")

                with pytest.raises(LLMAllModelsFailedError):
                    await manager.invoke(messages)


class TestLLMFallbackManagerMultipleFallbacks:
    """다중 Fallback 테스트"""

    @pytest.mark.asyncio
    async def test_tries_all_fallbacks_in_order(self, mock_llm):
        """Fallback을 순서대로 시도"""
        primary = LLMConfig(model="gpt-4o-mini", api_key="test")
        fallback1 = LLMConfig(model="gpt-3.5-turbo", api_key="test")
        fallback2 = LLMConfig(model="gpt-3.5-turbo-16k", api_key="test")

        call_sequence = []

        def create_mock_llm(model):
            instance = MagicMock()
            async def mock_invoke(*args, **kwargs):
                call_sequence.append(model)
                if model == "gpt-3.5-turbo-16k":
                    return AIMessage(content="final fallback")
                raise Exception(f"{model} failed")
            instance.ainvoke = mock_invoke
            return instance

        mock_llm.side_effect = lambda model, **kwargs: create_mock_llm(model)

        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback1, fallback2]
        )

        messages = [{"role": "user", "content": "test"}]

        with patch.object(manager._circuit_breakers["gpt-4o-mini"], "call") as mock1:
            mock1.side_effect = Exception("Primary failed")

            with patch.object(manager._circuit_breakers["gpt-3.5-turbo"], "call") as mock2:
                mock2.side_effect = Exception("Fallback1 failed")

                with patch.object(manager._circuit_breakers["gpt-3.5-turbo-16k"], "call") as mock3:
                    mock3.return_value = AIMessage(content="final fallback")

                    result = await manager.invoke(messages)

        assert result.content == "final fallback"


class TestLLMFallbackManagerStatistics:
    """통계 기능 테스트"""

    def test_get_all_stats_returns_all_circuit_breakers(self, llm_configs, mock_llm):
        """모든 Circuit Breaker 통계 반환"""
        primary, fallback = llm_configs
        manager = LLMFallbackManager(
            primary_config=primary,
            fallback_configs=[fallback]
        )

        stats = manager.get_all_stats()

        assert "gpt-4o-mini" in stats
        assert "gpt-3.5-turbo" in stats
        assert stats["gpt-4o-mini"]["state"] == "closed"
        assert stats["gpt-3.5-turbo"]["state"] == "closed"
