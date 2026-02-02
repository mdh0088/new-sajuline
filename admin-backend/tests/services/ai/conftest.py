"""
AI 서비스 테스트용 fixtures
"""
import pytest
from unittest.mock import Mock, AsyncMock
from langchain_openai import ChatOpenAI


@pytest.fixture
def mock_llm():
    """Mock LLM 인스턴스"""
    llm = Mock(spec=ChatOpenAI)
    llm.ainvoke = AsyncMock(return_value="Mocked response")
    return llm


@pytest.fixture
def mock_redis_url():
    """Mock Redis URL"""
    return "redis://localhost:6379/1"


@pytest.fixture
def sample_state():
    """샘플 AI Assistant State"""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="Hello")],
        "user_id": "test_user",
        "session_id": "test_session",
        "current_agent": None,
        "query_context": None
    }
