# Story 4.1: 예시 질문 및 질의 히스토리

Status: ready-for-dev

## Story

As a 관리자,
I want 예시 질문을 보고 이전 질의 히스토리를 조회하기를,
so that AI 어시스턴트를 쉽게 시작하고 이전 작업을 이어갈 수 있다.

## Acceptance Criteria

1. 도메인별 예시 질문 목록이 표시된다 (최소 10개)
   - 매출: "오늘 매출", "이번 주 결제 건수"
   - 사용자: "신규 가입자 수", "활성 사용자"
   - 상담사: "상담사별 매출", "평균 상담 시간"
2. 예시 질문 클릭 시 입력 필드에 자동 입력된다
3. 최근 질의 히스토리가 표시된다 (최대 20개)
   - 질문, 실행 시간, 결과 요약
4. 히스토리 항목 클릭 시 해당 질의가 재실행된다
5. 히스토리 검색 기능이 제공된다

## Tasks / Subtasks

- [ ] Task 1: 예시 질문 설정 구현 (AC: 1)
  - [ ] `src/services/ai/config/example_questions.py` 생성
  - [ ] `EXAMPLE_QUESTIONS` 도메인별 질문 목록 정의
  - [ ] 최소 10개 이상 예시 질문
- [ ] Task 2: 예시 질문 서비스 구현 (AC: 1, 2)
  - [ ] `src/services/ai/services/example_service.py` 생성
  - [ ] `ExampleQuestionService` 클래스 구현
  - [ ] `get_examples()` 메서드 구현
  - [ ] 카테고리 필터링 지원
- [ ] Task 3: 히스토리 모델 구현 (AC: 3)
  - [ ] `src/models/ai/ai_query_history.py` 생성
  - [ ] `AIQueryHistory` SQLAlchemy 모델 정의
  - [ ] Alembic 마이그레이션 생성
- [ ] Task 4: 히스토리 서비스 구현 (AC: 3, 4, 5)
  - [ ] `src/services/ai/services/history_service.py` 생성
  - [ ] `AIHistoryService` 클래스 구현
  - [ ] `save_query()` 메서드 구현
  - [ ] `get_history()` 메서드 구현
  - [ ] 검색 기능 (`ilike` 쿼리)
- [ ] Task 5: API 엔드포인트 구현 (AC: 1-5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] `GET /api/v1/ai/examples` 엔드포인트
  - [ ] `GET /api/v1/ai/history` 엔드포인트
  - [ ] 응답 스키마 정의
- [ ] Task 6: Redis 캐시 적용 (AC: 1)
  - [ ] 예시 질문 캐싱 (TTL: 1시간)
- [ ] Task 7: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/services/test_example_service.py` 생성
  - [ ] `tests/services/ai/services/test_history_service.py` 생성
- [ ] Task 8: 통합 테스트 작성
  - [ ] API 엔드포인트 테스트
  - [ ] 히스토리 저장/조회 테스트
- [ ] Task 9: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

첫 사용자는 "무엇을 질문해야 할지" 모르는 경우가 많습니다. 예시 질문을 제공하여 온보딩을 돕고, 이전 질의 히스토리로 작업 연속성을 제공합니다.

### Example Questions Configuration

```python
# src/services/ai/config/example_questions.py
EXAMPLE_QUESTIONS = {
    "매출": [
        {"question": "오늘 매출 얼마야?", "description": "당일 총 매출 조회"},
        {"question": "이번 주 결제 건수", "description": "주간 결제 현황"},
        {"question": "이번 달 매출 추이", "description": "월간 일별 매출"},
        {"question": "상담사별 매출 순위", "description": "상담사 실적 비교"},
    ],
    "사용자": [
        {"question": "오늘 신규 가입자 수", "description": "당일 가입 현황"},
        {"question": "이번 달 활성 사용자", "description": "MAU 조회"},
        {"question": "최근 7일 가입 추이", "description": "일별 가입자 트렌드"},
    ],
    "상담": [
        {"question": "오늘 상담 건수", "description": "당일 상담 현황"},
        {"question": "상담사별 평균 상담 시간", "description": "효율성 분석"},
        {"question": "미완료 상담 목록", "description": "처리 필요 건"},
    ],
}
```

### History Model

```python
# src/models/ai/ai_query_history.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from src.core.database import Base

class AIQueryHistory(Base):
    __tablename__ = "t_ai_query_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("t_admin.id"), nullable=False, index=True)
    query_id = Column(String(36), unique=True, nullable=False)
    question = Column(Text, nullable=False)
    answer_summary = Column(String(500))
    db_scope = Column(String(20), default="mariadb")
    execution_time_ms = Column(Integer)
    row_count = Column(Integer)
    status = Column(String(20))  # success, error
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

### History Service

```python
# src/services/ai/services/history_service.py
class AIHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_query(self, history: AIQueryHistory) -> None:
        """질의 히스토리 저장"""
        self.db.add(history)
        await self.db.commit()

    async def get_history(
        self,
        admin_id: int,
        limit: int = 20,
        search: str | None = None
    ) -> List[AIQueryHistory]:
        """히스토리 조회"""
        query = select(AIQueryHistory).where(
            AIQueryHistory.admin_id == admin_id
        ).order_by(AIQueryHistory.created_at.desc())

        if search:
            query = query.where(
                AIQueryHistory.question.ilike(f"%{search}%")
            )

        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
```

### API Endpoints

```python
# GET /api/v1/ai/examples
@router.get("/examples", response_model=ExampleQuestionsResponse)
async def get_example_questions(
    category: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
):
    """예시 질문 목록 조회"""
    return await example_service.get_examples(category)

# GET /api/v1/ai/history
@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    limit: int = Query(default=20, le=50),
    search: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """질의 히스토리 조회"""
    return await history_service.get_history(
        admin_id=current_admin.id,
        limit=limit,
        search=search
    )
```

### Dependencies

**Prerequisite Stories:**
- Story 2-4: 자연어 응답 생성 (히스토리 저장 대상)

**Blocked Stories:**
- Story 4-3: 자동완성 기능 (히스토리 기반)

### Architecture Requirements

- **FR18**: 예시 질문 목록 ✓
- **FR19**: 질의 히스토리 조회 ✓

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
