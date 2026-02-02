# Story 2.3: MariaDB 질의 실행 및 허용 필터링

Status: ready-for-dev

## Story

As a 시스템,
I want 생성된 SQL을 MariaDB에서 실행하고 허용된 테이블만 접근하기를,
so that 안전하게 데이터를 조회할 수 있다.

## Acceptance Criteria

1. MariaDB 에이전트가 SQL을 실행한다
   - aiomysql 비동기 드라이버 사용
   - 기존 `get_db()` 연결 재사용 또는 전용 풀 생성
2. 화이트리스트 테이블/컬럼만 접근이 허용된다
   - 사전 정의된 테이블 목록
   - 역할별 허용 테이블 (Story 1-3 연동)
3. 허용되지 않은 테이블 접근 시 에러가 반환된다
   - 에러 코드: `AIBI_TABLE_NOT_ALLOWED`
   - 접근 시도 로깅
4. 쿼리 결과 행 수가 1000개로 제한된다
   - 초과 시 결과 truncate + 경고 메시지
   - 전체 행 수 정보 제공
5. 연결 풀이 5-20 connections로 관리된다
   - min_size: 5, max_size: 20
   - 연결 누수 방지 (context manager)

## Tasks / Subtasks

- [ ] Task 1: MariaDB 에이전트 구현 (AC: 1, 4)
  - [ ] `src/services/ai/agents/mariadb_agent.py` 생성
  - [ ] `MariaDBAgent` 클래스 구현
  - [ ] `QueryResult` 데이터클래스 정의
  - [ ] `execute_query()` 비동기 메서드 구현
  - [ ] LIMIT 절 확인/추가 로직
  - [ ] 쿼리 타임아웃 (30초) 구현
- [ ] Task 2: 연결 풀 관리자 구현 (AC: 5)
  - [ ] `src/services/ai/tools/mariadb_tool.py` 생성
  - [ ] `MariaDBConnectionPool` 클래스 구현
  - [ ] 싱글톤 패턴 적용
  - [ ] Context manager 지원
- [ ] Task 3: 화이트리스트 설정 구현 (AC: 2, 3)
  - [ ] `src/services/ai/config/table_whitelist.py` 생성
  - [ ] `BASE_ALLOWED_TABLES` 상수 정의
  - [ ] `SENSITIVE_TABLES` 상수 정의
  - [ ] `get_allowed_tables()` 함수 구현
- [ ] Task 4: 테이블 접근 권한 검증 (AC: 3)
  - [ ] 테이블 추출 로직 (SQLValidator 재사용)
  - [ ] 허용되지 않은 테이블 에러 처리
  - [ ] 접근 시도 로깅
- [ ] Task 5: 단위 테스트 작성 (AC: 1-5)
  - [ ] `tests/services/ai/unit/test_mariadb_agent.py` 생성
  - [ ] 테이블 접근 권한 테스트
  - [ ] 행 수 제한 테스트
  - [ ] 연결 풀 동작 테스트
- [ ] Task 6: 통합 테스트 작성
  - [ ] 실제 DB 연결 테스트
  - [ ] 타임아웃 테스트
- [ ] Task 7: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

Story 2-2에서 생성된 SQL을 실제 MariaDB에서 실행하고 결과를 반환합니다. 보안을 위해 화이트리스트 테이블/컬럼만 접근을 허용하고, 결과 행 수를 제한합니다.

### MariaDB Agent

```python
# src/services/ai/agents/mariadb_agent.py
from typing import List, Dict, Any
from dataclasses import dataclass
import aiomysql

@dataclass
class QueryResult:
    success: bool
    data: List[Dict[str, Any]] | None = None
    columns: List[str] | None = None
    row_count: int = 0
    total_count: int | None = None
    truncated: bool = False
    error_code: str | None = None
    error_message: str | None = None
    execution_time_ms: int = 0

class MariaDBAgent:
    """MariaDB 질의 실행 에이전트"""

    MAX_ROWS = 1000
    QUERY_TIMEOUT = 30  # 초

    def __init__(self, pool: aiomysql.Pool):
        self.pool = pool

    async def execute_query(
        self,
        sql: str,
        allowed_tables: set[str],
        max_rows: int | None = None
    ) -> QueryResult:
        """SQL 실행 및 결과 반환"""
        # 구현...
```

### Connection Pool Manager

```python
# src/services/ai/tools/mariadb_tool.py
import aiomysql
from contextlib import asynccontextmanager

class MariaDBConnectionPool:
    """MariaDB 연결 풀 관리"""

    _pool: aiomysql.Pool | None = None

    @classmethod
    async def get_pool(cls) -> aiomysql.Pool:
        """연결 풀 반환 (싱글톤)"""
        if cls._pool is None:
            cls._pool = await aiomysql.create_pool(
                host=settings.maria_host,
                port=settings.maria_port,
                user=settings.maria_user,
                password=settings.maria_password,
                db=settings.maria_database,
                minsize=5,
                maxsize=20,
                autocommit=True,
                charset='utf8mb4',
                connect_timeout=10,
            )
        return cls._pool
```

### Table Whitelist Configuration

```python
# src/services/ai/config/table_whitelist.py

BASE_ALLOWED_TABLES: Set[str] = {
    "t_payment",
    "t_user",
    "t_counselor",
    "t_order",
    "t_consultation",
    "t_mileage",
    "t_point_transaction",
    "t_notice",
    "t_banner",
}

SENSITIVE_TABLES: Set[str] = {
    "t_admin",
    "t_user_password",
    "t_payment_card",
    "t_user_identity",
}

def get_allowed_tables(role: AIRole) -> Set[str]:
    """역할별 허용 테이블 목록 반환"""
    tables = BASE_ALLOWED_TABLES.copy()
    tables.update(ROLE_EXTRA_TABLES.get(role, set()))
    return tables
```

### Edge Cases

- **빈 결과**: 정상 응답, `data: []`, 친절한 메시지
- **연결 풀 고갈**: 대기 후 타임아웃, 적절한 에러 메시지
- **SQL 실행 에러**: 문법 오류, 존재하지 않는 컬럼 등 → 사용자 친화적 메시지
- **트랜잭션**: SELECT only이므로 트랜잭션 불필요 (autocommit)

### Dependencies

**Prerequisite Stories:**
- Story 1-3: 역할 기반 접근 제어 설정 (허용 테이블 목록)
- Story 2-2: LLM 기반 SQL 생성 에이전트 (SQL 입력)

**Blocked Stories:**
- Story 2-4: 자연어 응답 생성 및 결과 포맷팅 (쿼리 결과 필요)
- Story 7-1: MSSQL 에이전트 구현 (유사한 패턴으로 구현)

### DB 계정 권한 설정

```sql
-- AI BI 전용 읽기 전용 계정 생성
CREATE USER 'ai_bi_maria_ro'@'%' IDENTIFIED BY 'secure_password';

-- SELECT 권한만 부여 (특정 테이블)
GRANT SELECT ON sajuline.t_payment TO 'ai_bi_maria_ro'@'%';
GRANT SELECT ON sajuline.t_user TO 'ai_bi_maria_ro'@'%';
-- ... 기타 허용 테이블

FLUSH PRIVILEGES;
```

### Architecture Requirements

- **FR7**: MariaDB 조회 ✓
- **FR9**: 허용 테이블/컬럼만 조회 ✓
- **NFR-I1**: 연결 풀 크기 5-20 ✓
- **NFR-R4**: 연결 누수 0건 (context manager 사용)

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#DB-Integration]
- [Source: _bmad-output/project-context.md#Database-Patterns]

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
