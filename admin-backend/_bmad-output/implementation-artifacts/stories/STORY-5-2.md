# Story 5.2: 답변 수정 기능

Status: ready-for-dev

## Story

As a 관리자,
I want 잘못된 AI 답변을 수정하여 제출하기를,
so that 정확한 데이터로 AI가 학습할 수 있다.

## Acceptance Criteria

1. "답변 수정" 버튼이 각 응답에 제공된다
2. 수정 모드에서 자연어 답변을 편집할 수 있다
3. 수정된 답변이 원본과 함께 저장된다
4. 수정 이력이 관리된다
5. 수정된 답변이 향후 학습 데이터로 표시된다

## Tasks / Subtasks

- [ ] Task 1: 수정 모델 구현 (AC: 3, 4, 5)
  - [ ] `src/models/ai/ai_feedback_correction.py` 생성
  - [ ] `AIFeedbackCorrection` SQLAlchemy 모델 정의
  - [ ] `is_training_data`, `reviewed` 플래그 포함
  - [ ] Alembic 마이그레이션 생성
- [ ] Task 2: 수정 스키마 구현 (AC: 2, 3)
  - [ ] `src/schemas/ai/correction_schema.py` 생성
  - [ ] `CorrectionRequest` 스키마 정의
  - [ ] `CorrectionResponse` 스키마 정의
  - [ ] `CorrectionHistoryResponse` 스키마 정의
- [ ] Task 3: 수정 서비스 구현 (AC: 3, 4, 5)
  - [ ] `src/services/ai/services/correction_service.py` 생성
  - [ ] `AICorrectionService` 클래스 구현
  - [ ] `save_correction()` 메서드 구현
  - [ ] `get_corrections()` 메서드 구현
  - [ ] `get_training_data()` 메서드 구현
- [ ] Task 4: API 엔드포인트 구현 (AC: 1-5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] `PUT /api/v1/ai/feedback/{query_id}/correction` 엔드포인트
  - [ ] `GET /api/v1/ai/feedback/{query_id}/corrections` 엔드포인트
- [ ] Task 5: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/services/test_correction_service.py` 생성
  - [ ] `tests/api/v1/test_ai_correction_api.py` 생성
- [ ] Task 6: 통합 테스트 작성
  - [ ] 수정 제출 E2E 테스트
  - [ ] 수정 이력 조회 테스트
- [ ] Task 7: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI 응답이 부정확할 경우 사용자가 직접 올바른 답변을 제출할 수 있습니다. 이 수정 데이터는 향후 AI 모델 개선을 위한 학습 데이터로 활용됩니다.

이 스토리는 Phase 1.5에서 구현됩니다.

### API Endpoints

```python
# PUT /api/v1/ai/feedback/{query_id}/correction
@router.put(
    "/feedback/{query_id}/correction",
    response_model=CorrectionResponse
)
async def submit_correction(
    query_id: str,
    request: CorrectionRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI 응답 수정 제출"""
    correction = await correction_service.save_correction(
        admin_id=current_admin.id,
        query_id=query_id,
        correction=request
    )
    return CorrectionResponse(
        success=True,
        correction_id=correction.id,
        message="답변 수정이 제출되었습니다. 검토 후 반영됩니다."
    )

# GET /api/v1/ai/feedback/{query_id}/corrections
@router.get(
    "/feedback/{query_id}/corrections",
    response_model=CorrectionHistoryResponse
)
async def get_correction_history(
    query_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """특정 질의의 수정 이력 조회"""
    corrections = await correction_service.get_corrections(query_id)
    return CorrectionHistoryResponse(
        query_id=query_id,
        corrections=corrections,
        total_count=len(corrections)
    )
```

### Request/Response Schemas

```python
# src/schemas/ai/correction_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CorrectionRequest(BaseModel):
    """답변 수정 요청"""
    corrected_answer: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="수정된 자연어 답변"
    )
    correction_reason: Optional[str] = Field(
        None,
        max_length=500,
        description="수정 사유"
    )

class CorrectionResponse(BaseModel):
    """수정 제출 응답"""
    success: bool
    correction_id: int
    message: str

class CorrectionItem(BaseModel):
    """수정 이력 항목"""
    id: int
    admin_id: int
    original_answer: str
    corrected_answer: str
    correction_reason: Optional[str]
    is_training_data: bool
    created_at: datetime

class CorrectionHistoryResponse(BaseModel):
    """수정 이력 응답"""
    query_id: str
    corrections: List[CorrectionItem]
    total_count: int
```

### Correction Model

```python
# src/models/ai/ai_feedback_correction.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from datetime import datetime
from src.core.database import Base

class AIFeedbackCorrection(Base):
    __tablename__ = "t_ai_feedback_correction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("t_admin.id"), nullable=False, index=True)
    query_id = Column(String(36), nullable=False, index=True)
    original_answer = Column(Text, nullable=False)
    corrected_answer = Column(Text, nullable=False)
    correction_reason = Column(String(500), nullable=True)
    is_training_data = Column(Boolean, default=True)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("t_admin.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

### Correction Service

```python
# src/services/ai/services/correction_service.py
class AICorrectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_correction(
        self,
        admin_id: int,
        query_id: str,
        correction: CorrectionRequest
    ) -> AIFeedbackCorrection:
        """수정 저장"""
        history = await self._get_query_history(query_id)
        if not history:
            raise ValueError(f"Query not found: {query_id}")

        db_correction = AIFeedbackCorrection(
            admin_id=admin_id,
            query_id=query_id,
            original_answer=history.answer_summary or "",
            corrected_answer=correction.corrected_answer,
            correction_reason=correction.correction_reason,
            is_training_data=True,
            reviewed=False
        )
        self.db.add(db_correction)
        await self.db.commit()
        await self.db.refresh(db_correction)
        return db_correction

    async def get_training_data(
        self,
        limit: int = 100,
        reviewed_only: bool = True
    ) -> List[AIFeedbackCorrection]:
        """학습 데이터 조회"""
        query = select(AIFeedbackCorrection).where(
            AIFeedbackCorrection.is_training_data == True
        )
        if reviewed_only:
            query = query.where(AIFeedbackCorrection.reviewed == True)
        query = query.order_by(AIFeedbackCorrection.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
```

### 학습 데이터 활용

수정된 데이터는 다음 용도로 활용됩니다:
1. **프롬프트 개선**: Few-shot 예시로 활용
2. **품질 분석**: 빈번한 오류 패턴 파악
3. **향후 Fine-tuning**: 충분한 데이터 축적 시 모델 학습

### 검토 워크플로우

```
사용자 수정 제출 → 관리자 검토 큐 → 승인/반려 → 학습 데이터 플래그
```

### Dependencies

**Prerequisite Stories:**
- Story 5-1: 피드백 제출 인터페이스

**Blocked Stories:**
- 없음

### Architecture Requirements

- **FR25**: 답변 수정 제출 ✓

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
