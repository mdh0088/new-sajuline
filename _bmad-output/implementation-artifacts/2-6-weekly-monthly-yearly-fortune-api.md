# Story 2.6: 주간/월간/연간 운세 API 확장

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **로그인한 사용자**,
I want **주간, 월간, 연간 운세를 API로 조회 (FR11, FR12, FR13)**,
So that **다양한 기간의 AI 운세 분석 결과를 확인할 수 있다**.

## Acceptance Criteria

1. **AC1**: Given 로그인한 사용자가 사주 정보를 등록했을 때, When `GET /api/v1/fortune/weekly` API를 호출하면, Then 이번 주 기준 주간 운세가 반환된다 And Redis 캐시 TTL은 7일이다

2. **AC2**: Given 로그인한 사용자가 사주 정보를 등록했을 때, When `GET /api/v1/fortune/monthly` API를 호출하면, Then 이번 달 기준 월간 운세가 반환된다 And Redis 캐시 TTL은 30일이다

3. **AC3**: Given 로그인한 사용자가 사주 정보를 등록했을 때, When `GET /api/v1/fortune/yearly` API를 호출하면, Then 올해 기준 연간 운세가 반환된다 And Redis 캐시 TTL은 365일이다

4. **AC4**: Given 각 기간별 운세 응답 시, When API가 반환되면, Then 응답 스키마는 일일 운세와 동일하며, `fortune_type`이 각각 `weekly`, `monthly`, `yearly`로 구분된다 And 해당 기간에 맞는 운세 내용이 생성된다 (주간: 7일 흐름, 월간: 월별 흐름, 연간: 연간 운세)

5. **AC5**: Given 비로그인 사용자일 때, When 주간/월간/연간 API를 호출하면, Then HTTP 401 Unauthorized 반환

6. **AC6**: Given 사주 정보가 등록되지 않은 사용자일 때, When 주간/월간/연간 API를 호출하면, Then HTTP 400과 `{ success: false, error: { code: "SAJU_INFO_REQUIRED", message: "사주 정보를 먼저 등록해주세요" } }` 반환

7. **AC7**: Given 기간별 운세 API, When 단위 테스트가 실행되면, Then 커버리지 85% 이상 달성

## Tasks / Subtasks

- [x] **Task 1: 기간별 프롬프트 템플릿 추가** (AC: 4)
  - [x] `backend/src/core/prompts.py` 수정
  - [x] `WEEKLY_FORTUNE_USER_PROMPT_TEMPLATE` 추가 (7일 흐름 강조)
  - [x] `MONTHLY_FORTUNE_USER_PROMPT_TEMPLATE` 추가 (월별 운세 흐름)
  - [x] `YEARLY_FORTUNE_USER_PROMPT_TEMPLATE` 추가 (연간 대운 흐름)
  - [x] 각 프롬프트에 기간 특성 반영 (주간: 요일별 조언, 월간: 월초/중/말 구분, 연간: 계절별 흐름)

- [x] **Task 2: LangChain 체인 기간별 메서드 추가** (AC: 4)
  - [x] `backend/src/core/langchain_chain.py` 수정
  - [x] `generate_weekly_fortune()` 메서드 추가
  - [x] `generate_monthly_fortune()` 메서드 추가
  - [x] `generate_yearly_fortune()` 메서드 추가
  - [x] 공통 프롬프트 체인 생성 패턴 적용

- [x] **Task 3: FortuneService 기간별 메서드 추가** (AC: 1, 2, 3, 4)
  - [x] `backend/src/services/fortune_service.py` 수정
  - [x] `get_weekly_fortune()` 메서드 추가
  - [x] `get_monthly_fortune()` 메서드 추가
  - [x] `get_yearly_fortune()` 메서드 추가
  - [x] `get_weekly_fortune_with_status()` 메서드 추가 (캐시 상태 반환)
  - [x] `get_monthly_fortune_with_status()` 메서드 추가
  - [x] `get_yearly_fortune_with_status()` 메서드 추가
  - [x] 기간별 target_date 계산 로직 구현 (주간: 월요일 기준, 월간: 1일 기준)

- [x] **Task 4: FortuneCacheService TTL 확장** (AC: 1, 2, 3)
  - [x] `backend/src/services/fortune_cache_service.py` 확인 (이미 구현됨)
  - [x] FortuneType.WEEKLY TTL: 7일 (604800초)
  - [x] FortuneType.MONTHLY TTL: 30일 (2592000초)
  - [x] FortuneType.YEARLY TTL: 365일 (31536000초)
  - [x] 캐시 키 패턴 확인: `fortune:{type}:{user_id}:{period_key}`

- [x] **Task 5: Fortune API 엔드포인트 추가** (AC: 1, 2, 3, 5, 6)
  - [x] `backend/src/api/v1/fortune_api.py` 수정
  - [x] `GET /weekly` 엔드포인트 추가
  - [x] `GET /monthly` 엔드포인트 추가
  - [x] `GET /yearly` 엔드포인트 추가
  - [x] 공통 인증 및 사주 정보 검증 로직 재사용 (`_validate_user_and_get_saju()`)
  - [x] X-Cache 헤더 설정
  - [x] Rate Limiting: 100/minute (일일 운세와 동일)

- [x] **Task 6: 단위 테스트 작성** (AC: 7)
  - [x] `backend/tests/unit/api/test_fortune_api.py` 확장
  - [x] 주간 운세 정상 조회 테스트
  - [x] 월간 운세 정상 조회 테스트
  - [x] 연간 운세 정상 조회 테스트
  - [x] 각 기간별 캐시 히트/미스 테스트
  - [x] 인증 실패 테스트 (각 엔드포인트)
  - [x] 사주 정보 미등록 테스트 (각 엔드포인트)
  - [x] 각 기간별 fortune_type 검증

## Dev Notes

### 필수 준수 사항 (Architecture Compliance)

**파일 위치:**
```
backend/src/
├── api/v1/
│   └── fortune_api.py          # 수정: weekly/monthly/yearly 엔드포인트 추가
├── core/
│   ├── prompts.py              # 수정: 기간별 프롬프트 템플릿 추가
│   └── langchain_chain.py      # 수정: 기간별 생성 메서드 추가
└── services/
    ├── fortune_service.py      # 수정: 기간별 조회 메서드 추가
    └── fortune_cache_service.py # 수정: 기간별 TTL 설정

backend/tests/unit/api/
└── test_fortune_api.py         # 수정: 기간별 테스트 추가
```

**⚠️ 중요: 기존 코드 재사용 필수**
- 새로운 파일 생성 금지 (기존 파일 수정만)
- Story 2.4, 2.5에서 구현된 패턴을 그대로 따름
- 중복 코드 최소화 (공통 로직 추출)

### 이전 스토리 학습 포인트 (반드시 활용)

**Story 2.4에서 구현된 LangChain 체인 (그대로 재사용):**
```python
# backend/src/core/langchain_chain.py
from src.core.langchain_chain import DailyFortuneChain

# 기존 DailyFortuneChain 클래스에 메서드만 추가
# 새 클래스 생성 금지!
```

**Story 2.5에서 구현된 API 패턴 (그대로 재사용):**
```python
# backend/src/api/v1/fortune_api.py
from src.api.v1.fortune_api import router  # 기존 라우터에 엔드포인트 추가

# 인증 패턴 (동일하게 사용):
current_user: TokenPayload = Depends(get_current_user)

# 사주 정보 검증 (동일하게 사용):
user = await user_repo.get_by_id(current_user.sub)
if not user or not user.birth_date:
    raise HTTPException(status_code=400, detail={"code": "SAJU_INFO_REQUIRED", ...})

# 응답 패턴 (동일하게 사용):
response.headers["X-Cache"] = cache_status
return APIResponseBuilder.ok(data=fortune, message="주간 운세 조회 성공")
```

**Story 2.3에서 구현된 캐시 서비스 (확장 필요):**
```python
# backend/src/services/fortune_cache_service.py
# 기존 TTL 설정:
CACHE_TTL = {
    FortuneType.DAILY: 86400,      # 24시간
    FortuneType.WEEKLY: 604800,    # 7일 (추가 필요)
    FortuneType.MONTHLY: 2592000,  # 30일 (추가 필요)
    FortuneType.YEARLY: 31536000,  # 365일 (추가 필요)
}

# 캐시 키 패턴 (동일):
# fortune:{type}:{user_id}:{date}
# weekly: fortune:weekly:{user_id}:{week_start_date}
# monthly: fortune:monthly:{user_id}:{year}-{month}
# yearly: fortune:yearly:{user_id}:{year}
```

### 기간별 프롬프트 템플릿 설계

**주간 운세 프롬프트 (추가):**
```python
# backend/src/core/prompts.py

WEEKLY_FORTUNE_USER_PROMPT_TEMPLATE = """
오늘 날짜: {today}
주간 시작일: {week_start}
주간 종료일: {week_end}
사용자 일간: {ilgan} ({ilgan_oheng} {ilgan_yin_yang})

[주간 일진 흐름]
{weekly_pillar_summary}

[십성 관계]
일간({ilgan}) → 주간 주요 십성: {main_sipsung}
해석: {sipsung_interpretation}

[지지 관계]
{jiji_relation}
해석: {jiji_interpretation}

이번 주({week_start} ~ {week_end})의 운세를 JSON 형식으로 작성해주세요.
- 주초/주중/주말의 흐름을 고려하여 조언해주세요.
- 각 섹션은 50~150자로 작성해주세요.
"""
```

**월간 운세 프롬프트 (추가):**
```python
MONTHLY_FORTUNE_USER_PROMPT_TEMPLATE = """
오늘 날짜: {today}
대상 월: {target_month} ({month_name})
사용자 일간: {ilgan} ({ilgan_oheng} {ilgan_yin_yang})

[월간 일진 흐름]
월주(월간+월지): {month_pillar}
해석: {month_interpretation}

[십성 관계]
일간({ilgan}) → 월간({month_gan}) = {main_sipsung}
해석: {sipsung_interpretation}

[지지 관계]
{jiji_relation}
해석: {jiji_interpretation}

{target_month}의 월간 운세를 JSON 형식으로 작성해주세요.
- 월초/월중/월말의 흐름을 고려하여 조언해주세요.
- 각 섹션은 50~150자로 작성해주세요.
"""
```

**연간 운세 프롬프트 (추가):**
```python
YEARLY_FORTUNE_USER_PROMPT_TEMPLATE = """
오늘 날짜: {today}
대상 연도: {target_year}년
사용자 일간: {ilgan} ({ilgan_oheng} {ilgan_yin_yang})

[연간 대운]
연주(연간+연지): {year_pillar}
{year_pillar} 해석: {year_interpretation}

[십성 관계]
일간({ilgan}) → 연간({year_gan}) = {main_sipsung}
해석: {sipsung_interpretation}

[지지 관계]
{jiji_relation}
해석: {jiji_interpretation}

{target_year}년의 연간 운세를 JSON 형식으로 작성해주세요.
- 봄/여름/가을/겨울 계절별 흐름을 고려하여 조언해주세요.
- 특히 올해의 전체적인 방향과 주의점을 강조해주세요.
- 각 섹션은 50~150자로 작성해주세요.
"""
```

### 기간별 날짜 계산 로직

```python
# backend/src/services/fortune_service.py

from datetime import date, timedelta

def get_week_start(target_date: date) -> date:
    """주의 시작일(월요일) 계산"""
    return target_date - timedelta(days=target_date.weekday())

def get_week_end(target_date: date) -> date:
    """주의 종료일(일요일) 계산"""
    return target_date + timedelta(days=6 - target_date.weekday())

def get_month_key(target_date: date) -> str:
    """월간 캐시 키용 문자열 (예: "2026-01")"""
    return target_date.strftime("%Y-%m")

def get_year_key(target_date: date) -> str:
    """연간 캐시 키용 문자열 (예: "2026")"""
    return str(target_date.year)
```

### 연주/월주 계산 로직 (saju_calculator 확장 필요 여부 확인)

**현재 saju_calculator.py에 있는 함수:**
- `get_ilju(date)` → 일주(일간+일지) 계산

**필요한 추가 함수 (Story 2.6에서 구현 또는 확인):**
```python
# 월주 계산이 필요한 경우 (간단 버전):
def get_month_pillar(target_date: date) -> tuple[str, str]:
    """월주(월간+월지) 계산"""
    # 간략화: 월지는 월에 따라 고정
    # 월간은 연간에 따라 계산 (복잡한 절입시간 계산 생략)
    MONTH_JIJI = ["인", "묘", "진", "사", "오", "미", "신", "유", "술", "해", "자", "축"]
    month = target_date.month
    jiji = MONTH_JIJI[(month + 1) % 12]  # 정월=인월
    # 월간 계산은 복잡하므로 Phase 2로 미룸, 일단 고정값 사용
    return "?", jiji  # 월간은 추후 구현

def get_year_pillar(target_date: date) -> tuple[str, str]:
    """연주(연간+연지) 계산"""
    # 기준: 2000년 = 경진년
    CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
    JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
    base_year = 2000
    base_gan_idx = 6  # 경
    base_ji_idx = 4   # 진
    diff = target_date.year - base_year
    gan = CHEONGAN[(base_gan_idx + diff) % 10]
    ji = JIJI[(base_ji_idx + diff) % 12]
    return gan, ji
```

**⚠️ 중요: 월간(月干) 계산은 절입시간에 따라 달라지므로 복잡합니다.**
**MVP에서는 월주 계산을 생략하고, 일주(일진)를 기준으로 주간/월간 운세를 생성합니다.**
**연주(年柱)는 간단히 계산 가능 → get_year_pillar() 구현 필요**

### API 엔드포인트 설계

```python
# backend/src/api/v1/fortune_api.py

@router.get(
    "/weekly",
    response_model=APIResponse[FortuneResponse],
    summary="주간 운세 조회",
    description="로그인한 사용자의 주간 AI 운세를 조회합니다."
)
@limiter.limit("100/minute")
async def get_weekly_fortune(
    response: Response,
    fortune_service: FortuneServiceDep,
    user_repo: UserRepositoryDep,
    current_user: TokenPayload = Depends(get_current_user),
) -> APIResponse[FortuneResponse]:
    """주간 운세 조회 API (이번 주 월요일 ~ 일요일)"""
    log = get_logger_with_request_id()
    user_id = current_user.sub

    # 사용자 및 사주 정보 확인 (공통 로직)
    user = await _validate_user_saju(user_repo, user_id, log)

    # 일주 계산 (생년월일에서)
    birth_stem, birth_branch = get_ilju(user.birth_date)

    # 주간 운세 조회
    fortune, cache_status = await fortune_service.get_weekly_fortune_with_status(
        user_id=user_id,
        birth_stem=birth_stem,
        birth_branch=birth_branch,
    )

    response.headers["X-Cache"] = cache_status

    log.info(
        "API: Weekly fortune retrieved",
        user_id=user_id,
        cache_status=cache_status,
        source=fortune.source
    )

    return APIResponseBuilder.ok(data=fortune, message="주간 운세 조회 성공")


@router.get(
    "/monthly",
    response_model=APIResponse[FortuneResponse],
    summary="월간 운세 조회",
    description="로그인한 사용자의 월간 AI 운세를 조회합니다."
)
@limiter.limit("100/minute")
async def get_monthly_fortune(
    response: Response,
    fortune_service: FortuneServiceDep,
    user_repo: UserRepositoryDep,
    current_user: TokenPayload = Depends(get_current_user),
) -> APIResponse[FortuneResponse]:
    """월간 운세 조회 API (이번 달)"""
    # ... get_weekly_fortune과 동일한 패턴
    # fortune_service.get_monthly_fortune_with_status() 호출


@router.get(
    "/yearly",
    response_model=APIResponse[FortuneResponse],
    summary="연간 운세 조회",
    description="로그인한 사용자의 연간 AI 운세를 조회합니다."
)
@limiter.limit("100/minute")
async def get_yearly_fortune(
    response: Response,
    fortune_service: FortuneServiceDep,
    user_repo: UserRepositoryDep,
    current_user: TokenPayload = Depends(get_current_user),
) -> APIResponse[FortuneResponse]:
    """연간 운세 조회 API (올해)"""
    # ... get_weekly_fortune과 동일한 패턴
    # fortune_service.get_yearly_fortune_with_status() 호출


# 공통 검증 함수 (추출)
async def _validate_user_saju(user_repo: UserRepository, user_id: str, log) -> User:
    """사용자 및 사주 정보 검증"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        log.warning("API: User not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")

    if not user.birth_date:
        log.warning("API: Saju info not registered", user_id=user_id)
        raise HTTPException(
            status_code=400,
            detail={"code": "SAJU_INFO_REQUIRED", "message": "사주 정보를 먼저 등록해주세요"}
        )

    return user
```

### 캐시 키 전략

| 운세 유형 | 캐시 키 패턴 | TTL | 예시 |
|----------|-------------|-----|------|
| 일일 | `fortune:daily:{user_id}:{date}` | 24h | `fortune:daily:abc:2026-01-28` |
| 주간 | `fortune:weekly:{user_id}:{week_start}` | 7d | `fortune:weekly:abc:2026-01-27` |
| 월간 | `fortune:monthly:{user_id}:{year-month}` | 30d | `fortune:monthly:abc:2026-01` |
| 연간 | `fortune:yearly:{user_id}:{year}` | 365d | `fortune:yearly:abc:2026` |

### 주의사항: 안티패턴 방지

**❌ 절대 하지 말 것:**
```python
# 잘못: 새로운 Chain 클래스 생성
class WeeklyFortuneChain:  # ❌ DailyFortuneChain에 메서드 추가해야 함
    pass

# 잘못: 새로운 Service 클래스 생성
class WeeklyFortuneService:  # ❌ FortuneService에 메서드 추가해야 함
    pass

# 잘못: 캐시 TTL 하드코딩
redis.setex(key, 604800, value)  # ❌ FortuneCacheService의 CACHE_TTL 사용

# 잘못: 날짜 계산 로직 중복
# fortune_api.py와 fortune_service.py에서 각각 구현 ❌
# fortune_service.py에서만 구현하고 API는 서비스 호출만 ✅

# 잘못: 인증 로직 복붙
if not user or not user.birth_date:  # 3번 반복 ❌
# _validate_user_saju() 공통 함수로 추출 ✅

# 잘못: 절입시간 복잡한 계산 시도
# MVP에서는 월간(月干) 계산 생략 ✅
```

**✅ 올바른 패턴:**
```python
# 기존 클래스에 메서드 추가
class DailyFortuneChain:
    async def generate_fortune(self, ...) -> LLMFortuneOutput:
        """일일 운세 생성"""
        ...

    async def generate_weekly_fortune(self, ...) -> LLMFortuneOutput:  # ✅ 추가
        """주간 운세 생성"""
        ...

# 기존 서비스에 메서드 추가
class FortuneService:
    async def get_daily_fortune(...):
        ...

    async def get_weekly_fortune(...):  # ✅ 추가
        """주간 운세 조회"""
        ...

# 공통 로직 추출
async def _validate_user_saju(user_repo, user_id, log) -> User:  # ✅
    """사용자 및 사주 정보 검증 (공통)"""
    ...
```

### 테스트 전략

**기존 테스트 파일 확장:**
```python
# backend/tests/unit/api/test_fortune_api.py

class TestWeeklyFortuneAPI:
    """주간 운세 API 테스트"""

    async def test_get_weekly_fortune_success(self, mock_fortune_service, mock_user_repo, mock_current_user):
        """정상 주간 운세 조회"""
        # fortune_type이 "weekly"인지 확인

    async def test_get_weekly_fortune_cache_hit(self, ...):
        """캐시 히트 시 X-Cache: HIT"""

    async def test_get_weekly_fortune_unauthorized(self):
        """비로그인 시 401 에러"""

    async def test_get_weekly_fortune_no_saju_info(self, mock_current_user, mock_user_repo):
        """사주 정보 미등록 시 400 에러"""


class TestMonthlyFortuneAPI:
    """월간 운세 API 테스트"""
    # ... 동일 패턴


class TestYearlyFortuneAPI:
    """연간 운세 API 테스트"""
    # ... 동일 패턴
```

### 성능 요구사항

| 항목 | 목표 | 근거 |
|------|------|------|
| 캐시 히트 응답 | p95 < 300ms | NFR-P1 |
| 신규 생성 응답 | p95 < 3초 | NFR-P2 |
| Rate Limit | 100 req/min | NFR-S8 |
| LLM 타임아웃 | 10초 | Architecture |

### Project Structure Notes

**수정 대상 파일:**
```
backend/
├── src/
│   ├── api/v1/
│   │   └── fortune_api.py          # 수정: weekly/monthly/yearly 엔드포인트
│   ├── core/
│   │   ├── prompts.py              # 수정: 기간별 프롬프트 템플릿
│   │   └── langchain_chain.py      # 수정: 기간별 생성 메서드
│   ├── services/
│   │   ├── fortune_service.py      # 수정: 기간별 조회 메서드
│   │   └── fortune_cache_service.py # 수정: TTL 상수 (확인 필요)
│   └── common/utils/
│       └── saju_calculator.py      # 수정: get_year_pillar() 추가 (선택)
└── tests/unit/api/
    └── test_fortune_api.py         # 수정: 기간별 테스트 추가
```

**신규 생성 없음** (기존 파일 수정만)

### References

- [Tech Spec] `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md`
- [Architecture] `docs/architecture/core-architectural-decisions.md#AI 운세 캐싱 전략`
- [Epics] `_bmad-output/planning-artifacts/epics.md#Story 2.6`
- [Previous Story 2.4] `_bmad-output/implementation-artifacts/2-4-langchain-rag-chain.md`
- [Previous Story 2.5] `_bmad-output/implementation-artifacts/2-5-daily-fortune-api-endpoint.md`
- [Cache Service] `backend/src/services/fortune_cache_service.py`
- [API Pattern] `backend/src/api/v1/fortune_api.py`
- [Prompts] `backend/src/core/prompts.py`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A - 구현 중 오류 없음

### Completion Notes List

1. **Task 1 완료**: 기간별 프롬프트 템플릿 6개 추가 (시스템 + 사용자 프롬프트 x 3)
   - 주간: 주초/주중/주말 흐름 강조
   - 월간: 월초/월중/월말 흐름 강조
   - 연간: 봄/여름/가을/겨울 계절별 흐름 강조

2. **Task 2 완료**: DailyFortuneChain에 3개 메서드 추가
   - `generate_weekly_fortune()`, `generate_monthly_fortune()`, `generate_yearly_fortune()`
   - 각 메서드별 전용 프롬프트 체인 생성

3. **Task 3 완료**: FortuneService에 6개 메서드 추가
   - 기간별 운세 조회 메서드 3개 + _with_status 버전 3개
   - 주간 일진 요약 빌드 헬퍼 메서드 추가
   - saju_calculator에 연주/월지 계산 함수 추가

4. **Task 4 확인**: FortuneCacheService에 이미 기간별 TTL 구현됨 (Story 2.3에서)

5. **Task 5 완료**: API 엔드포인트 3개 추가
   - GET /weekly, /monthly, /yearly
   - 공통 검증 함수 `_validate_user_and_get_saju()` 추출

6. **Task 6 완료**: 테스트 케이스 20개 이상 추가
   - TestWeeklyFortuneAPI, TestMonthlyFortuneAPI, TestYearlyFortuneAPI, TestFortuneAPICommon

### File List

**Modified Files:**
- `backend/src/core/prompts.py` - 기간별 프롬프트 템플릿 추가
- `backend/src/core/langchain_chain.py` - 기간별 운세 생성 메서드 추가
- `backend/src/services/fortune_service.py` - 기간별 운세 조회 메서드 추가
- `backend/src/api/v1/fortune_api.py` - GET /weekly, /monthly, /yearly 엔드포인트 추가
- `backend/src/common/utils/saju_calculator.py` - 연주/월지 계산 함수 추가
- `backend/tests/unit/api/test_fortune_api.py` - 주간/월간/연간 API 테스트 추가

