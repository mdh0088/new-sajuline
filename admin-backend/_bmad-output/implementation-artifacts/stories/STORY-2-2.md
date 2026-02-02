# Story 2.2: LLM 기반 SQL 생성 에이전트

Status: ready-for-dev

## Story

As a 시스템,
I want 자연어 질의를 SQL로 변환할 수 있기를,
so that MariaDB에서 데이터를 조회할 수 있다.

## Acceptance Criteria

1. OpenAI gpt-4o-mini를 사용하여 자연어를 SQL로 변환한다
   - LangChain `ChatOpenAI` 클래스 사용
   - 모델: `gpt-4o-mini` (설정으로 변경 가능)
2. 시스템 프롬프트에 DB 스키마 정보가 포함된다
   - 테이블 목록 및 컬럼 정보
   - 컬럼 타입 및 설명
   - 테이블 간 관계 (FK)
   - 예시 질문-SQL 쌍 (Few-shot)
3. SELECT 문만 생성되도록 제한된다
   - INSERT, UPDATE, DELETE, DROP 등 차단
   - 생성된 SQL 파싱하여 검증
4. 생성된 SQL이 응답에 포함된다 (선택적 표시)
   - `include_sql=True` 시 반환
5. LLM 호출 타임아웃이 10초로 설정된다
   - 타임아웃 시 적절한 에러 반환
6. 날짜 자연어가 올바르게 파싱된다
   - "오늘" → `CURDATE()`
   - "어제" → `DATE_SUB(CURDATE(), INTERVAL 1 DAY)`
   - "이번 달" → `MONTH(created_at) = MONTH(CURDATE())`
   - "지난 주" → 적절한 날짜 범위

## Tasks / Subtasks

- [ ] Task 1: SQL 생성 에이전트 구현 (AC: 1, 5)
  - [ ] `src/services/ai/agents/sql_agent.py` 생성
  - [ ] `SQLGenerationAgent` 클래스 구현
  - [ ] `ChatOpenAI` 설정 (model, temperature, timeout)
  - [ ] `SQLGenerationResult` 데이터클래스 정의
  - [ ] `generate_sql()` 비동기 메서드 구현
- [ ] Task 2: 프롬프트 템플릿 구현 (AC: 2, 6)
  - [ ] `src/services/ai/prompts/sql_generation.py` 생성
  - [ ] `SQL_SYSTEM_PROMPT` 템플릿 정의
  - [ ] 날짜 표현 변환 규칙 포함
  - [ ] Few-shot 예시 쌍 포함
- [ ] Task 3: 스키마 로더 구현 (AC: 2)
  - [ ] `src/services/ai/tools/schema_loader.py` 생성
  - [ ] `SchemaLoader` 클래스 구현
  - [ ] 테이블별 스키마 정보 캐싱
  - [ ] 테이블 스키마 Markdown 형식 생성
- [ ] Task 4: SQL 검증기 구현 (AC: 3)
  - [ ] `src/services/ai/validators/sql_validator.py` 생성
  - [ ] `SQLValidator` 클래스 구현
  - [ ] `FORBIDDEN_KEYWORDS` 상수 정의
  - [ ] sqlparse 기반 SQL 파싱
  - [ ] SELECT 문 검증 로직
  - [ ] 테이블 추출 로직
- [ ] Task 5: 단위 테스트 작성 (AC: 1-6)
  - [ ] `tests/services/ai/unit/test_sql_agent.py` 생성
  - [ ] `tests/services/ai/unit/test_sql_validator.py` 생성
  - [ ] LLM Mock을 사용한 SQL 생성 테스트
  - [ ] 날짜 파싱 테스트
  - [ ] SELECT only 검증 테스트
  - [ ] 금지 키워드 차단 테스트
- [ ] Task 6: Golden Dataset 테스트 작성
  - [ ] `tests/services/ai/golden/queries.json` 생성
  - [ ] 최소 20개 질문-SQL 쌍 정의
  - [ ] 패턴 매칭 기반 검증
- [ ] Task 7: 통합 테스트 작성
  - [ ] 실제 LLM 호출 테스트 (Mock 가능)
  - [ ] 다양한 질문 유형 테스트
- [ ] Task 8: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI BI 어시스턴트의 핵심 기능은 자연어를 SQL로 변환하는 것입니다. 이 스토리에서는 OpenAI GPT-4o-mini를 사용하여 관리자의 자연어 질문을 유효한 SELECT SQL 문으로 변환하는 에이전트를 구현합니다.

### SQL Generation Agent

```python
# src/services/ai/agents/sql_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config.settings import settings

class SQLGenerationAgent:
    """자연어를 SQL로 변환하는 에이전트"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.ai_llm_model,  # gpt-4o-mini
            temperature=0,  # 결정적 출력
            timeout=settings.ai_llm_timeout,  # 10초
            api_key=settings.openai_api_key,
        )
        self.prompt = self._build_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def generate_sql(
        self,
        question: str,
        schema_info: str,
        allowed_tables: list[str]
    ) -> SQLGenerationResult:
        """자연어 질문을 SQL로 변환"""
        # 구현...
```

### System Prompt Template

```python
# src/services/ai/prompts/sql_generation.py

SQL_SYSTEM_PROMPT = """당신은 MariaDB SQL 전문가입니다. 사용자의 자연어 질문을 정확한 SQL SELECT 문으로 변환합니다.

## 규칙
1. **SELECT 문만 생성**: INSERT, UPDATE, DELETE, DROP 등은 절대 생성하지 마세요.
2. **허용된 테이블만 사용**: {allowed_tables}
3. **안전한 SQL**: SQL Injection 패턴을 생성하지 마세요.
4. **결과 제한**: 항상 LIMIT 절을 포함하세요 (기본 100).

## 현재 날짜
{current_date}

## 날짜 표현 변환
- "오늘" → CURDATE()
- "어제" → DATE_SUB(CURDATE(), INTERVAL 1 DAY)
- "이번 주" → YEARWEEK(created_at) = YEARWEEK(CURDATE())
- "이번 달" → YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())

## 데이터베이스 스키마
{schema_info}

## 출력 형식
SQL만 출력하세요. 설명이나 마크다운 코드 블록 없이 순수 SQL만 반환합니다.
"""
```

### SQL Validator

```python
# src/services/ai/validators/sql_validator.py
import sqlparse
from dataclasses import dataclass
from typing import List, Set

class SQLValidator:
    """생성된 SQL 검증"""

    FORBIDDEN_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC',
        'EXECUTE', 'XP_', 'SP_'
    }

    @classmethod
    async def validate(
        cls,
        sql: str,
        allowed_tables: Set[str]
    ) -> SQLValidationResult:
        """SQL 유효성 검증"""
        # 구현...
```

### Edge Cases

- **모호한 질문**: "매출" → "어떤 기간의 매출인지 더 구체적으로 질문해주세요" 안내
- **복잡한 조인**: 3개 이상 테이블 조인 시 성능 경고
- **집계 없는 대량 조회**: LIMIT 강제 적용
- **LLM 환각 (Hallucination)**: 존재하지 않는 테이블/컬럼 생성 시 검증에서 차단

### LLM 비용 예측

| 모델 | 입력 토큰 | 출력 토큰 | 예상 비용/요청 |
|------|----------|----------|---------------|
| gpt-4o-mini | ~1500 | ~100 | ~$0.0003 |
| gpt-4-turbo | ~1500 | ~100 | ~$0.02 |

일 100회 질의 기준: 월 ~$1 (gpt-4o-mini)

### Dependencies

**Prerequisite Stories:**
- Story 1-1: LangGraph 기반 AI 인프라 설정 (LangChain 의존성)
- Story 2-1: 자연어 질의 입력 인터페이스 (엔드포인트)

**Blocked Stories:**
- Story 2-3: MariaDB 질의 실행 및 허용 필터링 (생성된 SQL 필요)
- Story 3-1: 4-Layer Security 프레임워크 (SQL 검증 확장)

### Architecture Requirements

- **AR10**: gpt-4o-mini 사용 ✓
- **AR11**: Adaptive 실행 패턴 (단일 에이전트로 시작)
- **NFR-I4**: LLM API 타임아웃 10초 ✓
- **NFR-P1**: 응답 시간 p95 ≤ 3초 (SQL 생성만 ~1초 목표)

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#LLM-Integration]
- [Source: _bmad-output/planning-artifacts/architecture.md#Text-to-SQL]
- [LangChain ChatOpenAI 문서](https://python.langchain.com/docs/integrations/chat/openai)

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
