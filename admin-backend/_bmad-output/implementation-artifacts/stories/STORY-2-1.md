# Story 2.1: 자연어 질의 입력 인터페이스

Status: ready-for-dev

## Story

As a 관리자,
I want 자연어로 데이터 질문을 입력할 수 있기를,
so that SQL을 몰라도 데이터를 조회할 수 있다.

## Acceptance Criteria

1. API 엔드포인트 `POST /api/v1/ai/query`가 구현된다
   - 인증 필수 (Story 1-2 의존)
   - Rate Limit 적용 (Story 1-3 의존)
2. 입력 유효성 검사가 수행된다
   - 빈 값 체크: 최소 5자 이상
   - 최대 길이: 500자 이내
   - 금지 패턴: SQL 키워드 직접 입력 차단 (SELECT, DROP 등)
3. 요청 스키마 `AIQueryRequest`가 정의된다
   - `question: str` (필수, 5-500자)
   - `db_scope: Literal["mariadb", "mssql", "cross"]` (기본값: mariadb)
   - `max_rows: int` (기본값: 100, 최대: 5000)
   - `include_sql: bool` (기본값: False)
   - `stream: bool` (기본값: False, Phase 2)
   - `accessibility_mode: bool` (기본값: False)
4. 응답 스키마 `AIQueryResponse`가 정의된다
   - `success: bool`
   - `query_id: str` (UUID)
   - `answer: str`
   - `data: List[Dict] | None`
   - `generated_sql: str | None`
   - `execution_time_ms: int`
   - `suggestions: List[str]`
5. 요청 ID가 UUID로 생성되어 추적에 사용된다
6. 유효성 검사 실패 시 적절한 에러 응답이 반환된다
   - 400 Bad Request with detail message

## Tasks / Subtasks

- [ ] Task 1: API 엔드포인트 구현 (AC: 1, 5)
  - [ ] `src/api/v1/ai_assistant_api.py`에 `/query` 엔드포인트 추가
  - [ ] 인증 및 Rate Limit 의존성 적용
  - [ ] UUID 기반 query_id 생성
  - [ ] 실행 시간 측정 로직 추가
- [ ] Task 2: 요청 스키마 정의 (AC: 3)
  - [ ] `src/schemas/ai/query_schema.py` 생성
  - [ ] `AIQueryRequest` Pydantic 모델 정의
  - [ ] field_validator로 금지 패턴 검사
- [ ] Task 3: 응답 스키마 정의 (AC: 4)
  - [ ] `AIQueryResponse` Pydantic 모델 정의
  - [ ] `AIQueryMetadata` 모델 정의
  - [ ] `AIErrorResponse` 모델 정의
- [ ] Task 4: 입력 유효성 검사 구현 (AC: 2, 6)
  - [ ] `src/services/ai/validators/input_validator.py` 생성
  - [ ] `ValidationResult` 데이터클래스 정의
  - [ ] `validate_query_input()` 함수 구현
  - [ ] 금지 패턴 정규식 정의
- [ ] Task 5: 에러 응답 스키마 정의 (AC: 6)
  - [ ] `src/schemas/ai/error_schema.py` 생성
  - [ ] `AIErrorCode` 상수 정의
- [ ] Task 6: 단위 테스트 작성 (AC: 1-6)
  - [ ] `tests/services/ai/unit/test_input_validator.py` 생성
  - [ ] `tests/api/v1/test_ai_query_endpoint.py` 생성
  - [ ] 유효한 질의 요청 테스트
  - [ ] 질문 길이 검증 테스트
  - [ ] SQL 키워드 차단 테스트
- [ ] Task 7: 통합 테스트 작성
  - [ ] 인증/Rate Limit 통합 테스트
  - [ ] 유효성 검사 실패 케이스 테스트
- [ ] Task 8: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI BI 어시스턴트의 핵심 기능은 관리자가 "오늘 매출 얼마야?"와 같은 자연어 질문을 입력하면 데이터베이스에서 답변을 제공하는 것입니다. 이 스토리는 자연어 질의를 받아들이는 API 엔드포인트와 입력 유효성 검사를 구현합니다.

### Request Schema

```python
# src/schemas/ai/query_schema.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Dict, Any
import uuid
import re

class AIQueryRequest(BaseModel):
    """AI 질의 요청 스키마"""
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="자연어 질문"
    )
    db_scope: Literal["mariadb", "mssql", "cross"] = Field(
        default="mariadb",
        description="조회 대상 DB"
    )
    max_rows: int = Field(
        default=100,
        ge=1,
        le=5000,
        description="최대 결과 행 수"
    )
    include_sql: bool = Field(
        default=False,
        description="생성된 SQL 포함 여부"
    )
    stream: bool = Field(
        default=False,
        description="SSE 스트리밍 응답 (Phase 2)"
    )
    accessibility_mode: bool = Field(
        default=False,
        description="접근성 모드 (테이블 대신 텍스트 요약)"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """질문 유효성 검사"""
        # 금지 패턴 체크
        forbidden_patterns = [
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b",
            r";\s*--",  # SQL 주석
            r"UNION\s+SELECT",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("SQL 키워드를 직접 입력할 수 없습니다. 자연어로 질문해주세요.")
        return v.strip()
```

### Response Schema

```python
class AIQueryResponse(BaseModel):
    """AI 질의 응답 스키마"""
    success: bool
    query_id: str = Field(description="요청 추적용 UUID")
    answer: str = Field(description="자연어 답변")
    answer_summary: str | None = Field(
        default=None,
        description="접근성 모드용 텍스트 요약"
    )
    data: List[Dict[str, Any]] | None = Field(
        default=None,
        description="테이블 형태 결과 데이터"
    )
    generated_sql: str | None = Field(
        default=None,
        description="생성된 SQL (include_sql=True 시)"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")
    suggestions: List[str] = Field(
        default_factory=list,
        description="후속 질문 제안"
    )
    metadata: AIQueryMetadata | None = None
```

### Input Validator

```python
# src/services/ai/validators/input_validator.py
from dataclasses import dataclass
from typing import List
import re

@dataclass
class ValidationResult:
    is_valid: bool
    error_code: str | None = None
    message: str | None = None
    suggestions: List[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

async def validate_query_input(question: str) -> ValidationResult:
    """질의 입력 추가 유효성 검사"""

    # 의미 없는 입력 체크
    if len(question.strip()) < 5:
        return ValidationResult(
            is_valid=False,
            error_code="AIBI_QUESTION_TOO_SHORT",
            message="질문이 너무 짧습니다. 더 구체적으로 질문해주세요.",
            suggestions=["예: '오늘 매출 얼마야?'", "예: '이번 달 신규 가입자 수'"]
        )

    # 숫자/특수문자만 있는 경우
    if re.match(r'^[\d\s\W]+$', question):
        return ValidationResult(
            is_valid=False,
            error_code="AIBI_INVALID_INPUT",
            message="유효한 질문을 입력해주세요.",
            suggestions=["자연어로 질문을 입력해주세요."]
        )

    return ValidationResult(is_valid=True)
```

### Edge Cases

- **빈 문자열/공백만**: 400 에러 + 명확한 메시지
- **SQL 직접 입력**: 400 에러 + "자연어로 질문해주세요" 안내
- **최대 길이 초과**: 400 에러 + 길이 제한 안내
- **특수문자만**: 400 에러 + 유효한 질문 예시 제공

### Dependencies

**Prerequisite Stories:**
- Story 1-1: LangGraph 기반 AI 인프라 설정 (AI 서비스 구조)
- Story 1-2: 기존 인증 시스템 연동 (인증 의존성)
- Story 1-3: 역할 기반 접근 제어 설정 (Rate Limit)

**Blocked Stories:**
- Story 2-2: LLM 기반 SQL 생성 에이전트 (이 엔드포인트 위에 구현)
- Story 4-1: 예시 질문 및 질의 히스토리 (질의 저장 필요)
- Story 5-1: 피드백 제출 인터페이스 (query_id 필요)

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#API-Endpoints]
- [Source: _bmad-output/project-context.md#Schema-Patterns]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
