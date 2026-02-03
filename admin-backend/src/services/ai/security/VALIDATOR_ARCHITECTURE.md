# SQL Validator Architecture

## Overview

프로젝트에는 **두 개의 SQL 검증 시스템**이 있습니다. 각각 다른 목적과 범위를 가지고 있습니다.

## 1. SQLValidator (Story 2-2)
**위치**: `src/services/ai/validators/sql_validator.py`

**목적**: SQL 생성 에이전트의 **출력 품질 검증**
- LLM이 생성한 SQL의 구조적 정확성 확인
- 파싱 가능 여부 검증 (sqlparse 사용)
- SELECT 문인지 확인

**범위**:
- 기본적인 SQL 구조 검증
- 파싱 가능성 체크
- 단순 키워드 확인

**Story**: AI-002 (SQL 생성 에이전트)

## 2. Layer2SQLValidator (Story 3-1)
**위치**: `src/services/ai/security/layer2_validator.py`

**목적**: **보안 중심의 심층 검증** (4-Layer Security Framework의 Layer 2)
- SQL Injection 방지
- 금지 키워드 차단 (INSERT, DELETE, DROP 등)
- 위험 패턴 탐지 (UNION, stacked queries, comments 등)
- 테이블 화이트리스트 검증
- 스키마 prefix 처리

**범위**:
- 보안 위협 탐지 및 차단
- 다층 패턴 매칭 (정규식 기반)
- 세밀한 보안 정책 적용

**Story**: 3-1 (4-Layer Security Framework)

## Integration Strategy

### Current State (Story 3-1 완료 후)
```
SQL Generation (Story 2-2)
     ↓
[Layer 2 Validation] ← SecurityPipeline.validate_sql()
     ↓
SQL Execution (Story 2-3)
     ↓
[Layer 3 Sanitization] ← SecurityPipeline.sanitize_result()
```

### Recommended Integration
두 Validator를 **순차적으로 적용**:

1. **SQLValidator** (품질): LLM 출력이 유효한 SELECT 문인지 확인
2. **Layer2SQLValidator** (보안): 보안 정책 위반 여부 검증

```python
# 1단계: 품질 검증 (Story 2-2)
from src.services.ai.validators.sql_validator import SQLValidator
quality_check = SQLValidator.validate(sql)
if not quality_check.is_valid:
    raise ValueError("Invalid SQL structure")

# 2단계: 보안 검증 (Story 3-1)
from src.services.ai.security import SecurityPipeline
security_check = SecurityPipeline.validate_sql(sql, allowed_tables)
if not security_check.is_safe:
    raise SecurityError("Security policy violation")
```

## Decision Rationale

### 왜 하나로 통합하지 않았나?
1. **관심사 분리 (Separation of Concerns)**
   - SQLValidator: 품질 (Quality)
   - Layer2SQLValidator: 보안 (Security)

2. **테스트 커버리지**
   - 각 Validator는 독립적으로 100% 테스트 커버리지 달성
   - 통합 시 테스트 복잡도 증가

3. **확장성**
   - 보안 정책은 자주 변경됨 (새로운 위협 대응)
   - 품질 검증은 상대적으로 안정적

4. **Story 독립성**
   - Story 2-2와 3-1은 독립적으로 완료 가능
   - 의존성 최소화

## Future Considerations

### Option A: Keep Separate (권장)
- 현재 상태 유지
- 각 Validator의 독립성 보장
- 순차 적용으로 명확한 책임 분리

### Option B: Create Wrapper
- CompositeValidator 생성
- 내부적으로 두 Validator 순차 호출
- 외부 API는 단순화

### Option C: Merge (비권장)
- 두 Validator를 하나로 통합
- 코드 복잡도 증가
- 테스트 유지보수 어려움

## Documentation References
- **Story 2-2**: `_bmad-output/implementation-artifacts/stories/STORY-2-2.md`
- **Story 3-1**: `_bmad-output/implementation-artifacts/stories/STORY-3-1.md`
- **Architecture**: `_bmad-output/planning-artifacts/architecture.md#Security-Architecture`

---

**Last Updated**: 2026-02-03
**Author**: Claude Sonnet 4.5 (Code Review - Story 3-1)
