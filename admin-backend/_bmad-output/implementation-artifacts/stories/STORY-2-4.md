# Story 2.4: 자연어 응답 생성 및 결과 포맷팅

Status: ready-for-dev

## Story

As a 관리자,
I want 질의 결과를 자연어 답변과 테이블로 확인하기를,
so that 데이터를 쉽게 이해할 수 있다.

## Acceptance Criteria

1. LLM이 쿼리 결과를 자연어 요약으로 변환한다
   - 핵심 수치 강조
   - 비교 정보 포함 (전일 대비, 전주 대비 등)
   - 한국어 자연스러운 표현
2. 테이블 형태의 결과가 함께 표시된다
   - 컬럼 이름 한글화 (매핑 테이블)
   - 숫자 포맷팅 (천 단위 구분)
   - 날짜 포맷팅 (YYYY-MM-DD)
3. 결과가 없을 경우 적절한 메시지가 표시된다
   - "조회 결과가 없습니다."
   - 대안 질문 제안
4. 응답 시간이 p95 3초 이내이다
   - SQL 생성 + 실행 + 포맷팅 전체
5. TypedDict 기반 응답 타입이 사용된다
   - BaseAgentOutput → AIQueryResponse

## Tasks / Subtasks

- [ ] Task 1: 응답 생성 에이전트 구현 (AC: 1, 3)
  - [ ] `src/services/ai/agents/response_agent.py` 생성
  - [ ] `ResponseGenerationAgent` 클래스 구현
  - [ ] `ResponseGenerationResult` 데이터클래스 정의
  - [ ] `generate_response()` 비동기 메서드 구현
  - [ ] 빈 결과 처리 로직
- [ ] Task 2: 응답 프롬프트 템플릿 구현 (AC: 1)
  - [ ] `src/services/ai/prompts/response_generation.py` 생성
  - [ ] `RESPONSE_SYSTEM_PROMPT` 정의
  - [ ] 숫자 포맷 규칙 포함
  - [ ] 예시 응답 포함
- [ ] Task 3: 응답 포맷터 구현 (AC: 2)
  - [ ] `src/services/ai/utils/response_formatter.py` 생성
  - [ ] `ResponseFormatter` 클래스 구현
  - [ ] 숫자/날짜/금액 포맷팅 메서드
- [ ] Task 4: 컬럼 매핑 구현 (AC: 2)
  - [ ] `src/services/ai/config/column_mappings.py` 생성
  - [ ] `COLUMN_MAPPINGS` 상수 정의
  - [ ] `get_column_display_name()` 함수 구현
- [ ] Task 5: API 통합 (AC: 4, 5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] 응답 생성 에이전트 연동
  - [ ] 테이블 데이터 포맷팅 적용
- [ ] Task 6: 단위 테스트 작성 (AC: 1-5)
  - [ ] `tests/services/ai/unit/test_response_agent.py` 생성
  - [ ] `tests/services/ai/unit/test_response_formatter.py` 생성
  - [ ] 포맷팅 테스트 (숫자, 날짜, 금액)
- [ ] Task 7: 통합 테스트 작성
  - [ ] 전체 플로우 E2E 테스트
  - [ ] 응답 시간 p95 < 3초 검증
- [ ] Task 8: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

데이터베이스 쿼리 결과를 단순히 테이블로 보여주는 것은 사용자 친화적이지 않습니다. 이 스토리에서는 LLM을 사용하여 쿼리 결과를 자연어로 요약하고, 동시에 테이블 형태로도 제공합니다.

### Response Generation Agent

```python
# src/services/ai/agents/response_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ResponseGenerationAgent:
    """쿼리 결과를 자연어 응답으로 변환하는 에이전트"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.ai_llm_model,
            temperature=0.3,  # 약간의 창의성
            timeout=settings.ai_llm_timeout,
            api_key=settings.openai_api_key,
        )
        self.prompt = self._build_prompt()

    async def generate_response(
        self,
        question: str,
        sql: str,
        result_data: list[dict],
        columns: list[str]
    ) -> ResponseGenerationResult:
        """쿼리 결과를 자연어 응답으로 변환"""
        # 구현...
```

### Response Prompt

```python
# src/services/ai/prompts/response_generation.py

RESPONSE_SYSTEM_PROMPT = """당신은 데이터 분석 결과를 친절하게 설명하는 AI 어시스턴트입니다.

## 규칙
1. **한국어로 자연스럽게**: 존댓말 사용, 친근한 톤
2. **핵심 수치 강조**: 중요한 숫자는 명확하게
3. **비교 정보 추가**: 가능하면 전일/전주/전월 대비 비교
4. **인사이트 제공**: 단순 수치 나열이 아닌 의미 전달
5. **간결함**: 3-5문장 이내

## 숫자 포맷
- 금액: 천 단위 구분 (예: 1,250,000원)
- 퍼센트: 소수점 1자리 (예: 12.5%)
- 큰 숫자: 만/억 단위 (예: 1억 2천만원)
"""
```

### Response Formatter

```python
# src/services/ai/utils/response_formatter.py
from typing import List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class ResponseFormatter:
    """응답 데이터 포맷터"""

    @staticmethod
    def format_table_data(
        data: List[Dict[str, Any]],
        columns: List[str],
        column_mappings: Dict[str, str] | None = None
    ) -> List[Dict[str, Any]]:
        """테이블 데이터 포맷팅"""
        # 구현...

    @staticmethod
    def format_money(amount: int | float | Decimal) -> str:
        """금액 포맷팅"""
        amount = float(amount)
        if amount >= 100_000_000:
            return f"{amount / 100_000_000:.1f}억원"
        elif amount >= 10_000:
            return f"{amount / 10_000:.0f}만원"
        else:
            return f"{amount:,.0f}원"
```

### Column Mappings

```python
# src/services/ai/config/column_mappings.py

COLUMN_MAPPINGS = {
    "id": "ID",
    "user_id": "사용자 ID",
    "counselor_id": "상담사 ID",
    "amount": "금액",
    "status": "상태",
    "created_at": "생성일시",
    "name": "이름",
    "total_sales": "총 매출",
    "count": "건수",
    "average": "평균",
}
```

### Edge Cases

- **빈 결과**: "조회 결과가 없습니다" + 대안 제안
- **대용량 결과**: 요약 강조, 상세는 테이블로
- **복잡한 집계**: 여러 지표를 명확하게 구분
- **NULL 값**: "-"로 표시

### Dependencies

**Prerequisite Stories:**
- Story 2-3: MariaDB 질의 실행 및 허용 필터링 (쿼리 결과)

**Blocked Stories:**
- Story 2-5: SQL 확인 및 접근성 모드 (응답 포맷 확장)
- Story 4-2: 사용자 친화적 에러 및 대안 제안 (응답 패턴 재사용)

### Architecture Requirements

- **FR3**: 자연어 답변 제공 ✓
- **FR4**: 테이블 형태 표시 ✓
- **AR13-AR15**: TypedDict 타입, BaseAgentOutput ✓
- **NFR-P1**: 응답 시간 p95 ≤ 3초 ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Response-Generation]
- [Source: _bmad-output/project-context.md#LLM-Patterns]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
