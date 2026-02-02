# Story 2.5: SQL 확인 및 접근성 모드

Status: ready-for-dev

## Story

As a 관리자,
I want 생성된 SQL을 선택적으로 확인하고 접근성 모드로 텍스트 요약을 받기를,
so that 투명성과 접근성이 보장된다.

## Acceptance Criteria

1. "SQL 보기" 토글 기능이 제공된다
   - `include_sql=true` 파라미터로 활성화
   - 기본값: false (SQL 숨김)
2. 토글 시 생성된 SQL이 코드 블록으로 표시된다
   - `generated_sql` 필드에 SQL 포함
   - 구문 하이라이팅 지원 (프론트엔드)
3. 접근성 모드 설정이 제공된다
   - `accessibility_mode=true` 파라미터
   - 사용자 설정으로 기본값 저장 가능 (향후)
4. 접근성 모드에서는 테이블 대신 텍스트 요약만 제공된다
   - `answer_summary` 필드에 상세 텍스트 요약
   - `data` 필드는 null 또는 빈 배열
5. 스크린리더 호환 마크업이 적용된다
   - 응답에 ARIA 라벨 정보 포함 (프론트엔드용)
   - 숫자 읽기 친화적 포맷

## Tasks / Subtasks

- [ ] Task 1: 접근성 포맷터 구현 (AC: 4, 5)
  - [ ] `src/services/ai/utils/accessibility_formatter.py` 생성
  - [ ] `AccessibilityFormatter` 클래스 구현
  - [ ] `format_for_screen_reader()` 메서드 구현
  - [ ] 숫자 읽기 포맷 변환
- [ ] Task 2: 접근성 프롬프트 구현 (AC: 4)
  - [ ] `src/services/ai/prompts/accessibility_response.py` 생성
  - [ ] `ACCESSIBILITY_RESPONSE_PROMPT` 정의
  - [ ] 스크린리더 친화적 응답 규칙
- [ ] Task 3: 응답 스키마 확장 (AC: 1, 2, 3, 4, 5)
  - [ ] `AIQueryResponse`에 `answer_summary` 필드 추가
  - [ ] `AccessibilityHints` 스키마 정의
  - [ ] `accessibility_hints` 필드 추가
- [ ] Task 4: API 통합 (AC: 1-5)
  - [ ] `include_sql` 파라미터 처리
  - [ ] `accessibility_mode` 파라미터 처리
  - [ ] 접근성 모드 응답 생성 로직
- [ ] Task 5: 단위 테스트 작성 (AC: 1-5)
  - [ ] `tests/services/ai/unit/test_accessibility_formatter.py` 생성
  - [ ] 숫자 읽기 포맷 테스트
  - [ ] 빈 결과 테스트
- [ ] Task 6: 통합 테스트 작성
  - [ ] `include_sql=true` 테스트
  - [ ] `accessibility_mode=true` 테스트
- [ ] Task 7: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

일부 관리자는 AI가 생성한 SQL을 직접 확인하고 싶어합니다. 또한 시각 장애가 있는 관리자를 위해 테이블 대신 텍스트 요약만 제공하는 접근성 모드가 필요합니다.

이 스토리는 Phase 1.5에서 구현하며, 사용자 경험 향상에 초점을 맞춥니다.

### Accessibility Formatter

```python
# src/services/ai/utils/accessibility_formatter.py
from typing import List, Dict, Any

class AccessibilityFormatter:
    """접근성 모드 응답 포맷터"""

    @staticmethod
    def format_for_screen_reader(
        answer: str,
        data: List[Dict[str, Any]],
        columns: List[str]
    ) -> str:
        """스크린리더 친화적 텍스트 요약 생성"""
        parts = [answer, ""]

        if not data:
            return answer

        parts.append(f"총 {len(data)}개의 결과가 있습니다.")
        # ...

    @staticmethod
    def _format_value_for_speech(value: Any) -> str:
        """값을 음성 출력 친화적으로 포맷"""
        if value is None:
            return "값 없음"
        elif isinstance(value, (int, float)):
            if value >= 100_000_000:
                return f"{value // 100_000_000}억 {(value % 100_000_000) // 10_000}만"
            elif value >= 10_000:
                return f"{value // 10_000}만 {value % 10_000}"
            return f"{value:,}"
        return str(value)
```

### Accessibility Response Prompt

```python
# src/services/ai/prompts/accessibility_response.py

ACCESSIBILITY_RESPONSE_PROMPT = """당신은 시각 장애인을 위한 데이터 분석 결과를 설명하는 AI 어시스턴트입니다.

## 규칙
1. **상세한 설명**: 테이블을 볼 수 없으므로 모든 정보를 텍스트로
2. **숫자 읽기**: 큰 숫자는 "1억 2천만원"처럼 읽기 쉽게
3. **순서 표시**: "첫 번째", "두 번째" 등 순서 명시
4. **비교 정보**: 수치 간 비교를 명확하게 설명
5. **요약 먼저**: 핵심 내용을 먼저, 상세 내용은 나중에
"""
```

### Response Schema Extension

```python
class AccessibilityHints(BaseModel):
    """프론트엔드 접근성 구현을 위한 힌트"""
    aria_label: str = "AI 분석 결과"
    aria_live: str = "polite"
    row_count: int = 0
    column_count: int = 0
```

### Edge Cases

- **SQL에 민감 정보**: SQL 표시 전 민감 테이블 참조 확인
- **긴 SQL**: 접기/펼치기 지원 (프론트엔드)
- **대용량 결과 접근성**: 요약 + "더 보기" 패턴

### Dependencies

**Prerequisite Stories:**
- Story 2-4: 자연어 응답 생성 및 결과 포맷팅 (기반 응답 구조)

**Blocked Stories:**
- 없음 (Phase 1.5 완료 기능)

### Architecture Requirements

- **FR5**: 생성된 SQL 확인 (선택적) ✓
- **FR6**: 접근성 텍스트 요약 ✓
- **NFR-A1**: 스크린리더 호환 ✓
- **NFR-A3**: 텍스트 요약 모드 ✓

### 접근성 테스트 체크리스트

- [ ] 스크린리더 (VoiceOver/NVDA)로 결과 읽기 테스트
- [ ] 키보드만으로 SQL 토글 조작
- [ ] 색상 대비 확인 (SQL 구문 하이라이팅)
- [ ] 포커스 관리 확인

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Accessibility]
- [WCAG 2.1 AA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
