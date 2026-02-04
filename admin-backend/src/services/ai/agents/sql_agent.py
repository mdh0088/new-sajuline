"""
MariaDB Text-to-SQL 에이전트.

자연어 질의를 SQL로 변환합니다.

Stories: AI-002, STORY-6-1
FRs: FR-011, FR-012, FR-013, FR29
"""

import time
from dataclasses import dataclass
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.common.logging import get_logger
from src.config.settings import Settings
from src.services.ai.utils.llm_fallback import (
    LLMFallbackManager,
    LLMConfig,
    LLMAllModelsFailedError,
)
from src.services.ai.utils.graceful_degradation import (
    GracefulDegradationManager,
    DegradationLevel,
)

logger = get_logger(__name__)


@dataclass
class SQLGenerationResult:
    """SQL 생성 결과"""

    success: bool
    sql: Optional[str]
    error: Optional[str]
    metadata: dict


class SQLGenerationAgent:
    """자연어를 SQL로 변환하는 에이전트

    OpenAI gpt-4o-mini를 사용하여 관리자의 자연어 질문을
    유효한 SELECT SQL 문으로 변환합니다.

    Attributes:
        llm: LangChain ChatOpenAI 인스턴스
        prompt: SQL 생성을 위한 프롬프트 템플릿
        chain: LLM 실행 체인
    """

    def __init__(self, settings: Settings):
        """SQL Generation Agent 초기화

        Args:
            settings: 애플리케이션 설정
        """
        self.settings = settings

        # LLM Fallback Manager 초기화 (gpt-4o-mini → gpt-3.5-turbo)
        primary_config = LLMConfig(
            model=settings.ai_llm_model,  # gpt-4o-mini
            api_key=settings.openai_api_key,
            temperature=0,
            timeout=settings.ai_llm_timeout,
            max_retries=2,
        )

        fallback_config = LLMConfig(
            model=getattr(settings, "ai_llm_fallback_model", "gpt-3.5-turbo"),
            api_key=settings.openai_api_key,
            temperature=0,
            timeout=settings.ai_llm_timeout,
            max_retries=2,
        )

        self.llm_manager = LLMFallbackManager(
            primary_config=primary_config,
            fallback_configs=[fallback_config],
        )

        # Graceful Degradation Manager 초기화
        self.degradation_manager = GracefulDegradationManager()

        # 프롬프트 템플릿 구성
        self.prompt = self._build_prompt()

        # 기존 LLM (호환성 유지, 실제로는 llm_manager 사용)
        self.llm = self.llm_manager.get_primary_llm()

        # LLM 실행 체인 구성 (prompt → llm → parser)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _build_prompt(self) -> ChatPromptTemplate:
        """SQL 생성을 위한 프롬프트 템플릿 구성

        Returns:
            ChatPromptTemplate: 시스템 프롬프트와 사용자 입력을 포함한 템플릿
        """
        from src.services.ai.prompts.sql_generation import SQL_SYSTEM_PROMPT

        return ChatPromptTemplate.from_messages(
            [
                ("system", SQL_SYSTEM_PROMPT),
                ("user", "{question}"),
            ]
        )

    async def generate_sql(
        self, question: str, schema_info: str, allowed_tables: list[str]
    ) -> SQLGenerationResult:
        """자연어 질문을 SQL로 변환

        Args:
            question: 사용자의 자연어 질문
            schema_info: 데이터베이스 스키마 정보 (Markdown 형식)
            allowed_tables: 허용된 테이블 목록

        Returns:
            SQLGenerationResult: SQL 생성 결과 (성공/실패, SQL, 에러 메시지, 메타데이터)

        Examples:
            >>> agent = SQLGenerationAgent(settings)
            >>> result = await agent.generate_sql(
            ...     question="오늘 가입한 사용자 조회",
            ...     schema_info="TABLE users (id INT, created_at DATETIME)",
            ...     allowed_tables=["users"]
            ... )
            >>> print(result.sql)
            'SELECT * FROM users WHERE DATE(created_at) = CURDATE() LIMIT 100'
        """
        start_time = time.time()

        # 빈 질문 검증
        if not question or not question.strip():
            return SQLGenerationResult(
                success=False,
                sql=None,
                error="질문이 비어있습니다",
                metadata={
                    "agent": "sql_generation_agent",
                    "duration_ms": 0,
                    "timestamp": time.time(),
                },
            )

        try:
            # 프롬프트 메시지 구성
            messages = self.prompt.format_messages(
                question=question,
                schema_info=schema_info,
                allowed_tables=", ".join(allowed_tables),
                current_date=time.strftime("%Y-%m-%d"),
            )

            # LLM Fallback Manager를 통한 호출
            llm_response = await self.llm_manager.invoke(messages)

            # 응답 파싱
            response = llm_response.content

            # 마크다운 코드 블록 제거
            sql = self._clean_sql_response(response)

            duration_ms = int((time.time() - start_time) * 1000)

            # 성공 로깅
            logger.info(
                "llm_sql_generation_success",
                extra={
                    "event": "llm_sql_generation",
                    "agent": "sql_generation_agent",
                    "question": question[:50],  # 민감정보 보호: 처음 50자만
                    "sql_length": len(sql),
                    "duration_ms": duration_ms,
                    "model": self.settings.ai_llm_model,
                },
            )

            # 성공 시 FULL 레벨 유지
            self.degradation_manager.set_level(DegradationLevel.FULL)

            return SQLGenerationResult(
                success=True,
                sql=sql,
                error=None,
                metadata={
                    "agent": "sql_generation_agent",
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "model": self.settings.ai_llm_model,
                    "degradation_level": self.degradation_manager.current_level.name,
                },
            )

        except LLMAllModelsFailedError as e:
            # 모든 LLM 모델 실패 시 Degradation 레벨 설정
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = "모든 LLM 모델이 실패했습니다"

            self.degradation_manager.set_level(DegradationLevel.CACHED)

            logger.error(
                "llm_all_models_failed",
                extra={
                    "event": "llm_all_models_failed",
                    "agent": "sql_generation_agent",
                    "error": str(e),
                    "question": question[:50],
                    "duration_ms": duration_ms,
                    "degradation_level": self.degradation_manager.current_level.name,
                },
                exc_info=True,
            )

            return SQLGenerationResult(
                success=False,
                sql=None,
                error=error_msg,
                metadata={
                    "agent": "sql_generation_agent",
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "degradation_level": self.degradation_manager.current_level.name,
                },
            )

        except (TimeoutError, Exception) as e:
            # TimeoutError, asyncio.TimeoutError, httpx 타임아웃 모두 처리
            if "timeout" in str(e).lower() or isinstance(e, TimeoutError):
                duration_ms = int((time.time() - start_time) * 1000)
                error_msg = "LLM 호출 시간 초과 (10초)"

                logger.error(
                    "llm_sql_generation_timeout",
                    extra={
                        "event": "llm_sql_generation_error",
                        "agent": "sql_generation_agent",
                        "error": error_msg,
                        "question": question[:50],  # 민감정보 보호: 처음 50자만
                        "duration_ms": duration_ms,
                    },
                    exc_info=True,
                )

                return SQLGenerationResult(
                    success=False,
                    sql=None,
                    error=error_msg,
                    metadata={
                        "agent": "sql_generation_agent",
                        "duration_ms": duration_ms,
                        "timestamp": time.time(),
                    },
                )
            # 타임아웃 아닌 다른 예외는 아래로 전파
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"SQL 생성 중 오류 발생: {str(e)}"

            logger.error(
                "llm_sql_generation_error",
                extra={
                    "event": "llm_sql_generation_error",
                    "agent": "sql_generation_agent",
                    "error": error_msg,
                    "question": question[:50],  # 민감정보 보호: 처음 50자만
                    "duration_ms": duration_ms,
                },
                exc_info=True,
            )

            return SQLGenerationResult(
                success=False,
                sql=None,
                error=error_msg,
                metadata={
                    "agent": "sql_generation_agent",
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                },
            )

    def _clean_sql_response(self, response: str) -> str:
        """LLM 응답에서 순수 SQL만 추출

        LLM이 마크다운 코드 블록(```sql ... ```)으로 감싸서 반환하는 경우
        이를 제거하고 순수 SQL만 추출합니다.

        Args:
            response: LLM 응답 문자열

        Returns:
            str: 정제된 SQL 문자열
        """
        import re

        sql = response.strip()

        # 정규식으로 마크다운 코드 블록 제거 (sql, SQL, mysql 등 모두 처리)
        pattern = r"^```(?:sql|SQL|mysql|MySQL)?\s*\n?(.+?)```$"
        match = re.match(pattern, sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()

        return sql
