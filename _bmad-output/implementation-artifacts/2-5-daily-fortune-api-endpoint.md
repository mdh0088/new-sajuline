# Story 2.5: 일일 운세 API 엔드포인트

Status: completed

## Story

As a **로그인한 사용자**,
I want **일일 운세를 API로 조회 (FR10)**,
So that **오늘의 AI 운세 분석 결과를 확인할 수 있다**.

## Acceptance Criteria

1. **AC1**: Given 로그인한 사용자가 사주 정보를 등록했을 때, When `GET /api/v1/fortune/daily` API를 호출하면, Then 오늘 날짜 기준 일일 운세가 JSON 형식으로 반환된다
   - 응답 스키마: `{ success: true, data: { target_date, fortune_type, day_pillar: { stem, branch }, overall, love, career, health, wealth, source, created_at } }`
   - 응답 시간: p95 < 300ms (캐시 히트) 또는 < 3초 (신규 생성)

2. **AC2**: Given 사주 정보가 등록되지 않은 사용자일 때, When API를 호출하면, Then HTTP 400과 `{ success: false, error: { code: "SAJU_INFO_REQUIRED", message: "사주 정보를 먼저 등록해주세요" } }` 반환

3. **AC3**: Given 비로그인 사용자일 때, When API를 호출하면, Then HTTP 401 Unauthorized 반환

4. **AC4**: Given 특정 날짜의 운세를 조회할 때, When `GET /api/v1/fortune/daily?date=2026-01-28` 쿼리 파라미터로 호출하면, Then 해당 날짜의 운세가 반환된다 (과거 7일까지만 허용)

5. **AC5**: Given 허용 범위를 벗어난 날짜 요청 시, When 8일 이상 과거 또는 미래 날짜로 호출하면, Then HTTP 400과 `{ success: false, error: { code: "INVALID_DATE_RANGE", message: "조회 가능한 날짜 범위를 벗어났습니다" } }` 반환

6. **AC6**: Given 캐시된 운세를 반환할 때, When 응답이 생성되면, Then 응답 헤더에 `X-Cache: HIT` 또는 `X-Cache: MISS`가 포함된다

7. **AC7**: Given Fortune API 라우터, When 단위 테스트가 실행되면, Then 커버리지 85% 이상 달성

## Tasks / Subtasks

- [x] **Task 1: Fortune API 라우터 생성** (AC: 1, 6)
  - [x] `backend/src/api/v1/fortune_api.py` 파일 생성
  - [x] APIRouter 설정 (prefix="/fortune", tags=["fortune"])
  - [x] `GET /daily` 엔드포인트 기본 구조 구현
  - [x] Response 헤더에 X-Cache 설정

- [x] **Task 2: 인증 및 사주 정보 검증** (AC: 2, 3)
  - [x] `Depends(get_current_user)` 인증 적용
  - [x] 사용자의 사주 정보(birth_stem, birth_branch) 확인
  - [x] 사주 정보 미등록 시 HTTP 400 + SAJU_INFO_REQUIRED 에러
  - [x] CustomException 또는 HTTPException 사용

- [x] **Task 3: 날짜 파라미터 처리** (AC: 4, 5)
  - [x] date 쿼리 파라미터 정의 (Optional, 기본값: 오늘)
  - [x] 날짜 범위 검증 (과거 7일 ~ 오늘)
  - [x] 범위 초과 시 HTTP 400 + INVALID_DATE_RANGE 에러
  - [x] 날짜 형식 검증 (YYYY-MM-DD)

- [x] **Task 4: FortuneService 연동** (AC: 1)
  - [x] FortuneServiceDep 의존성 주입
  - [x] fortune_service.get_daily_fortune() 호출
  - [x] 캐시 상태(cache_status) 처리
  - [x] FortuneResponse → APIResponse 변환

- [x] **Task 5: Rate Limiting 적용** (AC: 1)
  - [x] @limiter.limit("100/minute") 데코레이터 적용
  - [x] Rate limit 초과 시 HTTP 429 반환 (slowapi 기본 동작)
  - [x] 테스트에서 limiter.enabled = False로 비활성화

- [x] **Task 6: 라우터 등록** (AC: 1)
  - [x] `backend/src/api/v1/__init__.py`에 fortune_router import
  - [x] `backend/src/main.py`에 라우터 include

- [x] **Task 7: 단위 테스트 작성** (AC: 7)
  - [x] `backend/tests/unit/api/test_fortune_api.py` 생성
  - [x] 정상 응답 테스트 (캐시 히트/미스)
  - [x] 사주 정보 미등록 에러 테스트
  - [x] 인증 실패 테스트
  - [x] 날짜 범위 초과 테스트
  - [x] 14개 테스트 케이스 작성 완료

## Dev Notes

### 필수 준수 사항 (Architecture Compliance)

**파일 위치:**
```
backend/src/api/v1/
├── fortune_api.py          # 신규: Fortune API 라우터
└── __init__.py             # 수정: fortune_router 추가

backend/src/
└── main.py                 # 수정: fortune_router include

backend/tests/unit/api/
└── test_fortune_api.py     # 신규: 단위 테스트
```

**기존 패턴 필수 참조:**
- `backend/src/api/v1/user_api.py` - 라우터 구조, 인증, 로깅, Rate Limiting
- `backend/src/core/dependencies.py` - FortuneServiceDep 이미 정의됨
- `backend/src/common/response/__init__.py` - APIResponse, APIResponseBuilder

### 이전 스토리 학습 포인트 (반드시 활용)

**Story 2-1에서 생성된 모델:**
- `FortuneHistory`: 운세 이력 (user_id, fortune_type, target_date, content)
- `FortuneType`: Enum (DAILY, WEEKLY, MONTHLY, YEARLY)

**Story 2-2에서 생성된 유틸리티:**
```python
# backend/src/common/utils/saju_calculator.py
from src.common.utils.saju_calculator import get_ilju, calculate_sipsung
```

**Story 2-3에서 생성된 캐시 서비스:**
```python
# backend/src/services/fortune_cache_service.py
from src.services.fortune_cache_service import FortuneCacheService
# 캐시 상태: "HIT" | "DB_HIT" | "MISS"
```

**Story 2-4에서 생성된 FortuneService (핵심):**
```python
# backend/src/services/fortune_service.py
from src.services.fortune_service import FortuneService
from src.core.dependencies import FortuneServiceDep

# FortuneService.get_daily_fortune() 메서드 시그니처:
async def get_daily_fortune(
    self,
    user_id: str,
    birth_stem: str,    # 사용자 일간 (갑, 을, 병 ...)
    birth_branch: str,  # 사용자 일지 (자, 축, 인 ...)
    target_date: Optional[date] = None
) -> FortuneResponse:
    """
    일일 운세 조회 (캐시 → LLM → 폴백)
    Returns: FortuneResponse with source ("llm" | "fallback" | "cache")
    """
```

**Story 2-4에서 생성된 FortuneResponse 스키마:**
```python
# backend/src/schemas/fortune_schema.py
from src.schemas.fortune_schema import FortuneResponse, DayPillar

class DayPillar(BaseModel):
    stem: str   # "갑"
    branch: str # "진"

class FortuneResponse(BaseModel):
    target_date: date
    fortune_type: str           # "daily"
    day_pillar: DayPillar
    overall: str                # 총운
    love: str                   # 애정운
    career: str                 # 직장운
    health: str                 # 건강운
    wealth: str                 # 재물운
    lucky_color: Optional[str]
    lucky_number: Optional[int]
    source: str                 # "llm" | "fallback" | "cache"
```

**dependencies.py에 이미 정의된 DI:**
```python
# 이미 존재함 - 추가 작업 불필요
FortuneServiceDep = Annotated[FortuneService, Depends(get_fortune_service)]
FortuneCacheServiceDep = Annotated[FortuneCacheService, Depends(get_fortune_cache_service)]
```

### Fortune API 라우터 설계

```python
# backend/src/api/v1/fortune_api.py

"""
AI 운세 API 엔드포인트
"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.common.middleware.rate_limit import limiter
from src.common.logging import get_logger_with_request_id
from src.common.response import APIResponse, APIResponseBuilder, ok, fail
from src.core.dependencies import FortuneServiceDep
from src.schemas.fortune_schema import FortuneResponse
from src.services.auth_service import get_current_user, TokenPayload

router = APIRouter(prefix="/fortune", tags=["fortune"])


@router.get(
    "/daily",
    response_model=APIResponse[FortuneResponse],
    summary="일일 운세 조회",
    description="로그인한 사용자의 일일 AI 운세를 조회합니다."
)
@limiter.limit("100/minute")
async def get_daily_fortune(
    response: Response,
    fortune_service: FortuneServiceDep,
    current_user: TokenPayload = Depends(get_current_user),
    target_date: Optional[date] = Query(
        None,
        alias="date",
        description="조회할 날짜 (YYYY-MM-DD, 기본: 오늘, 과거 7일까지)"
    )
) -> APIResponse[FortuneResponse]:
    """
    일일 운세 조회 API

    - **로그인 필수**: JWT 토큰 인증
    - **사주 정보 필수**: 사용자의 birth_stem, birth_branch 등록 필요
    - **날짜 범위**: 오늘 ~ 과거 7일
    - **캐싱**: Redis 24시간 + DB 영구 저장
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub

    log.info("API: Daily fortune request", user_id=user_id, target_date=str(target_date))

    # 1. 날짜 검증
    today = date.today()
    if target_date is None:
        target_date = today
    else:
        min_date = today - timedelta(days=7)
        if target_date < min_date or target_date > today:
            log.warning("API: Invalid date range", target_date=str(target_date))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_DATE_RANGE",
                    "message": "조회 가능한 날짜 범위를 벗어났습니다 (오늘 ~ 과거 7일)"
                }
            )

    # 2. 사주 정보 확인
    # Note: current_user에서 birth_stem, birth_branch 가져오기
    # TokenPayload에 사주 정보가 없으면 DB에서 조회 필요
    birth_stem = getattr(current_user, 'birth_stem', None)
    birth_branch = getattr(current_user, 'birth_branch', None)

    if not birth_stem or not birth_branch:
        log.warning("API: Saju info not registered", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SAJU_INFO_REQUIRED",
                "message": "사주 정보를 먼저 등록해주세요"
            }
        )

    # 3. 운세 조회
    fortune, cache_status = await fortune_service.get_daily_fortune_with_status(
        user_id=user_id,
        birth_stem=birth_stem,
        birth_branch=birth_branch,
        target_date=target_date
    )

    # 4. X-Cache 헤더 설정
    response.headers["X-Cache"] = cache_status

    log.info(
        "API: Daily fortune retrieved",
        user_id=user_id,
        target_date=str(target_date),
        cache_status=cache_status,
        source=fortune.source
    )

    return APIResponseBuilder.ok(
        data=fortune,
        message="일일 운세 조회 성공"
    )
```

### 사주 정보 조회 전략

**현재 TokenPayload에 birth_stem/birth_branch가 없는 경우:**
```python
# 옵션 1: User 모델에서 조회 (권장)
# UserRepository를 FortuneService에 추가하거나 별도 조회

# backend/src/api/v1/fortune_api.py (수정안)
from src.core.dependencies import FortuneServiceDep, UserRepositoryDep

@router.get("/daily", ...)
async def get_daily_fortune(
    ...,
    user_repo: UserRepositoryDep,  # 추가
):
    # 사용자 정보 조회
    user = await user_repo.get_by_id(current_user.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    birth_stem = user.birth_stem
    birth_branch = user.birth_branch

    if not birth_stem or not birth_branch:
        raise HTTPException(
            status_code=400,
            detail={"code": "SAJU_INFO_REQUIRED", "message": "사주 정보를 먼저 등록해주세요"}
        )
```

**User 모델에 사주 필드 확인 필요:**
```python
# backend/src/models/user_model.py 확인 필요
# - birth_stem: str (일간, 갑~계)
# - birth_branch: str (일지, 자~해)
# - 또는 birth_datetime에서 계산

# 만약 birth_datetime만 있다면:
from src.common.utils.saju_calculator import get_ilju
birth_stem, birth_branch = get_ilju(user.birth_date)
```

### FortuneService 수정 필요 사항

**현재 get_daily_fortune()은 캐시 상태를 반환하지 않음:**
```python
# Story 2-4 구현 시 cache_status 반환 필요
# 또는 별도 메서드 생성

# 옵션 1: 기존 메서드 수정
async def get_daily_fortune(...) -> tuple[FortuneResponse, str]:
    # ... 기존 로직 ...
    return fortune, cache_status  # "HIT" | "DB_HIT" | "MISS"

# 옵션 2: 새 메서드 추가 (권장 - 하위 호환성)
async def get_daily_fortune_with_status(...) -> tuple[FortuneResponse, str]:
    # 캐시 확인
    cached, status = await self.cache_service.get_cached_fortune(...)
    if cached:
        return cached, status

    # LLM 호출
    fortune = await self._generate_fortune(...)
    await self.cache_service.set_fortune_cache(...)
    return fortune, "MISS"
```

### 에러 핸들링 패턴

**기존 프로젝트 패턴 참조 (user_api.py, auth_api.py):**
```python
from src.exceptions.custom_exceptions import BaseAppException

# HTTPException 사용 (단순 에러)
raise HTTPException(
    status_code=400,
    detail={"code": "SAJU_INFO_REQUIRED", "message": "사주 정보를 먼저 등록해주세요"}
)

# 또는 CustomException 사용 (통합 에러 핸들링)
class SajuInfoRequiredException(BaseAppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="SAJU_INFO_REQUIRED",
            message="사주 정보를 먼저 등록해주세요"
        )

raise SajuInfoRequiredException()
```

### 라우터 등록

**backend/src/api/v1/__init__.py:**
```python
from src.api.v1.fortune_api import router as fortune_router

# 기존 라우터들...
__all__ = [
    # ... 기존 라우터들 ...
    "fortune_router",
]
```

**backend/src/main.py:**
```python
from src.api.v1 import fortune_router

# 라우터 등록 (기존 패턴 따름)
app.include_router(fortune_router, prefix="/api/v1")
```

### 주의사항: 안티패턴 방지

**❌ 절대 하지 말 것:**
```python
# 잘못: FortuneService 재구현
async def get_daily_fortune(...):
    llm = ChatOpenAI(...)  # ❌ 이미 FortuneService에 있음

# 잘못: 캐시 로직 직접 구현
redis_client.get(f"fortune:daily:{user_id}")  # ❌ FortuneCacheService 사용

# 잘못: saju_calculator 함수 재구현
def calculate_ilju(...):  # ❌ 이미 존재함

# 잘못: 타임아웃 없는 LLM 호출
# FortuneService 내부에서 이미 10초 타임아웃 설정됨

# 잘못: dependencies.py에 중복 DI 추가
def get_fortune_service(...):  # ❌ 이미 존재함
```

**✅ 올바른 패턴:**
```python
# 기존 DI 사용
from src.core.dependencies import FortuneServiceDep, UserRepositoryDep

# 기존 서비스 호출
fortune = await fortune_service.get_daily_fortune(...)

# 기존 유틸리티 사용
from src.common.utils.saju_calculator import get_ilju

# 기존 응답 빌더 사용
from src.common.response import APIResponseBuilder
return APIResponseBuilder.ok(data=fortune, message="성공")
```

### 테스트 전략

**단위 테스트:**
```python
# backend/tests/unit/api/test_fortune_api.py

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.schemas.fortune_schema import FortuneResponse, DayPillar


class TestDailyFortuneAPI:
    """일일 운세 API 테스트"""

    @pytest.fixture
    def mock_fortune_service(self):
        """FortuneService Mock"""
        service = AsyncMock()
        service.get_daily_fortune_with_status.return_value = (
            FortuneResponse(
                target_date=date.today(),
                fortune_type="daily",
                day_pillar=DayPillar(stem="갑", branch="진"),
                overall="오늘은 좋은 날입니다.",
                love="로맨틱한 하루",
                career="승진 기회",
                health="건강 양호",
                wealth="재물운 상승",
                source="llm"
            ),
            "MISS"
        )
        return service

    @pytest.fixture
    def mock_current_user(self):
        """인증된 사용자 Mock"""
        return MagicMock(
            sub="user-123",
            birth_stem="갑",
            birth_branch="자"
        )

    async def test_get_daily_fortune_success(
        self, mock_fortune_service, mock_current_user
    ):
        """정상 운세 조회"""
        with patch("src.api.v1.fortune_api.get_current_user", return_value=mock_current_user):
            with patch("src.core.dependencies.get_fortune_service", return_value=mock_fortune_service):
                response = client.get("/api/v1/fortune/daily")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.headers.get("X-Cache") == "MISS"

    async def test_get_daily_fortune_cache_hit(
        self, mock_fortune_service, mock_current_user
    ):
        """캐시 히트 시 X-Cache: HIT"""
        mock_fortune_service.get_daily_fortune_with_status.return_value = (
            FortuneResponse(...),
            "HIT"
        )
        # ... 테스트 로직

    async def test_get_daily_fortune_no_saju_info(self, mock_current_user):
        """사주 정보 미등록 시 400 에러"""
        mock_current_user.birth_stem = None
        mock_current_user.birth_branch = None

        with patch("src.api.v1.fortune_api.get_current_user", return_value=mock_current_user):
            response = client.get("/api/v1/fortune/daily")

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "SAJU_INFO_REQUIRED"

    async def test_get_daily_fortune_unauthorized(self):
        """비로그인 시 401 에러"""
        response = client.get("/api/v1/fortune/daily")
        assert response.status_code == 401

    async def test_get_daily_fortune_invalid_date_range(self, mock_current_user):
        """날짜 범위 초과 시 400 에러"""
        old_date = (date.today() - timedelta(days=10)).isoformat()

        with patch("src.api.v1.fortune_api.get_current_user", return_value=mock_current_user):
            response = client.get(f"/api/v1/fortune/daily?date={old_date}")

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_DATE_RANGE"

    async def test_get_daily_fortune_with_specific_date(
        self, mock_fortune_service, mock_current_user
    ):
        """특정 날짜 운세 조회"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        with patch("src.api.v1.fortune_api.get_current_user", return_value=mock_current_user):
            response = client.get(f"/api/v1/fortune/daily?date={yesterday}")

        assert response.status_code == 200
        mock_fortune_service.get_daily_fortune_with_status.assert_called_once()
```

### 성능 요구사항

| 항목 | 목표 | 근거 |
|------|------|------|
| 캐시 히트 응답 | p95 < 300ms | NFR-P1 |
| 신규 생성 응답 | p95 < 3초 | NFR-P2 |
| Rate Limit | 100 req/min | NFR-S8 |
| LLM 타임아웃 | 10초 | Story 2-4 |

### Project Structure Notes

**신규 생성:**
```
backend/
├── src/api/v1/
│   └── fortune_api.py          # Fortune API 라우터
└── tests/unit/api/
    └── test_fortune_api.py     # 단위 테스트
```

**수정:**
```
backend/
├── src/api/v1/__init__.py      # fortune_router 추가
├── src/main.py                 # 라우터 등록
└── src/services/fortune_service.py  # get_daily_fortune_with_status 추가 (선택)
```

### References

- [Tech Spec] `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md#Task 14-15`
- [Architecture] `docs/architecture/implementation-patterns-consistency-rules.md`
- [Previous Story 2.4] `_bmad-output/implementation-artifacts/2-4-langchain-rag-chain.md`
- [Previous Story 2.3] `_bmad-output/implementation-artifacts/2-3-fortune-cache-system.md`
- [API Pattern] `backend/src/api/v1/user_api.py` - 라우터 구조, 인증
- [DI Pattern] `backend/src/core/dependencies.py` - FortuneServiceDep
- [Response Pattern] `backend/src/common/response/__init__.py` - APIResponseBuilder

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- httpx 0.28.1 및 starlette 0.36.3 버전 호환성 문제로 TestClient 대신 ASGITransport 사용
- TrustedHostMiddleware로 인해 테스트 base_url을 "localhost"로 설정 필요
- Redis 연결 없이 테스트하기 위해 모든 의존성(get_fortune_service, get_user_repository) 모킹 필요

### Completion Notes List

1. Fortune API 라우터 (`src/api/v1/fortune_api.py`) 구현 완료
   - GET /api/v1/fortune/daily 엔드포인트
   - 인증 필수 (get_current_user)
   - 사주 정보 검증 (birth_date 필드에서 일주 계산)
   - 날짜 범위 검증 (오늘 ~ 과거 7일)
   - X-Cache 헤더 설정 (HIT/MISS)
   - Rate Limiting: @limiter.limit("100/minute") 적용

2. 단위 테스트 14개 작성 완료
   - 정상 조회 (캐시 히트/미스)
   - 사주 정보 미등록 에러 (400)
   - 인증 실패 에러 (401)
   - 사용자 미발견 에러 (404)
   - 날짜 범위 초과 에러 (400)
   - 엣지 케이스 (7일/8일 전, 오늘 날짜, 생년월일 형식 오류)
   - 테스트 시 limiter.enabled = False로 비활성화

3. Rate Limiting 적용 완료
   - slowapi limiter 사용 (분당 100회 제한)
   - Redis DB 2번 사용 (rate_limit 전용)
   - 초과 시 HTTP 429 Too Many Requests 반환

### File List

**신규 생성:**
- `backend/src/api/v1/fortune_api.py` - Fortune API 라우터
- `backend/tests/unit/api/test_fortune_api.py` - 단위 테스트 (14개)

**수정:**
- `backend/src/api/v1/__init__.py` - fortune_router import 추가
- `backend/src/main.py` - fortune_router 등록, openapi 태그 추가

