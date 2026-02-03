"""
응답 생성 에이전트.

쿼리 결과를 자연어 요약으로 변환하는 에이전트.
핵심 수치 강조, 비교 정보 포함, 한국어 자연스러운 표현 제공.

Stories: 2-4
FRs: FR-011, FR-013
"""

import time
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.common.logging import get_logger
from src.config.settings import Settings
from src.services.ai.utils.llm_helpers import call_llm_with_fallback

logger = get_logger(__name__)


@dataclass
class ResponseGenerationResult:
    """응답 생성 결과"""

    success: bool
    natural_language_response: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    execution_time_ms: int = 0


class ResponseGenerationAgent:
    """쿼리 결과를 자연어 응답으로 변환하는 에이전트

    LLM을 사용하여 쿼리 결과를 사용자 친화적인 한국어 응답으로 변환합니다.
    """

    def __init__(
        self, llm: ChatOpenAI, settings: Settings, max_sample_rows: int = 10
    ):
        """
        Args:
            llm: LangChain ChatOpenAI 인스턴스
            settings: 애플리케이션 설정 (폴백 LLM 등)
            max_sample_rows: LLM에 전달할 최대 행 수 (기본값: 10)
        """
        self.llm = llm
        self.settings = settings
        self.max_sample_rows = max_sample_rows
        self.prompt = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        """응답 생성용 프롬프트 템플릿 생성"""
        from src.services.ai.prompts.response_generation import (
            PROMPT_VERSION,
            RESPONSE_SYSTEM_PROMPT,
            RESPONSE_USER_TEMPLATE,
        )

        self.prompt_version = PROMPT_VERSION
        return ChatPromptTemplate.from_messages(
            [
                ("system", RESPONSE_SYSTEM_PROMPT),
                ("user", RESPONSE_USER_TEMPLATE),
            ]
        )

    async def generate_response(
        self,
        question: str,
        sql: str,
        result_data: list[dict],
        columns: list[str],
    ) -> ResponseGenerationResult:
        """쿼리 결과를 자연어 응답으로 변환

        Args:
            question: 사용자 질문
            sql: 실행된 SQL 쿼리
            result_data: 쿼리 결과 데이터
            columns: 결과 컬럼 목록

        Returns:
            ResponseGenerationResult: 응답 생성 결과
        """
        start_time = time.time()

        try:
            # 빈 결과 처리
            if not result_data or len(result_data) == 0:
                response = await self._handle_empty_result(question)
                return ResponseGenerationResult(
                    success=True,
                    natural_language_response=response,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # LLM 호출하여 자연어 응답 생성
            # 대용량 데이터는 샘플만 전달 (토큰 제한 고려)
            if len(result_data) > self.max_sample_rows:
                sampled_data = result_data[: self.max_sample_rows]
                data_summary = (
                    f"(처음 {self.max_sample_rows}개 행만 표시, 총 {len(result_data)}개)"
                )
            else:
                sampled_data = result_data
                data_summary = ""

            chain = self.prompt | self.llm
            input_data = {
                "question": question,
                "sql": sql,
                "result_data": str(sampled_data) + data_summary,
                "columns": ", ".join(columns),
                "row_count": len(result_data),
            }

            # Project Context LLM Call Pattern 적용: call_llm_with_fallback 사용
            result = await call_llm_with_fallback(
                chain=chain,
                input_data=input_data,
                settings=self.settings,
                agent_name="response_generation",
            )

            # Extract content from AIMessage or convert to string
            if hasattr(result, "content"):
                response_text = str(result.content)
            else:
                response_text = str(result)

            execution_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "response_generated",
                extra={
                    "event": "response_generated",
                    "execution_time_ms": execution_time_ms,
                    "result_length": len(result_data),
                    "response_length": len(response_text),
                    "prompt_version": self.prompt_version,
                },
            )

            return ResponseGenerationResult(
                success=True,
                natural_language_response=response_text,
                execution_time_ms=execution_time_ms,
            )

        except TimeoutError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"LLM 호출 타임아웃: {str(e)}"

            logger.error(
                "response_generation_timeout",
                extra={
                    "event": "response_generation_timeout",
                    "error": str(e),
                    "execution_time_ms": execution_time_ms,
                },
            )

            return ResponseGenerationResult(
                success=False,
                error_code="AIBI_RESPONSE_TIMEOUT",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            # OpenAI API 특정 에러 처리
            from openai import (
                APIConnectionError,
                APITimeoutError,
                AuthenticationError,
                RateLimitError,
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            # 에러 타입별 세분화 처리
            if isinstance(e, RateLimitError):
                error_code = "AIBI_RATE_LIMIT_EXCEEDED"
                error_msg = "LLM API 요청 한도를 초과했습니다."
                event = "response_generation_rate_limit"
            elif isinstance(e, APIConnectionError):
                error_code = "AIBI_API_CONNECTION_ERROR"
                error_msg = "LLM API 연결에 실패했습니다."
                event = "response_generation_connection_error"
            elif isinstance(e, APITimeoutError):
                error_code = "AIBI_API_TIMEOUT"
                error_msg = "LLM API 응답 시간이 초과되었습니다."
                event = "response_generation_api_timeout"
            elif isinstance(e, AuthenticationError):
                error_code = "AIBI_API_AUTH_ERROR"
                error_msg = "LLM API 인증에 실패했습니다."
                event = "response_generation_auth_error"
            else:
                error_code = "AIBI_RESPONSE_GENERATION_ERROR"
                error_msg = f"응답 생성 중 에러 발생: {str(e)}"
                event = "response_generation_error"

            logger.error(
                event,
                extra={
                    "event": event,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": execution_time_ms,
                },
            )

            return ResponseGenerationResult(
                success=False,
                error_code=error_code,
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )

    async def _handle_empty_result(self, question: str) -> str:
        """빈 결과에 대한 응답 생성

        비용 절감을 위해 템플릿 기반 메시지를 사용하고,
        필요한 경우에만 LLM을 호출합니다.

        Args:
            question: 사용자 질문

        Returns:
            str: 빈 결과에 대한 자연어 응답
        """
        # 간단한 템플릿 기반 메시지 (LLM 호출 없이)
        # 비용 절감 및 응답 속도 개선
        # 프롬프트 예시와 일관성 유지
        return (
            "조회 결과가 없습니다. "
            "해당 기간의 데이터가 없거나 다른 조건으로 조회해보시는 건 어떨까요?"
        )
