"""
LLM 호출 헬퍼 함수.

프로젝트 표준 LLM Call Pattern을 구현합니다.
폴백 메커니즘과 재시도 로직을 제공하여 안정성을 보장합니다.

Stories: 2-4
Reference: _bmad-output/project-context.md#LLM-Call-Pattern
"""

import asyncio
import time
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from src.common.logging import get_logger
from src.config.settings import Settings

logger = get_logger(__name__)


async def call_llm_with_fallback(
    chain: Runnable,
    input_data: dict[str, Any],
    settings: Settings,
    agent_name: str = "unknown",
    max_retries: int = 2,
) -> Any:
    """프라이머리 LLM 호출 및 실패 시 폴백 LLM 사용

    Args:
        chain: LangChain Runnable (프롬프트 | LLM)
        input_data: 프롬프트 입력 데이터
        settings: 애플리케이션 설정
        agent_name: 에이전트 이름 (로깅용)
        max_retries: 최대 재시도 횟수 (기본값: 2)

    Returns:
        LLM 응답 (AIMessage 또는 str)

    Raises:
        Exception: 모든 재시도 및 폴백이 실패한 경우
    """
    start_time = time.time()
    retry_count = 0
    last_error = None

    # Primary LLM 시도 (재시도 포함)
    while retry_count < max_retries:
        try:
            logger.info(
                "llm_call_attempt",
                extra={
                    "event": "llm_call_attempt",
                    "agent": agent_name,
                    "model": settings.ai_llm_model,
                    "retry": retry_count,
                    "attempt_type": "primary",
                },
            )

            result = await chain.ainvoke(input_data)
            execution_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "llm_call_success",
                extra={
                    "event": "llm_call_success",
                    "agent": agent_name,
                    "model": settings.ai_llm_model,
                    "execution_time_ms": execution_time_ms,
                    "attempt_type": "primary",
                    "retries": retry_count,
                },
            )

            return result

        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            # 재시도 가능한 에러
            last_error = e
            retry_count += 1

            logger.warning(
                "llm_call_retry",
                extra={
                    "event": "llm_call_retry",
                    "agent": agent_name,
                    "model": settings.ai_llm_model,
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "retry": retry_count,
                    "max_retries": max_retries,
                },
            )

            # 재시도 전 대기 (exponential backoff)
            if retry_count < max_retries:
                wait_time = 2**retry_count  # 1초, 2초, 4초...
                await asyncio.sleep(wait_time)

        except AuthenticationError as e:
            # 재시도 불가능한 에러 - 즉시 실패
            logger.error(
                "llm_call_auth_error",
                extra={
                    "event": "llm_call_auth_error",
                    "agent": agent_name,
                    "model": settings.ai_llm_model,
                    "error": str(e),
                },
            )
            raise

        except Exception as e:
            # 기타 예외는 즉시 실패
            last_error = e
            logger.error(
                "llm_call_unexpected_error",
                extra={
                    "event": "llm_call_unexpected_error",
                    "agent": agent_name,
                    "model": settings.ai_llm_model,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            raise

    # Primary LLM 모든 재시도 실패 - Fallback LLM 시도
    logger.warning(
        "llm_call_fallback_attempt",
        extra={
            "event": "llm_call_fallback_attempt",
            "agent": agent_name,
            "primary_model": settings.ai_llm_model,
            "fallback_model": settings.ai_llm_fallback_model,
            "primary_retries": max_retries,
        },
    )

    try:
        # Fallback LLM 인스턴스 생성
        fallback_llm = ChatOpenAI(
            model=settings.ai_llm_fallback_model,
            temperature=0.3,
            timeout=settings.ai_llm_timeout,
            api_key=settings.openai_api_key,
        )

        # Chain 재구성 (프롬프트는 유지, LLM만 교체)
        # chain은 (prompt | llm) 형태이므로 첫 번째 컴포넌트(프롬프트)를 추출
        if hasattr(chain, "first") and hasattr(chain.first, "to_messages"):
            prompt = chain.first
            fallback_chain = prompt | fallback_llm
        else:
            # Chain 구조가 다른 경우 전체 chain 사용 (LLM만 교체)
            fallback_chain = chain.first | fallback_llm if hasattr(chain, "first") else chain | fallback_llm

        result = await fallback_chain.ainvoke(input_data)
        execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "llm_call_fallback_success",
            extra={
                "event": "llm_call_fallback_success",
                "agent": agent_name,
                "fallback_model": settings.ai_llm_fallback_model,
                "execution_time_ms": execution_time_ms,
            },
        )

        return result

    except Exception as fallback_error:
        # Fallback도 실패 - 최종 실패
        execution_time_ms = int((time.time() - start_time) * 1000)

        logger.error(
            "llm_call_complete_failure",
            extra={
                "event": "llm_call_complete_failure",
                "agent": agent_name,
                "primary_model": settings.ai_llm_model,
                "fallback_model": settings.ai_llm_fallback_model,
                "primary_error": str(last_error),
                "fallback_error": str(fallback_error),
                "execution_time_ms": execution_time_ms,
            },
        )

        # Primary 에러를 우선적으로 raise (더 의미있는 에러)
        raise last_error if last_error else fallback_error
