# Project Context: admin-backend AI BI Assistant

> AI 에이전트가 구현 전 반드시 읽어야 할 핵심 규칙과 패턴

**Generated:** 2026-01-30
**Source:** `_bmad-output/planning-artifacts/architecture.md`

---

## Critical Constraints (위반 시 구현 실패)

### 1. Infrastructure Constraint
```
❌ 새로운 인프라 추가 불가
✅ 기존 인프라만 사용: Redis, MariaDB, MSSQL 2005, 기존 로깅
```

### 2. MSSQL 2005 Legacy
```python
# ❌ WRONG - async 드라이버 사용 불가
import aioodbc  # MSSQL 2005는 지원 안 함

# ✅ CORRECT - pymssql + asyncio.to_thread()
import pymssql
result = await asyncio.to_thread(sync_mssql_query, sql)
```

### 3. Encoding
```python
# MSSQL 2005 결과는 EUC-KR → UTF-8 변환 필수
def decode_euckr(value: str) -> str:
    if isinstance(value, bytes):
        return value.decode('euc-kr', errors='replace')
    return value
```

---

## Import Patterns

```python
# ✅ 절대 경로 (권장)
from src.services.ai.state import AgentState
from src.services.ai.agents.base import BaseAgent
from src.common.logging import get_logger

# ✅ 상대 경로 (같은 패키지 내)
from .base import BaseAgent
from ..tools.sql_validator import SQLValidatorTool
```

---

## Dependency Injection Pattern

```python
# ✅ CORRECT - 생성자 주입
class MariaDBAgent(BaseAgent):
    def __init__(
        self,
        llm: ChatOpenAI,
        schema_loader: SchemaLoader,
        settings: Settings,
    ):
        self.llm = llm
        self.schema_loader = schema_loader
        self.settings = settings

# ✅ FastAPI Depends 활용
@router.post("/chat")
async def chat(
    request: ChatRequest,
    graph: AIGraph = Depends(get_ai_graph),
):
    ...
```

---

## Dependency Direction Rules

```
API → Graph → Agents → Tools/Security → Common/Config

❌ FORBIDDEN:
   - Tools → Agents
   - Agents → Graph
   - 순환 참조
```

---

## Type Patterns

### Agent Output Types
```python
from typing import TypedDict

class AgentMetadata(TypedDict):
    agent: str
    duration_ms: int
    timestamp: str

class BaseAgentOutput(TypedDict):
    success: bool
    error: str | None
    metadata: AgentMetadata

class SQLResultData(TypedDict):
    rows: list[dict]
    columns: list[str]
    row_count: int

class SQLAgentOutput(BaseAgentOutput):
    data: SQLResultData | None
```

### State Type (LangGraph)
```python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    execution_plan: str | None
    results: dict[str, SQLAgentOutput]
    final_response: str | None
```

---

## Error Handling Pattern

```python
class AIError(Exception):
    def __init__(
        self,
        code: str,              # AI_ERR_XXX
        technical_message: str, # 로깅용
        user_message: str,      # 사용자 표시용
        suggestion: str | None = None,
        recoverable: bool = True,
    ):
        ...

# 에러 코드
AI_ERR_001 = "LLM_TIMEOUT"      # → "잠시 후 다시 시도해 주세요"
AI_ERR_002 = "INVALID_QUERY"    # → "질문을 다르게 표현해 주세요"
AI_ERR_003 = "DB_UNAVAILABLE"   # → "데이터 조회가 일시적으로 불가합니다"
AI_ERR_004 = "RATE_LIMITED"     # → "요청이 너무 많습니다"
```

---

## LLM Call Pattern

```python
# ✅ 항상 폴백 래퍼 사용
async def call_llm_with_fallback(
    prompt: str,
    settings: Settings,
) -> str:
    try:
        return await call_primary_llm(prompt, settings)
    except Exception:
        if retry_count >= 3:
            return await call_fallback_llm(prompt, settings)
        raise

# 타임아웃 설정 필수
LLM_TIMEOUT = 30  # seconds
```

---

## Logging Pattern

```python
# ✅ 필수 필드 포함
logger.info(
    "llm_call",
    extra={
        "event": "llm_call",
        "agent": "supervisor",
        "user_id": user_id,
        "session_id": session_id,
        "duration_ms": duration_ms,
        "prompt_version": PROMPT_VERSION,  # 프롬프트 버전 필수
    }
)

# Audit Trail (AI 쿼리 실행 시)
logger.info(
    "ai_query_executed",
    extra={
        "user_id": user_id,
        "session_id": session_id,
        "query_text": user_query,
        "tables_accessed": ["payments", "members"],
        "row_count": 150,
    }
)
```

---

## Prompt Version Management

```python
# prompts/supervisor.py
PROMPT_VERSION = "1.0.0"  # 시맨틱 버전

SUPERVISOR_SYSTEM_PROMPT = """..."""

# 프롬프트 변경 시 반드시 버전 업데이트
# MAJOR: 의도 분류 로직 변경
# MINOR: 프롬프트 개선
# PATCH: 오타/문구 수정
```

---

## SSE Event Format

```python
EVENT_TYPES = ["thinking", "query", "executing", "result", "error", "done"]

# ✅ 정의된 타입만 사용
async def send_sse_event(
    event_type: str,  # EVENT_TYPES 중 하나
    message: str,
    agent: str,
):
    assert event_type in EVENT_TYPES
    yield f"data: {json.dumps({
        'event': event_type,
        'data': {
            'message': message,
            'agent': agent,
            'timestamp': datetime.utcnow().isoformat(),
        }
    })}\n\n"
```

---

## Configuration (settings.py)

```python
# AI 설정은 기존 settings.py에 통합
class Settings(BaseSettings):
    # AI Assistant Settings
    ai_feature_enabled: bool = True
    ai_debug_mode: bool = False
    ai_llm_model: str = "gpt-4o-mini"
    ai_llm_fallback_model: str = "gpt-3.5-turbo"
    ai_timeout_llm_call: int = 30
    ai_timeout_single_agent: int = 45
    ai_timeout_request: int = 60
    ai_rate_limit_super_admin: int = 60
    ai_rate_limit_admin: int = 30
    ai_rate_limit_viewer: int = 10
    ai_max_concurrent_cross_db: int = 5
```

---

## Test Requirements

| 영역 | 커버리지 | 필수 |
|------|----------|------|
| `security/` | 100% | **필수** |
| `tools/sql_validator.py` | 100% | **필수** |
| Unit Tests 전체 | 80%+ | 권장 |

### LLM Mock Fixture
```python
# tests/services/ai/conftest.py
@pytest.fixture
def mock_llm():
    with patch("langchain_openai.ChatOpenAI") as mock:
        mock.return_value.invoke.return_value = AIMessage(content="mocked")
        yield mock
```

### Golden Dataset
```json
// tests/services/ai/golden/queries.json
{
  "version": "1.0.0",
  "compatible_prompt_versions": ["1.0.x"],
  "semantic_similarity_threshold": 0.85,
  "cases": [...]
}
```

---

## File Documentation Standard

```python
"""
{파일 설명}

Stories: {관련 스토리 ID}
FRs: {관련 FR ID}
"""

# 예시
"""
MariaDB Text-to-SQL 에이전트.

Schema RAG로 테이블 구조를 로드하고 자연어를 SQL로 변환합니다.

Stories: AI-002, AI-003
FRs: FR-011, FR-012, FR-013
"""
```

---

## Anti-Patterns (금지 사항)

```python
# ❌ 직접 LLM 호출 금지
response = llm.invoke(prompt)

# ✅ 폴백 래퍼 사용
response = await call_llm_with_fallback(prompt, settings)


# ❌ 타입 없는 dict 반환 금지
return {"success": True, "data": rows}

# ✅ TypedDict 사용
return SQLAgentOutput(success=True, data=result, ...)


# ❌ 에러 직접 raise 금지
raise Exception("DB error")

# ✅ AIError로 래핑
raise AIError(
    code="AI_ERR_003",
    technical_message="Connection refused",
    user_message="데이터 조회가 일시적으로 불가합니다",
)


# ❌ SQL 검증 없이 실행 금지
cursor.execute(generated_sql)

# ✅ 검증 후 실행
validated = sql_validator.validate(generated_sql)
if validated.is_safe:
    cursor.execute(validated.sql)
```

---

## Quick Reference

| 항목 | 값 |
|------|-----|
| LLM Primary | gpt-4o-mini |
| LLM Fallback | gpt-3.5-turbo |
| LLM Timeout | 30초 |
| Request Timeout | 60초 |
| Cross-DB 동시성 | 5개 |
| Schema Cache TTL | 1시간 |
| Security 테스트 | 100% 필수 |

---

**Full Architecture:** `_bmad-output/planning-artifacts/architecture.md`
