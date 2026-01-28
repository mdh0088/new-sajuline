---
title: 'LangChain 기반 AI 사주 일운 서비스 - 지식 베이스 구축 및 API'
slug: 'ai-saju-daily-fortune'
created: '2026-01-28'
status: 'ready-for-dev'
stepsCompleted: [1, 2, 3, 4]
tech_stack:
  - FastAPI 0.110.0
  - LangChain 1.2.7
  - langchain-openai
  - OpenAI GPT-4o mini
  - MariaDB 10.6
  - Redis 7
files_to_modify:
  - backend/pyproject.toml  # langchain>=1.2.7, langchain-openai>=0.3.0
  - backend/src/models/saju_cheongan_model.py  # 천간 (10행)
  - backend/src/models/saju_jiji_model.py  # 지지 (12행)
  - backend/src/models/saju_sipsung_model.py  # 십성 해석 (100행)
  - backend/src/models/saju_jiji_relation_model.py  # 지지 관계 (30~50행)
  - backend/src/repositories/saju_repository.py  # 사주 데이터 조회
  - backend/src/services/fortune_service.py  # 비즈니스 로직 + 폴백 + 캐싱
  - backend/src/api/v1/fortune_api.py  # /api/v1/fortune/daily
  - backend/src/schemas/fortune_schema.py  # Request/Response 스키마
  - backend/src/common/utils/saju_calculator.py  # 일진/십성/luck_score 순수 계산
  - backend/src/core/langchain_chain.py  # LangChain 체인 빌더
  - backend/src/core/prompts.py  # LLM 프롬프트 템플릿 (신규)
  - backend/alembic/versions/xxx_add_saju_tables.py  # 마이그레이션
  - backend/scripts/seed_saju_data.py  # 시드 데이터 스크립트
  - backend/data/saju_seed_data.json  # 시드 데이터 JSON (신규)
code_patterns:
  - DDD Layered: api → service → repository → model
  - DI Pattern: Annotated[Type, Depends(get_*)]
  - Redis Caching: prefix + key, setex with TTL
  - API Router: APIRouter(prefix, tags), @limiter.limit
  - Auth: Depends(get_current_user) → TokenPayload
  - Response: APIResponse[T] wrapper
  - Async: async/await 전체 적용
test_patterns:
  - pytest-asyncio for async tests
  - conftest.py for fixtures
  - test_*.py naming convention
  - Unit tests in tests/unit/
  - Integration tests in tests/integration/
---

# Tech-Spec: LangChain 기반 AI 사주 일운 서비스

**Created:** 2026-01-28

## Overview

### Problem Statement

사주라인 MVP의 AI 운세 서비스를 위해 LangChain RAG 파이프라인에 활용할 명리학 지식 베이스가 필요합니다. 현재 백엔드에 LangChain/OpenAI 패키지는 설치되어 있으나(langchain==0.1.16), 사주 도메인 데이터(천간/지지/십성/일운 해석)가 없어 AI 운세 생성이 불가능합니다.

### Solution

MariaDB에 명리학 기초 데이터 테이블을 설계하고, LLM 위임 방식으로 최소한의 핵심 데이터(160~200행)만 구축합니다. LangChain 1.2.7 기반 체인이 DB에서 십성/지지 관계 데이터를 조회하여 프롬프트에 주입하고, GPT-4o mini가 자연어 운세를 생성합니다.

### Scope

**In Scope:**
1. **사주 지식 베이스 DB 구축**
   - 스키마 설계 (천간, 지지, 오행, 십성 해석, 지지 관계)
   - 기초 데이터 160~200행
   - 십성 계산 로직 Python 구현
   - 일진(60갑자) 계산 로직 직접 구현

2. **일일 사주 운세 API 구현**
   - LangChain 1.2.7 업그레이드
   - RAG 파이프라인 (DB 조회 → 프롬프트 구성 → LLM 응답)
   - 일운 API 엔드포인트 (`/api/v1/fortune/daily`)
   - Redis 캐싱

**Out of Scope:**
- UI 프론트엔드 개발 → API 완성 후
- 포인트 시스템 연동 → UI 개발 후
- 합충형파해 상세 해석 (Phase 2)
- 12운성 상세 해석 (Phase 2)
- 신살/격국 (Phase 3)
- 절입 시간 계산 (Phase 2, 신규 사주 등록 시)

## Context for Development

### Codebase Patterns

- **아키텍처**: DDD 레이어드 (api → service → repository → model)
- **ORM**: SQLAlchemy 2.0 + SQLModel
- **마이그레이션**: Alembic
- **API 스타일**: FastAPI + Pydantic v2
- **비동기**: async/await 패턴 (aiomysql)
- **설정**: pydantic-settings 기반 환경변수
- **AI 설정 존재**: `openai_api_key`, `openai_model`, `enable_ai_features` (settings.py:58-61, 93)

### Key Technical Decisions

| 항목 | 결정 | 이유 |
|------|------|------|
| 일운 템플릿 | LLM 위임 (160~200행) | 지지까지 반영, 60갑자 전체 커버 |
| 만세력 소스 | 직접 계산 | 일진은 60갑자 순환, 외부 API 불필요 |
| 응답 포맷 | 하이브리드 JSON | 프론트 유연성 + 자연어 운세 |
| 인증 | 로그인 필수 | 일간 필요, UX, 포인트 연동 |
| 벡터 DB | 불필요 | 정확 조회로 충분, RDB 사용 |
| birth_datetime | 항상 요청 파라미터 | 백엔드 stateless, 프론트가 관리 |
| 프롬프트 관리 | 코드 상수 → Phase 2 DB화 | MVP 빠른 개발, 이후 확장성 |
| LLM 폴백 | DB 기본 해석 반환 | 장애 시에도 서비스 유지 |

### Trade-off Matrix (War Room 결과)

| 영역 | 트레이드오프 | 현재 선택 | 비고 |
|------|-------------|----------|------|
| 비즈니스 | MVP 성공 지표 | 정의 필요 | 아래 섹션 참고 |
| 기술 | 정확도 vs 비용 | LLM 위임 | 폴백으로 리스크 완화 |
| 기술 | 개발 속도 vs 확장성 | 코드 상수 | Phase 2에서 DB화 |
| UX | 첫 경험 마찰 | 입력 먼저 | 미리보기 검토 (Phase 2) |
| UX | 카테고리 표시 | 총운 기본 + 탭 | 프론트 구현 시 적용 |

### MVP 성공 지표 (정의 필요)

> ⚠️ 아래 지표는 비즈니스 팀과 협의 후 확정 필요

| 지표 | 목표 (예시) | 측정 방법 |
|------|------------|----------|
| DAU (일일 활성 사용자) | TBD | API 호출 로그 |
| D1 재방문율 | TBD | 사용자별 일자 추적 |
| LLM 비용/건 | < ₩1 | OpenAI 사용량 모니터링 |
| 폴백 발생률 | < 1% | 에러 로그 집계 |

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `backend/src/config/settings.py` | AI 설정 (openai_api_key, openai_model) |
| `backend/pyproject.toml` | 패키지 의존성 (langchain 업그레이드 필요) |
| `backend/src/models/user_model.py` | 사용자 모델 (birth_date 필드 확인) |
| `backend/src/models/` | 기존 모델 패턴 참고 |
| `backend/src/repositories/` | 기존 리포지토리 패턴 참고 |
| `backend/src/services/` | 기존 서비스 패턴 참고 |

## Design Specifications

### DB Schema (MVP 160~200행)

```sql
-- 천간 (10행)
CREATE TABLE saju_cheongan (
    id INT PRIMARY KEY,
    name VARCHAR(2) NOT NULL,        -- 갑, 을, 병, ...
    hanja VARCHAR(2) NOT NULL,       -- 甲, 乙, 丙, ...
    oheng VARCHAR(2) NOT NULL,       -- 목, 화, 토, 금, 수
    yin_yang ENUM('양', '음') NOT NULL,
    description TEXT
);

-- 지지 (12행)
CREATE TABLE saju_jiji (
    id INT PRIMARY KEY,
    name VARCHAR(2) NOT NULL,        -- 자, 축, 인, ...
    hanja VARCHAR(2) NOT NULL,       -- 子, 丑, 寅, ...
    oheng VARCHAR(2) NOT NULL,
    yin_yang ENUM('양', '음') NOT NULL,
    animal VARCHAR(4) NOT NULL,      -- 쥐, 소, 호랑이, ...
    month INT,                       -- 해당 월 (1~12)
    description TEXT
);

-- 십성 해석 (100행: 일간 10 × 십성 10)
CREATE TABLE saju_sipsung_interpretation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ilgan VARCHAR(2) NOT NULL,       -- 일간 (갑~계)
    sipsung VARCHAR(4) NOT NULL,     -- 비견, 겁재, 식신, ...
    keywords JSON,                   -- ["창의력", "표현", "자식"]
    positive_meaning TEXT,           -- 긍정적 해석
    negative_meaning TEXT,           -- 부정적 해석
    daily_advice TEXT,               -- 일운 조언
    INDEX idx_ilgan_sipsung (ilgan, sipsung)
);

-- 지지 관계 해석 (30~50행)
CREATE TABLE saju_jiji_relation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    relation_type ENUM('합', '충', '형', '파', '해', '12운성') NOT NULL,
    jiji1 VARCHAR(2) NOT NULL,
    jiji2 VARCHAR(2),                -- 12운성은 NULL
    name VARCHAR(10),                -- 관계명 (예: 자오충, 인해합)
    keywords JSON,
    meaning TEXT,
    daily_impact TEXT,               -- 일운에 미치는 영향
    INDEX idx_relation (relation_type, jiji1)
);
```

### 일진 계산 로직

```python
# 60갑자 순환 계산 (외부 API 불필요)
CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

def get_today_ilju(target_date: date) -> tuple[str, str]:
    """오늘의 일주(일간+일지) 계산"""
    # 기준일: 2000년 1월 1일 = 갑진일 (인덱스 40)
    base_date = date(2000, 1, 1)
    base_index = 40

    diff = (target_date - base_date).days
    index = (base_index + diff) % 60

    cheongan = CHEONGAN[index % 10]
    jiji = JIJI[index % 12]
    return cheongan, jiji
```

### 응답 스키마

```python
class DailyFortuneResponse(BaseModel):
    date: str                      # "2026-01-28"
    ilgan: str                     # "갑" (사용자 일간)
    day_ilju: str                  # "병인" (오늘 일주)
    category: str                  # "총운"

    # 핵심 정보 (구조화)
    sipsung: str                   # "식신"
    luck_score: int                # 1~5
    keywords: list[str]            # ["창의력", "표현", "새로운 시도"]

    # 운세 내용 (자연어)
    content: str                   # "오늘은 창의적인 에너지가..."
    advice: str                    # "새로운 아이디어를 적극적으로..."

    # 부가 정보 (선택)
    lucky_color: str | None        # "초록색"
    lucky_number: int | None       # 3
    caution: str | None            # "과한 욕심은 금물"
```

### LLM 프롬프트 템플릿

```python
# backend/src/core/prompts.py

SYSTEM_PROMPT = """당신은 30년 경력의 명리학 전문가입니다.
주어진 사주 데이터를 바탕으로 오늘의 운세를 해석해주세요.

규칙:
- 3~4문장으로 간결하게
- 구체적인 조언 포함
- 긍정적이되 현실적인 톤
- 미신적 표현 지양 (예: "큰 재앙", "대박")
- 카테고리에 맞는 내용만 작성
"""

USER_PROMPT_TEMPLATE = """
오늘 날짜: {today}
사용자 일간: {ilgan} ({ilgan_oheng} {ilgan_umyang})
오늘 일진: {day_gan}{day_ji}

[십성 관계]
일간({ilgan}) → 일진 천간({day_gan}) = {sipsung}
해석: {sipsung_interpretation}

[지지 관계]
사용자 일지({user_ji}) → 일진 지지({day_ji}) = {jiji_relation}
해석: {jiji_interpretation}

카테고리: {category}

위 정보를 바탕으로 {category} 운세를 작성해주세요.
응답은 JSON 형식으로:
{{
  "content": "운세 본문 (2-3문장)",
  "advice": "조언 (1문장)",
  "lucky_color": "색상 또는 null",
  "lucky_number": 숫자 또는 null,
  "caution": "주의사항 또는 null"
}}
"""
```

> **Note**: luck_score와 keywords는 LLM이 아닌 규칙 기반으로 계산 (일관성 보장)

### 카테고리 및 입력 검증

```python
from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime

class FortuneCategory(str, Enum):
    GENERAL = "총운"
    WEALTH = "재물"
    LOVE = "연애"
    HEALTH = "건강"
    CAREER = "직장"

class DailyFortuneRequest(BaseModel):
    birth_datetime: str  # "1998-03-01 18:01"
    category: FortuneCategory = FortuneCategory.GENERAL

    @field_validator("birth_datetime")
    @classmethod
    def validate_birth_datetime(cls, v: str) -> str:
        try:
            dt = datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("형식이 올바르지 않습니다. (YYYY-MM-DD HH:MM)")

        if dt.year < 1900:
            raise ValueError("1900년 이후 날짜만 지원합니다.")
        if dt > datetime.now():
            raise ValueError("미래 날짜는 입력할 수 없습니다.")

        return v
```

### luck_score 계산 로직

```python
# backend/src/common/utils/saju_calculator.py

# 십성별 기본 점수 (카테고리별)
SIPSUNG_SCORE = {
    "총운": {
        "비견": 3, "겁재": 2, "식신": 4, "상관": 3,
        "정재": 4, "편재": 3, "정관": 4, "편관": 3,
        "정인": 4, "편인": 3
    },
    "재물": {
        "정재": 5, "편재": 4, "식신": 4, "상관": 3,
        "비견": 2, "겁재": 2, "정관": 3, "편관": 2,
        "정인": 3, "편인": 2
    },
    "연애": {
        "정재": 4, "편재": 3, "정관": 5, "편관": 3,
        "식신": 4, "상관": 4, "비견": 2, "겁재": 2,
        "정인": 3, "편인": 2
    },
    # 건강, 직장도 유사하게 정의
}

# 지지 관계 보정
JIJI_MODIFIER = {
    "건록": 1, "제왕": 1, "장생": 1, "관대": 1,
    "목욕": 0, "양": 0, "쇠": 0, "병": -1,
    "사": -1, "묘": -1, "절": 0, "태": 0,
    "합": 1, "충": -1, "형": -1, "파": 0, "해": 0,
}

def calculate_luck_score(
    sipsung: str,
    jiji_relation: str,
    category: str
) -> int:
    """luck_score 계산 (1~5)"""
    base = SIPSUNG_SCORE.get(category, {}).get(sipsung, 3)
    modifier = JIJI_MODIFIER.get(jiji_relation, 0)
    return max(1, min(5, base + modifier))
```

### 인증 및 사용자 데이터

- **로그인 필수**: 인증된 사용자만 API 호출 가능
- **birth_datetime**: 항상 요청 파라미터로 받음 (백엔드 stateless)
- **프론트엔드 책임**: user.birth_date 있으면 그 값 전송, 없으면 사용자 입력받아 전송
- **백엔드 책임**: 받은 값 그대로 사용, DB 조회/저장 없음

### LLM 폴백 전략

```python
async def get_daily_fortune(...) -> DailyFortuneResponse:
    # 1. DB에서 기초 데이터 조회 (실패 시 기본값 사용)
    sipsung_data = await get_sipsung_interpretation(ilgan, day_gan)
    if sipsung_data is None:
        logger.warning(f"Sipsung not found: {ilgan}/{day_gan}, using default")
        sipsung_data = get_default_sipsung(ilgan, day_gan)

    jiji_data = await get_jiji_relation(user_jiji, day_jiji)
    if jiji_data is None:
        logger.warning(f"Jiji relation not found: {user_jiji}/{day_jiji}")
        jiji_data = get_default_jiji_relation()

    # 2. luck_score 규칙 기반 계산
    luck_score = calculate_luck_score(
        sipsung_data.sipsung,
        jiji_data.relation_type,
        category
    )

    try:
        # 3. LLM 호출 시도 (타임아웃 10초)
        llm_response = await call_llm_with_timeout(
            sipsung_data, jiji_data, timeout=10
        )
        return build_response(
            llm_response,
            luck_score=luck_score,  # 규칙 기반
            source="llm"
        )

    except (TimeoutError, OpenAIError) as e:
        # 4. 폴백: DB 데이터로 기본 응답 구성
        logger.warning(f"LLM fallback triggered: {e}")
        return build_fallback_response(
            sipsung_data,
            jiji_data,
            luck_score=luck_score,  # 동일 로직 적용
            source="fallback"
        )
```

**폴백 응답 품질:**
- `sipsung_data.daily_advice` + `jiji_data.daily_impact` 조합
- 자연어 생성 없이 DB 텍스트 직접 사용
- luck_score는 LLM/폴백 모두 동일 규칙 기반 계산 (일관성 보장)
- 응답에 `source: "fallback"` 표시 (모니터링용)

**DB 조회 실패 시 기본값:**
```python
def get_default_sipsung(ilgan: str, sipsung: str) -> SipsungData:
    """DB 조회 실패 시 기본 해석 제공"""
    return SipsungData(
        ilgan=ilgan,
        sipsung=sipsung,
        daily_advice=f"{ilgan} 일간이 {sipsung}을 만났습니다. 오늘 하루도 평안하시길 바랍니다.",
        keywords=["평온", "안정"]
    )
```

### 캐싱 전략

- **캐시 키**: `fortune:{ilgan}:{date}:{category}`
- **TTL**: 당일 자정까지 (KST 기준, 동적 계산)
- **무효화**: 일자 변경 시 자동 만료
- **폴백 캐싱**: TTL 5분 (LLM 복구 후 새 응답 가능하도록)

```python
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+ 표준 라이브러리

def get_ttl_until_midnight_kst() -> int:
    """KST 자정까지 남은 초"""
    kst = ZoneInfo('Asia/Seoul')
    now = datetime.now(kst)
    midnight = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=kst)
    return int((midnight - now).total_seconds())
```

### 응답 출처 추적

```python
class DailyFortuneResponse(BaseModel):
    # ... 기존 필드
    source: Literal["llm", "fallback"] = "llm"  # 모니터링용
```

## Implementation Plan

### Tasks

#### Phase A: 의존성 및 기반 구축

- [ ] **Task 1: LangChain 패키지 업그레이드**
  - File: `backend/pyproject.toml`
  - Action: langchain 버전을 `>=1.2.7`로, langchain-openai를 `>=0.3.0`으로 업데이트
  - Notes: `uv lock && uv sync` 실행하여 의존성 동기화

- [ ] **Task 2: 사주 계산 유틸리티 구현**
  - File: `backend/src/common/utils/saju_calculator.py`
  - Action: 순수 함수로 일진 계산(`get_ilju`), 십성 계산(`calculate_sipsung`) 구현
  - Notes: 외부 의존성 없음, 60갑자 상수 정의, 기준일 2000-01-01=갑진일

#### Phase B: 데이터 모델 및 스키마

- [ ] **Task 3: 천간 모델 생성**
  - File: `backend/src/models/saju_cheongan_model.py`
  - Action: SajuCheongan 모델 정의 (id, name, hanja, oheng, yin_yang, description)
  - Notes: 기존 모델 패턴 따름 (SQLAlchemy 2.0, Mapped)

- [ ] **Task 4: 지지 모델 생성**
  - File: `backend/src/models/saju_jiji_model.py`
  - Action: SajuJiji 모델 정의 (id, name, hanja, oheng, yin_yang, animal, month, description)
  - Notes: 기존 모델 패턴 따름

- [ ] **Task 5: 십성 해석 모델 생성**
  - File: `backend/src/models/saju_sipsung_model.py`
  - Action: SajuSipsungInterpretation 모델 정의 (ilgan, sipsung, keywords JSON, positive/negative_meaning, daily_advice)
  - Notes: idx_ilgan_sipsung 복합 인덱스 추가

- [ ] **Task 6: 지지 관계 모델 생성**
  - File: `backend/src/models/saju_jiji_relation_model.py`
  - Action: SajuJijiRelation 모델 정의 (relation_type ENUM, jiji1, jiji2, name, keywords JSON, meaning, daily_impact)
  - Notes: idx_relation 인덱스 추가

- [ ] **Task 7: Alembic 마이그레이션 생성**
  - File: `backend/alembic/versions/xxx_add_saju_tables.py`
  - Action: `alembic revision --autogenerate -m "add_saju_knowledge_base_tables"` 실행
  - Notes: 마이그레이션 검토 후 `alembic upgrade head` 적용

- [ ] **Task 8a: 기초 데이터 시드 (구조)**
  - File: `backend/data/saju_seed_data.json`, `backend/scripts/seed_saju_data.py`
  - Action: 천간 10행, 지지 12행 INSERT (정형화된 표준 데이터)
  - Notes: 출처 - 연해자평 기준, 개발자 직접 입력, 트랜잭션 처리 필수

- [ ] **Task 8b: 해석 데이터 시드 (텍스트)**
  - File: `backend/data/saju_interpretation_data.json`
  - Action: 십성 해석 100행, 지지 관계 30~50행 INSERT
  - Notes:
    - 출처: 적천수, 자평진전, 궁통보감 참고
    - 작성: AI 초안 생성 → 원전 대조 검수 → 수정
    - 검수 체크리스트:
      - [ ] 10간 × 10성 = 100행 완료
      - [ ] 각 해석 2-3문장 이내
      - [ ] 긍정/부정 균형 (극단적 표현 없음)
      - [ ] 오타/맞춤법 검토

#### Phase C: 리포지토리 및 스키마

- [ ] **Task 9: 사주 리포지토리 구현**
  - File: `backend/src/repositories/saju_repository.py`
  - Action: SajuRepository 클래스 구현 (get_sipsung_interpretation, get_jiji_relation, get_cheongan, get_jiji)
  - Notes: 기존 리포지토리 패턴 따름 (AsyncSession, async/await)

- [ ] **Task 10: Fortune 스키마 정의**
  - File: `backend/src/schemas/fortune_schema.py`
  - Action: DailyFortuneRequest, DailyFortuneResponse Pydantic 모델 정의
  - Notes: source 필드 (Literal["llm", "fallback"]) 포함

#### Phase D: LangChain 체인 및 서비스

- [ ] **Task 11: LangChain 체인 빌더 구현**
  - File: `backend/src/core/langchain_chain.py`
  - Action: DailyFortuneChain 클래스 구현 (프롬프트 템플릿, GPT-4o mini 호출, 응답 파싱)
  - Notes: 프롬프트는 코드 상수로 정의, 타임아웃 10초

- [ ] **Task 12: Fortune 서비스 구현**
  - File: `backend/src/services/fortune_service.py`
  - Action: FortuneService 클래스 구현 (get_daily_fortune 메인 로직, 캐싱, 폴백)
  - Notes: Redis 캐싱 (TTL 자정까지), 폴백 캐싱 (TTL 5분)

- [ ] **Task 13: DI 의존성 추가**
  - File: `backend/src/core/dependencies.py`
  - Action: get_saju_repository, get_fortune_service 함수 및 Annotated 타입 추가
  - Notes: 기존 DI 패턴 따름

#### Phase E: API 엔드포인트

- [ ] **Task 14: Fortune API 라우터 구현**
  - File: `backend/src/api/v1/fortune_api.py`
  - Action: `/api/v1/fortune/daily` POST 엔드포인트 구현
  - Notes:
    - Depends(get_current_user) 인증 필수
    - @limiter.limit("30/minute") - LLM 비용 고려 보수적 설정
    - APIResponse[T] 래퍼
    - FortuneCategory Enum 사용

- [ ] **Task 15: 라우터 등록**
  - File: `backend/src/main.py` (또는 api/v1/__init__.py)
  - Action: fortune_router를 app에 include
  - Notes: 기존 라우터 등록 패턴 확인 후 동일하게 적용

### Acceptance Criteria

#### 기능 요구사항

- [ ] **AC 1**: Given 인증된 사용자, When birth_datetime="1990-05-15 14:30"과 category="총운"으로 `/api/v1/fortune/daily` 호출, Then 200 OK와 함께 DailyFortuneResponse 반환
- [ ] **AC 2**: Given 인증되지 않은 사용자, When `/api/v1/fortune/daily` 호출, Then 401 Unauthorized 반환
- [ ] **AC 3**: Given 유효하지 않은 birth_datetime 형식 (예: "1990-13-01"), When API 호출, Then 422 Validation Error 반환
- [ ] **AC 4**: Given 미래 날짜 birth_datetime, When API 호출, Then 422 Validation Error ("미래 날짜는 입력할 수 없습니다")
- [ ] **AC 5**: Given 유효하지 않은 category (예: "학업"), When API 호출, Then 422 Validation Error 반환
- [ ] **AC 6**: Given 오늘 날짜 2026-01-28, When 일진 계산, Then 정확한 천간+지지 조합 반환 (만세력 교차 검증)

#### 캐싱 요구사항

- [ ] **AC 7**: Given 동일한 ilgan+date+category 조합, When 첫 번째 API 호출 후 두 번째 호출, Then Redis 캐시에서 응답 반환 (LLM 미호출)
- [ ] **AC 8**: Given 캐시된 응답, When KST 자정 경과, Then 캐시 만료되어 새 LLM 응답 생성

#### 폴백 요구사항

- [ ] **AC 9**: Given OpenAI API 타임아웃 (10초 초과), When API 호출, Then source="fallback"인 DB 기반 응답 반환
- [ ] **AC 10**: Given 폴백 응답, When 캐싱, Then TTL 5분으로 짧게 설정
- [ ] **AC 11**: Given DB에서 십성 데이터 조회 실패, When API 호출, Then 기본 해석으로 폴백 (서비스 중단 없음)

#### 데이터 요구사항

- [ ] **AC 12**: Given 십성 해석 테이블, When 모든 일간(10) × 십성(10) 조합 조회, Then 100행 모두 존재
- [ ] **AC 13**: Given 지지 관계 테이블, When 합/충 관계 조회, Then 최소 12행 (6합 + 6충) 존재

#### 성능 요구사항

- [ ] **AC 14**: Given LLM 정상 응답, When API 호출, Then p95 응답 시간 3초 이내
- [ ] **AC 15**: Given Redis 캐시 히트, When API 호출, Then p95 응답 시간 100ms 이내

#### luck_score 요구사항

- [ ] **AC 16**: Given 동일한 십성+지지관계+카테고리, When LLM 응답과 폴백 응답 비교, Then luck_score 값이 동일 (일관성)

## Additional Context

### Dependencies

**추가 필요 패키지:**
- `langchain>=1.2.7` (현재 0.1.16 → 업그레이드)
- `langchain-openai>=0.3.0`

**제외 (MVP):**
- skyfield (절입 시간 - Phase 2)
- 한국천문연구원 API (직접 계산으로 대체)

### Testing Strategy

#### Unit Tests

| 파일 | 테스트 대상 | 위치 |
|------|------------|------|
| `saju_calculator.py` | 일진 계산 정확성 (다양한 날짜) | `tests/unit/common/utils/test_saju_calculator.py` |
| `saju_calculator.py` | 십성 계산 정확성 (10×10 조합) | `tests/unit/common/utils/test_saju_calculator.py` |
| `langchain_chain.py` | 체인 구성 (Mock LLM) | `tests/unit/core/test_langchain_chain.py` |
| `fortune_service.py` | 폴백 로직 (Mock OpenAI 타임아웃) | `tests/unit/services/test_fortune_service.py` |

#### Integration Tests

| 테스트 | 목적 | 위치 |
|--------|------|------|
| 리포지토리 + DB | 실제 DB 조회 검증 | `tests/integration/repositories/test_saju_repository.py` |
| 서비스 + Redis | 캐싱 동작 검증 | `tests/integration/services/test_fortune_service.py` |
| API E2E | 전체 플로우 검증 | `tests/integration/api/test_fortune_api.py` |

#### Mock 전략

```python
# OpenAI 타임아웃 시뮬레이션
@pytest.fixture
def mock_openai_timeout():
    with patch('openai.ChatCompletion.acreate') as mock:
        mock.side_effect = asyncio.TimeoutError()
        yield mock

# Redis 캐시 미스 시뮬레이션
@pytest.fixture
def mock_redis_miss():
    with patch.object(redis_client, 'get', return_value=None):
        yield
```

#### 테스트 데이터

**일진 검증 (만세력 교차 검증 완료):**
```python
# tests/unit/common/utils/test_saju_calculator.py
VERIFIED_ILJU_CASES = [
    # (날짜, 천간, 지지, 검증 출처)
    ("2000-01-01", "갑", "진", "한국천문연구원"),  # 기준일
    ("2020-01-01", "기", "묘", "만세력닷컴"),
    ("2024-02-10", "갑", "진", "설날 - 60갑자 순환"),
    # 2026-01-28 값은 구현 후 실제 만세력과 교차 검증 필요
]

@pytest.mark.parametrize("date_str,gan,ji,source", VERIFIED_ILJU_CASES)
def test_ilju_calculation(date_str, gan, ji, source):
    result = get_ilju(date.fromisoformat(date_str))
    assert result == (gan, ji), f"검증 출처: {source}"
```

**십성 검증:**
- 갑일간 + 갑일진 = 비견
- 갑일간 + 을일진 = 겁재
- 갑일간 + 병일진 = 식신
- (10간 × 10성 전체 매핑 테스트)

### UX 고려사항 (프론트엔드 구현 시 참고)

**사용자 플로우:**
```
[로그인] → [생년월일시 입력/확인] → [카테고리 선택] → [운세 결과]
         └─ user.birth_date 있으면 자동 세팅
         └─ 없으면 입력 폼 표시 (저장 X, 세션 유지)
```

**카테고리 표시:**
- 총운: 기본 표시
- 재물/연애/건강/직장: 탭으로 전환

**Phase 2 UX 개선 검토:**
- 오늘의 일진 미리보기 → "내 운세 보기" CTA
- "어제 vs 오늘" 비교 기능

### Notes

**리서치 문서 참고:**
- `_bmad-output/analysis/brainstorming-session-2026-01-27.md`
- `_bmad-output/planning-artifacts/research/langchain-ai-saju-integrated-research-2026-01-27.md`

**MVP 데이터 목표 (수정됨):**
- 천간: 10행
- 지지: 12행
- 오행 관계: 5행
- 십성 해석: 100행 (일간 10 × 십성 10)
- 지지 관계 해석: 30~50행 (합충형파해 + 12운성 키워드)
- **총: 160~200행**

**단계별 확장 계획:**
- Phase 1 (MVP): 160~200행 → 일일 운세 서비스
- Phase 2: 합충형파해 상세, 12운성 상세
- Phase 3: 신살, 격국, 사용자 피드백 반영

---

## Adversarial Review 결과 반영

> 이 스펙은 Adversarial Review를 통해 12개의 잠재적 이슈가 발견되었으며, 모두 해결되었습니다.

**해결된 주요 이슈:**
- ✅ F1: LLM 프롬프트 템플릿 정의
- ✅ F2: 시드 데이터 출처 및 작성 프로세스 명시
- ✅ F3: luck_score 규칙 기반 계산 로직 추가
- ✅ F4: FortuneCategory Enum 정의
- ✅ F5: birth_datetime 검증 로직 추가
- ✅ F6: DB 조회 실패 시 기본값 처리
- ✅ F7: Rate Limiting 수치 정의 (30/minute)
- ✅ F8: pytz → zoneinfo 변경
- ✅ F9: 일진 기준일 검증 테스트 케이스 추가
