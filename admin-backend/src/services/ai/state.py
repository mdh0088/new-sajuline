"""
AI 어시스턴트 상태 타입 정의
"""

from typing import Annotated, Any, Dict, Optional, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AIAssistantState(TypedDict):
    """
    AI 어시스턴트 상태 타입 (LangGraph 공식 패턴)

    Attributes:
        messages: 대화 메시지 히스토리 (자동 병합)
        user_id: 사용자 ID
        session_id: 세션 ID
        current_agent: 현재 활성 에이전트
        query_context: 질의 컨텍스트 정보
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str
    current_agent: Optional[str]
    query_context: Optional[Dict[str, Any]]
