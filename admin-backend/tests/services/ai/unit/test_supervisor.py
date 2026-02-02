"""
Supervisor 에이전트 단위 테스트
"""
import pytest
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from src.services.ai.agents.supervisor import supervisor_node, create_supervisor_prompt


def test_supervisor_node_with_message(sample_state):
    """메시지가 있을 때 Supervisor 노드 테스트"""
    config = {}
    
    result = supervisor_node(sample_state, config)
    
    assert isinstance(result, Command)
    assert result.goto == "mariadb_agent"
    assert result.update["current_agent"] == "mariadb_agent"


def test_supervisor_node_without_message():
    """메시지가 없을 때 Supervisor 노드 테스트"""
    state = {
        "messages": [],
        "user_id": "test_user",
        "session_id": "test_session",
        "current_agent": None,
        "query_context": None
    }
    config = {}
    
    result = supervisor_node(state, config)
    
    assert isinstance(result, Command)
    assert result.goto == "end"


def test_create_supervisor_prompt():
    """Supervisor 프롬프트 생성 테스트"""
    prompt = create_supervisor_prompt()
    
    assert isinstance(prompt, str)
    assert "Supervisor" in prompt
    assert "mariadb_agent" in prompt
    assert "mssql_agent" in prompt
