"""
SQL Generation Agent 단위 테스트

LLM Mock을 사용하여 SQL 생성 에이전트를 테스트합니다.

Stories: AI-002
FRs: FR-011, FR-012
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from langchain_core.messages import AIMessage

from src.services.ai.agents.sql_agent import SQLGenerationAgent, SQLGenerationResult
from src.config.settings import Settings


@pytest.fixture
def mock_settings():
    """테스트용 Settings"""
    return Mock(
        ai_llm_model="gpt-4o-mini",
        ai_llm_timeout=10,
        openai_api_key="test-key",
    )


@pytest.fixture
def mock_llm():
    """LangChain ChatOpenAI Mock"""
    with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
        llm_instance = Mock()
        llm_instance.ainvoke = AsyncMock(
            return_value=AIMessage(content="SELECT * FROM users LIMIT 100")
        )
        mock.return_value = llm_instance
        yield mock


@pytest.mark.asyncio
class TestSQLGenerationAgent:
    """SQL Generation Agent 테스트"""

    async def test_agent_initialization(self, mock_settings, mock_llm):
        """에이전트가 올바르게 초기화되는지 테스트"""
        agent = SQLGenerationAgent(settings=mock_settings)

        # LLM이 올바른 설정으로 생성되었는지 확인
        mock_llm.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0,
            timeout=10,
            api_key="test-key",
        )

    async def test_generate_sql_success(self, mock_settings, mock_llm):
        """자연어를 SQL로 성공적으로 변환하는지 테스트"""
        agent = SQLGenerationAgent(settings=mock_settings)

        result = await agent.generate_sql(
            question="모든 사용자 조회",
            schema_info="TABLE users (id INT, name VARCHAR)",
            allowed_tables=["users"]
        )

        # 결과 검증
        assert isinstance(result, SQLGenerationResult)
        assert result.success is True
        assert result.sql == "SELECT * FROM users LIMIT 100"
        assert result.error is None

    async def test_generate_sql_with_timeout(self, mock_settings):
        """LLM 타임아웃 처리 테스트"""
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()
            llm_instance.ainvoke = AsyncMock(side_effect=TimeoutError("LLM timeout"))
            mock.return_value = llm_instance

            agent = SQLGenerationAgent(settings=mock_settings)

            result = await agent.generate_sql(
                question="사용자 조회",
                schema_info="TABLE users",
                allowed_tables=["users"]
            )

            # 타임아웃 에러가 적절히 처리되는지 확인
            assert result.success is False
            assert result.error is not None
            assert "timeout" in result.error.lower()

    async def test_generate_sql_strips_markdown(self, mock_settings):
        """LLM이 마크다운 코드 블록을 반환할 때 제거하는지 테스트"""
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()
            llm_instance.ainvoke = AsyncMock(
                return_value=AIMessage(content="```sql\nSELECT * FROM users\n```")
            )
            mock.return_value = llm_instance

            agent = SQLGenerationAgent(settings=mock_settings)

            result = await agent.generate_sql(
                question="사용자 조회",
                schema_info="TABLE users",
                allowed_tables=["users"]
            )

            # 마크다운이 제거되었는지 확인
            assert result.sql.strip() == "SELECT * FROM users"
            assert "```" not in result.sql

    async def test_generate_sql_empty_question(self, mock_settings, mock_llm):
        """빈 질문에 대한 에러 처리 테스트"""
        agent = SQLGenerationAgent(settings=mock_settings)

        result = await agent.generate_sql(
            question="",
            schema_info="TABLE users",
            allowed_tables=["users"]
        )

        # 빈 질문은 에러 처리되어야 함
        assert result.success is False
        assert result.error is not None

    async def test_result_dataclass_structure(self):
        """SQLGenerationResult 데이터클래스 구조 테스트"""
        # 성공 케이스
        result = SQLGenerationResult(
            success=True,
            sql="SELECT * FROM users",
            error=None,
            metadata={"agent": "sql_agent", "duration_ms": 100}
        )

        assert result.success is True
        assert result.sql == "SELECT * FROM users"
        assert result.error is None
        assert result.metadata["agent"] == "sql_agent"

        # 실패 케이스
        result = SQLGenerationResult(
            success=False,
            sql=None,
            error="Invalid query",
            metadata={"agent": "sql_agent", "duration_ms": 50}
        )

        assert result.success is False
        assert result.sql is None
        assert result.error == "Invalid query"
