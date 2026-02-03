"""
응답 생성 에이전트 단위 테스트

Stories: 2-4
FRs: FR-011, FR-013
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.messages import AIMessage

from src.services.ai.agents.response_agent import (
    ResponseGenerationAgent,
    ResponseGenerationResult,
)


@pytest.fixture
def mock_llm():
    """Mock LLM 인스턴스"""
    llm = Mock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content="총 매출은 1억 2천만원입니다. 전월 대비 15% 증가했습니다."))
    return llm


@pytest.fixture
def mock_settings():
    """Mock Settings 인스턴스"""
    settings = Mock()
    settings.ai_llm_model = "gpt-4o-mini"
    settings.ai_llm_fallback_model = "gpt-3.5-turbo"
    settings.ai_llm_timeout = 10
    settings.openai_api_key = "test-api-key"
    settings.ai_llm_max_sample_rows = 10
    return settings


@pytest.fixture
def sample_query_result():
    """샘플 쿼리 결과"""
    return {
        "question": "이번 달 총 매출은 얼마인가요?",
        "sql": "SELECT SUM(amount) as total_sales FROM payments WHERE MONTH(created_at) = MONTH(NOW())",
        "result_data": [
            {"total_sales": 120000000}
        ],
        "columns": ["total_sales"],
    }


@pytest.fixture
def empty_query_result():
    """빈 쿼리 결과"""
    return {
        "question": "작년 매출은 얼마인가요?",
        "sql": "SELECT SUM(amount) as total_sales FROM payments WHERE YEAR(created_at) = 2023",
        "result_data": [],
        "columns": ["total_sales"],
    }


class TestResponseGenerationAgent:
    """ResponseGenerationAgent 테스트"""

    def test_initialization(self, mock_llm, mock_settings):
        """에이전트 초기화 테스트"""
        agent = ResponseGenerationAgent(llm=mock_llm, settings=mock_settings)

        assert agent.llm == mock_llm
        assert agent.settings == mock_settings
        assert agent.prompt is not None

    @pytest.mark.asyncio
    async def test_generate_response_success(self, mock_llm, mock_settings, sample_query_result):
        """정상적인 응답 생성 테스트"""
        agent = ResponseGenerationAgent(llm=mock_llm, settings=mock_settings)

        result = await agent.generate_response(
            question=sample_query_result["question"],
            sql=sample_query_result["sql"],
            result_data=sample_query_result["result_data"],
            columns=sample_query_result["columns"],
        )

        assert isinstance(result, ResponseGenerationResult)
        assert result.success is True
        assert result.natural_language_response is not None
        assert "매출" in result.natural_language_response
        assert result.error_code is None
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_generate_response_empty_result(self, mock_llm, mock_settings, empty_query_result):
        """빈 결과에 대한 응답 생성 테스트"""
        # 빈 결과에 대한 LLM 응답 설정
        mock_llm.ainvoke = AsyncMock(
            return_value=AIMessage(content="조회 결과가 없습니다. 다른 기간으로 조회해보시는 건 어떨까요?")
        )

        agent = ResponseGenerationAgent(llm=mock_llm, settings=mock_settings)

        result = await agent.generate_response(
            question=empty_query_result["question"],
            sql=empty_query_result["sql"],
            result_data=empty_query_result["result_data"],
            columns=empty_query_result["columns"],
        )

        assert result.success is True
        assert result.natural_language_response is not None
        assert "조회 결과가 없습니다" in result.natural_language_response

    @pytest.mark.asyncio
    async def test_generate_response_llm_timeout(self, mock_llm, mock_settings, sample_query_result):
        """LLM 타임아웃 에러 처리 테스트"""
        # LLM 타임아웃 시뮬레이션
        mock_llm.ainvoke = AsyncMock(side_effect=TimeoutError("LLM timeout"))

        agent = ResponseGenerationAgent(llm=mock_llm, settings=mock_settings)

        result = await agent.generate_response(
            question=sample_query_result["question"],
            sql=sample_query_result["sql"],
            result_data=sample_query_result["result_data"],
            columns=sample_query_result["columns"],
        )

        assert result.success is False
        assert result.error_code == "AIBI_RESPONSE_TIMEOUT"
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_generate_response_llm_error(self, mock_llm, mock_settings, sample_query_result):
        """LLM 일반 에러 처리 테스트"""
        # LLM 에러 시뮬레이션
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM error"))

        agent = ResponseGenerationAgent(llm=mock_llm, settings=mock_settings)

        result = await agent.generate_response(
            question=sample_query_result["question"],
            sql=sample_query_result["sql"],
            result_data=sample_query_result["result_data"],
            columns=sample_query_result["columns"],
        )

        assert result.success is False
        assert result.error_code == "AIBI_RESPONSE_GENERATION_ERROR"
        assert result.error_message is not None


class TestResponseGenerationResult:
    """ResponseGenerationResult 데이터클래스 테스트"""

    def test_result_structure_success(self):
        """성공 결과 구조 테스트"""
        result = ResponseGenerationResult(
            success=True,
            natural_language_response="총 매출은 1억원입니다.",
            error_code=None,
            error_message=None,
            execution_time_ms=150,
        )

        assert result.success is True
        assert result.natural_language_response == "총 매출은 1억원입니다."
        assert result.error_code is None
        assert result.error_message is None
        assert result.execution_time_ms == 150

    def test_result_structure_error(self):
        """에러 결과 구조 테스트"""
        result = ResponseGenerationResult(
            success=False,
            natural_language_response=None,
            error_code="AIBI_RESPONSE_TIMEOUT",
            error_message="LLM 호출 타임아웃",
            execution_time_ms=30000,
        )

        assert result.success is False
        assert result.natural_language_response is None
        assert result.error_code == "AIBI_RESPONSE_TIMEOUT"
        assert result.error_message == "LLM 호출 타임아웃"
        assert result.execution_time_ms == 30000
