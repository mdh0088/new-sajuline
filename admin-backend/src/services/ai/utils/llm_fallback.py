"""
LLM Fallback Manager.

Primary 모델 실패 시 자동으로 Fallback 모델로 전환합니다.
각 모델별 Circuit Breaker로 장애를 추적하고 복구를 관리합니다.

Stories: STORY-6-1
FRs: FR29, NFR-R2, AR10
"""
from dataclasses import dataclass
from typing import List, Any
from langchain_openai import ChatOpenAI
import logging

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError
)

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 설정"""
    model: str
    api_key: str
    temperature: float = 0
    timeout: int = 10
    max_retries: int = 2


class LLMFallbackManager:
    """
    LLM Fallback 관리자.

    Primary 모델 실패 시 자동으로 Fallback 모델로 전환하고,
    Circuit Breaker 패턴으로 장애 복구를 관리합니다.

    Example:
        >>> primary = LLMConfig(model="gpt-4o-mini", api_key="key")
        >>> fallback = LLMConfig(model="gpt-3.5-turbo", api_key="key")
        >>> manager = LLMFallbackManager(primary, [fallback])
        >>> response = await manager.invoke(messages)
    """

    def __init__(
        self,
        primary_config: LLMConfig,
        fallback_configs: List[LLMConfig],
        circuit_breaker_config: CircuitBreakerConfig | None = None
    ):
        """
        LLM Fallback Manager 초기화.

        Args:
            primary_config: Primary LLM 설정
            fallback_configs: Fallback LLM 설정 리스트
            circuit_breaker_config: Circuit Breaker 설정
        """
        self.primary = primary_config
        self.fallbacks = fallback_configs
        self.cb_config = circuit_breaker_config or CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=3,
            timeout=30.0
        )

        # 각 모델별 Circuit Breaker
        self._circuit_breakers = {
            config.model: CircuitBreaker(
                name=f"llm_{config.model}",
                config=self.cb_config
            )
            for config in [primary_config] + fallback_configs
        }

        # LLM 인스턴스 생성
        self._llms = {
            config.model: self._create_llm(config)
            for config in [primary_config] + fallback_configs
        }

    def _create_llm(self, config: LLMConfig) -> ChatOpenAI:
        """
        LLM 인스턴스 생성.

        Args:
            config: LLM 설정

        Returns:
            ChatOpenAI 인스턴스
        """
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    async def invoke(
        self,
        messages: List[dict],
        **kwargs
    ) -> Any:
        """
        Fallback 지원 LLM 호출.

        Primary 모델부터 시도하고, 실패 시 Fallback 모델을 순서대로 시도합니다.

        Args:
            messages: LLM에 전달할 메시지 리스트
            **kwargs: 추가 LLM 파라미터

        Returns:
            LLM 응답

        Raises:
            LLMAllModelsFailedError: 모든 모델이 실패한 경우
        """
        all_configs = [self.primary] + self.fallbacks
        last_error = None

        for i, config in enumerate(all_configs):
            llm = self._llms[config.model]
            cb = self._circuit_breakers[config.model]

            try:
                result = await cb.call(
                    llm.ainvoke,
                    messages,
                    **kwargs
                )

                # Fallback 사용 시 로깅
                if i > 0:
                    logger.info(
                        f"LLM fallback success: primary={self.primary.model}, "
                        f"fallback={config.model}, level={i}"
                    )

                return result

            except CircuitBreakerOpenError as e:
                logger.warning(
                    f"Circuit breaker open for model {config.model}: {str(e)}"
                )
                last_error = e
                continue

            except Exception as e:
                logger.error(
                    f"LLM call failed for model {config.model}: {str(e)}, level={i}"
                )
                last_error = e
                continue

        # 모든 모델 실패
        raise LLMAllModelsFailedError(
            f"All LLM models failed. Last error: {last_error}"
        )

    def get_all_stats(self) -> dict:
        """
        모든 Circuit Breaker 상태 조회.

        Returns:
            모델별 Circuit Breaker 통계
        """
        return {
            model: cb.get_stats()
            for model, cb in self._circuit_breakers.items()
        }

    def get_primary_llm(self) -> ChatOpenAI:
        """
        Primary LLM 인스턴스 조회.

        Returns:
            Primary LLM 인스턴스
        """
        return self._llms[self.primary.model]


class LLMAllModelsFailedError(Exception):
    """모든 LLM 모델이 실패했을 때 발생하는 예외"""
    pass
