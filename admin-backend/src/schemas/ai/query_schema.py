"""
AI 질의 요청/응답 스키마.

자연어 질의를 받아 SQL을 생성하고 실행하는 API의 입출력 스키마를 정의합니다.

Stories: 2-1
FRs: FR-011, FR-012
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Dict, Any
import re


class AIQueryRequest(BaseModel):
    """AI 질의 요청 스키마"""

    question: str = Field(..., min_length=5, max_length=500, description="자연어 질문")
    db_scope: Literal["mariadb", "mssql", "cross"] = Field(
        default="mariadb", description="조회 대상 DB"
    )
    max_rows: int = Field(default=100, ge=1, le=5000, description="최대 결과 행 수")
    include_sql: bool = Field(default=False, description="생성된 SQL 포함 여부")
    stream: bool = Field(default=False, description="SSE 스트리밍 응답 (Phase 2)")
    accessibility_mode: bool = Field(
        default=False, description="접근성 모드 (테이블 대신 텍스트 요약)"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """질문 유효성 검사 - SQL 키워드 및 Injection 패턴 차단"""
        # 금지 패턴 체크 (포괄적 SQL Injection 방어)
        forbidden_patterns = [
            # DML/DDL 키워드
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE)\b",
            # SQL 주석 패턴
            r";\s*--",  # 인라인 주석
            r"/\*.*?\*/",  # 블록 주석
            r"--",  # 단순 주석
            # SQL Injection 공격 패턴
            r"UNION\s+(ALL\s+)?SELECT",
            r"\bOR\s+\d+\s*=\s*\d+",  # OR 1=1
            r"\bAND\s+\d+\s*=\s*\d+",  # AND 1=1
            # MSSQL 위험 프로시저/함수
            r"\b(sp_|xp_)\w+",  # sp_executesql, xp_cmdshell 등
            r"\bOPENROWSET\b",
            r"\bOPENQUERY\b",
            # 인코딩 우회 시도
            r"0x[0-9a-fA-F]+",  # Hex 인코딩
            r"\bCHAR\s*\(",  # CHAR() 함수
            r"\bCONCAT\s*\(",  # CONCAT으로 SQL 조립
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(
                    "SQL 키워드를 직접 입력할 수 없습니다. 자연어로 질문해주세요."
                )
        return v.strip()


class AIQueryMetadata(BaseModel):
    """AI 질의 메타데이터"""

    query_complexity: Literal["simple", "moderate", "complex"] = Field(
        default="simple", description="질의 복잡도"
    )
    db_scope_detected: str = Field(description="실제 사용된 DB 스코프")
    tables_accessed: List[str] = Field(
        default_factory=list, description="접근한 테이블 목록"
    )
    agents_used: List[str] = Field(
        default_factory=list, description="사용된 에이전트 목록"
    )


class AIQueryResponse(BaseModel):
    """AI 질의 응답 스키마"""

    success: bool = Field(description="요청 성공 여부")
    query_id: str = Field(description="요청 추적용 UUID")
    answer: str = Field(description="자연어 답변")
    answer_summary: str | None = Field(
        default=None, description="접근성 모드용 텍스트 요약"
    )
    data: List[Dict[str, Any]] | None = Field(
        default=None, description="테이블 형태 결과 데이터"
    )
    generated_sql: str | None = Field(
        default=None, description="생성된 SQL (include_sql=True 시)"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")
    suggestions: List[str] = Field(default_factory=list, description="후속 질문 제안")
    metadata: AIQueryMetadata | None = Field(
        default=None, description="질의 메타데이터"
    )
