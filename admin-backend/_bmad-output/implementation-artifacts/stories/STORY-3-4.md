# Story 3.4: 감사 로깅 및 Rate Limiting

Status: ready-for-dev

## Story

As a 시스템 관리자,
I want 모든 질의와 접근이 로깅되고 요청 빈도가 제한되기를,
so that 보안 감사와 남용 방지가 가능하다.

## Acceptance Criteria

1. 모든 AI 질의가 JSON 형식으로 로깅된다
   - 구조화된 JSON 로그 포맷
   - 로그 레벨: INFO (성공), WARNING (차단), ERROR (실패)
2. 로그에 요청 ID, 사용자, 질의, 결과 요약이 포함된다
   - request_id (UUID)
   - admin_id
   - question (원문)
   - generated_sql (마스킹 가능)
   - execution_time_ms
   - row_count
   - status (success/blocked/error)
3. 감사 로그가 90일간 보존된다
   - 로그 파일 로테이션
   - 자동 삭제 스케줄
4. Rate Limiting이 역할별로 적용된다
   - Super Admin: 60 req/min
   - Admin: 30 req/min
   - Viewer: 10 req/min
5. Rate Limit 초과 시 429 에러가 반환된다
   - Retry-After 헤더 포함
   - 친절한 에러 메시지

## Tasks / Subtasks

- [ ] Task 1: 감사 로거 구현 (AC: 1, 2)
  - [ ] `src/services/ai/audit/audit_logger.py` 생성
  - [ ] `AIQueryAuditLog` 데이터클래스 정의
  - [ ] `AIAuditLogger` 클래스 구현
  - [ ] `log_query()` 메서드 구현
  - [ ] `log_rate_limit_exceeded()` 메서드 구현
  - [ ] `log_security_event()` 메서드 구현
  - [ ] structlog JSON 포맷 적용
- [ ] Task 2: Rate Limiter 구현 (AC: 4, 5)
  - [ ] `src/services/ai/audit/rate_limiter.py` 생성
  - [ ] `AIRateLimiter` 클래스 구현 (Sliding Window)
  - [ ] `RateLimitResult` 데이터클래스 정의
  - [ ] `RATE_LIMITS` 역할별 상수 정의
  - [ ] `check_rate_limit()` 비동기 메서드 구현
  - [ ] `get_usage_stats()` 메서드 구현
- [ ] Task 3: Rate Limit 의존성 구현 (AC: 5)
  - [ ] `src/api/v1/dependencies/rate_limit.py` 생성
  - [ ] `rate_limit_dependency` FastAPI 의존성
  - [ ] 429 HTTPException 처리
  - [ ] Retry-After, X-RateLimit-* 헤더 추가
- [ ] Task 4: 로깅 설정 구현 (AC: 3)
  - [ ] `src/services/ai/audit/log_config.py` 생성
  - [ ] `configure_ai_audit_logging()` 함수 구현
  - [ ] TimedRotatingFileHandler (90일 보관)
  - [ ] structlog 프로세서 설정
- [ ] Task 5: API 통합 (AC: 1-5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] `rate_limit_dependency` 적용
  - [ ] 감사 로그 기록 통합
- [ ] Task 6: 단위 테스트 작성 (≥90% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/audit/test_audit_logger.py` 생성
  - [ ] `tests/services/ai/audit/test_rate_limiter.py` 생성
  - [ ] Rate limit 동작 테스트
  - [ ] 로그 포맷 테스트
- [ ] Task 7: 통합 테스트 작성
  - [ ] Rate limit 동작 E2E 테스트
  - [ ] 로그 파일 생성 확인
- [ ] Task 8: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI BI 어시스턴트의 모든 활동은 추적 가능해야 합니다. 감사 로그는 보안 사고 조사, 사용 패턴 분석, 컴플라이언스 준수에 필수입니다. 또한 Rate Limiting으로 시스템 남용과 LLM 비용 초과를 방지합니다.

### Audit Logger

```python
# src/services/ai/audit/audit_logger.py
import structlog
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any
import json

logger = structlog.get_logger()

@dataclass
class AIQueryAuditLog:
    """AI 질의 감사 로그"""
    request_id: str
    admin_id: int
    admin_role: str
    question: str
    db_scope: str
    generated_sql: str | None
    execution_time_ms: int
    row_count: int
    status: str  # success, blocked, error
    error_code: str | None = None
    error_message: str | None = None
    tables_accessed: list[str] | None = None
    masked_columns: list[str] | None = None
    timestamp: str | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

class AIAuditLogger:
    """AI 서비스 감사 로거"""

    @staticmethod
    async def log_query(audit_log: AIQueryAuditLog):
        """질의 감사 로그 기록"""
        log_data = asdict(audit_log)

        # SQL 민감 정보 마스킹 (옵션)
        if audit_log.generated_sql:
            log_data["generated_sql"] = audit_log.generated_sql[:500]

        if audit_log.status == "success":
            logger.info("ai_query_audit", **log_data)
        elif audit_log.status == "blocked":
            logger.warning("ai_query_blocked", **log_data)
        else:
            logger.error("ai_query_error", **log_data)

    @staticmethod
    async def log_rate_limit_exceeded(
        admin_id: int,
        admin_role: str,
        current_count: int,
        limit: int
    ):
        """Rate Limit 초과 로그"""
        logger.warning(
            "ai_rate_limit_exceeded",
            admin_id=admin_id,
            admin_role=admin_role,
            current_count=current_count,
            limit=limit,
            timestamp=datetime.utcnow().isoformat()
        )
```

### Rate Limiter (Sliding Window)

```python
# src/services/ai/audit/rate_limiter.py
import redis.asyncio as redis
from datetime import datetime
from dataclasses import dataclass
from src.services.ai.security.rbac import AIRole

@dataclass
class RateLimitResult:
    allowed: bool
    current_count: int
    limit: int
    retry_after: int | None = None
    window_reset: int | None = None

class AIRateLimiter:
    """AI 서비스 Rate Limiter (Sliding Window)"""

    # 역할별 제한 (요청/분)
    RATE_LIMITS = {
        AIRole.SUPER_ADMIN: 60,
        AIRole.ADMIN: 30,
        AIRole.VIEWER: 10,
    }

    # 시간당 제한
    HOURLY_LIMITS = {
        AIRole.SUPER_ADMIN: 600,
        AIRole.ADMIN: 300,
        AIRole.VIEWER: 100,
    }

    WINDOW_SIZE = 60  # 1분

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        admin_id: int,
        role: AIRole
    ) -> RateLimitResult:
        """Rate limit 확인 (Sliding Window Counter)"""
        limit = self.RATE_LIMITS.get(role, 10)
        now = datetime.utcnow()
        current_minute = now.strftime("%Y%m%d%H%M")

        # Redis 키: ai_ratelimit:{admin_id}:{minute}
        key = f"ai_ratelimit:{admin_id}:{current_minute}"

        # 현재 카운트 증가
        current = await self.redis.incr(key)

        # 첫 요청이면 만료 설정
        if current == 1:
            await self.redis.expire(key, self.WINDOW_SIZE + 10)

        if current > limit:
            ttl = await self.redis.ttl(key)
            retry_after = max(ttl, 1)

            return RateLimitResult(
                allowed=False,
                current_count=current,
                limit=limit,
                retry_after=retry_after,
                window_reset=retry_after
            )

        return RateLimitResult(
            allowed=True,
            current_count=current,
            limit=limit,
            window_reset=self.WINDOW_SIZE
        )

    async def get_usage_stats(
        self,
        admin_id: int,
        role: AIRole
    ) -> dict:
        """사용량 통계 조회"""
        now = datetime.utcnow()
        current_minute = now.strftime("%Y%m%d%H%M")
        key = f"ai_ratelimit:{admin_id}:{current_minute}"

        current = await self.redis.get(key)
        limit = self.RATE_LIMITS.get(role, 10)

        return {
            "current": int(current) if current else 0,
            "limit": limit,
            "remaining": max(0, limit - (int(current) if current else 0)),
            "reset_seconds": self.WINDOW_SIZE
        }
```

### Rate Limit Dependency

```python
# src/api/v1/dependencies/rate_limit.py
from fastapi import Depends, HTTPException, status, Request
from src.services.ai.audit.rate_limiter import AIRateLimiter, RateLimitResult
from src.services.ai.audit.audit_logger import AIAuditLogger
from src.services.ai.security.rbac import get_admin_ai_role

async def rate_limit_dependency(
    request: Request,
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis = Depends(get_redis),
) -> Admin:
    """Rate limit 검증 의존성"""
    role = get_admin_ai_role(current_admin)
    limiter = AIRateLimiter(redis_client)

    result = await limiter.check_rate_limit(current_admin.id, role)

    if not result.allowed:
        await AIAuditLogger.log_rate_limit_exceeded(
            admin_id=current_admin.id,
            admin_role=role.value,
            current_count=result.current_count,
            limit=result.limit
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"요청 한도를 초과했습니다. {result.retry_after}초 후 다시 시도해주세요.",
                "code": "AIBI_RATE_LIMITED",
                "retry_after": result.retry_after
            },
            headers={
                "Retry-After": str(result.retry_after),
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(result.window_reset)
            }
        )

    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(result.limit),
        "X-RateLimit-Remaining": str(result.limit - result.current_count),
        "X-RateLimit-Reset": str(result.window_reset)
    }

    return current_admin
```

### Logging Configuration

```python
# src/services/ai/audit/log_config.py
import structlog
import logging
from logging.handlers import TimedRotatingFileHandler

def configure_ai_audit_logging():
    """AI 감사 로깅 설정"""

    # 파일 핸들러 (90일 보관)
    file_handler = TimedRotatingFileHandler(
        filename="logs/ai_audit.log",
        when="midnight",
        interval=1,
        backupCount=90,  # 90일 보관
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    file_handler.setFormatter(
        logging.Formatter('%(message)s')  # structlog이 JSON 처리
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
```

### 로그 예시

```json
{
  "event": "ai_query_audit",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "admin_id": 123,
  "admin_role": "admin",
  "question": "오늘 매출 얼마야?",
  "db_scope": "mariadb",
  "generated_sql": "SELECT SUM(amount) FROM t_payment WHERE...",
  "execution_time_ms": 1523,
  "row_count": 1,
  "status": "success",
  "tables_accessed": ["t_payment"],
  "masked_columns": [],
  "timestamp": "2026-02-02T09:30:00.000Z"
}
```

### Dependencies

**Prerequisite Stories:**
- Story 1-3: 역할 기반 접근 제어 설정 (역할 정보)

**Blocked Stories:**
- Story 6-3: SLA 모니터링 및 알림 (로그 기반 알림)

**External Dependencies:**
- Redis (Rate Limiting)

### Architecture Requirements

- **FR17**: 질의/접근 로깅 ✓
- **FR28**: Rate Limiting ✓
- **NFR-S5**: 감사 로그 보존 90일 ✓
- **NFR-S6**: Rate Limiting 20 RPM / 200 RPH ✓
- **NFR-O1**: 구조화 로깅 JSON + 요청 ID ✓
- **AR18**: 역할별 Rate Limiting ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Audit-Logging]
- [RFC 6585 - HTTP 429 Too Many Requests](https://www.rfc-editor.org/rfc/rfc6585)

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
