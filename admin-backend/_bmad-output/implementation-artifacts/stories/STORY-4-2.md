# Story 4.2: 사용자 친화적 에러 및 대안 제안

Status: ready-for-dev

## Story

As a 관리자,
I want 에러 발생 시 친절한 메시지와 대안 질문을 받기를,
so that 에러 상황에서도 원하는 데이터를 찾을 수 있다.

## Acceptance Criteria

1. 기술적 에러가 사용자 친화적 메시지로 변환된다
2. 에러 시 관련된 대안 질문이 최대 3개 제안된다
3. 대안 질문 클릭 시 해당 질의가 실행된다
4. 에러 코드와 기술적 메시지가 선택적으로 표시된다
5. 에러 유형별 적절한 안내가 제공된다

## Tasks / Subtasks

- [ ] Task 1: 에러 핸들러 구현 (AC: 1, 4, 5)
  - [ ] `src/services/ai/utils/error_handler.py` 생성
  - [ ] `AIErrorHandler` 클래스 구현
  - [ ] `UserFriendlyError` 데이터클래스 정의
  - [ ] `ERROR_MAPPINGS` 에러 코드별 메시지 매핑
  - [ ] `handle_error()` 메서드 구현
- [ ] Task 2: 대안 제안 생성기 구현 (AC: 2, 3)
  - [ ] `src/services/ai/utils/suggestion_generator.py` 생성
  - [ ] `SuggestionGenerator` 클래스 구현
  - [ ] `SUGGESTION_TEMPLATES` 상수 정의
  - [ ] `generate()` 메서드 구현
  - [ ] `_extract_keyword()` 키워드 추출 로직
- [ ] Task 3: 에러 메시지 설정 구현 (AC: 1, 5)
  - [ ] `src/services/ai/config/error_messages.py` 생성
  - [ ] 에러 코드별 사용자 메시지 정의
  - [ ] 에러 유형별 안내 메시지
- [ ] Task 4: API 통합 (AC: 1-5)
  - [ ] `src/api/v1/ai_assistant_api.py` 업데이트
  - [ ] 에러 핸들러 적용
  - [ ] 응답에 대안 제안 포함
- [ ] Task 5: 단위 테스트 작성 (≥80% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/utils/test_error_handler.py` 생성
  - [ ] `tests/services/ai/utils/test_suggestion_generator.py` 생성
  - [ ] 에러 변환 테스트
  - [ ] 대안 생성 테스트
- [ ] Task 6: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

에러가 발생했을 때 기술적인 메시지만 보여주면 사용자는 좌절합니다. 친절한 에러 메시지와 함께 대안 질문을 제안하여 사용자가 문제를 해결할 수 있도록 돕습니다.

### Error Handler

```python
# src/services/ai/utils/error_handler.py
from dataclasses import dataclass
from typing import List

@dataclass
class UserFriendlyError:
    user_message: str
    suggestions: List[str]
    error_code: str
    technical_message: str | None = None

class AIErrorHandler:
    """AI 에러를 사용자 친화적으로 변환"""

    ERROR_MAPPINGS = {
        "AIBI_SQL_GEN_FAILED": {
            "message": "질문을 이해하지 못했어요. 다른 표현으로 질문해주세요.",
            "suggestions_template": "rephrase"
        },
        "AIBI_TABLE_NOT_ALLOWED": {
            "message": "해당 데이터에 접근 권한이 없습니다.",
            "suggestions_template": "alternative_data"
        },
        "AIBI_LLM_TIMEOUT": {
            "message": "AI 응답이 지연되고 있어요. 잠시 후 다시 시도해주세요.",
            "suggestions_template": "retry"
        },
        "AIBI_EMPTY_RESULT": {
            "message": "조회 결과가 없습니다.",
            "suggestions_template": "broaden_scope"
        },
        "AIBI_TOO_MANY_RESULTS": {
            "message": "결과가 너무 많습니다. 조건을 좁혀주세요.",
            "suggestions_template": "narrow_scope"
        },
    }

    @classmethod
    def handle_error(
        cls,
        error_code: str,
        original_question: str,
        technical_message: str | None = None
    ) -> UserFriendlyError:
        """에러를 사용자 친화적으로 변환"""
        mapping = cls.ERROR_MAPPINGS.get(error_code, {
            "message": "문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "suggestions_template": "general"
        })

        suggestions = SuggestionGenerator.generate(
            template=mapping["suggestions_template"],
            original_question=original_question
        )

        return UserFriendlyError(
            user_message=mapping["message"],
            suggestions=suggestions,
            error_code=error_code,
            technical_message=technical_message
        )
```

### Suggestion Generator

```python
# src/services/ai/utils/suggestion_generator.py
class SuggestionGenerator:
    """대안 질문 생성기"""

    SUGGESTION_TEMPLATES = {
        "rephrase": [
            "더 구체적으로: '{question}' → '이번 달 {keyword}'",
            "다른 표현: '총 {keyword}', '{keyword} 합계'",
            "기간 추가: '오늘 {keyword}', '이번 주 {keyword}'"
        ],
        "broaden_scope": [
            "기간을 넓혀보세요: '이번 달' → '최근 3개월'",
            "조건을 줄여보세요: 전체 데이터 조회",
            "다른 기준: '전체 {keyword}'"
        ],
        "narrow_scope": [
            "기간을 좁혀주세요: '이번 달만'",
            "특정 대상: '김철수 상담사만'",
            "요약으로 보기: '월별 요약'"
        ],
        "alternative_data": [
            "조회 가능: '매출 현황'",
            "조회 가능: '상담 건수'",
            "조회 가능: '사용자 통계'"
        ],
    }

    @classmethod
    def generate(
        cls,
        template: str,
        original_question: str,
        max_suggestions: int = 3
    ) -> List[str]:
        """대안 제안 생성"""
        templates = cls.SUGGESTION_TEMPLATES.get(template, [])

        keyword = cls._extract_keyword(original_question)

        suggestions = []
        for tmpl in templates[:max_suggestions]:
            suggestion = tmpl.format(
                question=original_question,
                keyword=keyword
            )
            suggestions.append(suggestion)

        return suggestions

    @staticmethod
    def _extract_keyword(question: str) -> str:
        """질문에서 핵심 키워드 추출"""
        keywords = ["매출", "결제", "사용자", "상담", "가입"]
        for kw in keywords:
            if kw in question:
                return kw
        return "데이터"
```

### Dependencies

**Prerequisite Stories:**
- Story 2-4: 자연어 응답 생성 (에러 응답 패턴)

**Blocked Stories:**
- 없음

### Architecture Requirements

- **FR20**: 사용자 친화적 에러 메시지 ✓
- **FR21**: 대안 질문 제안 ✓
- **AR16-AR17**: AIError 클래스, 에러 코드 체계 ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Error-Handling]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
