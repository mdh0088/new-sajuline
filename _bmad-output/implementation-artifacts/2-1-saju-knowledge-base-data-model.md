# Story 2.1: 사주 지식베이스 데이터 모델

Status: done

## Story

As a **시스템**,
I want **천간, 지지, 십성 등 사주 기초 데이터를 DB에 저장**,
So that **AI 운세 생성 시 사주 해석 지식을 RAG로 검색할 수 있다**.

## Acceptance Criteria

1. **AC1**: Given 백엔드 서버가 실행 중일 때, When 데이터베이스 마이그레이션이 실행되면, Then `saju_cheongan` (천간 10행), `saju_jiji` (지지 12행), `saju_sipsung_interpretation` (십성 100행), `saju_jiji_relation` (지지 관계 30~50행) 테이블이 생성된다
2. **AC2**: Given 천간 테이블, When 전체 조회 시, Then 10행 (갑~계)이 정확히 존재한다
3. **AC3**: Given 지지 테이블, When 전체 조회 시, Then 12행 (자~해)이 정확히 존재한다
4. **AC4**: Given 십성 해석 테이블, When 모든 일간(10) × 십성(10) 조합 조회 시, Then 100행 모두 존재한다
5. **AC5**: Given 지지 관계 테이블, When 합/충 관계 조회 시, Then 최소 12행 (6합 + 6충) 존재한다
6. **AC6**: Given `fortune_histories` 테이블, When 마이그레이션 실행 시, Then user_id, fortune_type, target_date, content, ai_model, prompt_version, created_at 컬럼이 포함된다

## Tasks / Subtasks

- [x] **Task 1: 천간(SajuCheongan) 모델 생성** (AC: 1, 2)
  - [x] `backend/src/models/saju_cheongan_model.py` 파일 생성
  - [x] 컬럼: id, name, hanja, oheng, yin_yang, description
  - [x] 기존 user_model.py 패턴 따름 (SQLAlchemy 2.0, Mapped)

- [x] **Task 2: 지지(SajuJiji) 모델 생성** (AC: 1, 3)
  - [x] `backend/src/models/saju_jiji_model.py` 파일 생성
  - [x] 컬럼: id, name, hanja, oheng, yin_yang, animal, month, description

- [x] **Task 3: 십성 해석(SajuSipsungInterpretation) 모델 생성** (AC: 1, 4)
  - [x] `backend/src/models/saju_sipsung_model.py` 파일 생성
  - [x] 컬럼: id(AUTO_INCREMENT), ilgan, sipsung, keywords(JSON), positive_meaning, negative_meaning, daily_advice
  - [x] 복합 인덱스: `idx_ilgan_sipsung (ilgan, sipsung)`

- [x] **Task 4: 지지 관계(SajuJijiRelation) 모델 생성** (AC: 1, 5)
  - [x] `backend/src/models/saju_jiji_relation_model.py` 파일 생성
  - [x] 컬럼: id(AUTO_INCREMENT), relation_type(ENUM), jiji1, jiji2, name, keywords(JSON), meaning, daily_impact
  - [x] 인덱스: `idx_relation (relation_type, jiji1)`

- [x] **Task 5: 운세 이력(FortuneHistory) 모델 생성** (AC: 6)
  - [x] `backend/src/models/fortune_history_model.py` 파일 생성
  - [x] 컬럼: id(UUID), user_id, fortune_type(ENUM), target_date, content, ai_model, prompt_version, created_at
  - [x] 복합 인덱스: `idx_user_type_date (user_id, fortune_type, target_date)`

- [x] **Task 6: 마이그레이션 SQL 생성** (AC: 1) - *수정: 오프라인 환경으로 SQL .md 파일 생성*
  - [x] 마이그레이션 파일 생성: `backend/alembic/versions/20260128_add_saju_knowledge_base_tables.py`
  - [x] SQL DDL 문서 생성: `backend/data/saju_knowledge_base_migration.md`
  - [ ] **[사용자 수동 실행 필요]** 운영 DB에서 DDL 실행

- [x] **Task 7: 시드 데이터 SQL 생성** (AC: 2, 3, 4, 5) - *수정: SQL INSERT 문으로 제공*
  - [x] `backend/data/saju_seed_data.json` 파일 생성 (천간 10행, 지지 12행)
  - [x] `backend/data/saju_knowledge_base_migration.md`에 INSERT SQL 포함
  - [ ] **[사용자 수동 실행 필요]** 운영 DB에서 INSERT SQL 실행

- [x] **Task 8: 시드 데이터 삽입 및 검증** (AC: 2, 3, 4, 5) - *사용자 수동 완료*
  - [x] `saju_knowledge_base_migration.md` 의 SQL 실행 완료
  - [x] DB 검증 쿼리 실행 완료

## Dev Notes

### 필수 준수 사항 (Architecture Compliance)

**테이블 네이밍:**
- 테이블명: snake_case (`saju_cheongan`, `saju_jiji`, `saju_sipsung_interpretation`, `saju_jiji_relation`, `fortune_histories`)
- 컬럼명: snake_case (`yin_yang`, `daily_advice`)
- FK: `{table}_id` 형식
- Index: `idx_{table}_{column}` 형식

**모델 패턴 (기존 코드 참조):**
```python
# 참조: backend/src/models/user_model.py

from datetime import datetime
from typing import Optional
from enum import Enum
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, Integer, Text, JSON, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

KST = ZoneInfo("Asia/Seoul")

class SajuCheongan(Base):
    """천간 테이블"""
    __tablename__ = "saju_cheongan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(2), nullable=False, comment="천간 이름 (갑~계)")
    # ... 나머지 컬럼
```

**Enum 정의:**
```python
class RelationType(str, Enum):
    """지지 관계 유형"""
    HAP = "합"      # 육합
    CHUNG = "충"    # 육충
    HYUNG = "형"    # 삼형
    PA = "파"       # 육파
    HAE = "해"      # 육해
    TWELVE = "12운성"

class FortuneType(str, Enum):
    """운세 유형"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
```

### DB 스키마 상세

**천간 테이블 (10행):**
| id | name | hanja | oheng | yin_yang | description |
|----|------|-------|-------|----------|-------------|
| 1  | 갑   | 甲    | 목    | 양       | 양목, 큰 나무... |
| 2  | 을   | 乙    | 목    | 음       | 음목, 작은 나무... |
| ... | ... | ...   | ...   | ...      | ... |

**지지 테이블 (12행):**
| id | name | hanja | oheng | yin_yang | animal | month | description |
|----|------|-------|-------|----------|--------|-------|-------------|
| 1  | 자   | 子    | 수    | 양       | 쥐     | 11    | ... |
| 2  | 축   | 丑    | 토    | 음       | 소     | 12    | ... |
| ... | ... | ...   | ...   | ...      | ...    | ...   | ... |

**십성 해석 테이블 (100행):**
| id | ilgan | sipsung | keywords | positive_meaning | negative_meaning | daily_advice |
|----|-------|---------|----------|------------------|------------------|--------------|
| 1  | 갑    | 비견    | ["경쟁","동료","형제"] | 협력과 동료애... | 경쟁과 갈등... | 동료와 협력하세요... |
| 2  | 갑    | 겁재    | ["경쟁","야망","욕심"] | 도전정신... | 과욕으로 인한... | 욕심을 절제하세요... |
| ... | ... | ... | ... | ... | ... | ... |

**지지 관계 테이블 (30~50행):**
| id | relation_type | jiji1 | jiji2 | name | keywords | meaning | daily_impact |
|----|---------------|-------|-------|------|----------|---------|--------------|
| 1  | 합            | 자    | 축    | 자축합 | ["결합","화합"] | 수토 결합... | 화합의 기운... |
| 2  | 충            | 자    | 오    | 자오충 | ["충돌","변화"] | 수화 충돌... | 변화와 갈등... |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 시드 데이터 출처 및 작성 프로세스

**출처:**
- 천간/지지: 연해자평 기준 표준 데이터 (개발자 직접 입력)
- 십성 해석: 적천수, 자평진전, 궁통보감 참고
- 지지 관계: 연해자평, 명리정종 참고

**작성 프로세스:**
1. AI 초안 생성
2. 원전 대조 검수
3. 긍정/부정 균형 확인 (극단적 표현 없음)
4. 오타/맞춤법 검토
5. 트랜잭션 처리 필수

### 시드 스크립트 패턴

```python
# backend/scripts/seed_saju_data.py
import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session_factory
from src.models.saju_cheongan_model import SajuCheongan
# ... 기타 imports

async def seed_data():
    async with async_session_factory() as session:
        async with session.begin():
            # 1. 기존 데이터 삭제 (개발 환경에서만)
            # 2. JSON 파일 로드
            # 3. 각 테이블에 데이터 삽입
            # 4. 커밋
            pass

if __name__ == "__main__":
    asyncio.run(seed_data())
```

### 테스트 전략

**단위 테스트 (tests/unit/models/):**
- 각 모델 생성 및 필드 검증
- Enum 값 검증
- 인덱스 존재 확인

**통합 테스트 (tests/integration/repositories/):**
- 실제 DB 조회 검증
- 시드 데이터 정합성 검증

### Project Structure Notes

**생성할 파일:**
```
backend/
├── src/models/
│   ├── saju_cheongan_model.py    # 신규
│   ├── saju_jiji_model.py        # 신규
│   ├── saju_sipsung_model.py     # 신규
│   ├── saju_jiji_relation_model.py # 신규
│   └── fortune_history_model.py  # 신규
├── data/
│   ├── saju_seed_data.json       # 신규
│   └── saju_interpretation_data.json # 신규
├── scripts/
│   └── seed_saju_data.py         # 신규
└── alembic/versions/
    └── xxx_add_saju_knowledge_base_tables.py # 자동 생성
```

### References

- [Tech Spec] `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md#DB Schema`
- [Architecture] `docs/architecture/implementation-patterns-consistency-rules.md#Naming Patterns`
- [Architecture] `docs/architecture/core-architectural-decisions.md#Data Architecture`
- [Model Pattern] `backend/src/models/user_model.py` (SQLAlchemy 2.0 패턴)
- [Repository Pattern] `backend/src/repositories/user_repository.py` (async/await 패턴)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- 모델 테스트 통과: 5개 모델 모두 컬럼, 인덱스, Enum 검증 완료
- DB 연결 불가: 오프라인 환경으로 운영 DB 접속 불가하여 SQL .md 파일로 대체 제공

### Completion Notes List

**2026-01-28 구현 완료:**

1. **모델 파일 생성 (Task 1-5)**: SQLAlchemy 2.0 Mapped 스타일로 5개 모델 생성
   - `SajuCheongan`: 천간 10행 (갑~계)
   - `SajuJiji`: 지지 12행 (자~해)
   - `SajuSipsungInterpretation`: 십성 해석 100행 (일간×십성), `idx_ilgan_sipsung` 인덱스
   - `SajuJijiRelation`: 지지 관계 (합/충/형/파/해), `idx_relation` 인덱스
   - `FortuneHistory`: 운세 이력 (UUID PK), `idx_user_type_date` 인덱스

2. **마이그레이션 및 시드 데이터 (Task 6-7)**: 오프라인 환경으로 SQL 문서 생성
   - `saju_knowledge_base_migration.md`: DDL + INSERT SQL 전체 포함
   - 사용자가 직접 운영 DB에서 실행 필요

3. **테스트 파일 생성**: `tests/unit/models/test_saju_models.py` (5개 모델 검증)

4. **Alembic 환경 수정**: `alembic/env.py`에 새 모델 import 추가

**사용자 수동 작업 완료:**
- ✅ `backend/data/saju_knowledge_base_migration.md` 파일의 SQL을 운영 DB에서 실행 완료
- ✅ DB 검증 쿼리 실행 완료

### File List

**생성된 파일:**
- [x] `backend/src/models/saju_cheongan_model.py` - 천간 모델
- [x] `backend/src/models/saju_jiji_model.py` - 지지 모델
- [x] `backend/src/models/saju_sipsung_model.py` - 십성 해석 모델
- [x] `backend/src/models/saju_jiji_relation_model.py` - 지지 관계 모델
- [x] `backend/src/models/fortune_history_model.py` - 운세 이력 모델
- [x] `backend/data/saju_seed_data.json` - 천간/지지 시드 데이터 (JSON)
- [x] `backend/data/saju_knowledge_base_migration.md` - DDL + INSERT SQL 전체 문서
- [x] `backend/alembic/versions/20260128_add_saju_knowledge_base_tables.py` - Alembic 마이그레이션
- [x] `backend/tests/unit/models/__init__.py` - 모델 테스트 패키지
- [x] `backend/tests/unit/models/test_saju_models.py` - 모델 단위 테스트

**수정된 파일:**
- [x] `backend/alembic/env.py` - 새 모델 import 추가

## Change Log

| 날짜 | 내용 |
|------|------|
| 2026-01-28 | Story 2.1 구현 - 5개 모델 생성, SQL 마이그레이션 문서 생성, 단위 테스트 작성 |
