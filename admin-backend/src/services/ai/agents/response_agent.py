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

    def __init__(self, llm: ChatOpenAI):
        """
        Args:
            llm: LangChain ChatOpenAI 인스턴스
        """
        self.llm = llm
        self.prompt = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        """응답 생성용 프롬프트 템플릿 생성"""
        from src.services.ai.prompts.response_generation import (
            RESPONSE_SYSTEM_PROMPT,
            RESPONSE_USER_TEMPLATE,
        )

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
            max_rows_for_llm = 10
            if len(result_data) > max_rows_for_llm:
                sampled_data = result_data[:max_rows_for_llm]
                data_summary = (
                    f"(처음 {max_rows_for_llm}개 행만 표시, 총 {len(result_data)}개)"
                )
            else:
                sampled_data = result_data
                data_summary = ""

            chain = self.prompt | self.llm
            result = await chain.ainvoke(
                {
                    "question": question,
                    "sql": sql,
                    "result_data": str(sampled_data) + data_summary,
                    "columns": ", ".join(columns),
                    "row_count": len(result_data),
                }
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
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"응답 생성 중 에러 발생: {str(e)}"

            logger.error(
                "response_generation_error",
                extra={
                    "event": "response_generation_error",
                    "error": str(e),
                    "execution_time_ms": execution_time_ms,
                },
            )

            return ResponseGenerationResult(
                success=False,
                error_code="AIBI_RESPONSE_GENERATION_ERROR",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )

    async def _handle_empty_result(self, question: str) -> str:
        """빈 결과에 대한 응답 생성

        Args:
            question: 사용자 질문

        Returns:
            str: 빈 결과에 대한 자연어 응답
        """
        # LLM을 사용하여 더 나은 대안 제안 생성
        try:
            chain = self.prompt | self.llm
            result = await chain.ainvoke(
                {
                    "question": question,
                    "sql": "",
                    "result_data": "[]",
                    "columns": "",
                    "row_count": 0,
                }
            )
            # Extract content from AIMessage or convert to string
            if hasattr(result, "content"):
                return str(result.content)
            else:
                return str(result)

        except Exception as e:
            logger.warning(
                "empty_result_response_fallback",
                extra={
                    "event": "empty_result_response_fallback",
                    "error": str(e),
                },
            )
            # 폴백: 간단한 기본 메시지
            return "조회 결과가 없습니다. 다른 조건으로 다시 조회해 주세요."
