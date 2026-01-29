"""
LangChain RAG 체인 빌더

Story 2.4 Task 4: LangChain 체인 빌더 구현 (AC: 1, 2, 3)
- 다중 LLM 지원: OpenAI, Anthropic (Claude), Google (Gemini)
- 환경 변수 LLM_PROVIDER로 모델 선택
- PromptTemplate + RunnableSequence 구성
- JSON 응답 파싱 로직 (Pydantic 검증)
- 재시도 로직 (1회, max_retries)

⚠️ LangChain 1.2.7 기반 구현 (2026-01 최신 안정 버전)
   공식 문서: https://python.langchain.com/docs/
"""
from typing import Any, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.core.prompts import FORTUNE_SYSTEM_PROMPT, FORTUNE_USER_PROMPT_TEMPLATE
from src.schemas.fortune_schema import LLMFortuneOutput
from src.config.settings import settings
from src.common.logging import logger, get_logger_with_request_id


LLMProvider = Literal["openai", "anthropic", "google"]


def create_llm(provider: LLMProvider) -> BaseChatModel:
    """
    LLM 프로바이더에 따라 적절한 ChatModel 인스턴스 생성

    Args:
        provider: LLM 프로바이더 ("openai" | "anthropic" | "google")

    Returns:
        BaseChatModel: LangChain 호환 Chat 모델

    Raises:
        ValueError: 지원하지 않는 프로바이더
        ImportError: 해당 프로바이더 패키지 미설치
    """
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            timeout=10,
            max_retries=1,
            api_key=settings.openai_api_key,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.anthropic_model,
            temperature=0.7,
            timeout=10,
            max_retries=1,
            api_key=settings.anthropic_api_key,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.google_model,
            temperature=0.7,
            timeout=10,
            max_retries=1,
            google_api_key=settings.google_api_key,
        )

    else:
        raise ValueError(f"지원하지 않는 LLM 프로바이더: {provider}")


class DailyFortuneChain:
    """
    LangChain RAG 체인 빌더 (LangChain 1.x)

    사주 데이터를 기반으로 LLM에게 운세를 생성하도록 요청합니다.
    타임아웃 10초, 자동 재시도 1회가 설정되어 있습니다.

    지원 LLM:
    - OpenAI: gpt-4o-mini, gpt-4, etc.
    - Anthropic: claude-sonnet-4-20250514, claude-3-5-haiku, etc.
    - Google: gemini-2.0-flash, gemini-1.5-pro, etc.
    """

    def __init__(self, provider: LLMProvider | None = None) -> None:
        """
        체인 초기화

        Args:
            provider: LLM 프로바이더 (기본값: 환경 변수 LLM_PROVIDER)

        - ChatModel: 환경 변수에 따라 선택
        - PydanticOutputParser: LLMFortuneOutput 스키마로 파싱
        - ChatPromptTemplate: 시스템 + 사용자 프롬프트 구성
        """
        self.provider = provider or settings.llm_provider
        self.llm = create_llm(self.provider)

        self.parser = PydanticOutputParser(pydantic_object=LLMFortuneOutput)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", FORTUNE_SYSTEM_PROMPT),
            ("human", FORTUNE_USER_PROMPT_TEMPLATE),
        ])

        # RunnableSequence: prompt -> llm -> parser
        self.chain = self.prompt | self.llm | self.parser

    async def generate_fortune(
        self,
        ilgan: str,
        ilgan_oheng: str,
        ilgan_yin_yang: str,
        day_gan: str,
        day_ji: str,
        sipsung: str,
        sipsung_interpretation: str,
        jiji_relation: str,
        jiji_interpretation: str,
        today: str,
    ) -> LLMFortuneOutput:
        """
        운세 생성

        Args:
            ilgan: 사용자 일간 (갑, 을, 병, ...)
            ilgan_oheng: 일간의 오행 (목, 화, 토, 금, 수)
            ilgan_yin_yang: 일간의 음양 (양, 음)
            day_gan: 오늘 천간
            day_ji: 오늘 지지
            sipsung: 십성 관계 (비견, 겁재, 식신, ...)
            sipsung_interpretation: 십성 해석 텍스트
            jiji_relation: 지지 관계 설명 (예: "자 ↔ 축 = 합")
            jiji_interpretation: 지지 관계 해석 텍스트
            today: 오늘 날짜 (ISO format)

        Returns:
            LLMFortuneOutput: 파싱된 운세 결과

        Raises:
            Exception: LLM 호출 실패 시 (재시도 포함 최대 2회 실패)
        """
        log = get_logger_with_request_id()

        log.info(
            "Generating fortune with LLM",
            provider=self.provider,
            model=self._get_model_name(),
            ilgan=ilgan,
            sipsung=sipsung,
            today=today
        )

        try:
            result = await self.chain.ainvoke({
                "ilgan": ilgan,
                "ilgan_oheng": ilgan_oheng,
                "ilgan_yin_yang": ilgan_yin_yang,
                "day_gan": day_gan,
                "day_ji": day_ji,
                "sipsung": sipsung,
                "sipsung_interpretation": sipsung_interpretation,
                "jiji_relation": jiji_relation,
                "jiji_interpretation": jiji_interpretation,
                "today": today,
            })

            log.info(
                "Fortune generated successfully",
                provider=self.provider,
                ilgan=ilgan,
                has_lucky_color=result.lucky_color is not None,
                has_lucky_number=result.lucky_number is not None
            )

            return result

        except Exception as e:
            log.error(
                "LLM fortune generation failed",
                provider=self.provider,
                error=str(e),
                ilgan=ilgan,
                sipsung=sipsung
            )
            raise

    def _get_model_name(self) -> str:
        """현재 프로바이더의 모델명 반환"""
        if self.provider == "openai":
            return settings.openai_model
        elif self.provider == "anthropic":
            return settings.anthropic_model
        elif self.provider == "google":
            return settings.google_model
        return "unknown"

    def get_chain_info(self) -> dict[str, Any]:
        """
        체인 구성 정보 반환 (디버깅용)

        Returns:
            dict: 체인 구성 정보
        """
        return {
            "provider": self.provider,
            "model": self._get_model_name(),
            "temperature": 0.7,
            "timeout": 10,
            "max_retries": 1,
            "output_schema": "LLMFortuneOutput",
        }
