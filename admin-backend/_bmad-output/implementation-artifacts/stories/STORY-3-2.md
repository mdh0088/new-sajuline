# Story 3.2: SQL Injection 방지 및 테이블 접근 제어

Status: done

## Change Log

- 2026-02-04: Story 3-2 구현 완료 - SQL Injection 탐지, 테이블 접근 제어, 보안 로깅, 퍼징 테스트 (199 tests passed, 100% 차단율 검증)
- 2026-02-04: 코드 리뷰 수정 완료 - Layer2Validator 통합 리팩토링, fuzzing assert 조건 강화, async 주석 추가

## Story

As a 시스템,
I want SQL Injection 공격을 차단하고 금지된 테이블 접근을 방지하기를,
so that 악의적 공격으로부터 데이터가 보호된다.

## Acceptance Criteria

1. SQL Injection 패턴이 탐지되면 요청이 차단된다
   - UNION Injection
   - Tautology (1=1)
   - Comment Injection (-- , /* */)
   - Stacked Queries (;)
   - Time-based Injection (SLEEP, BENCHMARK)
2. 금지된 테이블 접근 시도가 차단된다
   - 블랙리스트 테이블: t_admin, t_user_password 등
   - 시스템 테이블: information_schema, mysql.* 등
3. 차단된 모든 시도가 보안 로그에 기록된다
   - 로그 레벨: WARNING 또는 ERROR
   - 포함 정보: admin_id, 질문, 생성된 SQL, 차단 사유
4. SQL Injection 차단율이 100%이다
   - OWASP Top 10 SQL Injection 패턴 테스트
5. 화이트리스트 외 테이블 접근 차단율이 100%이다

## Tasks / Subtasks

- [x] Task 1: SQL Injection 탐지기 구현 (AC: 1, 4)
  - [x] `src/services/ai/security/injection_detector.py` 생성
  - [x] `SQLInjectionDetector` 클래스 구현
  - [x] `InjectionDetectionResult` 데이터클래스 정의
  - [x] `INJECTION_PATTERNS` OWASP 기반 패턴 정의
  - [x] `detect()` 메서드 구현 (risk_score 계산)
  - [x] 패턴별 위험도 가중치 로직
- [x] Task 2: 테이블 접근 제어 구현 (AC: 2, 5)
  - [x] `src/services/ai/security/table_guard.py` 생성
  - [x] `TableAccessGuard` 클래스 구현
  - [x] `TableAccessResult` 데이터클래스 정의
  - [x] `BLACKLIST_TABLES` 상수 정의
  - [x] `SYSTEM_TABLE_PATTERNS` 정규식 정의
  - [x] `check_access()` 메서드 구현
  - [x] 테이블 추출 로직 `_extract_all_tables()`
- [x] Task 3: 보안 로거 구현 (AC: 3)
  - [x] `src/services/ai/security/security_logger.py` 생성
  - [x] `SecurityLogger` 클래스 구현
  - [x] `log_injection_attempt()` 메서드 구현
  - [x] `log_table_access_denied()` 메서드 구현
  - [x] structlog JSON 포맷 적용
- [x] Task 4: Layer2SQLValidator 통합 리팩토링 (AC: 1-5)
  - [x] Layer2SQLValidator에 injection_detector 통합
  - [x] Layer2SQLValidator에 table_guard 통합
  - [x] 통합 테스트 작성 (test_layer2_security_integration.py)
- [x] Task 5: 보안 퍼징 테스트 작성 (100패턴) (AC: 4, 5)
  - [x] `tests/services/ai/security/fuzzing_patterns.py` 생성
  - [x] OWASP SQL Injection 패턴 120개 정의
  - [x] `tests/services/ai/security/test_injection_detector.py` 생성 (24 tests)
  - [x] `tests/services/ai/security/test_table_guard.py` 생성 (19 tests)
  - [x] `tests/services/ai/security/test_fuzzing_comprehensive.py` 생성 (156 tests)
  - [x] 100% 차단율 검증 테스트 (214 tests passed)
- [x] Task 6: 린팅/타입 체크 통과
  - [x] `black src/services/ai/security/` 실행
  - [x] `isort src/services/ai/security/` 실행
  - [x] `flake8 src/services/ai/security/` 실행
  - [x] `mypy src/services/ai/security/` 실행

## Dev Notes

### Background

Text-to-SQL 시스템은 SQL Injection 공격에 취약할 수 있습니다. 사용자가 악의적인 자연어 질문을 입력하여 시스템을 속이거나, LLM이 실수로 위험한 SQL을 생성할 수 있습니다. 이 스토리에서는 Layer 2 보안을 강화하여 SQL Injection을 100% 차단합니다.

### SQL Injection Detector

```python
# src/services/ai/security/injection_detector.py
from dataclasses import dataclass
from typing import List
import re

@dataclass
class InjectionDetectionResult:
    is_injection: bool
    patterns_detected: List[str]
    risk_score: float  # 0.0 ~ 1.0
    recommendation: str | None = None

class SQLInjectionDetector:
    """SQL Injection 탐지기"""

    # OWASP 기반 Injection 패턴 (29개)
    INJECTION_PATTERNS = {
        # Union-based
        "union_injection": r"UNION\s+(ALL\s+)?SELECT",
        "union_null": r"UNION\s+SELECT\s+NULL",

        # Tautology
        "tautology_numeric": r"(\d+)\s*=\s*\1",  # 1=1
        "tautology_string": r"'([^']+)'\s*=\s*'\1'",  # 'a'='a'
        "tautology_or": r"OR\s+1\s*=\s*1",
        "tautology_always_true": r"OR\s+'[^']*'\s*=\s*'[^']*'",
        "tautology_quote": r"'\s*OR\s+'",  # ' OR '

        # Comment injection
        "comment_inline": r"--[^\n]*",
        "comment_hash": r"#",
        "comment_block": r"/\*.*\*/",

        # Stacked queries
        "stacked_query": r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)",

        # Time-based
        "sleep_injection": r"SLEEP\s*\(\s*\d+\s*\)",
        "benchmark_injection": r"BENCHMARK\s*\(",
        "waitfor_injection": r"WAITFOR\s+DELAY",
        "pg_sleep": r"PG_SLEEP\s*\(",

        # Error-based
        "extractvalue": r"EXTRACTVALUE\s*\(",
        "updatexml": r"UPDATEXML\s*\(",

        # Out-of-band
        "load_file": r"LOAD_FILE\s*\(",
        "into_outfile": r"INTO\s+OUTFILE",
        "into_dumpfile": r"INTO\s+DUMPFILE",

        # Blind injection patterns
        "substring_blind": r"SUBSTRING\s*\([^,]+,\s*\d+,\s*1\s*\)",
        "ascii_blind": r"ASCII\s*\(\s*SUBSTRING",
        "if_blind": r"IF\s*\([^,]+,\s*(SLEEP|BENCHMARK)",

        # System info gathering
        "version_probe": r"@@VERSION|VERSION\s*\(\)",
        "database_probe": r"DATABASE\s*\(\)|SCHEMA\s*\(\)",
        "user_probe": r"CURRENT_USER|SESSION_USER|SYSTEM_USER",
        "system_table_mysql": r"\bmysql\.",
        "system_table_info_schema": r"\binformation_schema\.",

        # Hex encoding bypass
        "hex_encoding": r"0x[0-9a-fA-F]+",
        "char_encoding": r"CHAR\s*\(\s*\d+",
    }

    @classmethod
    def detect(cls, sql: str) -> InjectionDetectionResult:
        """SQL Injection 패턴 탐지"""
        detected_patterns = []
        risk_score = 0.0

        for name, pattern in cls.INJECTION_PATTERNS.items():
            if re.search(pattern, sql, re.IGNORECASE | re.DOTALL):
                detected_patterns.append(name)
                risk_score += cls._get_pattern_weight(name)

        risk_score = min(risk_score, 1.0)
        is_injection = len(detected_patterns) > 0

        recommendation = None
        if is_injection:
            recommendation = "SQL Injection 패턴이 감지되었습니다. 요청이 차단됩니다."

        return InjectionDetectionResult(
            is_injection=is_injection,
            patterns_detected=detected_patterns,
            risk_score=risk_score,
            recommendation=recommendation
        )

    @staticmethod
    def _get_pattern_weight(pattern_name: str) -> float:
        """패턴별 위험도 가중치"""
        high_risk = {
            "union_injection", "stacked_query", "load_file",
            "into_outfile", "into_dumpfile"
        }
        medium_risk = {
            "sleep_injection", "benchmark_injection", "tautology_or",
            "comment_double_dash", "comment_block"
        }

        if pattern_name in high_risk:
            return 0.5
        elif pattern_name in medium_risk:
            return 0.3
        return 0.1
```

### Table Access Guard

```python
# src/services/ai/security/table_guard.py
from typing import Set
from dataclasses import dataclass
import re

@dataclass
class TableAccessResult:
    allowed: bool
    blocked_tables: list[str]
    reason: str | None = None

class TableAccessGuard:
    """테이블 접근 제어"""

    # 절대 접근 금지 테이블 (역할과 무관)
    BLACKLIST_TABLES = {
        # 시스템 테이블
        "information_schema",
        "mysql",
        "performance_schema",
        "sys",

        # 민감 테이블 (슈퍼 관리자 제외 전체 차단)
        "t_admin",
        "t_user_password",
        "t_payment_card",
        "t_user_identity",
        "t_api_keys",
        "t_sessions",
    }

    # 시스템 테이블 패턴
    SYSTEM_TABLE_PATTERNS = [
        r"^mysql\.",
        r"^information_schema\.",
        r"^performance_schema\.",
        r"^sys\.",
    ]

    @classmethod
    def check_access(
        cls,
        sql: str,
        allowed_tables: Set[str],
        is_super_admin: bool = False
    ) -> TableAccessResult:
        """테이블 접근 권한 확인"""
        tables_in_sql = cls._extract_all_tables(sql)
        blocked_tables = []

        for table in tables_in_sql:
            table_lower = table.lower()

            # 1. 시스템 테이블 패턴 체크
            for pattern in cls.SYSTEM_TABLE_PATTERNS:
                if re.match(pattern, table_lower):
                    blocked_tables.append(table)
                    continue

            # 2. 블랙리스트 체크
            if table_lower in cls.BLACKLIST_TABLES:
                if not is_super_admin or table_lower in {
                    "t_user_password", "t_payment_card", "t_user_identity"
                }:
                    blocked_tables.append(table)
                    continue

            # 3. 화이트리스트 체크
            if table_lower not in {t.lower() for t in allowed_tables}:
                blocked_tables.append(table)

        if blocked_tables:
            return TableAccessResult(
                allowed=False,
                blocked_tables=blocked_tables,
                reason=f"접근이 허용되지 않은 테이블: {', '.join(blocked_tables)}"
            )

        return TableAccessResult(allowed=True, blocked_tables=[])

    @staticmethod
    def _extract_all_tables(sql: str) -> Set[str]:
        """SQL에서 모든 테이블 참조 추출"""
        tables = set()

        from_matches = re.findall(
            r'FROM\s+([`"\[]?\w+[`"\]]?(?:\.[`"\[]?\w+[`"\]]?)?)',
            sql, re.IGNORECASE
        )
        tables.update(from_matches)

        join_matches = re.findall(
            r'JOIN\s+([`"\[]?\w+[`"\]]?(?:\.[`"\[]?\w+[`"\]]?)?)',
            sql, re.IGNORECASE
        )
        tables.update(join_matches)

        cleaned = set()
        for t in tables:
            cleaned.add(re.sub(r'[`"\[\]]', '', t))

        return cleaned
```

### Security Logger

```python
# src/services/ai/security/security_logger.py
import structlog
from datetime import datetime
from typing import Any

logger = structlog.get_logger()

class SecurityLogger:
    """보안 이벤트 로거"""

    @staticmethod
    async def log_injection_attempt(
        admin_id: int,
        question: str,
        generated_sql: str,
        patterns_detected: list[str],
        risk_score: float
    ):
        """SQL Injection 시도 로깅"""
        logger.warning(
            "sql_injection_detected",
            event_type="SECURITY_INJECTION",
            admin_id=admin_id,
            question=question[:200],
            sql_preview=generated_sql[:500],
            patterns=patterns_detected,
            risk_score=risk_score,
            timestamp=datetime.utcnow().isoformat(),
            severity="HIGH"
        )

    @staticmethod
    async def log_table_access_denied(
        admin_id: int,
        question: str,
        blocked_tables: list[str]
    ):
        """테이블 접근 거부 로깅"""
        logger.warning(
            "table_access_denied",
            event_type="SECURITY_ACCESS_DENIED",
            admin_id=admin_id,
            question=question[:200],
            blocked_tables=blocked_tables,
            timestamp=datetime.utcnow().isoformat(),
            severity="MEDIUM"
        )
```

### 퍼징 테스트 데이터

```python
# tests/services/ai/security/fuzzing_patterns.py
INJECTION_TEST_PATTERNS = [
    # UNION
    "SELECT * FROM users UNION SELECT * FROM admin",
    "1 UNION ALL SELECT NULL,NULL,NULL--",

    # Tautology
    "1' OR '1'='1",
    "admin'--",
    "1 OR 1=1",

    # Comment
    "SELECT * FROM users--",
    "SELECT * FROM users/**/WHERE 1=1",

    # Time-based
    "1; SLEEP(10)--",
    "1' AND SLEEP(10)--",

    # Stacked
    "1; DROP TABLE users--",
    "1'; INSERT INTO admin VALUES('hacker')--",

    # ... 100개 이상
]
```

### Dependencies

**Prerequisite Stories:**
- Story 3-1: 4-Layer Security 프레임워크 (기본 구조)

**Blocked Stories:**
- 없음

### Architecture Requirements

- **FR14**: SQL Injection 차단 ✓
- **FR15**: 금지 테이블 접근 차단 ✓
- **NFR-S1**: SQL Injection 차단율 100% ✓
- **NFR-S3**: 민감 테이블 접근 차단 100% ✓
- **NFR-S7**: 보안 이벤트 로깅 ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Security-Architecture]
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (model ID: claude-sonnet-4-5-20250929)

### Debug Log References

없음 - 모든 테스트 첫 실행 시 통과

### Completion Notes List

**Task 1: SQL Injection 탐지기 구현 완료**
- OWASP Top 10 기반 SQL Injection 패턴 29개 정의
- InjectionDetectionResult 데이터클래스 (is_injection, patterns_detected, risk_score, recommendation)
- SQLInjectionDetector.detect() 메서드 구현
- 패턴별 위험도 가중치 (High: 0.5, Medium: 0.3, Low: 0.1)
- 24개 단위 테스트 작성 및 통과

**Task 2: 테이블 접근 제어 구현 완료**
- 블랙리스트 테이블 정의 (t_admin, t_user_password, t_payment_card, 시스템 테이블 등)
- TableAccessGuard.check_access() 메서드 구현
- 시스템 테이블 패턴 차단 (mysql.*, information_schema.* 등)
- 슈퍼 관리자 예외 처리 (일부 민감 테이블은 슈퍼 관리자도 차단)
- 19개 단위 테스트 작성 및 통과

**Task 3: 보안 로거 구현 완료**
- SecurityLogger.log_injection_attempt() 구현
- SecurityLogger.log_table_access_denied() 구현
- structlog 기반 JSON 구조화 로깅
- 타임스탬프, severity, admin_id 등 필수 필드 포함
- 6개 단위 테스트 작성 및 통과

**Task 4: Layer2SQLValidator 통합 리팩토링 완료**
- Layer2SQLValidator가 injection_detector와 table_guard를 직접 호출하도록 리팩토링
- 기존 중복 패턴 제거 및 Story 3-2 모듈 통합
- 9개 통합 테스트 작성 및 통과
- 코드 리뷰 후 추가 개선: 유지보수성 및 코드 중복 제거

**Task 5: 보안 퍼징 테스트 완료**
- OWASP 기반 SQL Injection 패턴 120개 정의 (fuzzing_patterns.py)
- 블랙리스트 테이블 접근 패턴 12개 정의
- 156개 파라미터화 퍼징 테스트 작성 및 100% 통과
- SQL Injection 차단율 100% 검증 완료
- 테이블 접근 차단율 100% 검증 완료
- 총 199개 테스트 통과 (24 + 19 + 156)

**Task 6: 린팅/타입 체크 완료**
- black 포매팅 4개 파일 적용
- isort import 정렬 3개 파일 적용
- flake8 린팅 통과 (새로 작성한 파일)
- mypy strict 타입 체크 통과 (3개 파일)

### File List

**생성된 파일:**
- src/services/ai/security/injection_detector.py
- src/services/ai/security/table_guard.py
- src/services/ai/security/security_logger.py
- tests/services/ai/security/test_injection_detector.py
- tests/services/ai/security/test_table_guard.py
- tests/services/ai/security/test_security_logger.py
- tests/services/ai/security/test_layer2_security_integration.py
- tests/services/ai/security/fuzzing_patterns.py
- tests/services/ai/security/test_fuzzing_comprehensive.py

**수정된 파일:**
- src/services/ai/security/layer2_validator.py (통합 리팩토링: injection_detector, table_guard 모듈 사용)
- tests/services/ai/security/fuzzing_patterns.py (assert 조건 강화: 100+ → 120+)
