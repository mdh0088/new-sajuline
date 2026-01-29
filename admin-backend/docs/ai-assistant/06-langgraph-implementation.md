# AI 관리자 어시스턴트 - LangGraph 구현 설계

> **문서 버전**: 1.0.0
> **최종 수정**: 2026-01-29
> **상태**: 설계 단계
> **관련 문서**: [아키텍처 개요](./01-architecture-overview.md) | [구현 로드맵](./03-implementation-roadmap.md)

---

## 1. 개요

LangGraph StateGraph 기반 멀티 에이전트 오케스트레이션 구현 설계서입니다.

### 1.1 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **단일 책임** | 각 노드는 하나의 명확한 역할만 수행 |
| **타입 안전성** | TypedDict 기반 상태 정의로 IDE 지원 |
| **병렬 처리** | asyncio.gather로 DB 조회 병렬화 |
| **Graceful Degradation** | 부분 실패 허용, 가능한 결과 반환 |
| **스트리밍 UX** | SSE로 실시간 진행 상태 전달 |

---

## 2. AgentState 설계

### 2.1 상태 타입 정의

```python
from typing import TypedDict, Optional
from pandas import DataFrame

class Task(TypedDict):
    """분할된 작업 단위"""
    id: str
    db: str                    # "mariadb" | "mssql" | "ga4"
    action: str                # "query" | "aggregate" | "join"
    description: str
    sql: Optional[str]
    params: dict

class AgentState(TypedDict):
    """LangGraph 전체 상태"""

    # ===== 입력 =====
    query: str                          # 원본 자연어 질문
    session_id: str                     # 대화 세션 ID

    # ===== 분석 결과 =====
    intent: str                         # 의도 분류
                                        # - "sales_query": 매출 조회
                                        # - "counselor_analysis": 상담사 분석
                                        # - "user_analysis": 유저 분석
                                        # - "cross_analysis": 크로스 DB 분석
                                        # - "traffic_analysis": 유입 분석

    required_dbs: list[str]             # 필요한 DB 목록
                                        # ["mariadb", "mssql", "ga4"]

    decomposed_tasks: list[Task]        # 분할된 작업들
    generated_sqls: dict[str, str]      # DB별 생성된 SQL

    # ===== 실행 결과 =====
    mariadb_result: Optional[DataFrame]
    mssql_result: Optional[DataFrame]
    ga4_result: Optional[DataFrame]
    merged_result: Optional[DataFrame]  # 크로스 조인 결과

    # ===== 출력 =====
    response: str                       # 자연어 응답
    data_table: Optional[str]           # Markdown 테이블
    suggestions: list[str]              # 후속 분석 제안 (최대 3개)

    # ===== 메타 정보 =====
    errors: list[str]                   # 발생한 에러들
    warnings: list[str]                 # 경고 메시지들
    execution_time: float               # 총 실행 시간 (초)
    token_usage: dict                   # LLM 토큰 사용량
```

---

## 3. 노드 플로우 설계

### 3.1 전체 노드 구조

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        LangGraph 노드 플로우                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐                                                             │
│  │  START  │                                                             │
│  └────┬────┘                                                             │
│       ▼                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐       │
│  │ parse_query │ →  │ classify_intent  │ →  │ decompose_tasks   │       │
│  │ (질문 파싱) │    │ (의도 분류)      │    │ (작업 분할)       │       │
│  └─────────────┘    └──────────────────┘    └─────────┬─────────┘       │
│                                                       │                  │
│                              ┌────────────────────────┼────────────────┐ │
│                              │ (conditional routing)  │                │ │
│                              ▼                        ▼                ▼ │
│                     ┌────────────────┐    ┌────────────────┐    ┌─────────────┐
│                     │ mariadb_agent  │    │  mssql_agent   │    │  ga4_agent  │
│                     │ (SQL 생성/실행)│    │ (SQL 생성/실행)│    │ (API 조회)  │
│                     └───────┬────────┘    └───────┬────────┘    └──────┬──────┘
│                             │                     │                    │ │
│                             └─────────────────────┼────────────────────┘ │
│                                                   ▼                      │
│                                        ┌───────────────────┐             │
│                                        │ aggregate_results │             │
│                                        │ (결과 수집)       │             │
│                                        └─────────┬─────────┘             │
│                                                  │                       │
│                    ┌─────────────────────────────┼─────────────────────┐ │
│                    ▼                             ▼                     ▼ │
│          ┌─────────────────┐          ┌─────────────────┐    ┌──────────────────┐
│          │   cross_join    │          │ validate_result │    │  detect_anomaly  │
│          │ (크로스 DB 조인)│          │ (결과 검증)     │    │  (이상치 탐지)   │
│          └────────┬────────┘          └────────┬────────┘    └────────┬─────────┘
│                   │                            │                      │ │
│                   └────────────────────────────┼──────────────────────┘ │
│                                                ▼                        │
│                                     ┌─────────────────────┐             │
│                                     │ synthesize_response │             │
│                                     │ (응답 생성)         │             │
│                                     └──────────┬──────────┘             │
│                                                ▼                        │
│                                     ┌─────────────────────┐             │
│                                     │ generate_suggestions│             │
│                                     │ (후속 제안 생성)    │             │
│                                     └──────────┬──────────┘             │
│                                                ▼                        │
│                                           ┌─────────┐                   │
│                                           │   END   │                   │
│                                           └─────────┘                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 노드별 상세 설명

| 노드 | 입력 | 출력 | 역할 |
|------|------|------|------|
| `parse_query` | query | parsed_query | 자연어 질문 정규화, 토큰화 |
| `classify_intent` | parsed_query | intent, required_dbs | 의도 분류, 필요 DB 결정 |
| `decompose_tasks` | intent, required_dbs | decomposed_tasks | 작업 분할, SQL 생성 |
| `mariadb_agent` | tasks | mariadb_result | MariaDB SQL 실행 |
| `mssql_agent` | tasks | mssql_result | MSSQL SQL 실행 |
| `ga4_agent` | tasks | ga4_result | GA4 API 조회 |
| `aggregate_results` | *_results | collected_results | 결과 수집 |
| `cross_join` | collected_results | merged_result | pandas 크로스 조인 |
| `validate_result` | merged_result | validated_result | 결과 검증 (row 수, 타입) |
| `detect_anomaly` | validated_result | warnings | 이상치 탐지 |
| `synthesize_response` | validated_result | response, data_table | 자연어 응답 생성 |
| `generate_suggestions` | response, intent | suggestions | 후속 분석 제안 |

---

## 4. 조건부 라우팅

### 4.1 라우팅 로직

```python
from typing import Sequence
from langgraph.graph import StateGraph, END

def route_to_agents(state: AgentState) -> Sequence[str]:
    """
    필요한 DB 에이전트로만 라우팅

    Returns:
        라우팅할 노드 이름들 (병렬 실행됨)
    """
    routes = []

    for db in state["required_dbs"]:
        if db == "mariadb":
            routes.append("mariadb_agent")
        elif db == "mssql":
            routes.append("mssql_agent")
        elif db == "ga4":
            routes.append("ga4_agent")

    # 빈 경우 에러 노드로
    if not routes:
        return ["error_handler"]

    return routes

# 그래프에 조건부 엣지 추가
workflow.add_conditional_edges(
    "decompose_tasks",
    route_to_agents,
    {
        "mariadb_agent": "mariadb_agent",
        "mssql_agent": "mssql_agent",
        "ga4_agent": "ga4_agent",
        "error_handler": "error_handler",
    }
)
```

### 4.2 의도별 라우팅 예시

| 질문 예시 | intent | required_dbs | 라우팅 |
|----------|--------|--------------|--------|
| "오늘 매출 얼마야?" | sales_query | ["mariadb"] | mariadb_agent |
| "김철수 상담시간" | counselor_analysis | ["mssql"] | mssql_agent |
| "매출 상위 상담사 상담시간" | cross_analysis | ["mariadb", "mssql"] | 둘 다 (병렬) |
| "카카오 유입 전환율" | traffic_analysis | ["mariadb", "ga4"] | 둘 다 (병렬) |

---

## 5. 병렬 실행 및 에러 처리

### 5.1 병렬 실행 구현

```python
import asyncio
from typing import Any

async def execute_agents_parallel(
    state: AgentState,
    agents: dict[str, callable]
) -> dict[str, Any]:
    """
    에이전트들을 병렬로 실행

    Args:
        state: 현재 상태
        agents: {db_name: agent_function} 매핑

    Returns:
        {db_name: result} 매핑
    """
    tasks = {}

    for db in state["required_dbs"]:
        if db in agents:
            tasks[db] = asyncio.create_task(
                execute_with_timeout(agents[db], state, timeout=10)
            )

    results = {}
    errors = []

    for db, task in tasks.items():
        try:
            results[db] = await task
        except asyncio.TimeoutError:
            errors.append(f"{db} 조회 타임아웃 (10초 초과)")
            results[db] = None
        except Exception as e:
            errors.append(f"{db} 오류: {str(e)}")
            results[db] = None

    return results, errors
```

### 5.2 Graceful Degradation

```python
async def aggregate_results_node(state: AgentState) -> AgentState:
    """
    결과 수집 및 부분 실패 처리
    """
    results = {
        "mariadb": state.get("mariadb_result"),
        "mssql": state.get("mssql_result"),
        "ga4": state.get("ga4_result"),
    }

    # 성공한 결과 수
    success_count = sum(1 for r in results.values() if r is not None)
    total_required = len(state["required_dbs"])

    if success_count == 0:
        # 완전 실패
        state["errors"].append("모든 데이터 소스 조회 실패")
        state["response"] = "죄송합니다. 데이터를 조회할 수 없습니다."
    elif success_count < total_required:
        # 부분 성공
        failed_dbs = [db for db in state["required_dbs"]
                      if results.get(db) is None]
        state["warnings"].append(
            f"일부 데이터 소스 조회 실패: {', '.join(failed_dbs)}"
        )

    return state
```

---

## 6. SSE 스트리밍

### 6.1 스트리밍 응답 구조

```python
from typing import AsyncGenerator
import json

class StreamEvent:
    """스트리밍 이벤트 타입"""
    STATUS = "status"       # 진행 상태
    PARTIAL = "partial"     # 부분 결과
    WARNING = "warning"     # 경고
    FINAL = "final"         # 최종 응답

async def stream_bi_response(
    query: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    """
    SSE 형식으로 응답 스트리밍

    Yields:
        SSE 형식의 이벤트 문자열
    """
    state = AgentState(query=query, session_id=session_id)

    # 1. 질문 분석
    yield format_sse(StreamEvent.STATUS, "질문 분석 중...")
    state = await parse_query_node(state)
    state = await classify_intent_node(state)

    yield format_sse(StreamEvent.STATUS,
        f"분석 완료: {state['intent']} → {state['required_dbs']}")

    # 2. 작업 분할
    yield format_sse(StreamEvent.STATUS, "쿼리 생성 중...")
    state = await decompose_tasks_node(state)

    # 3. 데이터 조회
    yield format_sse(StreamEvent.STATUS, "데이터 조회 중...")

    for db in state["required_dbs"]:
        yield format_sse(StreamEvent.STATUS, f"{db} 조회 중...")

        try:
            result = await execute_agent(db, state)
            state[f"{db}_result"] = result
            yield format_sse(StreamEvent.PARTIAL, {
                "db": db,
                "rows": len(result) if result is not None else 0,
                "status": "success"
            })
        except Exception as e:
            yield format_sse(StreamEvent.WARNING, f"{db} 조회 실패: {e}")

    # 4. 결과 통합
    yield format_sse(StreamEvent.STATUS, "결과 분석 중...")
    state = await aggregate_results_node(state)

    if len(state["required_dbs"]) > 1:
        state = await cross_join_node(state)

    # 5. 응답 생성
    yield format_sse(StreamEvent.STATUS, "응답 생성 중...")
    state = await synthesize_response_node(state)
    state = await generate_suggestions_node(state)

    # 6. 최종 응답
    yield format_sse(StreamEvent.FINAL, {
        "response": state["response"],
        "data_table": state.get("data_table"),
        "suggestions": state["suggestions"],
        "warnings": state.get("warnings", []),
        "execution_time": state["execution_time"]
    })

def format_sse(event_type: str, data: any) -> str:
    """SSE 형식으로 포맷팅"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
```

### 6.2 FastAPI 엔드포인트

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    AI BI 어시스턴트 스트리밍 응답
    """
    return StreamingResponse(
        stream_bi_response(request.query, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

## 7. 상태 저장 (Checkpointing)

### 7.1 Redis Checkpointer 설정

```python
from langgraph.checkpoint.redis import RedisSaver
from redis.asyncio import Redis

# Redis 연결
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_AI_DB,  # AI 전용 DB
    decode_responses=True
)

# Checkpointer 생성
checkpointer = RedisSaver(redis_client)

# 그래프 컴파일
app = workflow.compile(checkpointer=checkpointer)
```

### 7.2 대화 컨텍스트 유지

```python
async def invoke_with_context(
    query: str,
    session_id: str
) -> AgentState:
    """
    세션 컨텍스트를 유지하며 실행

    Args:
        query: 사용자 질문
        session_id: 대화 세션 ID

    Returns:
        최종 상태
    """
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    initial_state = AgentState(
        query=query,
        session_id=session_id,
        # 이전 상태는 checkpointer가 자동 복원
    )

    result = await app.ainvoke(initial_state, config)
    return result
```

### 7.3 컨텍스트 활용 예시

```python
# 첫 번째 질문
result1 = await invoke_with_context(
    "김철수 상담사 이번 달 매출 알려줘",
    session_id="user_123_session_456"
)
# 응답: "김철수 상담사의 이번 달 매출은 150만원입니다."

# 후속 질문 (컨텍스트 유지)
result2 = await invoke_with_context(
    "그 사람 상담시간도 알려줘",  # "김철수"를 명시하지 않음
    session_id="user_123_session_456"
)
# 응답: "김철수 상담사의 이번 달 상담시간은 45시간 30분입니다."
# → 이전 컨텍스트에서 "김철수"를 자동 참조
```

---

## 8. SQL 생성 노드 상세

### 8.1 Schema-aware RAG 구조

```python
from chromadb import Client
from langchain.embeddings import OpenAIEmbeddings

class SchemaRAG:
    """스키마 정보 기반 RAG"""

    def __init__(self):
        self.client = Client()
        self.collection = self.client.get_or_create_collection(
            name="db_schemas",
            embedding_function=OpenAIEmbeddings()
        )
        self._load_schemas()

    def _load_schemas(self):
        """스키마 문서 로드"""
        schemas = [
            {
                "id": "mariadb_t_payment",
                "content": """
                ## t_payment (결제 테이블)
                - **용도**: 포인트 충전 결제 내역
                - **주요 컬럼**:
                  - payment_id (PK): 결제 고유 ID
                  - user_id (FK→t_user): 결제한 유저
                  - amount: 결제 금액 (원)
                  - status: 상태 (SUCCESS, PENDING, FAILED, CANCELLED)
                  - created_at: 결제 일시
                - **자주 쓰는 쿼리**:
                  - 일별 매출: SUM(amount) WHERE status='SUCCESS' GROUP BY DATE(created_at)
                """,
                "metadata": {"db": "mariadb", "table": "t_payment"}
            },
            # ... 다른 테이블들
        ]

        for schema in schemas:
            self.collection.add(
                ids=[schema["id"]],
                documents=[schema["content"]],
                metadatas=[schema["metadata"]]
            )

    async def query(self, question: str, db: str = None) -> list[str]:
        """관련 스키마 검색"""
        where_filter = {"db": db} if db else None

        results = self.collection.query(
            query_texts=[question],
            n_results=5,
            where=where_filter
        )

        return results["documents"][0]
```

### 8.2 Few-shot 예시 관리

```python
FEW_SHOT_EXAMPLES = {
    "sales_query": [
        {
            "question": "오늘 매출 얼마야?",
            "sql": """
                SELECT SUM(amount) as total_sales
                FROM t_payment
                WHERE status = 'SUCCESS'
                  AND DATE(created_at) = CURDATE()
            """
        },
        {
            "question": "이번 달 일별 매출 추이",
            "sql": """
                SELECT DATE(created_at) as date,
                       SUM(amount) as daily_sales
                FROM t_payment
                WHERE status = 'SUCCESS'
                  AND created_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
                GROUP BY DATE(created_at)
                ORDER BY date
            """
        }
    ],
    "counselor_analysis": [
        {
            "question": "김철수 상담사 이번 달 상담시간",
            "sql": """
                SELECT
                    SUM(chattm) as total_seconds,
                    CAST(FLOOR(SUM(chattm) / 3600) AS VARCHAR(10)) + ':' +
                    RIGHT('0' + CAST((SUM(chattm) % 3600) / 60 AS VARCHAR(2)), 2) as formatted_time
                FROM tm60_chatlog
                WHERE m_code = (SELECT m_code FROM tm60_member WHERE m_nickname LIKE '%김철수%')
                  AND chatstart >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
            """
        }
    ]
}
```

### 8.3 SQL 생성기 구현

```python
class SQLGeneratorNode:
    """SQL 생성 노드"""

    def __init__(self):
        self.schema_rag = SchemaRAG()
        self.validator = SQLValidator()
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)

    async def generate(self, state: AgentState, target_db: str) -> str:
        """
        자연어 질문을 SQL로 변환
        """
        # 1. 관련 스키마 검색
        relevant_schemas = await self.schema_rag.query(
            state["query"],
            db=target_db
        )

        # 2. 유사 예시 검색
        similar_examples = self._find_similar_examples(
            state["intent"],
            target_db
        )

        # 3. 프롬프트 구성
        prompt = self._build_prompt(
            query=state["query"],
            schemas=relevant_schemas,
            examples=similar_examples,
            target_db=target_db
        )

        # 4. LLM 호출
        response = await self.llm.ainvoke(prompt)
        sql = self._extract_sql(response.content)

        # 5. 검증
        validation_result = self.validator.validate(sql, target_db)

        if not validation_result.is_valid:
            raise SQLValidationError(validation_result.errors)

        return sql

    def _build_prompt(self, query, schemas, examples, target_db):
        db_specific_rules = {
            "mariadb": "- MySQL/MariaDB 문법 사용",
            "mssql": """
                - MSSQL 2005 호환 문법 사용
                - OFFSET/FETCH 대신 TOP N 사용
                - CTE(WITH) 사용 금지
                - 날짜함수: DATEADD, DATEDIFF, GETDATE 사용
            """,
            "ga4": "- GA4 API 조회 파라미터로 변환"
        }

        return f"""
당신은 SQL 전문가입니다. 자연어 질문을 SQL로 변환하세요.

## 대상 데이터베이스
{target_db.upper()}

## 스키마 정보
{chr(10).join(schemas)}

## 참고 예시
{self._format_examples(examples)}

## 규칙
- SELECT 문만 사용 (INSERT, UPDATE, DELETE 금지)
- 테이블/컬럼은 스키마에 있는 것만 사용
- 결과는 최대 1000행으로 제한
{db_specific_rules.get(target_db, "")}

## 질문
{query}

## SQL
```sql
"""
```

---

## 9. 후속 제안 생성

### 9.1 규칙 기반 + LLM 하이브리드

```python
class SuggestionGenerator:
    """후속 분석 제안 생성기"""

    RULES = {
        "sales_decrease": [
            "상담사별 매출 비교해볼까요?",
            "전주 대비 변화를 분석할까요?",
            "시간대별 매출 패턴을 확인할까요?"
        ],
        "consultation_anomaly": [
            "평균 대비 상담시간 분석할까요?",
            "시간당 매출 효율을 계산할까요?",
            "상담 건수와 비교할까요?"
        ],
        "user_query": [
            "이 유저의 상담 이력을 볼까요?",
            "결제 패턴을 분석할까요?",
            "유사 유저와 비교할까요?"
        ],
        "traffic_query": [
            "다른 채널과 비교할까요?",
            "시간대별 유입 추이를 볼까요?",
            "전환 퍼널을 분석할까요?"
        ]
    }

    async def generate(self, state: AgentState) -> list[str]:
        suggestions = []

        # 1. 결과 패턴 분석
        patterns = self._detect_patterns(state["merged_result"])

        # 2. 규칙 기반 제안
        for pattern in patterns:
            if pattern in self.RULES:
                suggestions.extend(self.RULES[pattern][:2])

        # 3. LLM 기반 제안 (부족할 경우)
        if len(suggestions) < 3:
            llm_suggestions = await self._generate_llm_suggestions(state)
            suggestions.extend(llm_suggestions)

        # 4. 중복 제거 및 상위 3개 반환
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:3]

    def _detect_patterns(self, result: DataFrame) -> list[str]:
        """결과에서 패턴 감지"""
        patterns = []

        if result is None or result.empty:
            return patterns

        # 매출 감소 감지
        if "total_sales" in result.columns:
            # 전일/전주 대비 감소 여부 체크
            pass

        # 이상치 감지
        for col in result.select_dtypes(include=['number']).columns:
            mean = result[col].mean()
            std = result[col].std()
            if (result[col] > mean + 2*std).any():
                patterns.append("consultation_anomaly")

        return patterns
```

---

## 10. 전체 그래프 조립

### 10.1 그래프 정의

```python
from langgraph.graph import StateGraph, END

def create_bi_assistant_graph() -> StateGraph:
    """BI 어시스턴트 LangGraph 생성"""

    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("decompose_tasks", decompose_tasks_node)
    workflow.add_node("mariadb_agent", mariadb_agent_node)
    workflow.add_node("mssql_agent", mssql_agent_node)
    workflow.add_node("ga4_agent", ga4_agent_node)
    workflow.add_node("aggregate_results", aggregate_results_node)
    workflow.add_node("cross_join", cross_join_node)
    workflow.add_node("validate_result", validate_result_node)
    workflow.add_node("synthesize_response", synthesize_response_node)
    workflow.add_node("generate_suggestions", generate_suggestions_node)
    workflow.add_node("error_handler", error_handler_node)

    # 엣지 정의
    workflow.set_entry_point("parse_query")
    workflow.add_edge("parse_query", "classify_intent")
    workflow.add_edge("classify_intent", "decompose_tasks")

    # 조건부 라우팅 (에이전트로)
    workflow.add_conditional_edges(
        "decompose_tasks",
        route_to_agents,
        {
            "mariadb_agent": "mariadb_agent",
            "mssql_agent": "mssql_agent",
            "ga4_agent": "ga4_agent",
            "error_handler": "error_handler",
        }
    )

    # 에이전트 → 결과 수집
    workflow.add_edge("mariadb_agent", "aggregate_results")
    workflow.add_edge("mssql_agent", "aggregate_results")
    workflow.add_edge("ga4_agent", "aggregate_results")

    # 결과 처리
    workflow.add_edge("aggregate_results", "cross_join")
    workflow.add_edge("cross_join", "validate_result")
    workflow.add_edge("validate_result", "synthesize_response")
    workflow.add_edge("synthesize_response", "generate_suggestions")
    workflow.add_edge("generate_suggestions", END)

    workflow.add_edge("error_handler", END)

    return workflow

# 그래프 생성 및 컴파일
workflow = create_bi_assistant_graph()
app = workflow.compile(checkpointer=checkpointer)
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-29 | 초기 LangGraph 구현 설계 문서 작성 |
