# Story 5.1: 피드백 제출 인터페이스

Status: ready-for-dev

## Story

As a 관리자,
I want AI 응답에 대해 별점과 피드백을 제출하기를,
so that 서비스 개선에 기여할 수 있다.

## Acceptance Criteria

1. 각 응답에 1-5점 별점 평가 UI가 제공된다
2. 선택적 텍스트 피드백 입력란이 제공된다
3. 피드백 제출 시 확인 메시지가 표시된다
4. 피드백 제출이 비동기로 처리되어 UX가 방해받지 않는다
5. 제출된 피드백이 응답 ID와 연결된다

## Tasks / Subtasks

- [ ] Task 1: 피드백 모델 구현 (AC: 5)
  - [ ] `src/models/ai/ai_feedback.py` 생성
  - [ ] `AIFeedback` SQLAlchemy 모델 정의
  - [ ] Alembic 마이그레이션 생성
- [ ] Task 2: 피드백 스키마 구현 (AC: 1, 2)
  - [ ] `src/schemas/ai/feedback_schema.py` 생성
  - [ ] `AIFeedbackRequest` 스키마 정의
  - [ ] `AIFeedbackResponse` 스키마 정의
  - [ ] 1-5점 범위 검증
- [ ] Task 3: 피드백 서비스 구현 (AC: 4, 5)
  - [ ] `src/services/ai/services/feedback_service.py` 생성
  - [ ] `AIFeedbackService` 클래스 구현
  - [ ] `save_feedback()` 메서드 구현
  - [ ] `get_feedback_by_query()` 메서드 구현
- [ ] Task 4: API 엔드포인트 구현 (AC: 1-5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] `POST /api/v1/ai/feedback` 엔드포인트
  - [ ] BackgroundTasks로 비동기 처리
  - [ ] 확인 응답 반환
- [ ] Task 5: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/services/test_feedback_service.py` 생성
  - [ ] `tests/api/v1/test_ai_feedback_api.py` 생성
- [ ] Task 6: 통합 테스트 작성
  - [ ] 피드백 제출 E2E 테스트
  - [ ] 비동기 처리 검증
- [ ] Task 7: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI BI 어시스턴트의 품질 개선을 위해 사용자 피드백 수집이 필수입니다. 별점과 텍스트 피드백을 통해 응답 품질을 측정하고 개선 방향을 파악합니다.

### API Endpoint

```python
# POST /api/v1/ai/feedback
@router.post("/feedback", response_model=AIFeedbackResponse, status_code=201)
async def submit_feedback(
    request: AIFeedbackRequest,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI 응답 피드백 제출"""
    # 비동기 처리로 UX 방해 없음
    background_tasks.add_task(
        feedback_service.save_feedback,
        admin_id=current_admin.id,
        feedback=request
    )
    return AIFeedbackResponse(
        success=True,
        message="피드백이 제출되었습니다. 감사합니다!"
    )
```

### Request/Response Schemas

```python
# src/schemas/ai/feedback_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class AIFeedbackRequest(BaseModel):
    """피드백 제출 요청"""
    query_id: str = Field(..., description="질의 응답 ID")
    rating: int = Field(..., ge=1, le=5, description="1-5점 별점")
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="선택적 텍스트 피드백"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "rating": 4,
                "comment": "결과는 정확했지만 응답이 조금 느렸어요"
            }
        }

class AIFeedbackResponse(BaseModel):
    """피드백 제출 응답"""
    success: bool
    message: str
```

### Feedback Model

```python
# src/models/ai/ai_feedback.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from src.core.database import Base

class AIFeedback(Base):
    __tablename__ = "t_ai_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("t_admin.id"), nullable=False, index=True)
    query_id = Column(String(36), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

### Feedback Service

```python
# src/services/ai/services/feedback_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.ai.ai_feedback import AIFeedback
from src.schemas.ai.feedback_schema import AIFeedbackRequest

class AIFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_feedback(
        self,
        admin_id: int,
        feedback: AIFeedbackRequest
    ) -> AIFeedback:
        """피드백 저장"""
        db_feedback = AIFeedback(
            admin_id=admin_id,
            query_id=feedback.query_id,
            rating=feedback.rating,
            comment=feedback.comment
        )
        self.db.add(db_feedback)
        await self.db.commit()
        await self.db.refresh(db_feedback)
        return db_feedback
```

### 비동기 처리 장점

- 사용자 경험 향상: 피드백 제출 후 즉시 확인
- 서버 부하 분산: BackgroundTasks로 처리
- 실패 복구: 별도 큐로 재시도 가능

### Dependencies

**Prerequisite Stories:**
- Story 2-4: 자연어 응답 생성 (응답 ID 생성)

**Blocked Stories:**
- Story 5-2: 답변 수정 기능
- Story 5-3: 피드백 저장 및 분석 API

### Architecture Requirements

- **FR24**: 피드백 제공 ✓
- **FR26**: 1-5점 평가 ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Feedback-System]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
