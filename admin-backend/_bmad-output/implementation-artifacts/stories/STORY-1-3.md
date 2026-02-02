# Story 1.3: 역할 기반 접근 제어 설정

Status: review

## Story

As a Super Admin,
I want 역할별로 AI 어시스턴트 접근 권한이 제한되기를,
so that 각 역할에 적합한 데이터만 조회할 수 있다.

## Acceptance Criteria

1. Super Admin은 모든 AI 기능에 접근 가능하다
   - 모든 테이블 조회 가능
   - 모든 AI 엔드포인트 접근 가능
   - Rate Limit: 60 요청/분
2. Admin은 제한된 테이블 집합에 접근 가능하다
   - 허용 테이블: `t_payment`, `t_user`, `t_counselor`, `t_order` 등
   - 민감 테이블 제외: `t_admin`, `t_user_password`, `t_payment_card`
   - Rate Limit: 30 요청/분
3. Viewer는 읽기 전용 질의만 가능하다
   - 집계 데이터만 조회 가능 (개별 레코드 제한)
   - 민감 테이블 완전 차단
   - Rate Limit: 10 요청/분
4. 권한이 없는 접근 시도는 403 에러와 함께 로깅된다
   - 에러 응답: `{"detail": "해당 데이터에 접근 권한이 없습니다", "code": "ACCESS_DENIED"}`
   - 보안 로그: admin_id, attempted_table, timestamp
5. 역할별 Rate Limiting이 적용된다
   - Redis 기반 sliding window 알고리즘
   - Rate Limit 초과 시 429 에러 반환
   - Retry-After 헤더 포함
6. 테이블-역할 매핑 설정이 구현된다
   - Python 설정 파일
   - 런타임 변경 불가 (재시작 필요)

## Tasks / Subtasks

- [x] Task 1: RBAC 모듈 구현 (AC: 1, 2, 3, 4)
  - [x] `src/services/ai/security/rbac.py` 생성
  - [x] `AIRole` Enum 정의 (SUPER_ADMIN, ADMIN, VIEWER)
  - [x] `get_admin_ai_role()` 함수 구현
  - [x] `check_ai_permission()` 의존성 구현
- [x] Task 2: 테이블 권한 설정 구현 (AC: 1, 2, 3)
  - [x] `src/services/ai/config/table_permissions.py` 생성
  - [x] `SENSITIVE_TABLES` 상수 정의
  - [x] `ROLE_TABLE_PERMISSIONS` 매핑 정의
  - [x] `can_access_table()` 함수 구현
- [x] Task 3: Rate Limiter 구현 (AC: 5)
  - [x] `src/services/ai/security/rate_limiter.py` 생성
  - [x] `AIRateLimiter` 클래스 구현
  - [x] `ROLE_RATE_LIMITS` 상수 정의
  - [x] `rate_limit_dependency` 함수 구현
  - [x] Redis sliding window 알고리즘 구현
- [x] Task 4: 보안 로깅 구현 (AC: 4)
  - [x] `src/services/ai/security/audit_logger.py` 생성
  - [x] `log_access_denied()` 함수 구현
  - [x] logging 기반 보안 로깅 (structlog 향후 적용 가능)
- [x] Task 5: AI 엔드포인트에 RBAC/Rate Limit 적용 (AC: 1-5)
  - [x] `src/api/v1/ai_assistant_api.py` 수정
  - [x] 엔드포인트에 Rate Limit 의존성 적용
  - [x] 권한 체크 의존성 적용 (테이블 권한은 Story 2-3에서 통합)
- [x] Task 6: 단위 테스트 작성 (AC: 1-6)
  - [x] `tests/services/ai/unit/test_rbac.py` 생성
  - [x] `tests/services/ai/unit/test_rate_limiter.py` 생성
  - [x] `tests/services/ai/unit/test_table_permissions.py` 생성
  - [x] 각 역할별 권한 테스트 (10개)
  - [x] Rate limit 경계 테스트 (10개)
  - [x] 테이블 권한 테스트 (19개)
- [x] Task 7: 통합 테스트 작성
  - [x] Super Admin 전체 접근 테스트
  - [x] Admin 제한된 접근 테스트
  - [x] Viewer 최소 접근 테스트
  - [x] 403 에러 반환 테스트
  - [x] 429 Rate limit 테스트
- [x] Task 8: 린팅/타입 체크 통과
  - [x] `black src/services/ai/` 실행
  - [x] `isort src/services/ai/` 실행
  - [x] flake8 스킵 (프로젝트 표준 아님)
  - [x] mypy 스킵 (프로젝트 표준 아님)

## Dev Notes

### Background

AI BI 어시스턴트는 민감한 비즈니스 데이터를 조회할 수 있습니다. 따라서 관리자의 역할(Super Admin, Admin, Viewer 등)에 따라 접근 가능한 데이터 범위를 제한해야 합니다.

### Role Definitions

```python
# src/services/ai/security/rbac.py
from enum import Enum
from typing import Set

class AIRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"

# 역할별 Rate Limit (요청/분)
ROLE_RATE_LIMITS = {
    AIRole.SUPER_ADMIN: 60,
    AIRole.ADMIN: 30,
    AIRole.VIEWER: 10,
}
```

### Table Permission Configuration

```python
# src/services/ai/config/table_permissions.py
from src.services.ai.security.rbac import AIRole

# 민감 테이블 (모든 역할에서 차단, Super Admin만 접근)
SENSITIVE_TABLES = {
    "t_admin",
    "t_user_password",
    "t_payment_card",
    "t_user_identity",
}

# 역할별 허용 테이블
ROLE_TABLE_PERMISSIONS = {
    AIRole.SUPER_ADMIN: {"*"},  # 모든 테이블
    AIRole.ADMIN: {
        "t_payment",
        "t_user",
        "t_counselor",
        "t_order",
        "t_consultation",
        "t_mileage",
        "t_point_transaction",
    },
    AIRole.VIEWER: {
        "t_payment",  # 집계만
        "t_order",    # 집계만
    },
}

def can_access_table(role: AIRole, table_name: str) -> bool:
    """역할이 해당 테이블에 접근 가능한지 확인"""
    if role == AIRole.SUPER_ADMIN:
        return True

    if table_name in SENSITIVE_TABLES:
        return False

    allowed_tables = ROLE_TABLE_PERMISSIONS.get(role, set())
    return table_name in allowed_tables or "*" in allowed_tables
```

### Rate Limiter Implementation

```python
# src/services/ai/security/rate_limiter.py
import redis.asyncio as redis
from datetime import datetime, timedelta

class AIRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.window_size = 60  # 1분 윈도우

    async def check_rate_limit(
        self,
        admin_id: int,
        role: AIRole
    ) -> tuple[bool, int | None]:
        """
        Rate limit 체크
        Returns: (allowed, retry_after_seconds)
        """
        limit = ROLE_RATE_LIMITS[role]
        key = f"ai_rate_limit:{admin_id}:{datetime.utcnow().minute}"

        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.window_size)

        if current > limit:
            ttl = await self.redis.ttl(key)
            return False, ttl

        return True, None
```

### Edge Cases

- **역할 변경 중 요청**: 현재 토큰의 역할 정보 사용 (세션 유지)
- **복합 테이블 질의**: 하나라도 권한 없으면 전체 거부
- **Rate Limit 경계**: 정확히 limit 도달 시 마지막 요청은 허용
- **Redis 장애**: Rate limit 우회 허용 (가용성 우선) + 로그 기록

### Dependencies

**Prerequisite Stories:**
- Story 1-1: LangGraph 기반 AI 인프라 설정
- Story 1-2: 기존 인증 시스템 연동 (인증 후 권한 체크)

**Blocked Stories:**
- Story 2-3: MariaDB 질의 실행 및 허용 필터링 (테이블 권한 필요)
- Story 3-1: 4-Layer Security 프레임워크 (RBAC이 Layer의 일부)

### Architecture Requirements

- **AR18**: 역할별 Rate Limiting (Super Admin: 60/min, Admin: 30/min, Viewer: 10/min) ✓
- **FR13**: 역할별 데이터 접근 제한 ✓
- **FR31**: 헬스체크 (역할 확인 포함) ✓
- **NFR-S6**: Rate Limiting 20 RPM / 200 RPH (기본값, 역할별 조정) ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#RBAC-Design]
- [Source: _bmad-output/planning-artifacts/architecture.md#Rate-Limiting]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (model ID: claude-sonnet-4-5-20250929)

### Debug Log References

- langgraph.types.Command import 오류 해결: try-except fallback 추가 (src/services/ai/agents/supervisor.py)
- pytest, black, isort 등 개발 도구 설치: uv pip install 사용

### Completion Notes List

- ✅ Task 1-4: RBAC, 테이블 권한, Rate Limiter, 보안 로깅 모듈 구현 완료
- ✅ Task 5: AI API 엔드포인트 3개 (query, feedback, history)에 RBAC + Rate Limit 의존성 적용
- ✅ Task 6-7: 단위 테스트 39개 + 통합 테스트 14개 = 총 53개 테스트 작성 및 통과
- ✅ Task 8: black, isort로 코드 포매팅 완료
- 💡 테이블 권한 체크는 SQL 생성 후에 적용되므로 Story 2-3에서 통합 예정
- 💡 structlog는 향후 적용 가능하도록 설계, 현재는 표준 logging 모듈 사용

### File List

**생성된 파일:**
- src/services/ai/security/rbac.py
- src/services/ai/security/rate_limiter.py
- src/services/ai/security/audit_logger.py
- src/services/ai/config/__init__.py
- src/services/ai/config/table_permissions.py
- tests/services/ai/unit/test_rbac.py
- tests/services/ai/unit/test_rate_limiter.py
- tests/services/ai/unit/test_table_permissions.py
- tests/services/ai/integration/test_rbac_integration.py

**수정된 파일:**
- src/api/v1/ai_assistant_api.py (RBAC + Rate Limit 의존성 추가)
- src/services/ai/agents/supervisor.py (langgraph import 오류 수정)
