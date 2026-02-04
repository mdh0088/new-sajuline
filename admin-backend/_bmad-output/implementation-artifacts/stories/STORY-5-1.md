# Story 5.1: 피드백 제출 인터페이스

Status: done

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

- [x] Task 1: 피드백 모델 구현 (AC: 5)
  - [x] `src/models/ai/ai_feedback_model.py` 수정 (admin_id 타입 수정)
  - [x] `AIFeedback` SQLAlchemy 모델 정의
  - [x] 수동 마이그레이션 SQL 생성
- [x] Task 2: 피드백 스키마 구현 (AC: 1, 2)
  - [x] `src/schemas/ai/feedback_schema.py` 생성
  - [x] `AIFeedbackRequest` 스키마 정의
  - [x] `AIFeedbackResponse` 스키마 정의
  - [x] 1-5점 범위 검증
- [x] Task 3: 피드백 서비스 구현 (AC: 4, 5)
  - [x] `src/services/ai/services/feedback_service.py` 생성
  - [x] `AIFeedbackService` 클래스 구현
  - [x] `save_feedback()` 메서드 구현
  - [x] `get_feedback_by_query()` 메서드 구현
- [x] Task 4: API 엔드포인트 구현 (AC: 1-5)
  - [x] `src/api/v1/ai_assistant_api.py` 업데이트
  - [x] `POST /api/v1/ai/feedback` 엔드포인트
  - [x] BackgroundTasks로 비동기 처리
  - [x] 확인 응답 반환
- [x] Task 5: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [x] `tests/services/ai/services/test_feedback_service.py` 생성
  - [x] `tests/api/v1/test_ai_feedback_api.py` 생성
- [x] Task 6: 통합 테스트 작성
  - [x] 피드백 제출 E2E 테스트 (모델, 스키마, 서비스 레벨)
  - [x] 비동기 처리 검증 (BackgroundTasks 사용)
- [x] Task 7: 린팅/타입 체크 통과
  - [x] `black src/` 실행
  - [x] `isort src/` 실행
  - [x] `flake8 src/` 실행
  - [x] `mypy src/` 실행

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

**Task 1 완료 (2026-02-04)**:
- AIFeedback 모델 수정 완료 (admin_id 타입을 String(100)으로 변경, FK도 t_admin.admin_id로 수정)
- 7개 단위 테스트 작성 및 통과 (피드백 생성, 조회, 별점 범위, 인덱스 등)
- 수동 마이그레이션 SQL 작성 (`migrations/manual/create_t_ai_feedback.sql`)
- 테스트용 conftest.py 작성 (SQLite 인메모리 DB 사용)

**Task 2 완료 (2026-02-04)**:
- AIFeedbackRequest 스키마 작성 (query_id, rating, comment 필드)
- AIFeedbackResponse 스키마 작성 (success, message 필드)
- 1-5점 별점 범위 검증 추가 (Pydantic Field validator)
- 15개 단위 테스트 작성 및 통과 (필드 검증, 범위 검증, 예시 스키마 등)

**Task 3 완료 (2026-02-04)**:
- AIFeedbackService 클래스 구현 (비동기 DB 세션 사용)
- save_feedback() 메서드 구현 (피드백 저장 및 커밋)
- get_feedback_by_query() 메서드 구현 (query_id, admin_id로 조회)
- 6개 단위 테스트 작성 및 통과 (저장, 조회, 빈 결과 등)

**Task 4 완료 (2026-02-04)**:
- POST /api/v1/ai/feedback 엔드포인트 구현
- BackgroundTasks를 통한 비동기 피드백 저장 (UX 방해 없음)
- 즉시 성공 응답 반환 (201 Created)
- 구조화된 로깅 추가 (feedback_submitted, feedback_submission_failed)
- API 테스트 프레임워크 설정 (tests/api/v1/test_ai_feedback_api.py)

**Task 5-7 완료 (2026-02-04)**:
- 28개 단위/통합 테스트 작성 및 통과 (모델: 7, 스키마: 15, 서비스: 6)
- black, isort, flake8, mypy 모든 품질 검사 통과
- 코드 포매팅 및 정리 완료

**리뷰 후 수정 완료 (2026-02-04)**:
- HIGH #3: API 엔드포인트 DB 세션 수명 관리 오류 수정 (AsyncSessionLocal 독립 세션 사용)
- HIGH #6: Rating validator 중복 제거 (Field 제약만 사용)
- HIGH #1, #2, #4, #5: API 통합 테스트 10개 실제 구현 (BackgroundTasks, FK 무결성, 에러 처리, 로깅 검증)
- 총 테스트 개수: 38개 (모델: 7, 스키마: 15, 서비스: 6, API: 10)

### File List

- src/models/ai/ai_feedback_model.py (수정)
- src/schemas/ai/feedback_schema.py (생성)
- src/schemas/ai/__init__.py (수정)
- src/services/ai/services/feedback_service.py (생성)
- src/api/v1/ai_assistant_api.py (수정)
- migrations/manual/create_t_ai_feedback.sql (생성)
- tests/models/ai/test_ai_feedback.py (생성)
- tests/models/ai/conftest.py (생성)
- tests/schemas/ai/test_feedback_schema.py (생성)
- tests/services/ai/services/test_feedback_service.py (생성)
- tests/api/v1/test_ai_feedback_api.py (생성)
