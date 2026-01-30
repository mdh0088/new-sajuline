---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: 'complete'
completedAt: '2026-01-30'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/product-brief-admin-backend-2026-01-29.md'
  - '_bmad-output/planning-artifacts/research/technical-langgraph-multi-db-agent-research-2026-01-29.md'
  - 'docs/ai-assistant/00-index.md'
  - 'docs/ai-assistant/01-architecture-overview.md'
  - 'docs/ai-assistant/02-constraints.md'
  - 'docs/ai-assistant/03-implementation-roadmap.md'
  - 'docs/ai-assistant/04-risk-mitigation.md'
  - 'docs/ai-assistant/05-ga4-integration.md'
  - 'docs/ai-assistant/06-langgraph-implementation.md'
documentCounts:
  prd: 1
  brief: 1
  research: 1
  projectDocs: 7
workflowType: 'architecture'
projectType: 'brownfield'
project_name: 'admin-backend'
user_name: 'dongdong'
date: '2026-01-30'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
PRD에서 42개 기능 요구사항이 도출됨. 핵심 기능은 자연어 기반 데이터 조회(Text-to-SQL),
Multi-Agent 오케스트레이션(Supervisor 패턴), Cross-DB 조인(MariaDB+MSSQL+GA4),
실시간 스트리밍 응답(SSE)으로 구성됨.

주요 기능 영역:
- FR-001~010: 자연어 질의 처리 및 의도 분류
- FR-011~020: 데이터소스별 에이전트 실행
- FR-021~030: Cross-DB 조인 및 결과 통합
- FR-031~042: 응답 생성 및 스트리밍

**Non-Functional Requirements:**
33개 NFR 중 아키텍처 결정에 직접 영향을 미치는 핵심 요구사항:

| NFR ID | 카테고리 | 요구사항 | 아키텍처 영향 |
|--------|----------|----------|--------------|
| NFR-001 | 성능 | 단순 쿼리 <3초 | 캐싱, 쿼리 최적화 |
| NFR-002 | 성능 | 복합 쿼리 <10초 | 비동기 처리, 병렬화 |
| NFR-003 | 성능 | 첫 토큰 <1초 | SSE 스트리밍 |
| NFR-010 | 보안 | SQL Injection 방지 | 4-Layer Validation |
| NFR-015 | 호환성 | MSSQL 2005 지원 | pymssql, TDS 7.0/7.1 |
| NFR-020 | 가용성 | 99.5% SLA | Graceful Degradation |

**Scale & Complexity:**

- Primary domain: Backend AI/ML (LangGraph-based Multi-Agent System)
- Complexity level: High (Multi-DB, Multi-Agent, Real-time Streaming)
- Estimated architectural components: 15-20개 (에이전트, 서비스, 유틸리티)

**Phase별 복잡도:**

| Phase | 데이터소스 | 복잡도 | 핵심 기능 |
|-------|-----------|--------|-----------|
| Phase 1 (MVP) | MariaDB + MSSQL | Medium-High | 기본 Text-to-SQL |
| Phase 2 | + GA4 | High | Cross-DB 조인 |
| Phase 3-4 | Full | High | 고급 분석, 자동화 |

### Technical Constraints & Dependencies

**Hard Constraints:**
1. **MSSQL 2005 레거시**: TDS 7.0/7.1 프로토콜, 동기 pymssql만 사용 가능
2. **EUC-KR 인코딩**: 레거시 DB 문자 인코딩 변환 필수
3. **Async/Sync 혼합**: MariaDB(async) + MSSQL(sync) 동시 처리
4. **기존 3-Layer 아키텍처**: Brownfield 프로젝트로 기존 패턴 준수

**정량적 제한:**
- Thread Pool: `max_workers = min(32, CPU*5)` for asyncio.to_thread()
- MSSQL Timeout: 30초 (조정 가능, TDS 7.0 제한)
- pandas.merge() Memory: 단일 조인 결과 <100MB 권장
- LLM Rate Limit: OpenAI 분당 90K tokens (gpt-4), 조정 필요시 백오프

**Key Dependencies:**
- LangGraph/LangChain: Multi-Agent 오케스트레이션
- OpenAI API: LLM 추론 (Claude/GPT)
- Redis: 대화 상태 체크포인팅
- pandas: Cross-DB 조인 처리

### Cross-Cutting Concerns Identified

1. **에러 처리 전략**
   - 에이전트별 독립 실패 처리 (Graceful Degradation)
   - 폴백 메커니즘: 부분 결과 반환
   - 사용자 친화적 에러 메시지

2. **로깅 및 모니터링**
   - 구조화 로깅 (JSON format)
   - 쿼리 실행 시간 추적
   - LLM 토큰 사용량 모니터링
   - 감사 로그 (데이터 접근 추적)

3. **보안 레이어**
   - Layer 1: Prompt Engineering (시스템 프롬프트 주입)
   - Layer 2: SQL Validation (화이트리스트, 패턴 검증)
   - Layer 3: Result Validation (행 수 제한, 민감 데이터 마스킹)
   - Layer 4: User Confirmation (위험 쿼리 확인)

4. **상태 관리**
   - Redis 기반 대화 컨텍스트 저장
   - LangGraph Checkpointing
   - 세션 TTL 관리

5. **인코딩 처리**
   - MSSQL 2005 EUC-KR → UTF-8 변환
   - 특수문자 이스케이프 처리
   - 다국어 지원 고려

6. **회로 차단기 (Circuit Breaker)**
   - 외부 서비스 호출 실패 시 연쇄 실패 방지
   - 데이터소스별 독립적 Circuit Breaker
   - 폴백: 캐시된 스키마 정보 사용

7. **테스트 가능성 전략**
   - LLM 응답: Golden Dataset + Semantic Similarity 검증
   - SQL Validation: 규칙 기반 단위 테스트 100% 커버리지
   - E2E: 대화 시나리오 기반 통합 테스트

## Starter Template Evaluation

### Primary Technology Domain

**Brownfield AI/ML Backend Integration** - 기존 FastAPI 3-Layer 아키텍처에 LangGraph 기반 AI 모듈 추가

### Integration Options Considered

| Option | 접근법 | 의존성 수 | 적합도 |
|--------|--------|-----------|--------|
| A | LangGraph 표준 | ~15 | ⭐⭐⭐ 권장 |
| B | + LangSmith | ~18 | ⭐⭐ 프로덕션용 |
| C | Minimal | ~8 | ⭐ 경량화 필요시 |

### Selected Approach: LangGraph 표준 통합 (Option A)

**Rationale for Selection:**
- 공식 문서와 예제 풍부 → 구현 리스크 최소화
- Redis Checkpointing 내장 → 대화 상태 관리 용이
- Supervisor 패턴 공식 지원 → Multi-Agent 오케스트레이션 검증됨
- Phase 확장성 → GA4 에이전트 추가 시 일관된 패턴

**Initialization Commands:**

```bash
# Core AI dependencies
uv add langchain langchain-openai langgraph langchain-community

# Database connectors
uv add aiomysql pymssql

# Utilities
uv add pandas redis
```

### Architectural Decisions Established

**Language & Runtime:**
- Python 3.11 (기존 유지)
- Type hints 필수 (mypy strict)
- Async-first with sync fallback (asyncio.to_thread)

**AI Framework:**
- LangGraph StateGraph for agent orchestration
- LangChain for LLM abstraction
- Redis for conversation checkpointing

**Code Organization:**
- 기존 3-Layer 패턴 준수
- `src/services/ai/` 하위에 AI 모듈 집중
- agents/, tools/, prompts/ 서브디렉토리 분리

**Integration Pattern:**
- FastAPI SSE endpoint for streaming
- Pydantic schemas for request/response validation
- Existing logging/monitoring infrastructure reuse

### Proposed Module Structure

```
src/
├── api/v1/
│   └── ai_assistant_api.py      # AI 어시스턴트 엔드포인트
├── services/
│   └── ai/                       # AI 서비스 레이어
│       ├── __init__.py
│       ├── graph.py              # LangGraph StateGraph 정의
│       ├── agents/
│       │   ├── supervisor.py     # Supervisor 에이전트
│       │   ├── mariadb_agent.py  # MariaDB 쿼리 에이전트
│       │   ├── mssql_agent.py    # MSSQL 쿼리 에이전트
│       │   └── ga4_agent.py      # GA4 에이전트 (Phase 2)
│       ├── tools/
│       │   ├── sql_validator.py  # SQL 검증 도구
│       │   └── schema_rag.py     # 스키마 RAG
│       └── prompts/
│           └── system_prompts.py # 시스템 프롬프트
├── repositories/
│   └── ai/                       # AI 관련 리포지토리
│       └── schema_repository.py  # 스키마 메타데이터
└── schemas/
    └── ai/                       # AI 스키마
        └── assistant_schema.py   # 요청/응답 스키마
```

**Note:** 첫 번째 구현 스토리에서 이 의존성 설치 및 기본 구조 생성 진행

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (구현 차단):**
- LLM 제공자 선택 → OpenAI gpt-4o-mini (+ Fallback)
- 에이전트 실행 패턴 → Adaptive (Supervisor 기반, 휴리스틱 명시)
- Schema RAG 저장소 → Redis + JSON

**Important Decisions (아키텍처 형성):**
- Cross-DB 조인 캐싱 전략 → No Cache + 동시성 제한
- SSE 스트리밍 구현 → FastAPI 네이티브
- Rate Limiting → 역할 기반 차등

**Deferred Decisions (Post-MVP):**
- 벡터 DB 도입 (ChromaDB) → Phase 3+ 검토
- LangSmith 모니터링 → 프로덕션 안정화 후 검토

### Data Architecture

| 결정 | 선택 | 버전 | 근거 |
|------|------|------|------|
| Schema RAG 저장소 | Redis + JSON | Redis 7 | 기존 인프라 활용, 추가 서비스 도입 불가 |
| Cross-DB 조인 캐싱 | No Cache | - | 관리자 BI 특성상 데이터 최신성 우선 |
| 대화 상태 저장 | Redis Checkpointing | Redis 7 | LangGraph 내장 기능 활용 |

**Schema 캐싱 전략:**
```python
# Redis key 패턴
schema:{db_type}:{table_name} → JSON (테이블 메타데이터)
schema:{db_type}:_index → JSON (전체 테이블 목록)
# TTL: 1시간 (스키마 변경 빈도 낮음)
```

**Cross-DB 조인 동시성 제한:**
- 최대 동시 Cross-DB 조인: **5개**
- 초과 시: 큐잉 또는 "잠시 후 재시도" 응답
- 구현: `asyncio.Semaphore(5)`

### AI Agent Architecture

| 결정 | 선택 | 버전 | 근거 |
|------|------|------|------|
| LLM 제공자 | OpenAI | gpt-4o-mini + fallback | 비용 효율성, LangChain 통합 안정성 |
| 에이전트 실행 패턴 | Adaptive | - | Supervisor가 쿼리 분석 후 순차/병렬 결정 |
| Checkpointing | Redis | Redis 7 | 대화 컨텍스트 지속성, 기존 인프라 |

**Adaptive 실행 판단 휴리스틱:**
```python
def decide_execution_pattern(query_analysis: QueryAnalysis) -> str:
    # 단일 데이터소스
    if len(query_analysis.data_sources) == 1:
        return "single"

    # Cross-reference 키워드 감지 (상담사코드, 회원ID 등)
    cross_ref_keywords = ["상담사", "회원", "counselor", "user", "조인", "연결"]
    if any(kw in query_analysis.user_query for kw in cross_ref_keywords):
        return "sequential"

    # 독립 쿼리는 병렬
    return "parallel"
```

**LLM 폴백 전략:**
| 우선순위 | 모델 | 조건 |
|----------|------|------|
| Primary | gpt-4o-mini | 기본 |
| Fallback | gpt-3.5-turbo | Primary 3회 실패 시 |
| Degraded | 에러 메시지 | 전체 실패 시 "AI 일시 불가" |

### API & Communication Patterns

| 결정 | 선택 | 버전 | 근거 |
|------|------|------|------|
| SSE 스트리밍 | FastAPI StreamingResponse | FastAPI 0.110+ | 네이티브 지원, 추가 의존성 없음 |
| Rate Limiting | 역할 기반 차등 | - | 기존 인증 시스템 활용 |
| 에러 응답 형식 | 기존 패턴 유지 | - | Brownfield 일관성 |

**Rate Limiting 정책:**
| 역할 | 제한 | 근거 |
|------|------|------|
| Super Admin | 60 req/min | 무제한에 가까운 사용 |
| Admin | 30 req/min | 일반적 업무 사용 |
| Viewer | 10 req/min | 제한적 조회 |

### Infrastructure & Monitoring

| 결정 | 선택 | 버전 | 근거 |
|------|------|------|------|
| LLM 모니터링 | 기존 로깅 확장 | - | 추가 인프라 도입 불가 |
| 에러 추적 | Sentry (기존) | - | 기존 인프라 활용 |
| 메트릭 수집 | 구조화 로깅 | JSON | 기존 패턴 유지 |

**LLM 호출 로깅 구조:**
```json
{
  "event": "llm_call",
  "model": "gpt-4o-mini",
  "tokens": {"prompt": 1500, "completion": 200},
  "latency_ms": 1200,
  "user_id": "admin_123",
  "session_id": "conv_abc",
  "success": true
}
```

### Decision Impact Analysis

**Implementation Sequence:**
1. Redis 스키마 캐시 구조 설계
2. LangGraph StateGraph 기본 구조
3. Supervisor 에이전트 (Adaptive 휴리스틱 + 폴백)
4. 개별 DB 에이전트 (MariaDB → MSSQL 순)
5. SSE 스트리밍 엔드포인트
6. Rate Limiting 미들웨어

**Cross-Component Dependencies:**
- Schema RAG → 모든 DB 에이전트가 의존
- Supervisor → 모든 하위 에이전트 조율
- Redis Checkpointing → 대화 상태 공유
- Rate Limiting → AI 엔드포인트 전체 적용
- Semaphore → Cross-DB 조인 동시성 제어

**SLA 충족 전략:**
- LLM 폴백으로 단일 장애점 제거
- 동시성 제한으로 리소스 고갈 방지
- Graceful Degradation으로 부분 서비스 유지

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 5개 영역에서 AI 에이전트 간 불일치 가능성 식별

### Naming Patterns

**AI 모듈 네이밍 규칙:**

| 대상 | 패턴 | 예시 |
|------|------|------|
| 에이전트 클래스 | `{DB}Agent` | `MariaDBAgent`, `MSSQLAgent` |
| 에이전트 파일 | `{db}_agent.py` | `mariadb_agent.py` |
| 도구 클래스 | `{기능}Tool` | `SQLValidatorTool` |
| 프롬프트 상수 | `{AGENT}_SYSTEM_PROMPT` | `SUPERVISOR_SYSTEM_PROMPT` |
| 상태 키 | `snake_case` | `query_result`, `execution_plan` |

**기존 패턴 준수:**
- 변수/함수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`

### Structure Patterns

**프롬프트 관리:** 별도 `prompts/` 디렉토리에 에이전트별 파일로 분리
- 프롬프트 튜닝 빈번 예상
- 코드 변경 없이 프롬프트만 수정 가능

**테스트 위치:** `tests/services/ai/` 하위에 미러링 구조
```
tests/services/ai/
├── conftest.py           # LLM Mock fixtures
├── test_graph.py
├── agents/
│   ├── test_supervisor.py
│   └── test_mariadb_agent.py
├── tools/
│   └── test_sql_validator.py
└── golden/               # Golden Dataset
    ├── queries.json
    └── sql_validation.json
```

### Format Patterns

**상태 타입:** `TypedDict` 사용 (LangGraph 공식 패턴)

**에이전트 출력 타입 계층:**
```python
# 메타데이터 공통 타입
class AgentMetadata(TypedDict):
    agent: str
    duration_ms: int
    timestamp: str

# 베이스 출력
class BaseAgentOutput(TypedDict):
    success: bool
    error: str | None
    metadata: AgentMetadata

# SQL 에이전트 출력 (MariaDB, MSSQL 공통)
class SQLResultData(TypedDict):
    rows: list[dict]
    columns: list[str]
    row_count: int

class SQLAgentOutput(BaseAgentOutput):
    data: SQLResultData | None
```

**프롬프트 버전 관리:**
```python
# prompts/supervisor.py
PROMPT_VERSION = "1.0.0"  # 시맨틱 버전
SUPERVISOR_SYSTEM_PROMPT = """..."""

# 로그에 버전 포함
logger.info("llm_call", extra={"prompt_version": PROMPT_VERSION, ...})
```

**SSE 이벤트 포맷:**
```json
{
  "event": "thinking|query|executing|result|error|done",
  "data": {
    "message": "상태 메시지",
    "agent": "에이전트명",
    "timestamp": "ISO8601"
  }
}
```

### Communication Patterns

**로깅 필수 필드:**
- `event`: 이벤트 유형
- `agent`: 에이전트 식별자
- `user_id`: 사용자 ID
- `session_id`: 대화 세션 ID
- `duration_ms`: 실행 시간
- `prompt_version`: 프롬프트 버전 (LLM 호출 시)

### Process Patterns

**에러 처리:**
- `AgentError` 클래스로 에이전트별 에러 래핑
- `recoverable` 플래그로 재시도 가능 여부 표시
- Supervisor에서 에러 집계 및 사용자 메시지 생성

**LLM 호출:**
- `call_llm_with_fallback()` 래퍼 함수 사용 필수
- Primary 3회 실패 시 Fallback 모델 전환
- 모든 호출에 타임아웃 설정 (30초)

**테스트 패턴:**

1. **LLM Mock Fixture**
```python
# tests/services/ai/conftest.py
@pytest.fixture
def mock_llm():
    """LLM 호출을 deterministic하게 만드는 fixture"""
    with patch("langchain_openai.ChatOpenAI") as mock:
        mock.return_value.invoke.return_value = AIMessage(content="mocked")
        yield mock
```

2. **Golden Dataset 테스트**
```json
// tests/services/ai/golden/queries.json
[
  {
    "input": "이번 달 매출",
    "expected_tables": ["payments"],
    "expected_type": "single"
  },
  {
    "input": "상담사별 회원 수",
    "expected_tables": ["members", "counselors"],
    "expected_type": "sequential"
  }
]
```

3. **프롬프트 회귀 테스트**
- 프롬프트 변경 시 기존 Golden Dataset 테스트 통과 필수
- CI에서 자동 검증

### Enforcement Guidelines

**All AI Agents MUST:**
- 에이전트 출력은 반드시 정의된 타입(`SQLAgentOutput` 등) 준수
- 모든 DB 쿼리 실행 전 `SQLValidatorTool` 통과
- SSE 이벤트는 정의된 `EVENT_TYPES` 내에서만 사용
- 에러 발생 시 `AgentError`로 래핑하여 상위 전파
- 프롬프트 변경 시 `PROMPT_VERSION` 업데이트

**스토리 AC 가이드:**

각 스토리에는 다음 AC 포함 권장:
- [ ] 에이전트 출력이 정의된 타입(`SQLAgentOutput` 등)을 준수한다
- [ ] `metadata`에 `duration_ms`, `agent`, `timestamp` 포함
- [ ] 에러 시 `AgentError`로 래핑되어 상위 전파
- [ ] 관련 Golden Dataset 테스트 케이스 추가됨
- [ ] 프롬프트 변경 시 `PROMPT_VERSION` 업데이트됨

**Pattern Verification:**
- PR 리뷰 시 패턴 준수 체크리스트 확인
- mypy strict 모드로 타입 검증
- 단위 테스트에서 출력 포맷 검증
- Golden Dataset 테스트 CI 자동 실행

## Project Structure & Boundaries

### Complete Project Directory Structure

```
src/services/ai/
├── __init__.py                 # AI 서비스 패키지 초기화
├── graph.py                    # LangGraph StateGraph 정의
├── state.py                    # AgentState, TypedDict 출력 타입
├── llm.py                      # LLM 클라이언트 + 폴백 래퍼
├── agents/
│   ├── __init__.py
│   ├── base.py                 # BaseAgent 추상 클래스
│   ├── supervisor.py           # Supervisor 에이전트 (오케스트레이터)
│   ├── mariadb_agent.py        # MariaDB Text-to-SQL 에이전트
│   ├── mssql_agent.py          # MSSQL Text-to-SQL 에이전트
│   └── ga4_agent.py            # GA4 에이전트 (Phase 2)
├── tools/
│   ├── __init__.py
│   ├── sql_validator.py        # SQL 화이트리스트 검증
│   ├── schema_loader.py        # Redis 스키마 로더
│   └── data_merger.py          # Cross-DB 조인 (pandas.merge)
├── security/
│   ├── __init__.py
│   ├── sql_whitelist.py        # 허용 테이블/컬럼 정의
│   ├── data_masking.py         # PII 마스킹 유틸리티
│   └── query_patterns.py       # 위험 패턴 감지
├── prompts/
│   ├── __init__.py
│   ├── supervisor.py           # Supervisor 시스템 프롬프트
│   └── sql_agent.py            # SQL 에이전트 공통 프롬프트
└── utils/
    ├── __init__.py
    ├── encoding.py             # EUC-KR ↔ UTF-8 변환
    └── sse.py                  # SSE 이벤트 헬퍼

src/api/v1/
└── ai_assistant_api.py         # AI 어시스턴트 SSE 엔드포인트

src/common/middleware/
└── ai_rate_limit.py            # AI 역할 기반 Rate Limiting

src/schemas/ai/
├── __init__.py
├── assistant_schema.py         # 요청/응답 Pydantic 스키마
└── conversation_schema.py      # 대화 상태 스키마

tests/services/ai/
├── conftest.py                 # LLM Mock fixtures
├── unit/
│   ├── test_state.py
│   ├── test_llm.py
│   ├── agents/
│   │   ├── test_supervisor.py
│   │   ├── test_mariadb_agent.py
│   │   └── test_mssql_agent.py
│   ├── tools/
│   │   ├── test_sql_validator.py
│   │   └── test_schema_loader.py
│   └── security/
│       ├── test_sql_whitelist.py
│       └── test_data_masking.py
├── integration/
│   ├── test_graph_flow.py      # StateGraph 통합 테스트
│   ├── test_cross_db_join.py   # Cross-DB 조인 시나리오
│   └── test_sse_streaming.py   # SSE 엔드포인트 테스트
└── golden/
    ├── queries.json            # 질의 분류 Golden Dataset
    ├── sql_validation.json     # SQL 검증 케이스
    └── responses.json          # 응답 생성 케이스

docs/ai-assistant/dev-guides/
├── adding-new-agent.md         # 새 에이전트 추가 가이드
├── prompt-tuning.md            # 프롬프트 튜닝 가이드
└── testing-guide.md            # 테스트 작성 가이드
```

### Architectural Boundaries

**API Boundaries:**
- `POST /api/v1/ai/chat` - SSE 스트리밍 대화 엔드포인트
- `GET /api/v1/ai/conversations/{id}` - 대화 이력 조회
- `DELETE /api/v1/ai/conversations/{id}` - 대화 삭제
- 모든 AI 엔드포인트는 `ai_rate_limit` 미들웨어 적용

**Service Boundaries:**
- `ai/` 모듈은 `services/` 내 독립 영역
- 외부 의존성: `common/logging`, `config/settings`, `core/database`
- 다른 도메인 서비스(`user`, `counselor` 등)와 직접 의존 없음

**Security Boundaries:**
- Layer 1 (Prompt): `prompts/` - 시스템 프롬프트에 보안 지침 내장
- Layer 2 (Validation): `security/sql_whitelist.py` + `tools/sql_validator.py`
- Layer 3 (Result): `security/data_masking.py` - 결과 내 PII 마스킹
- Layer 4 (User): API 레벨 확인 다이얼로그 (위험 쿼리 시)

**Data Boundaries:**
- MariaDB: `aiomysql` async 접근 (기존 connection pool 재사용)
- MSSQL: `pymssql` sync 접근 (`asyncio.to_thread()` 래핑)
- Redis: 스키마 캐시 + LangGraph Checkpointing
- Cross-DB 조인: 메모리 내 `pandas.merge()`, 결과 <100MB 제한

### Configuration Pattern

**기존 `settings.py`에 통합:**
```python
# src/config/settings.py
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # AI Assistant Settings
    ai_debug_mode: bool = False
    ai_llm_model: str = "gpt-4o-mini"
    ai_llm_fallback_model: str = "gpt-3.5-turbo"
    ai_llm_timeout: int = 30
    ai_rate_limit_super_admin: int = 60
    ai_rate_limit_admin: int = 30
    ai_rate_limit_viewer: int = 10
    ai_max_concurrent_cross_db: int = 5
    ai_schema_cache_ttl: int = 3600
```

**환경 변수 네이밍:**
- `AI_DEBUG_MODE`, `AI_LLM_MODEL`, `AI_LLM_TIMEOUT` 등
- 기존 환경 변수 패턴(`UPPER_SNAKE_CASE`) 준수

### Requirements to Structure Mapping

**Epic/FR 매핑:**

| FR 범위 | 기능 영역 | 매핑 위치 |
|---------|-----------|-----------|
| FR-001~010 | 질의 분류 | `agents/supervisor.py`, `prompts/supervisor.py` |
| FR-011~015 | MariaDB 에이전트 | `agents/mariadb_agent.py` |
| FR-016~020 | MSSQL 에이전트 | `agents/mssql_agent.py` |
| FR-021~030 | Cross-DB 조인 | `tools/data_merger.py` |
| FR-031~042 | 응답 생성/스트리밍 | `utils/sse.py`, API 레이어 |

**Cross-Cutting Concerns 매핑:**

| 관심사 | 매핑 위치 |
|--------|-----------|
| SQL Injection 방지 | `security/`, `tools/sql_validator.py` |
| 에러 처리 | `agents/base.py` (AgentError) |
| 로깅 | 기존 `common/logging/` 확장 |
| Rate Limiting | `common/middleware/ai_rate_limit.py` |
| 인코딩 변환 | `utils/encoding.py` |

### File Documentation Standard

**모든 AI 모듈 파일 docstring:**
```python
"""
{파일 설명}

Stories: {관련 스토리 ID}
FRs: {관련 FR ID}
"""
```

**예시:**
```python
# agents/mariadb_agent.py
"""
MariaDB Text-to-SQL 에이전트.

Schema RAG로 테이블 구조를 로드하고 자연어를 SQL로 변환합니다.

Stories: AI-002, AI-003
FRs: FR-011, FR-012, FR-013
"""
```

### Test Organization

**테스트 레벨:**

| 레벨 | 위치 | 목적 |
|------|------|------|
| Unit | `tests/services/ai/unit/` | 개별 함수/클래스 검증 |
| Integration | `tests/services/ai/integration/` | 에이전트 흐름 검증 |
| Golden | `tests/services/ai/golden/` | LLM 응답 일관성 검증 |

**Golden Dataset 구조:**
```json
// golden/queries.json
{
  "version": "1.0.0",
  "cases": [
    {
      "id": "Q001",
      "input": "이번 달 매출 알려줘",
      "expected": {
        "intent": "query",
        "data_sources": ["mariadb"],
        "execution_type": "single"
      }
    }
  ]
}
```

### Development Workflow Integration

**새 에이전트 추가 절차:**
1. `agents/` 하위에 `{name}_agent.py` 생성
2. `BaseAgent` 상속, `execute()` 구현
3. `prompts/` 하위에 프롬프트 파일 추가
4. `graph.py`에 노드 등록
5. `tests/unit/agents/` 에 단위 테스트 추가
6. Golden Dataset에 테스트 케이스 추가

**프롬프트 변경 절차:**
1. `prompts/` 파일 수정
2. `PROMPT_VERSION` 업데이트
3. Golden Dataset 테스트 실행
4. 회귀 없음 확인 후 PR

**상세 가이드:**
- `docs/ai-assistant/dev-guides/adding-new-agent.md`
- `docs/ai-assistant/dev-guides/prompt-tuning.md`
- `docs/ai-assistant/dev-guides/testing-guide.md`

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
모든 기술 선택이 충돌 없이 동작함:
- LangGraph + Redis Checkpointing: 공식 지원
- FastAPI SSE + LangGraph Streaming: 네이티브 통합
- aiomysql(async) + pymssql(sync): asyncio.to_thread() 패턴으로 해결

**Pattern Consistency:**
- 네이밍: snake_case/PascalCase 전 영역 일관
- 구조: 기존 3-Layer 패턴 준수
- 타입: TypedDict 기반 출력 타입 계층 통일
- 로깅: 기존 패턴 확장 (prompt_version, audit trail 추가)
- Import: 프로젝트 루트 기준 절대 경로 표준화

**Structure Alignment:**
- 프로젝트 구조가 모든 아키텍처 결정을 지원
- 경계가 명확히 정의됨 (API, Service, Security, Data)
- 테스트 구조가 소스 구조를 미러링
- 의존성 방향 규칙 정의됨 (상위→하위 단방향)

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
- FR-001~042: 전체 42개 FR이 아키텍처적으로 지원됨
- 각 FR 범위가 특정 모듈에 매핑됨

**Non-Functional Requirements Coverage:**
- 성능 (NFR-001~003): SSE 스트리밍, 캐싱, 병렬화로 지원
- 보안 (NFR-010): 4-Layer Security + Audit Trail로 완전 커버
- 호환성 (NFR-015): pymssql + TDS 7.0/7.1로 지원
- 가용성 (NFR-020): 4단계 Graceful Degradation + Feature Flag

### Implementation Readiness Validation ✅

**Decision Completeness:**
- 모든 Critical 결정에 버전 명시
- Adaptive 실행 휴리스틱 코드 예시 제공
- 폴백 전략 4단계 정의
- 의존성 주입 패턴 명시

**Structure Completeness:**
- 파일 레벨까지 전체 구조 정의
- 테스트 3-레벨 분리 (unit/integration/golden)
- 개발 가이드 3개 문서 명시
- Import 경로 패턴 표준화

**Pattern Completeness:**
- 네이밍, 구조, 통신, 프로세스 패턴 완비
- 출력 타입 계층 정의
- Golden Dataset 테스트 구조 + 버전 매핑
- 사용자 친화적 에러 구조

### Development Patterns

**Import 경로 표준:**
```python
# 절대 경로 (권장)
from src.services.ai.state import AgentState
from src.common.logging import get_logger

# 상대 경로 (같은 패키지 내)
from .base import BaseAgent
```

**의존성 주입:**
```python
class BaseAgent(ABC):
    def __init__(self, llm: ChatOpenAI, schema_loader: SchemaLoader, settings: Settings):
        ...

# FastAPI Depends 활용
def get_ai_graph(settings = Depends(get_settings), redis = Depends(get_redis)) -> AIGraph:
    ...
```

**Debug 모드 동작:**

| 설정 | ai_debug_mode=True | ai_debug_mode=False |
|------|-------------------|---------------------|
| 프롬프트 로깅 | 전체 | 요약만 |
| SQL 로깅 | 원문 | 마스킹 |
| SSE thinking | 포함 | 제외 |
| 에러 상세 | 전체 | 사용자용만 |

### Operational Patterns

**Health Check Endpoint:**
```
GET /api/v1/ai/health
Response: {status, components: {llm, redis, mariadb, mssql}, degradation_level}
```

**Feature Flags:**

| Flag | 기본값 | 용도 |
|------|--------|------|
| `ai_feature_enabled` | true | AI 전체 On/Off |
| `ai_cross_db_enabled` | true | Cross-DB 조인 On/Off |
| `ai_streaming_enabled` | true | SSE 스트리밍 On/Off |

### Error Handling Pattern

**에러 코드 체계:**

| 코드 | 의미 | 사용자 메시지 |
|------|------|--------------|
| AI_ERR_001 | LLM Timeout | 잠시 후 다시 시도해 주세요 |
| AI_ERR_002 | Invalid Query | 질문을 다르게 표현해 주세요 |
| AI_ERR_003 | DB Unavailable | 데이터 조회가 일시적으로 불가합니다 |
| AI_ERR_004 | Rate Limited | 요청이 너무 많습니다 |

**에러 구조:**
```python
class AIError:
    code: str              # AI_ERR_XXX
    technical_message: str # 로깅/디버그용
    user_message: str      # 사용자 표시용
    suggestion: str | None # 대안 제시
    recoverable: bool      # 재시도 가능 여부
```

### Dependency Direction Rules

```
API → Graph → Agents → Tools/Security → Common/Config
        ↓
   (단방향만 허용)
        ↓
❌ Tools → Agents (금지)
❌ Agents → Graph (금지)
❌ 순환 참조 (금지)
```

### Test Coverage Targets

| 영역 | 목표 | 필수 |
|------|------|------|
| Security 모듈 | 100% | ✅ |
| SQL Validator | 100% | ✅ |
| Unit Tests 전체 | 80%+ | 권장 |
| Integration | 주요 흐름 | 권장 |
| Golden Dataset | 50+ 케이스 | 권장 |

### Graceful Degradation Strategy

| Level | 조건 | 동작 | 사용자 영향 |
|-------|------|------|-------------|
| 1 | LLM Primary 실패 | Fallback 모델 전환 | 없음 |
| 2 | Cross-DB 과부하 | 단일 DB만 허용 | 복합 분석 제한 알림 |
| 3 | LLM 전체 실패 | 캐시 기반 응답 | 기본 정보만 제공 알림 |
| 4 | 시스템 장애 | 에러 메시지 | 서비스 불가 알림 |

### Timeout Hierarchy

| 레벨 | 설정 | 기본값 |
|------|------|--------|
| LLM Call | `ai_timeout_llm_call` | 30초 |
| Single Agent | `ai_timeout_single_agent` | 45초 |
| Full Request | `ai_timeout_request` | 60초 |
| SSE Keepalive | `ai_sse_keepalive_interval` | 15초 |

### Security Audit Trail

**필수 로깅 필드:** user_id, session_id, query_text, tables_accessed, row_count, timestamp

**Session 바인딩:** Redis Key `ai:session:{user_id}:{conversation_id}`, 로드 시 사용자 검증 필수

### Test Strategy Enhancement

**Golden Dataset 버전 관리:**
- `compatible_prompt_versions` 필드로 프롬프트-테스트 매핑
- `semantic_similarity_threshold: 0.85` (85% 유사도 통과)

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] 프로젝트 컨텍스트 철저 분석
- [x] 규모 및 복잡도 평가 (High)
- [x] 기술 제약 식별 (MSSQL 2005, 인프라 추가 불가)
- [x] Cross-cutting 관심사 7개 매핑

**✅ Architectural Decisions**
- [x] Critical 결정 버전과 함께 문서화
- [x] 기술 스택 완전 명시
- [x] 통합 패턴 정의 (Supervisor, Adaptive)
- [x] 성능 고려사항 반영 (Timeout 계층, 동시성)

**✅ Implementation Patterns**
- [x] 네이밍 규칙 확립
- [x] Import 경로 패턴 표준화
- [x] 의존성 주입 패턴 명시
- [x] 의존성 방향 규칙 정의
- [x] 에러 처리 패턴 (사용자 친화적)

**✅ Project Structure**
- [x] 완전한 디렉토리 구조 정의
- [x] 컴포넌트 경계 확립
- [x] 통합 지점 매핑
- [x] 요구사항-구조 매핑 완료

**✅ Security & Compliance**
- [x] 4-Layer Security 정의
- [x] Audit Trail 로깅 구조
- [x] Session 바인딩 검증

**✅ Operational Readiness**
- [x] Health Check 엔드포인트 정의
- [x] Feature Flag 전략
- [x] Graceful Degradation 4단계
- [x] Debug 모드 동작 명시

**✅ Testing Strategy**
- [x] 3-Level 테스트 구조
- [x] 커버리지 목표 정의
- [x] Golden Dataset 버전 매핑
- [x] Semantic Similarity 임계값

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION ✅

**Confidence Level:** High
- 모든 검증 항목 통과
- Critical 갭 없음
- Party Mode 2회 리뷰로 완전 보완
- 개발자/운영/품질 관점 모두 반영

**Key Strengths:**
1. 기존 3-Layer 아키텍처와 완전 통합
2. 4-Layer Security + Audit Trail로 보안 강화
3. 4단계 Graceful Degradation + Feature Flag로 운영 안정성
4. 의존성 주입 + 방향 규칙으로 테스트 용이성 확보
5. 사용자 친화적 에러 체계로 UX 개선
6. Health Check로 운영 모니터링 지원
7. 기존 인프라만 활용 (Redis, 기존 로깅)

**Areas for Future Enhancement:**
1. Phase 2: GA4 Agent, 질의 예시 제공, 피드백 수집
2. Phase 3+: 벡터 DB (ChromaDB), LangSmith 검토
3. 문서: Quick Reference Card 추가

### Implementation Handoff

**AI Agent Guidelines:**
- 모든 아키텍처 결정을 문서 그대로 따를 것
- Import 경로, 의존성 주입 패턴 준수
- 의존성 방향 규칙 준수 (상위→하위 단방향)
- Timeout 계층 구조 적용
- Audit Trail 로깅 필수
- 사용자 친화적 에러 메시지 적용
- Security 모듈 100% 테스트 커버리지 필수

**First Implementation Priority:**
1. `src/services/ai/state.py` - AgentState, 출력 타입
2. `src/services/ai/llm.py` - LLM 클라이언트 + 폴백 + Timeout
3. `src/services/ai/errors.py` - AIError 클래스 + 에러 코드
4. `src/services/ai/agents/base.py` - BaseAgent (DI 패턴)
5. `src/services/ai/tools/schema_loader.py` - Redis 스키마 로더
6. `src/services/ai/security/` - 보안 모듈 (100% 테스트)
7. `src/api/v1/ai_assistant_api.py` - Health Check + Feature Flag

---

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2026-01-30
**Document Location:** `_bmad-output/planning-artifacts/architecture.md`

### Final Architecture Deliverables

**📋 Complete Architecture Document**
- 모든 아키텍처 결정이 버전과 함께 문서화됨
- AI 에이전트 일관성을 위한 구현 패턴 정의
- 전체 파일 및 디렉토리를 포함한 프로젝트 구조
- 요구사항-아키텍처 매핑 완료
- 일관성과 완전성을 확인하는 검증 완료

**🏗️ Implementation Ready Foundation**
- 15+ 아키텍처 결정
- 10+ 구현 패턴 정의
- 20+ 아키텍처 컴포넌트
- FR 42개 + NFR 33개 완전 지원

**📚 AI Agent Implementation Guide**
- 검증된 버전이 포함된 기술 스택
- 구현 충돌을 방지하는 일관성 규칙
- 명확한 경계가 있는 프로젝트 구조
- 통합 패턴 및 통신 표준

### Project Success Factors

**🎯 Clear Decision Framework**
모든 기술 선택이 명확한 근거와 함께 협업으로 결정됨

**🔧 Consistency Guarantee**
구현 패턴과 규칙이 여러 AI 에이전트가 호환되고 일관된 코드를 생성하도록 보장

**📋 Complete Coverage**
모든 프로젝트 요구사항이 아키텍처적으로 지원됨

**🔒 Security & Operations**
4-Layer Security, Audit Trail, 4단계 Degradation, Feature Flag로 운영 안정성 확보

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** 본 문서의 아키텍처 결정 및 패턴을 기반으로 구현 시작

**Document Maintenance:** 구현 중 주요 기술 결정이 있을 경우 이 아키텍처 문서 업데이트

