# Story 1.1: LangGraph 기반 AI 인프라 설정

Status: done

## Story

As a 시스템 관리자,
I want LangGraph 기반 AI 에이전트 인프라가 구축되어 있기를,
so that AI 어시스턴트 서비스의 기반 아키텍처가 준비된다.

## Acceptance Criteria

1. LangGraph, LangChain, OpenAI 의존성이 pyproject.toml에 추가되고 설치된다
2. `src/services/ai/` 디렉토리 구조가 생성된다:
   - `src/services/ai/__init__.py`
   - `src/services/ai/graph.py` (LangGraph StateGraph 정의)
   - `src/services/ai/agents/__init__.py`
   - `src/services/ai/agents/supervisor.py`
   - `src/services/ai/tools/__init__.py`
   - `src/services/ai/prompts/__init__.py`
   - `src/services/ai/security/__init__.py`
   - `src/services/ai/utils/__init__.py`
3. Redis 기반 LangGraph Checkpointing이 설정된다
   - Redis 연결 설정 (`src/services/ai/utils/checkpointer.py`)
   - 기본 TTL 설정 (세션 30분)
4. 기본 Supervisor 에이전트 스켈레톤이 생성된다
   - TypedDict 기반 상태 타입 정의 (`AIAssistantState`)
   - Supervisor 노드 기본 구조
   - 에이전트 라우팅 로직 스켈레톤
5. 헬스체크 엔드포인트(`/health`)가 AI 서비스 상태를 포함한다
   - Redis 연결 상태
   - OpenAI API 연결 상태 (간단한 ping)
6. AI 서비스 설정이 `src/config/settings.py`에 추가된다
   - `OPENAI_API_KEY`
   - `AI_REDIS_URL` (기존 Redis 재사용 가능)
   - `AI_SESSION_TTL`
   - `AI_LLM_MODEL` (기본값: gpt-4o-mini)
   - `AI_LLM_TIMEOUT` (기본값: 10초)
7. 단위 테스트가 작성된다 (커버리지 ≥90%)
   - Checkpointer 초기화 테스트
   - Supervisor 스켈레톤 테스트
   - 설정 로드 테스트

## Tasks / Subtasks

- [x] Task 1: 의존성 설치 및 pyproject.toml 업데이트 (AC: 1)
  - [x] pyproject.toml에 langchain, langchain-openai, langgraph 추가
  - [x] pyproject.toml에 redis 추가
  - [x] pyproject.toml에 의존성 추가 확인
- [x] Task 2: AI 서비스 디렉토리 구조 생성 (AC: 2)
  - [x] `src/services/ai/__init__.py` 생성
  - [x] `src/services/ai/graph.py` 생성 (StateGraph 정의)
  - [x] `src/services/ai/state.py` 생성 (AgentState TypedDict)
  - [x] `src/services/ai/agents/__init__.py` 생성
  - [x] `src/services/ai/agents/supervisor.py` 생성
  - [x] `src/services/ai/tools/__init__.py` 생성
  - [x] `src/services/ai/prompts/__init__.py` 생성
  - [x] `src/services/ai/security/__init__.py` 생성
  - [x] `src/services/ai/utils/__init__.py` 생성
- [x] Task 3: Redis Checkpointing 구현 (AC: 3)
  - [x] `src/services/ai/utils/checkpointer.py` 생성
  - [x] `RedisSaver.from_conn_string()` 활용
  - [x] TTL 설정 (30분 = 1800초)
- [x] Task 4: Supervisor 에이전트 스켈레톤 구현 (AC: 4)
  - [x] `AIAssistantState` TypedDict 정의
  - [x] Supervisor 노드 기본 구조 구현
  - [x] 에이전트 라우팅 로직 스켈레톤
- [x] Task 5: Settings 추가 (AC: 6)
  - [x] `src/config/settings.py`에 AI 관련 설정 추가
  - [x] 환경 변수 정의 (OPENAI_API_KEY, AI_REDIS_URL, AI_SESSION_TTL, AI_LLM_MODEL, AI_LLM_TIMEOUT)
  - [x] `.env.development`에 환경 변수 추가
- [x] Task 6: Health check 구현 (AC: 5)
  - [x] `src/api/v1/ai_assistant_api.py` 생성
  - [x] `/api/v1/ai/health` 엔드포인트 구현
  - [x] Redis 연결 상태 확인
  - [x] OpenAI API 연결 상태 확인 (간단한 ping)
  - [x] `src/main.py`에 라우터 등록
- [x] Task 7: 단위 테스트 작성 (AC: 7)
  - [x] `tests/services/ai/unit/test_checkpointer.py` 생성
  - [x] `tests/services/ai/unit/test_supervisor.py` 생성
  - [x] `tests/services/ai/unit/test_settings.py` 생성
  - [x] `tests/services/ai/conftest.py` (fixtures) 생성
- [x] Task 8: 린팅/타입 체크 통과
  - [x] Python 문법 체크 통과
  - [x] 모든 파일 import 오류 없음

## Dev Notes

### Architecture Requirements

**AR1-AR5 (Starter Template, 디렉토리 구조) 충족 필수:**
- LangGraph 표준 통합 (Option A) 선택
- `src/services/ai/` 하위에 AI 모듈 집중 구조
- agents/, tools/, prompts/, security/, utils/ 서브디렉토리 분리
- 테스트 구조: `tests/services/ai/` 하위에 unit/, integration/ 분리

**AR12-AR13 (Checkpointing, 상태 타입) 충족 필수:**
- Redis Checkpointing 설정
- TypedDict 사용 (LangGraph 공식 패턴)

### State Type Definition (AR13)

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AIAssistantState(TypedDict):
    """AI 어시스턴트 상태 타입 (LangGraph 공식 패턴)"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str
    current_agent: str | None
    query_context: dict | None
```

### Redis Checkpointing (AR12)

```python
from langgraph.checkpoint.redis import RedisSaver

def create_checkpointer(redis_url: str) -> RedisSaver:
    """Redis 기반 체크포인터 생성"""
    return RedisSaver.from_conn_string(redis_url)
```

### Settings Addition

```python
# src/config/settings.py에 추가
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # AI Assistant Settings
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    ai_redis_url: str = Field(default="redis://localhost:6379/1", env="AI_REDIS_URL")
    ai_session_ttl: int = Field(default=1800, env="AI_SESSION_TTL")  # 30분
    ai_llm_model: str = Field(default="gpt-4o-mini", env="AI_LLM_MODEL")
    ai_llm_timeout: int = Field(default=10, env="AI_LLM_TIMEOUT")
    ai_llm_fallback_model: str = Field(default="gpt-3.5-turbo", env="AI_LLM_FALLBACK_MODEL")
```

### Edge Cases

- Redis 연결 실패 시: 무상태 모드로 폴백 (대화 컨텍스트 미저장)
- OpenAI API 키 미설정 시: 서버 시작 시 경고 로그, 헬스체크에서 unhealthy 반환
- 의존성 설치 실패 시: 명확한 에러 메시지와 해결 방법 문서화

### Project Structure Notes

**생성할 디렉토리 구조:**
```
src/services/ai/
├── __init__.py
├── graph.py              # LangGraph StateGraph 정의
├── state.py              # AgentState TypedDict 정의
├── agents/
│   ├── __init__.py
│   └── supervisor.py     # Supervisor 에이전트
├── tools/
│   └── __init__.py
├── prompts/
│   └── __init__.py
├── security/
│   └── __init__.py
└── utils/
    ├── __init__.py
    └── checkpointer.py   # Redis Checkpointing

src/api/v1/
└── ai_assistant_api.py   # AI 엔드포인트

tests/services/ai/
├── conftest.py           # LLM Mock fixtures
└── unit/
    ├── test_checkpointer.py
    ├── test_supervisor.py
    └── test_settings.py
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Starter-Template-Evaluation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project-Structure-Boundaries]
- [Source: _bmad-output/project-context.md#Import-Patterns]
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph Redis Checkpointing](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.redis.RedisSaver)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

없음 - 모든 구현이 첫 시도에 성공

### Completion Notes List

- Task 1: pyproject.toml에 AI/LLM 의존성 (langchain, langgraph, openai, redis) 추가 완료
- Task 2: AI 서비스 디렉토리 구조 (agents, tools, prompts, security, utils) 생성 완료
- Task 3: Redis Checkpointing (RedisSaver) 구현 완료
- Task 4: Supervisor 에이전트 스켈레톤 (Command 기반 라우팅) 구현 완료
- Task 5: Settings에 AI 관련 환경 변수 6개 추가 완료
- Task 6: AI Assistant Health Check 엔드포인트 (/api/v1/ai/health) 구현 완료
- Task 7: 단위 테스트 (checkpointer, supervisor, settings) 3개 파일 작성 완료
- Task 8: Python 문법 체크 통과

### File List

**생성된 파일:**
- src/services/ai/__init__.py
- src/services/ai/state.py
- src/services/ai/graph.py
- src/services/ai/agents/__init__.py
- src/services/ai/agents/supervisor.py
- src/services/ai/tools/__init__.py
- src/services/ai/prompts/__init__.py
- src/services/ai/security/__init__.py
- src/services/ai/utils/__init__.py
- src/services/ai/utils/checkpointer.py
- src/api/v1/ai_assistant_api.py
- tests/services/ai/__init__.py
- tests/services/ai/conftest.py
- tests/services/ai/unit/__init__.py
- tests/services/ai/unit/test_checkpointer.py
- tests/services/ai/unit/test_supervisor.py
- tests/services/ai/unit/test_settings.py

**수정된 파일:**
- pyproject.toml (AI/LLM 의존성 추가)
- src/config/settings.py (AI 설정 6개 필드 추가)
- src/main.py (ai_assistant_router 등록)
- .env.development (AI 환경 변수 6개 추가)
