"""
Supervisor 에이전트 - 멀티 에이전트 오케스트레이션
"""

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

try:
    from langgraph.types import Command
except ImportError:
    # Fallback for older langgraph versions
    from typing import Any as Command

from ..state import AIAssistantState


class SupervisorResponse(TypedDict):
    """Supervisor 응답 타입"""

    next_agent: Literal["mariadb_agent", "mssql_agent", "end"]
    reasoning: str


def supervisor_node(state: AIAssistantState, config: dict) -> Command:
    """
    Supervisor 에이전트 노드 - 다음 에이전트 결정

    Args:
        state: 현재 AI 어시스턴트 상태
        config: LangGraph 설정

    Returns:
        다음 노드로의 Command
    """
    # 현재는 스켈레톤 구현
    # 실제 구현은 Story 2.2에서 진행

    # 마지막 사용자 메시지 추출
    last_message = state["messages"][-1] if state["messages"] else None

    if not last_message:
        return Command(goto="end")

    # 기본 라우팅 로직 (향후 LLM 기반으로 교체)
    # Phase 1에서는 MariaDB만 지원
    return Command(goto="mariadb_agent", update={"current_agent": "mariadb_agent"})


def create_supervisor_prompt() -> str:
    """Supervisor 시스템 프롬프트 생성"""
    return """당신은 AI BI 어시스턴트의 Supervisor입니다.
사용자의 질문을 분석하여 적절한 에이전트로 라우팅합니다.

현재 사용 가능한 에이전트:
- mariadb_agent: MariaDB 질의 담당
- mssql_agent: MSSQL 질의 담당 (Phase 2)
- end: 작업 완료

사용자의 질문을 분석하여 next_agent를 결정하세요."""
