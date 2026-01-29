"""
LangChain RAG 체인 단위 테스트

Story 2.4 Task 8: DailyFortuneChain 테스트 (AC: 2)
- LLM Mock 테스트 (정상 응답)
- 타임아웃/에러 테스트
- JSON 파싱 테스트
- 다중 프로바이더 테스트 (OpenAI, Anthropic, Google)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import date

from src.core.langchain_chain import DailyFortuneChain, create_llm, LLMProvider
from src.schemas.fortune_schema import LLMFortuneOutput


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI 정상 응답 데이터"""
    return LLMFortuneOutput(
        overall="오늘은 창의적인 에너지가 넘칩니다. 새로운 아이디어가 떠오르는 하루가 될 것입니다.",
        love="연인과 함께하는 시간이 행복합니다. 작은 선물이나 다정한 말 한마디가 큰 기쁨을 줄 수 있습니다.",
        career="업무에서 좋은 성과를 낼 수 있습니다. 동료들과의 협업이 원활하게 진행됩니다.",
        health="규칙적인 운동을 권장합니다. 가벼운 스트레칭으로 하루를 시작해보세요.",
        wealth="재물운이 상승합니다. 계획적인 소비가 중요합니다.",
        lucky_color="초록색",
        lucky_number=7
    )


@pytest.fixture
def mock_chain_input():
    """테스트용 체인 입력 데이터"""
    return {
        "ilgan": "갑",
        "ilgan_oheng": "목",
        "ilgan_yin_yang": "양",
        "day_gan": "을",
        "day_ji": "축",
        "sipsung": "겁재",
        "sipsung_interpretation": "오늘은 경쟁보다 협력이 중요합니다.",
        "jiji_relation": "자 ↔ 축 = 합",
        "jiji_interpretation": "조화로운 에너지가 흐릅니다.",
        "today": "2026-01-29",
    }


@pytest.mark.unit
class TestCreateLLM:
    """create_llm() 팩토리 함수 테스트"""

    @patch('src.core.langchain_chain.settings')
    @patch('langchain_openai.ChatOpenAI')
    def test_create_openai_llm(self, mock_chat, mock_settings):
        """OpenAI LLM 생성"""
        mock_settings.openai_model = "gpt-4o-mini"
        mock_settings.openai_api_key = "test-key"
        mock_chat.return_value = Mock()

        llm = create_llm("openai")

        mock_chat.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.7,
            timeout=10,
            max_retries=1,
            api_key="test-key",
        )

    @patch('src.core.langchain_chain.settings')
    @patch('langchain_anthropic.ChatAnthropic')
    def test_create_anthropic_llm(self, mock_chat, mock_settings):
        """Anthropic LLM 생성"""
        mock_settings.anthropic_model = "claude-sonnet-4-20250514"
        mock_settings.anthropic_api_key = "test-key"
        mock_chat.return_value = Mock()

        llm = create_llm("anthropic")

        mock_chat.assert_called_once_with(
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            timeout=10,
            max_retries=1,
            api_key="test-key",
        )

    @patch('src.core.langchain_chain.settings')
    @patch('langchain_google_genai.ChatGoogleGenerativeAI')
    def test_create_google_llm(self, mock_chat, mock_settings):
        """Google LLM 생성"""
        mock_settings.google_model = "gemini-2.0-flash"
        mock_settings.google_api_key = "test-key"
        mock_chat.return_value = Mock()

        llm = create_llm("google")

        mock_chat.assert_called_once_with(
            model="gemini-2.0-flash",
            temperature=0.7,
            timeout=10,
            max_retries=1,
            google_api_key="test-key",
        )

    def test_create_unsupported_llm(self):
        """지원하지 않는 프로바이더"""
        with pytest.raises(ValueError) as exc_info:
            create_llm("unsupported")
        assert "지원하지 않는 LLM 프로바이더" in str(exc_info.value)


@pytest.mark.unit
class TestDailyFortuneChainInit:
    """DailyFortuneChain 초기화 테스트"""

    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    def test_chain_initialization_with_default_provider(
        self,
        mock_settings,
        mock_create_llm
    ):
        """기본 프로바이더로 체인 초기화"""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm

        chain = DailyFortuneChain()

        assert chain.provider == "openai"
        mock_create_llm.assert_called_once_with("openai")

    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    def test_chain_initialization_with_explicit_provider(
        self,
        mock_settings,
        mock_create_llm
    ):
        """명시적 프로바이더로 체인 초기화"""
        mock_settings.anthropic_model = "claude-sonnet-4-20250514"
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm

        chain = DailyFortuneChain(provider="anthropic")

        assert chain.provider == "anthropic"
        mock_create_llm.assert_called_once_with("anthropic")

    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    def test_get_chain_info(self, mock_settings, mock_create_llm):
        """체인 정보 조회"""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain()
        info = chain.get_chain_info()

        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4o-mini"
        assert info["temperature"] == 0.7
        assert info["timeout"] == 10
        assert info["max_retries"] == 1
        assert info["output_schema"] == "LLMFortuneOutput"


@pytest.mark.unit
class TestGenerateFortune:
    """generate_fortune() 메서드 테스트"""

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_generate_fortune_success(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_openai_response,
        mock_chain_input
    ):
        """AC2: LLM Mock으로 정상 운세 생성"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain()
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(return_value=mock_openai_response)

        result = await chain.generate_fortune(**mock_chain_input)

        assert result is not None
        assert isinstance(result, LLMFortuneOutput)
        assert result.overall is not None
        assert result.love is not None
        assert result.career is not None
        assert result.health is not None
        assert result.wealth is not None
        assert result.lucky_color == "초록색"
        assert result.lucky_number == 7

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_generate_fortune_timeout(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_chain_input
    ):
        """AC3: 타임아웃 시 예외 발생"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain()
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(side_effect=TimeoutError("Request timed out"))

        with pytest.raises(TimeoutError):
            await chain.generate_fortune(**mock_chain_input)

        mock_log.error.assert_called()

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_generate_fortune_api_error(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_chain_input
    ):
        """AC3: API 에러 시 예외 발생"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain()
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(side_effect=Exception("OpenAI API Error"))

        with pytest.raises(Exception) as exc_info:
            await chain.generate_fortune(**mock_chain_input)

        assert "OpenAI API Error" in str(exc_info.value)

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_generate_fortune_invalid_json(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_chain_input
    ):
        """JSON 파싱 에러 테스트"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain()
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(side_effect=ValueError("Invalid JSON format"))

        with pytest.raises(ValueError):
            await chain.generate_fortune(**mock_chain_input)


@pytest.mark.unit
class TestMultiProviderSupport:
    """다중 프로바이더 지원 테스트"""

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_anthropic_provider(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_openai_response,
        mock_chain_input
    ):
        """Anthropic 프로바이더 테스트"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.anthropic_model = "claude-sonnet-4-20250514"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain(provider="anthropic")
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(return_value=mock_openai_response)

        assert chain.provider == "anthropic"

        result = await chain.generate_fortune(**mock_chain_input)
        assert result is not None

    @patch('src.core.langchain_chain.get_logger_with_request_id')
    @patch('src.core.langchain_chain.create_llm')
    @patch('src.core.langchain_chain.settings')
    async def test_google_provider(
        self,
        mock_settings,
        mock_create_llm,
        mock_logger,
        mock_openai_response,
        mock_chain_input
    ):
        """Google 프로바이더 테스트"""
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_settings.google_model = "gemini-2.0-flash"
        mock_create_llm.return_value = Mock()

        chain = DailyFortuneChain(provider="google")
        chain.chain = AsyncMock()
        chain.chain.ainvoke = AsyncMock(return_value=mock_openai_response)

        assert chain.provider == "google"

        result = await chain.generate_fortune(**mock_chain_input)
        assert result is not None


@pytest.mark.unit
class TestFortuneOutputValidation:
    """LLMFortuneOutput 스키마 검증 테스트"""

    def test_valid_output(self):
        """AC4: 유효한 출력 형식"""
        output = LLMFortuneOutput(
            overall="오늘의 총운입니다. 좋은 하루가 될 것입니다. 긍정적인 마음으로 하루를 시작하세요.",
            love="연인과의 관계가 좋습니다. 소통을 많이 하세요.",
            career="업무에서 성과를 낼 수 있습니다. 집중력을 유지하세요.",
            health="건강에 유의하세요. 규칙적인 운동이 도움됩니다.",
            wealth="재물운이 좋습니다. 계획적인 소비를 권장합니다.",
            lucky_color="파란색",
            lucky_number=3
        )

        assert output.overall is not None
        assert output.lucky_number == 3
        assert 1 <= output.lucky_number <= 99

    def test_output_without_optional_fields(self):
        """AC4: 선택 필드 없이도 유효"""
        output = LLMFortuneOutput(
            overall="오늘의 총운입니다. 좋은 하루가 될 것입니다. 긍정적인 마음으로 하루를 시작하세요.",
            love="연인과의 관계가 좋습니다.",
            career="업무에서 성과를 낼 수 있습니다.",
            health="건강에 유의하세요.",
            wealth="재물운이 좋습니다.",
            lucky_color=None,
            lucky_number=None
        )

        assert output.lucky_color is None
        assert output.lucky_number is None

    def test_output_short_text_padding(self):
        """AC4: 짧은 텍스트 자동 패딩"""
        output = LLMFortuneOutput(
            overall="짧음",
            love="연인과의 관계가 좋습니다. 소통을 많이 하세요.",
            career="업무에서 성과를 낼 수 있습니다.",
            health="건강에 유의하세요.",
            wealth="재물운이 좋습니다.",
        )

        assert len(output.overall) >= 10

    def test_output_long_text_truncation(self):
        """AC4: 긴 텍스트 자동 자름"""
        long_text = "가" * 250
        output = LLMFortuneOutput(
            overall=long_text,
            love="연인과의 관계가 좋습니다. 소통을 많이 하세요.",
            career="업무에서 성과를 낼 수 있습니다.",
            health="건강에 유의하세요.",
            wealth="재물운이 좋습니다.",
        )

        assert len(output.overall) <= 200


@pytest.mark.unit
class TestPromptTemplate:
    """프롬프트 템플릿 테스트"""

    def test_system_prompt_exists(self):
        """시스템 프롬프트 존재 확인"""
        from src.core.prompts import FORTUNE_SYSTEM_PROMPT
        assert FORTUNE_SYSTEM_PROMPT is not None
        assert "명리학" in FORTUNE_SYSTEM_PROMPT or "전문가" in FORTUNE_SYSTEM_PROMPT
        assert "JSON" in FORTUNE_SYSTEM_PROMPT

    def test_user_prompt_template_exists(self):
        """사용자 프롬프트 템플릿 존재 확인"""
        from src.core.prompts import FORTUNE_USER_PROMPT_TEMPLATE
        assert FORTUNE_USER_PROMPT_TEMPLATE is not None
        assert "{ilgan}" in FORTUNE_USER_PROMPT_TEMPLATE
        assert "{sipsung}" in FORTUNE_USER_PROMPT_TEMPLATE
        assert "{day_gan}" in FORTUNE_USER_PROMPT_TEMPLATE

    def test_prompt_has_all_required_placeholders(self):
        """프롬프트에 필수 플레이스홀더 포함 확인"""
        from src.core.prompts import FORTUNE_USER_PROMPT_TEMPLATE
        required_placeholders = [
            "{ilgan}",
            "{ilgan_oheng}",
            "{ilgan_yin_yang}",
            "{day_gan}",
            "{day_ji}",
            "{sipsung}",
            "{sipsung_interpretation}",
            "{jiji_relation}",
            "{jiji_interpretation}",
            "{today}"
        ]

        for placeholder in required_placeholders:
            assert placeholder in FORTUNE_USER_PROMPT_TEMPLATE, \
                f"Missing placeholder: {placeholder}"
