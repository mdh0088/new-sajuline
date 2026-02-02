# Story 3.1: 4-Layer Security 프레임워크

Status: ready-for-dev

## Story

As a 시스템,
I want 4계층 보안 프레임워크가 적용되기를,
so that 다층 방어로 데이터 보안이 보장된다.

## Acceptance Criteria

1. Layer 1 (Prompt): 시스템 프롬프트에 보안 지침이 내장된다
   - SELECT only 명시
   - 허용 테이블 목록 명시
   - 금지 패턴 설명
2. Layer 2 (Validation): SQL 화이트리스트 검증이 구현된다
   - 허용된 키워드만 통과
   - 금지 키워드 탐지 및 차단
   - 테이블 이름 화이트리스트 검증
3. Layer 3 (Result): 결과 내 PII 마스킹이 구현된다
   - 마스킹 대상 필드 정의
   - 마스킹 규칙 적용
4. Layer 4 (User): 위험 쿼리 시 확인 다이얼로그가 표시된다
   - 대용량 조회 경고
   - 복잡한 조인 경고
5. 보안 모듈 테스트 커버리지가 100%이다

## Tasks / Subtasks

- [ ] Task 1: Layer 1 프롬프트 보안 구현 (AC: 1)
  - [ ] `src/services/ai/security/layer1_prompt.py` 생성
  - [ ] `SECURITY_SYSTEM_PROMPT` 상수 정의
  - [ ] `build_secure_prompt()` 함수 구현
- [ ] Task 2: Layer 2 SQL 검증 구현 (AC: 2)
  - [ ] `src/services/ai/security/layer2_validator.py` 생성
  - [ ] `Layer2SQLValidator` 클래스 구현
  - [ ] `SecurityValidationResult` 데이터클래스 정의
  - [ ] `FORBIDDEN_KEYWORDS` 상수 정의
  - [ ] `DANGEROUS_PATTERNS` 정규식 정의
  - [ ] `WARNING_PATTERNS` 정규식 정의
- [ ] Task 3: Layer 3 결과 검증 구현 (AC: 3)
  - [ ] `src/services/ai/security/layer3_result.py` 생성
  - [ ] `Layer3ResultValidator` 클래스 구현
  - [ ] `ResultValidationResult` 데이터클래스 정의
  - [ ] `SENSITIVE_COLUMNS` 상수 정의
- [ ] Task 4: Layer 4 사용자 확인 구현 (AC: 4)
  - [ ] `src/services/ai/security/layer4_user.py` 생성
  - [ ] `Layer4UserConfirmation` 클래스 구현
  - [ ] `UserConfirmationRequired` 데이터클래스 정의
- [ ] Task 5: SecurityPipeline 통합 (AC: 1-5)
  - [ ] `src/services/ai/security/__init__.py` 업데이트
  - [ ] `SecurityPipeline` 클래스 구현
- [ ] Task 6: 단위 테스트 작성 (100% 커버리지) (AC: 5)
  - [ ] `tests/services/ai/security/test_layer1.py` 생성
  - [ ] `tests/services/ai/security/test_layer2.py` 생성
  - [ ] `tests/services/ai/security/test_layer3.py` 생성
  - [ ] `tests/services/ai/security/test_layer4.py` 생성
  - [ ] 금지 키워드 차단 테스트
  - [ ] 위험 패턴 차단 테스트
  - [ ] 테이블 화이트리스트 테스트
- [ ] Task 7: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

AI BI 어시스턴트는 자연어를 SQL로 변환하므로 다양한 보안 위협에 노출됩니다. SQL Injection, 민감 데이터 노출, 권한 우회 등을 방지하기 위해 4계층 보안 프레임워크를 구축합니다.

### 4-Layer Security Architecture

```
Layer 1: Prompt Engineering (입력 단계)
├── 시스템 프롬프트에 보안 지침 내장
├── 허용된 테이블/컬럼만 스키마에 포함
└── SELECT only 제약 명시

Layer 2: SQL Validation (생성 단계)
├── SQL 화이트리스트 검증
├── 금지 키워드 탐지
├── 테이블/컬럼 존재 여부 확인
└── 위험 패턴 차단 (UNION, 서브쿼리 등)

Layer 3: Result Validation (결과 단계)
├── 결과 행 수 제한 (1000건)
├── PII 마스킹
└── 이상치 탐지

Layer 4: User Confirmation (사용자 단계)
├── 위험 쿼리 확인 요청
├── 생성된 SQL 미리보기 옵션
└── 실행 취소 옵션
```

### Layer 2: SQL Validator

```python
# src/services/ai/security/layer2_validator.py

class Layer2SQLValidator:
    """Layer 2: SQL 보안 검증"""

    FORBIDDEN_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE',
        'XP_', 'SP_', 'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE'
    }

    DANGEROUS_PATTERNS = [
        r'UNION\s+(?:ALL\s+)?SELECT',  # UNION Injection
        r';\s*SELECT',  # Stacked queries
        r'--',  # SQL comments
        r'/\*.*\*/',  # Block comments
        r'BENCHMARK\s*\(',  # Time-based injection
        r'SLEEP\s*\(',  # Time-based injection
        r'information_schema',  # Schema enumeration
    ]

    @classmethod
    def validate(
        cls,
        sql: str,
        allowed_tables: Set[str]
    ) -> SecurityValidationResult:
        """SQL 보안 검증 수행"""
        # 구현...
```

### Layer 3: Result Validator

```python
# src/services/ai/security/layer3_result.py

class Layer3ResultValidator:
    """Layer 3: 결과 보안 검증 및 처리"""

    MAX_ROWS = 1000
    SENSITIVE_COLUMNS = {
        'password', 'passwd', 'pwd',
        'resident_number', 'ssn', 'jumin',
        'card_number', 'credit_card',
        'bank_account', 'account_number',
        'secret', 'api_key', 'token'
    }

    @classmethod
    def validate_and_sanitize(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str]
    ) -> tuple[List[Dict[str, Any]], ResultValidationResult]:
        """결과 검증 및 정제"""
        # 구현...
```

### Layer 4: User Confirmation

```python
# src/services/ai/security/layer4_user.py

class Layer4UserConfirmation:
    """Layer 4: 사용자 확인 필요 여부 판단"""

    LARGE_RESULT_THRESHOLD = 500
    COMPLEX_JOIN_THRESHOLD = 3

    @classmethod
    def check_confirmation_needed(
        cls,
        sql: str,
        estimated_rows: int | None = None
    ) -> UserConfirmationRequired:
        """사용자 확인 필요 여부 확인"""
        # 구현...
```

### Dependencies

**Prerequisite Stories:**
- Story 2-2: LLM 기반 SQL 생성 에이전트 (SQL 검증 대상)
- Story 2-3: MariaDB 질의 실행 (결과 검증 대상)

**Blocked Stories:**
- Story 3-2: SQL Injection 방지 (Layer 2 확장)
- Story 3-3: 민감 데이터 마스킹 (Layer 3 확장)
- Story 3-4: 감사 로깅 (보안 이벤트 로깅)

### Architecture Requirements

- **AR6**: Layer 1 (Prompt) 시스템 프롬프트에 보안 지침 내장 ✓
- **AR7**: Layer 2 (Validation) SQL 화이트리스트 + 패턴 검증 ✓
- **AR8**: Layer 3 (Result) 결과 내 PII 마스킹, 행 수 제한 ✓
- **AR9**: Layer 4 (User) 위험 쿼리 시 확인 다이얼로그 ✓
- **AR23**: Security 모듈 100% 테스트 커버리지 ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Security-Architecture]
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
