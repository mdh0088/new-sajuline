"""
AI 예시 질문, 히스토리 스키마.

Stories: 4-1
FRs: FR18, FR19
"""
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 예시 질문 스키마 ====================

class ExampleQuestionItem(BaseModel):
    """예시 질문 항목."""
    question: str = Field(description="예시 질문 텍스트")
    description: str = Field(description="질문 설명")


class ExampleCategory(BaseModel):
    """예시 질문 카테고리."""
    name: str = Field(description="카테고리 이름")
    questions: list[ExampleQuestionItem] = Field(description="질문 목록")


class ExampleQuestionsResponse(BaseModel):
    """예시 질문 목록 응답.

    AC1: 도메인별 예시 질문 목록 표시
    """
    categories: list[ExampleCategory] = Field(description="카테고리별 예시 질문")


# ==================== 히스토리 스키마 ====================

class QueryHistoryItem(BaseModel):
    """질의 히스토리 항목.

    AC3: 질문, 실행 시간, 결과 요약
    """
    id: int = Field(description="히스토리 ID")
    query_id: str = Field(description="질의 고유 ID")
    question: str = Field(description="사용자 질문")
    answer_summary: str | None = Field(default=None, description="응답 요약")
    db_scope: str = Field(description="DB 범위")
    execution_time_ms: int | None = Field(default=None, description="실행 시간 (밀리초)")
    row_count: int | None = Field(default=None, description="결과 행 수")
    status: str = Field(description="실행 상태")
    created_at: datetime = Field(description="생성 일시")

    class Config:
        from_attributes = True  # SQLAlchemy 모델 변환 지원


class QueryHistoryResponse(BaseModel):
    """질의 히스토리 응답.

    AC3: 최근 질의 히스토리 표시 (최대 20개)
    AC5: 히스토리 검색 기능
    """
    history: list[QueryHistoryItem] = Field(description="히스토리 목록")
    total_count: int = Field(description="총 히스토리 개수")
