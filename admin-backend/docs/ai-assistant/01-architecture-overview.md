# AI 관리자 어시스턴트 - 아키텍처 개요

> **문서 버전**: 1.1.0
> **최종 수정**: 2026-01-29
> **상태**: 설계 단계
> **관련 문서**: [리스크 평가](./04-risk-mitigation.md) | [GA4 연동](./05-ga4-integration.md)

---

## 1. 프로젝트 개요

### 1.1 목표
LangGraph 기반 멀티 에이전트 시스템을 구축하여, 사이트 관리자가 **자연어로 이기종 DB를 조회**하고 **인사이트 보고서**를 받을 수 있는 대화형 BI 어시스턴트 서비스 구현

### 1.2 핵심 특징
- **대화형 인터페이스**: 정적 보고서가 아닌 문답식 AI 대화
- **멀티 DB 통합 조회**: MariaDB + MSSQL 2005 + GA4 (향후)
- **프로액티브 인사이트**: 답변 후 후속 분석 자동 제안
- **읽기 전용 보안**: DB 수정 절대 불가, 조회만 허용

### 1.3 주요 사용자
- 사이트 관리자 (Admin)

### 1.4 예상 질의 유형
| 유형 | 예시 질문 | 데이터 소스 |
|------|----------|------------|
| 매출 분석 | "오늘 매출 얼마야?" | MariaDB |
| 유저 행동 | "이번 달 VIP 유저 누구야?" | MariaDB |
| 상담사 성과 | "김철수 상담사 이번 주 상담시간?" | MSSQL |
| 크로스 분석 | "매출 상위 상담사의 평균 상담시간?" | MariaDB + MSSQL |
| 유입 분석 | "결제 유저 중 어떤 유입 경로가 전환율 높아?" | MariaDB + GA4 |

---

## 2. 핵심 요구사항 (First Principles)

### 2.1 도출된 근본적 진실

| # | 근본 진실 | 시스템 영향 |
|---|-----------|------------|
| 1 | 보고서가 아닌 **대화형 BI** | 문답 UI + 스트리밍 응답 |
| 2 | **크로스 DB 조인** 필수 | 메모리 내 조인 또는 가상 뷰 |
| 3 | tm60_chatlog가 **진실의 원천** | 이 테이블 중심 쿼리 설계 |
| 4 | **읽기 전용** 절대 원칙 | DB/코드 이중 보안 |
| 5 | **인사이트 → 액션** 흐름 | 후속 분석 제안 로직 |
| 6 | **GA4 통합** 확장 | 멀티 소스 에이전트 |

### 2.2 데이터 소스 구성

```
┌─────────────── MariaDB (주 데이터) ───────────────┐
│  t_user          - 유저 프로필, 상태              │
│  t_counselor     - 상담사 프로필, 등급            │
│  t_payment       - 결제/매출 내역                 │
│  t_point_product - 포인트 상품                    │
│  ...기타 테이블                                   │
└──────────────────────────────────────────────────┘

┌─────────────── MSSQL 2005 (ARS) ─────────────────┐
│  tm60_member     - 상담사 ARS 정보               │
│  tm60_users      - 유저 ARS 정보                 │
│  tm60_chatlog    - 상담 로그, 포인트, 시간 ★핵심 │
└──────────────────────────────────────────────────┘

┌─────────────── GA4 (Phase 2) ────────────────────┐
│  유입 경로, 페이지뷰, 세션, 전환 퍼널            │
└──────────────────────────────────────────────────┘
```

### 2.3 크로스 DB 연결 키

| 엔티티 | MariaDB | MSSQL | 연결 키 |
|--------|---------|-------|---------|
| 상담사 | `t_counselor.counselor_code` | `tm60_member.m_code` | counselor_code = m_code |
| 유저 | `t_user.user_id` | `tm60_users.u_id` | user_id = u_id |
| 상담로그 | - | `tm60_chatlog.m_code`, `tm60_chatlog.u_id` | 위 키로 조인 |

---

## 3. 아키텍처 선택 (Morphological Analysis)

### 3.1 선택된 조합: "확장 가능한 멀티 에이전트" (조합 B)

| 파라미터 | 최종 선택 | 구현 방식 |
|----------|----------|----------|
| **쿼리 생성** | Schema-aware RAG + Few-shot | ChromaDB + 프롬프트 예시 |
| **DB 연결** | 병렬 조회 | asyncio.gather + run_in_executor |
| **에이전트 구조** | 멀티 에이전트 (DB별 1:1) | LangGraph StateGraph |
| **Supervisor** | 오케스트레이터형 | Task 분할 → 병렬 실행 → 통합 |
| **응답 형식** | 스트리밍 + 테이블 | SSE + Markdown 테이블 |
| **크로스 조인** | pandas + 템플릿 | merge() + 사전정의 패턴 |
| **보안** | 이중 + 결과 필터링 | SQL 검증 + DB 권한 + 마스킹 |

### 3.2 Supervisor 전략: 오케스트레이터형

```
[자연어 질문] → [Supervisor: 작업 분할]
                       │
               ┌───────┼───────┐
               ▼       ▼       ▼
           [Task1] [Task2] [Task3]  ← 병렬 실행
               │       │       │
               └───────┼───────┘
                       ▼
             [Aggregator: 결과 통합]
                       ▼
             [Synthesizer: 인사이트 도출]
```

**장점**:
- 복잡한 크로스 DB 분석 자연스럽게 처리
- "매출 떨어졌네 → 원인 분석" 같은 후속 분석 제안 가능
- GA4 등 새 데이터 소스 추가 시 확장 용이

---

## 4. 시스템 아키텍처

### 4.1 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🎯 Admin BI Assistant                                │
│                     (LangGraph Orchestrator)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  📥 INPUT LAYER                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐                │
│  │ 자연어 질문  │ →  │ Query Parser │ →  │ Intent Classifier│               │
│  └─────────────┘    └──────────────┘    └─────────────────┘                │
│                               │                   │                        │
│                               ▼                   ▼                        │
│                    ┌─────────────────────────────────────┐                 │
│                    │     Task Decomposer (작업 분할)     │                 │
│                    └─────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🤖 AGENT LAYER (병렬 실행)                                                 │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ 📊 MariaDB Agent│  │ 📞 MSSQL Agent  │  │ 📈 GA4 Agent    │            │
│  │                 │  │                 │  │   (Phase 2)     │            │
│  │ • 매출/결제     │  │ • 상담 로그     │  │ • 유입 경로     │            │
│  │ • 유저 프로필   │  │ • 포인트 사용   │  │ • 페이지뷰      │            │
│  │ • 상담사 정보   │  │ • 상담 시간     │  │ • 전환율        │            │
│  │ [Async Engine]  │  │ [Sync Engine]   │  │ [GA4 API]       │            │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │
│           │                    │                    │                      │
│           ▼                    ▼                    ▼                      │
│  ┌─────────────────────────────────────────────────────────────────┐      │
│  │                    🛡️ Security Layer                            │      │
│  │  • SQL Parser (SELECT만 허용)                                   │      │
│  │  • Whitelist Validator                                          │      │
│  │  • Read-Only DB User (DB 레벨 권한)                             │      │
│  └─────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔗 AGGREGATION LAYER                                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐      │
│  │                    Cross-DB Joiner                              │      │
│  │                                                                 │      │
│  │   MariaDB 결과 ──┐       ┌── MSSQL 결과                        │      │
│  │                  ▼       ▼                                      │      │
│  │            ┌─────────────────┐                                  │      │
│  │            │  pandas.merge() │  ← counselor_code = m_code      │      │
│  │            │  메모리 조인     │  ← user_id = u_id               │      │
│  │            └─────────────────┘                                  │      │
│  │                    │                                            │      │
│  │                    ▼                                            │      │
│  │            ┌─────────────────┐                                  │      │
│  │            │ 통합 DataFrame  │                                  │      │
│  │            └─────────────────┘                                  │      │
│  └─────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  💬 OUTPUT LAYER                                                            │
│                                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────────────┐       │
│  │ Response Synthesizer│ →  │ 📝 자연어 응답                      │       │
│  └─────────────────────┘    │ "이번 달 총 매출은 1,234만원입니다" │       │
│                              │                                     │       │
│  ┌─────────────────────┐    │ 📊 데이터 테이블 (Markdown)         │       │
│  │ Proactive Suggester │ →  │                                     │       │
│  └─────────────────────┘    │ 💡 후속 분석 제안                   │       │
│                              │ • "상담사별 매출 비교할까요?"       │       │
│                              └─────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 LangGraph 플로우

```python
# 개념적 LangGraph 구조
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# 노드 정의
workflow.add_node("parse_query", parse_query_node)
workflow.add_node("decompose_tasks", task_decomposer_node)
workflow.add_node("mariadb_agent", mariadb_agent_node)
workflow.add_node("mssql_agent", mssql_agent_node)
workflow.add_node("aggregate_results", aggregator_node)
workflow.add_node("synthesize_response", synthesizer_node)

# 엣지 정의
workflow.add_edge("parse_query", "decompose_tasks")
workflow.add_conditional_edges(
    "decompose_tasks",
    route_to_agents,  # 필요한 에이전트로 라우팅
    {
        "mariadb_only": "mariadb_agent",
        "mssql_only": "mssql_agent",
        "both": "parallel_agents",  # 병렬 실행
    }
)
workflow.add_edge("aggregate_results", "synthesize_response")
workflow.add_edge("synthesize_response", END)
```

---

## 5. 프로젝트 구조

### 5.1 디렉토리 구조 (제안)

```
src/
├── ai/                          # 🆕 AI 어시스턴트 모듈
│   ├── __init__.py
│   ├── config.py               # LLM 설정 (OpenAI/Claude)
│   │
│   ├── agents/                 # 에이전트 정의
│   │   ├── __init__.py
│   │   ├── supervisor.py       # 오케스트레이터 Supervisor
│   │   ├── mariadb_agent.py    # MariaDB 전문 에이전트
│   │   ├── mssql_agent.py      # MSSQL 전문 에이전트
│   │   └── ga4_agent.py        # GA4 에이전트 (Phase 2)
│   │
│   ├── graphs/                 # LangGraph 정의
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # 메인 그래프 (StateGraph)
│   │   └── nodes.py            # 노드 함수들
│   │
│   ├── tools/                  # 에이전트 도구
│   │   ├── __init__.py
│   │   ├── sql_generator.py    # Text-to-SQL (Few-shot + RAG)
│   │   ├── sql_validator.py    # SQL 보안 검증
│   │   ├── db_executor.py      # DB 실행기 (async/sync 통합)
│   │   └── cross_joiner.py     # pandas 크로스 조인
│   │
│   ├── schemas/                # RAG용 스키마 문서
│   │   ├── mariadb_schema.md   # MariaDB 테이블 설명
│   │   ├── mssql_schema.md     # MSSQL 테이블 설명
│   │   └── join_patterns.md    # 자주 쓰는 조인 패턴
│   │
│   └── prompts/                # 프롬프트 템플릿
│       ├── supervisor.py
│       ├── sql_generation.py
│       └── response_synthesis.py
│
├── api/v1/
│   └── ai_assistant_api.py     # 🆕 AI 어시스턴트 API 엔드포인트
│
├── models/ars/
│   └── tm60_chatlog_model.py   # 🆕 추가 필요
│
└── ... (기존 구조 유지)
```

### 5.2 추가 필요 의존성

```toml
# pyproject.toml에 추가
dependencies = [
    # ... 기존 의존성 ...

    # LangChain / LangGraph
    "langchain>=0.1.0",
    "langchain-openai>=0.0.5",      # 또는 langchain-anthropic
    "langgraph>=0.0.20",

    # RAG (스키마 임베딩)
    "chromadb>=0.4.0",              # 벡터 DB (로컬)
    "tiktoken>=0.5.0",              # 토큰 카운팅

    # GA4 (Phase 2)
    # "google-analytics-data>=0.18.0",
]
```

---

## 6. 구현 로드맵

### Phase 1: MVP (기본 기능)
- [ ] tm60_chatlog 모델 추가
- [ ] LangGraph 기본 구조 구축
- [ ] MariaDB Agent 구현
- [ ] MSSQL Agent 구현
- [ ] 단일 DB 질의 지원
- [ ] 기본 응답 생성

### Phase 2: 크로스 DB 지원
- [ ] Cross-DB Joiner 구현
- [ ] pandas 메모리 조인
- [ ] 자주 쓰는 조인 패턴 템플릿화
- [ ] 크로스 DB 질의 지원

### Phase 3: 고도화
- [ ] GA4 Agent 추가
- [ ] 프로액티브 인사이트 제안
- [ ] 스트리밍 응답
- [ ] 응답 캐싱

---

## 7. 참고 문서

- [02-constraints.md](./02-constraints.md) - 기술적 제약사항 (작성 예정)
- [03-security.md](./03-security.md) - 보안 설계 (작성 예정)
- [04-api-spec.md](./04-api-spec.md) - API 명세 (작성 예정)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-29 | 초기 아키텍처 설계 (브레인스토밍 결과) |
| 1.1.0 | 2026-01-29 | GA4 Agent, 리스크 평가 문서 연결 추가 |
