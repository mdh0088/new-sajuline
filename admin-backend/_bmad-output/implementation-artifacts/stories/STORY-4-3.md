# Story 4.3: 자동완성 기능

Status: ready-for-dev

## Story

As a 관리자,
I want 질의 입력 시 자동완성 제안을 받기를,
so that 빠르게 정확한 질문을 작성할 수 있다.

## Acceptance Criteria

1. 입력 중 실시간 자동완성 제안이 표시된다
2. 자주 사용된 질문이 우선 제안된다
3. 테이블/컬럼 이름이 자동완성에 포함된다
4. 키보드로 자동완성 항목을 선택할 수 있다
5. 캐시 히트율이 30% 이상이다

## Tasks / Subtasks

- [ ] Task 1: 자동완성 서비스 구현 (AC: 1, 2, 3)
  - [ ] `src/services/ai/services/autocomplete_service.py` 생성
  - [ ] `AutocompleteService` 클래스 구현
  - [ ] `suggest()` 메서드 구현
  - [ ] `_search_popular_questions()` 인기 질문 검색
  - [ ] `_search_keywords()` 키워드 검색
  - [ ] `index_question()` 질문 인덱싱
- [ ] Task 2: Redis 자동완성 인덱스 구현 (AC: 2, 5)
  - [ ] Redis ZRANGEBYLEX 기반 prefix 검색
  - [ ] 점수 기반 정렬 (사용 빈도)
  - [ ] 캐시 TTL 설정
- [ ] Task 3: API 엔드포인트 구현 (AC: 1, 4)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] `GET /api/v1/ai/autocomplete` 엔드포인트
  - [ ] `AutocompleteResponse` 스키마 정의
- [ ] Task 4: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/services/test_autocomplete_service.py` 생성
  - [ ] 자동완성 결과 테스트
  - [ ] 캐시 히트율 검증 테스트
- [ ] Task 5: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

자동완성은 사용자가 빠르게 정확한 질문을 입력하도록 돕습니다. 자주 사용된 질문, 테이블/컬럼 이름을 기반으로 실시간 제안을 제공합니다.

이 스토리는 Phase 1.5에서 구현됩니다.

### API Endpoint

```python
# GET /api/v1/ai/autocomplete
@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=5, le=10),
    current_admin: Admin = Depends(get_current_admin),
):
    """자동완성 제안"""
    return await autocomplete_service.suggest(q, limit)
```

### Autocomplete Service

```python
# src/services/ai/services/autocomplete_service.py
class AutocompleteService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis

    async def suggest(self, query: str, limit: int = 5) -> List[str]:
        """자동완성 제안"""
        suggestions = []

        # 1. 캐시된 인기 질문에서 검색
        popular = await self._search_popular_questions(query, limit)
        suggestions.extend(popular)

        # 2. 테이블/컬럼 키워드 검색
        if len(suggestions) < limit:
            keywords = await self._search_keywords(query, limit - len(suggestions))
            suggestions.extend(keywords)

        return suggestions[:limit]

    async def _search_popular_questions(self, query: str, limit: int) -> List[str]:
        """인기 질문 검색"""
        # Redis ZRANGEBYLEX로 prefix 검색
        key = "ai:autocomplete:questions"
        results = await self.redis.zrangebylex(
            key,
            f"[{query}",
            f"[{query}\xff",
            start=0,
            num=limit
        )
        return [r.decode() for r in results]

    async def index_question(self, question: str):
        """질문 인덱싱 (사용 시마다 점수 증가)"""
        key = "ai:autocomplete:questions"
        await self.redis.zincrby(key, 1, question)
```

### Debounce (Frontend 참고)

```typescript
// 프론트엔드 참고
const debouncedSearch = useDebounceFn(async (query: string) => {
  if (query.length < 2) return;
  const response = await api.get('/ai/autocomplete', { params: { q: query } });
  suggestions.value = response.data.suggestions;
}, 300); // 300ms debounce
```

### Dependencies

**Prerequisite Stories:**
- Story 4-1: 예시 질문 및 질의 히스토리 (히스토리 기반 인덱싱)

**Blocked Stories:**
- 없음

**External Dependencies:**
- Redis (자동완성 인덱스)

### Architecture Requirements

- **FR22**: 자동완성 (Phase 1.5) ✓
- **NFR-P5**: 캐시 히트율 ≥ 30% ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Query-Experience]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
