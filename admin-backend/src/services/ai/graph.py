"""
LangGraph StateGraph 정의
"""

from typing import Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from .agents.supervisor import supervisor_node
from .state import AIAssistantState


def create_ai_assistant_graph(
    checkpointer: Optional[BaseCheckpointSaver] = None,
) -> StateGraph:
    """
    AI 어시스턴트 그래프 생성

    Args:
        checkpointer: Redis 체크포인터 (선택사항)

    Returns:
        컴파일된 StateGraph
    """
    # StateGraph 생성
    workflow = StateGraph(AIAssistantState)

    # Supervisor 노드 추가
    workflow.add_node("supervisor", supervisor_node)

    # 진입점 설정
    workflow.set_entry_point("supervisor")

    # 임시 엔드 노드 추가 (실제 에이전트는 Story 2.2에서 추가)
    workflow.add_node("mariadb_agent", lambda state: state)
    workflow.add_edge("mariadb_agent", END)

    # 그래프 컴파일
    compiled_graph = workflow.compile(checkpointer=checkpointer)

    return compiled_graph
