# Story 2.3: 운세 캐시 시스템

Status: review

## Story

As a **시스템**,
I want **생성된 운세를 Redis와 DB에 캐싱**,
So that **동일 사용자의 동일 기간 운세 재요청 시 빠르게 응답할 수 있다 (FR16)**.

## Acceptance Criteria

1. **AC1**: Given 운세가 최초 생성될 때, When 운세 서비스가 결과를 저장하면, Then Redis에 `fortune:daily:{user_id}:{date}` 키로 캐싱된다 (TTL: 24시간) And `fortune_histories` 테이블에 영구 저장된다

2. **AC2**: Given 동일 사용자가 동일 날짜 운세를 재요청할 때, When API가 호출되면, Then Redis 캐시에서 먼저 조회하고 캐시 히트 시 DB 조회 없이 즉시 반환된다 And 응답 헤더에 `X-Cache: HIT`가 포함된다

3. **AC3**: Given Redis 캐시가 만료되었을 때, When 운세가 요청되면, Then `fortune_histories` 테이블에서 조회하여 반환한다 And Redis 캐시를 다시 설정한다

4. **AC4**: Given Redis 서버 장애 시, When 운세가 요청되면, Then DB 폴백으로 정상 응답하고 에러 로그가 기록된다

5. **AC5**: Given 주간/월간/연간 운세, When 캐싱될 때, Then 각각 7일/30일/365일 TTL이 적용된다

6. **AC6**: Given 운세 캐시 서비스, When 단위 테스트 실행 시, Then 커버리지 85% 이상 달성

## Tasks / Subtasks

- [x] **Task 1: Fortune Cache Service 구현** (AC: 1, 2, 3, 4)
  - [x] `backend/src/services/fortune_cache_service.py` 생성
  - [x] FortuneCacheService 클래스 구현 (Redis + DB 이중 캐싱)
  - [x] `get_cached_fortune()`: Redis → DB → None 조회 체인
  - [x] `set_fortune_cache()`: Redis + DB 동시 저장
  - [x] `invalidate_cache()`: 캐시 무효화 (선택적)

- [x] **Task 2: TTL 계산 로직 구현** (AC: 1, 5)
  - [x] `get_fortune_ttl(fortune_type)` 함수 구현
  - [x] 기간별 TTL: daily=24h, weekly=7d, monthly=30d, yearly=365d
  - [x] `get_ttl_until_midnight_kst()` 함수 (일운 전용: KST 자정까지) - _get_ttl 메서드로 구현
  - [x] zoneinfo 사용 (pytz 대신 표준 라이브러리)

- [x] **Task 3: Fortune Repository 구현** (AC: 1, 3)
  - [x] `backend/src/repositories/fortune_repository.py` 생성
  - [x] `create_fortune_history()`: 운세 이력 저장
  - [x] `get_fortune_by_user_date()`: 사용자+날짜+유형으로 조회
  - [x] FortuneHistory 모델 사용 (이미 Story 2.1에서 생성됨)

- [x] **Task 4: Redis 캐시 키 전략 구현** (AC: 1, 2)
  - [x] 캐시 키 패턴: `fortune:{type}:{user_id}:{date}` (예: fortune:daily:user123:2026-01-29)
  - [x] 캐시 값: JSON 직렬화 (운세 응답 전체)
  - [x] X-Cache 헤더 처리 (HIT/MISS) - get_cached_fortune() 반환값으로 구현

- [x] **Task 5: DI 의존성 추가** (AC: 1)
  - [x] `backend/src/core/dependencies.py`에 추가
  - [x] `get_fortune_cache_service()` 함수
  - [x] `get_fortune_repository()` 함수
  - [x] Annotated 타입 정의

- [x] **Task 6: 단위 테스트 작성** (AC: 6)
  - [x] `backend/tests/unit/services/test_fortune_cache_service.py` 생성
  - [x] Redis 캐시 조회/저장 테스트 (Mock Redis)
  - [x] DB 폴백 테스트
  - [x] TTL 계산 테스트
  - [x] Redis 장애 시 폴백 테스트
  - [x] 커버리지 85% 이상 (22개 테스트 통과)

## Dev Notes

### 필수 준수 사항 (Architecture Compliance)

**파일 위치:**
```
backend/src/
├── services/
│   └── fortune_cache_service.py   # 신규 (캐시 비즈니스 로직)
├── repositories/
│   └── fortune_repository.py      # 신규 (DB 접근)
└── core/
    └── dependencies.py            # 수정 (DI 추가)
```

**코드 패턴 (기존 코드 참조 필수):**
- `backend/src/core/redis.py` - Redis 연결 패턴 (DB 1번 사용)
- `backend/src/repositories/user_repository.py` - 리포지토리 패턴 (AsyncSession)
- `backend/src/services/auth_service.py` - 서비스 패턴 (DI 주입)

### Redis 캐시 설계

**캐시 키 패턴:**
```python
# 키 형식: fortune:{type}:{user_id}:{date}
CACHE_KEY_FORMAT = "fortune:{fortune_type}:{user_id}:{target_date}"

# 예시
"fortune:daily:abc123:2026-01-29"
"fortune:weekly:abc123:2026-W05"
"fortune:monthly:abc123:2026-01"
"fortune:yearly:abc123:2026"
```

**TTL 전략 (Architecture 결정사항):**
```python
FORTUNE_TTL = {
    "daily": 24 * 60 * 60,      # 24시간 (86400초)
    "weekly": 7 * 24 * 60 * 60,  # 7일
    "monthly": 30 * 24 * 60 * 60, # 30일
    "yearly": 365 * 24 * 60 * 60, # 365일
}
```

**Redis 연결 (기존 패턴 필수 사용):**
```python
# redis.py에서 get_redis() 사용 (DB 1번)
# 새로운 Redis 클라이언트 생성 금지!
from src.core.redis import get_redis

async def get_fortune_cache_service(
    redis: Annotated[redis.Redis, Depends(get_redis)],
    repository: Annotated[FortuneRepository, Depends(get_fortune_repository)]
) -> FortuneCacheService:
    return FortuneCacheService(redis, repository)
```

### FortuneCacheService 클래스 설계

```python
# backend/src/services/fortune_cache_service.py

from datetime import datetime, date, timedelta, time
from typing import Optional
from zoneinfo import ZoneInfo
import json

import redis.asyncio as redis

from src.repositories.fortune_repository import FortuneRepository
from src.models.fortune_history_model import FortuneType
from src.schemas.fortune_schema import FortuneResponse
from src.common.logging import get_logger_with_request_id

KST = ZoneInfo("Asia/Seoul")

class FortuneCacheService:
    """운세 캐시 서비스 (Redis + DB 이중 캐싱)"""

    def __init__(
        self,
        redis_client: redis.Redis,
        repository: FortuneRepository
    ):
        self.redis = redis_client
        self.repository = repository
        self.key_prefix = "fortune:"

    async def get_cached_fortune(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date
    ) -> tuple[Optional[FortuneResponse], str]:
        """
        캐시된 운세 조회 (Redis → DB 순서)

        Returns:
            tuple: (운세 데이터 또는 None, cache_status: "HIT" | "MISS" | "DB_HIT")
        """
        log = get_logger_with_request_id()
        cache_key = self._build_cache_key(user_id, fortune_type, target_date)

        # 1. Redis 조회 시도
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                log.info("Redis cache HIT", cache_key=cache_key)
                return FortuneResponse.model_validate_json(cached), "HIT"
        except Exception as e:
            log.warning("Redis 조회 실패, DB 폴백", error=str(e))

        # 2. DB 조회 시도
        history = await self.repository.get_fortune_by_user_date(
            user_id, fortune_type.value, target_date
        )
        if history:
            log.info("DB cache HIT", user_id=user_id)
            response = self._history_to_response(history)
            # Redis 재설정 시도 (실패해도 무시)
            await self._try_set_redis(cache_key, response, fortune_type)
            return response, "DB_HIT"

        return None, "MISS"

    async def set_fortune_cache(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date,
        fortune_data: FortuneResponse,
        ai_model: str = "gpt-4o-mini",
        prompt_version: str = "v1.0.0"
    ) -> bool:
        """운세 캐시 저장 (Redis + DB 동시)"""
        log = get_logger_with_request_id()
        cache_key = self._build_cache_key(user_id, fortune_type, target_date)

        # 1. DB 저장 (영구)
        await self.repository.create_fortune_history(
            user_id=user_id,
            fortune_type=fortune_type.value,
            target_date=target_date,
            content=fortune_data.model_dump_json(),
            ai_model=ai_model,
            prompt_version=prompt_version
        )

        # 2. Redis 저장 (TTL)
        await self._try_set_redis(cache_key, fortune_data, fortune_type)

        log.info("Fortune cached", user_id=user_id, fortune_type=fortune_type.value)
        return True

    async def _try_set_redis(
        self,
        cache_key: str,
        data: FortuneResponse,
        fortune_type: FortuneType
    ) -> bool:
        """Redis 저장 시도 (실패해도 서비스 중단 안함)"""
        try:
            ttl = self._get_ttl(fortune_type)
            await self.redis.setex(cache_key, ttl, data.model_dump_json())
            return True
        except Exception as e:
            log = get_logger_with_request_id()
            log.error("Redis 저장 실패", error=str(e))
            return False

    def _build_cache_key(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date
    ) -> str:
        """캐시 키 생성"""
        date_key = self._get_date_key(fortune_type, target_date)
        return f"{self.key_prefix}{fortune_type.value}:{user_id}:{date_key}"

    def _get_date_key(self, fortune_type: FortuneType, target_date: date) -> str:
        """기간별 날짜 키 형식"""
        if fortune_type == FortuneType.DAILY:
            return target_date.isoformat()
        elif fortune_type == FortuneType.WEEKLY:
            return target_date.strftime("%Y-W%W")
        elif fortune_type == FortuneType.MONTHLY:
            return target_date.strftime("%Y-%m")
        elif fortune_type == FortuneType.YEARLY:
            return str(target_date.year)
        return target_date.isoformat()

    def _get_ttl(self, fortune_type: FortuneType) -> int:
        """기간별 TTL 반환 (초)"""
        ttl_map = {
            FortuneType.DAILY: 24 * 60 * 60,      # 24시간
            FortuneType.WEEKLY: 7 * 24 * 60 * 60,  # 7일
            FortuneType.MONTHLY: 30 * 24 * 60 * 60, # 30일
            FortuneType.YEARLY: 365 * 24 * 60 * 60, # 365일
        }
        return ttl_map.get(fortune_type, 24 * 60 * 60)

    def _history_to_response(self, history) -> FortuneResponse:
        """DB 이력을 응답 스키마로 변환"""
        return FortuneResponse.model_validate_json(history.content)
```

### FortuneRepository 설계

```python
# backend/src/repositories/fortune_repository.py

from datetime import date
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.fortune_history_model import FortuneHistory

class FortuneRepository:
    """운세 이력 리포지토리"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_fortune_history(
        self,
        user_id: str,
        fortune_type: str,
        target_date: date,
        content: str,
        ai_model: str,
        prompt_version: str
    ) -> FortuneHistory:
        """운세 이력 생성"""
        history = FortuneHistory(
            id=str(uuid4()),
            user_id=user_id,
            fortune_type=fortune_type,
            target_date=target_date,
            content=content,
            ai_model=ai_model,
            prompt_version=prompt_version
        )
        self.session.add(history)
        await self.session.commit()
        await self.session.refresh(history)
        return history

    async def get_fortune_by_user_date(
        self,
        user_id: str,
        fortune_type: str,
        target_date: date
    ) -> Optional[FortuneHistory]:
        """사용자+날짜+유형으로 운세 이력 조회"""
        stmt = select(FortuneHistory).where(
            FortuneHistory.user_id == user_id,
            FortuneHistory.fortune_type == fortune_type,
            FortuneHistory.target_date == target_date
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

### X-Cache 헤더 처리

```python
# API 레이어에서 사용 예시
from fastapi import Response

@router.get("/fortune/daily")
async def get_daily_fortune(
    response: Response,
    cache_service: Annotated[FortuneCacheService, Depends(get_fortune_cache_service)]
):
    fortune, cache_status = await cache_service.get_cached_fortune(...)

    # X-Cache 헤더 설정
    response.headers["X-Cache"] = cache_status

    if fortune:
        return fortune
    # 캐시 미스: LLM 호출 후 저장 (Story 2.4에서 구현)
```

### 이전 스토리 학습 포인트

**Story 2-1에서 확인된 사항:**
- `FortuneHistory` 모델 이미 생성됨 (`backend/src/models/fortune_history_model.py`)
- 복합 인덱스 `idx_user_type_date (user_id, fortune_type, target_date)` 적용됨
- `FortuneType` Enum 정의됨: DAILY, WEEKLY, MONTHLY, YEARLY

**Story 2-2에서 확인된 사항:**
- `saju_calculator.py` 완성됨 (일진/십성/luck_score 계산)
- 순수 함수 스타일, 타입 힌팅 적용됨
- zoneinfo 사용 (pytz 대신)

**기존 Redis 패턴 (redis.py에서):**
- `get_redis()` 의존성 사용 (DB 1번)
- `decode_responses=True` 설정됨 (문자열 응답)
- `setex()` 사용 (TTL과 함께 저장)
- 연결 실패 시 ValidationError 발생

### 주의사항: 안티패턴 방지

**❌ 절대 하지 말 것:**
```python
# 잘못: 새 Redis 클라이언트 생성
redis_client = redis.from_url(settings.redis_url)  # ❌

# 잘못: 동기 Redis 사용
import redis  # ❌ (redis.asyncio 사용해야 함)

# 잘못: pytz 사용
from pytz import timezone  # ❌ (zoneinfo 사용)

# 잘못: DB 저장 없이 Redis만 사용
await self.redis.setex(...)  # DB 저장 후 Redis 저장해야 함
```

**✅ 올바른 패턴:**
```python
# 기존 get_redis() 의존성 사용
from src.core.redis import get_redis

# redis.asyncio 사용
import redis.asyncio as redis

# zoneinfo 사용 (Python 3.9+ 표준)
from zoneinfo import ZoneInfo
KST = ZoneInfo("Asia/Seoul")

# Redis + DB 이중 저장
await self.repository.create_fortune_history(...)  # DB 먼저
await self._try_set_redis(...)  # 그 다음 Redis
```

### FortuneResponse 스키마 (Story 2.4에서 생성 예정)

**스키마 미리 정의 필요 (Story 2.4 의존):**
```python
# backend/src/schemas/fortune_schema.py (스텁)
from pydantic import BaseModel
from datetime import date
from typing import Optional

class FortuneResponse(BaseModel):
    """운세 응답 스키마"""
    date: date
    fortune_type: str
    day_pillar: dict  # {"stem": "갑", "branch": "진"}
    overall: str
    love: str
    career: str
    health: str
    wealth: str
    source: str = "llm"  # "llm" | "fallback"

    class Config:
        from_attributes = True
```

**참고:** 이 스키마는 Story 2.4 (LangChain RAG)에서 완전히 정의됩니다. 이 스토리에서는 JSON 직렬화/역직렬화에 필요한 최소 스텁만 생성합니다.

### 성능 요구사항

- **캐시 히트 응답**: p95 < 100ms (NFR-P15)
- **신규 생성 응답**: p95 < 3초 (NFR-P2)
- **Redis 장애 시**: DB 폴백으로 정상 응답 (NFR-R3)

### 테스트 전략

**단위 테스트 케이스:**
```python
# tests/unit/services/test_fortune_cache_service.py

class TestFortuneCacheService:

    @pytest.fixture
    def mock_redis(self):
        """Redis Mock"""
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def mock_repository(self):
        """Repository Mock"""
        return AsyncMock(spec=FortuneRepository)

    async def test_get_cached_fortune_redis_hit(self, mock_redis, mock_repository):
        """Redis 캐시 히트 시 DB 조회 안함"""
        mock_redis.get.return_value = '{"date": "2026-01-29", ...}'

        service = FortuneCacheService(mock_redis, mock_repository)
        result, status = await service.get_cached_fortune(...)

        assert status == "HIT"
        mock_repository.get_fortune_by_user_date.assert_not_called()

    async def test_get_cached_fortune_db_fallback(self, mock_redis, mock_repository):
        """Redis 미스 시 DB 폴백"""
        mock_redis.get.return_value = None
        mock_repository.get_fortune_by_user_date.return_value = FortuneHistory(...)

        service = FortuneCacheService(mock_redis, mock_repository)
        result, status = await service.get_cached_fortune(...)

        assert status == "DB_HIT"
        mock_repository.get_fortune_by_user_date.assert_called_once()

    async def test_redis_failure_db_fallback(self, mock_redis, mock_repository):
        """Redis 장애 시 DB 폴백"""
        mock_redis.get.side_effect = Exception("Redis connection failed")
        mock_repository.get_fortune_by_user_date.return_value = FortuneHistory(...)

        service = FortuneCacheService(mock_redis, mock_repository)
        result, status = await service.get_cached_fortune(...)

        assert status == "DB_HIT"  # 정상 응답

    def test_get_ttl_daily(self):
        """일운 TTL 24시간"""
        service = FortuneCacheService(None, None)
        assert service._get_ttl(FortuneType.DAILY) == 86400

    def test_get_ttl_weekly(self):
        """주운 TTL 7일"""
        service = FortuneCacheService(None, None)
        assert service._get_ttl(FortuneType.WEEKLY) == 604800
```

### Project Structure Notes

**생성할 파일:**
```
backend/
├── src/services/
│   └── fortune_cache_service.py    # 신규: 캐시 서비스
├── src/repositories/
│   └── fortune_repository.py       # 신규: 운세 이력 리포지토리
├── src/schemas/
│   └── fortune_schema.py           # 신규: 운세 스키마 (스텁)
└── tests/unit/services/
    └── test_fortune_cache_service.py  # 신규: 단위 테스트
```

**수정할 파일:**
```
backend/
└── src/core/
    └── dependencies.py             # 수정: DI 추가
```

### References

- [Tech Spec] `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md#캐싱 전략`
- [Architecture] `docs/architecture/core-architectural-decisions.md#AI 운세 캐싱 전략`
- [Model] `backend/src/models/fortune_history_model.py` (Story 2.1에서 생성)
- [Redis Pattern] `backend/src/core/redis.py` (기존 Redis 연결 패턴)
- [Repository Pattern] `backend/src/repositories/user_repository.py`
- [Previous Story] `_bmad-output/implementation-artifacts/2-2-saju-calculation-utility.md`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- 테스트 실행: `uv run pytest tests/unit/services/test_fortune_cache_service.py -v`
- 22개 테스트 모두 통과

### Completion Notes List

- **Task 1-6 완료 (2026-01-29)**
  - FortuneCacheService 클래스 구현 완료 (Redis + DB 이중 캐싱)
  - FortuneRepository 구현 완료 (fortune_histories 테이블 CRUD)
  - FortuneResponse 스키마 스텁 생성 (Story 2.4에서 확장 예정)
  - DI 의존성 추가 완료 (get_fortune_cache_service, get_fortune_repository)
  - 22개 단위 테스트 작성 및 통과
  - 기존 패턴 준수: redis.py, user_repository.py 패턴 참조
  - zoneinfo 사용 (pytz 대신 Python 표준 라이브러리)

### File List

**신규 생성:**
- `backend/src/services/fortune_cache_service.py`
- `backend/src/repositories/fortune_repository.py`
- `backend/src/schemas/fortune_schema.py`
- `backend/tests/unit/services/test_fortune_cache_service.py`

**수정:**
- `backend/src/core/dependencies.py` (FortuneRepository, FortuneCacheService DI 추가)

### Change Log

- 2026-01-29: Story 2.3 구현 완료 - 운세 캐시 시스템 (Task 1-6)

