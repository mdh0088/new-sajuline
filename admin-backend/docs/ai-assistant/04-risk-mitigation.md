# AI 관리자 어시스턴트 - 리스크 평가 및 완화 전략

> **문서 버전**: 1.0.0
> **최종 수정**: 2026-01-29
> **상태**: 설계 단계

---

## 1. 개요

AI BI 어시스턴트 개발 및 운영 시 예상되는 리스크와 체계적인 완화 전략을 정의합니다.

---

## 2. 리스크 매트릭스

### 2.1 전체 리스크 요약

| 순위 | 리스크 | 영향도 | 발생확률 | 완화 전략 |
|------|--------|--------|----------|----------|
| 1 | LLM 환각으로 잘못된 SQL 생성 | 🔴 높음 | 중간 | 4중 방어 체계 |
| 2 | MSSQL 2005 호환성 문제 | 🟠 중간 | 높음 | TDS 7.0/7.1 + 호환 쿼리 패턴 |
| 3 | 크로스 DB 조인 성능 저하 | 🟡 중간 | 중간 | 페이지네이션 + 인덱스 활용 |
| 4 | LLM API 비용 초과 | 🟡 중간 | 높음 | 캐싱 + Multi-LLM 전략 |
| 5 | GA4 API 할당량 초과 | 🟢 낮음 | 낮음 | 캐싱 + 배치 조회 |
| 6 | 보안 취약점 (SQL Injection) | 🔴 높음 | 낮음 | SQL 파싱 + 화이트리스트 |
| 7 | 응답 지연 (UX 저하) | 🟡 중간 | 중간 | SSE 스트리밍 + 병렬 실행 |

---

## 3. 상세 리스크 분석 및 완화 전략

### 3.1 🔴 LLM 환각 방지 (4중 방어 체계)

#### 리스크 설명
LLM이 잘못된 SQL을 생성하여 의도하지 않은 데이터 조회, 오류 발생, 또는 잘못된 비즈니스 판단을 유발할 수 있음.

#### 4중 방어 체계

```
┌─────────────────────────────────────────────────────────────────────┐
│                        4중 방어 체계                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: Prompt Engineering                                        │
│  ├── Few-shot 예시로 정확한 SQL 패턴 학습                           │
│  ├── Schema-aware RAG로 테이블/컬럼 정보 주입                       │
│  ├── 명확한 제약조건 프롬프트                                       │
│  └── 도메인 특화 SQL 템플릿 제공                                    │
│                           ↓                                         │
│  Layer 2: SQL 검증 (Pre-Execution)                                  │
│  ├── AST 파싱으로 SELECT만 허용 (sqlparse)                          │
│  ├── 화이트리스트 키워드 검증                                       │
│  ├── 테이블/컬럼 존재 여부 검증 (스키마 메타데이터)                  │
│  ├── 위험 패턴 탐지 (UNION, 서브쿼리 depth, JOIN 개수)              │
│  └── SQL 구문 Lint 검사                                             │
│                           ↓                                         │
│  Layer 3: 결과 검증 (Post-Execution)                                │
│  ├── 결과 row 수 임계값 체크 (MAX_ROWS=1000)                        │
│  ├── 이상치 탐지 (극단적 수치, NULL 비율)                           │
│  ├── 데이터 타입 검증                                               │
│  └── 빈 결과 처리 및 안내                                           │
│                           ↓                                         │
│  Layer 4: 사용자 확인 (Human-in-the-Loop)                           │
│  ├── 생성된 SQL 미리보기 (옵션)                                     │
│  ├── 위험 쿼리 시 확인 요청                                         │
│  ├── 실행 취소 옵션                                                 │
│  └── 피드백 수집 (정확/부정확)                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 구현 예시

```python
# Layer 2: SQL 검증기
class SQLValidator:
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER', 'BY',
        'GROUP', 'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
        'ON', 'AS', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'TOP',
        'DISTINCT', 'BETWEEN', 'IN', 'LIKE', 'IS', 'NULL', 'NOT'
    }

    BLOCKED_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'XP_', 'SP_', 'GRANT',
        'REVOKE', 'DENY', 'SHUTDOWN', 'BACKUP', 'RESTORE'
    }

    def validate(self, sql: str) -> ValidationResult:
        # 1. 키워드 검증
        # 2. AST 파싱
        # 3. 테이블/컬럼 검증
        # 4. 위험 패턴 탐지
        pass
```

---

### 3.2 🟠 MSSQL 2005 호환성

#### 리스크 설명
MSSQL 2005는 최신 SQL 문법을 지원하지 않아 쿼리 실패 또는 예상치 못한 결과 발생 가능.

#### 제한사항 및 해결책

| 제한사항 | 설명 | 해결책 |
|----------|------|--------|
| TDS 프로토콜 | TDS 8.0 미지원 | pymssql + TDS 7.0/7.1 명시 |
| OFFSET/FETCH | 페이지네이션 미지원 | TOP N + 서브쿼리 사용 |
| CTE (WITH 절) | 미지원 | 서브쿼리로 대체 |
| 윈도우 함수 일부 | ROW_NUMBER() 제한적 | 자체 조인으로 구현 |
| TRY_CAST | 미지원 | CAST + 에러 핸들링 |
| EUC-KR 인코딩 | 한글 깨짐 | charset='euc-kr' 설정 |

#### 호환 쿼리 패턴 라이브러리

```python
# MSSQL 2005 호환 쿼리 패턴
MSSQL_2005_PATTERNS = {
    "pagination": """
        SELECT TOP {limit} *
        FROM (
            SELECT TOP {offset + limit} *
            FROM {table}
            ORDER BY {order_by} ASC
        ) AS t
        ORDER BY {order_by} DESC
    """,
    "date_this_month_start": """
        DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
    """,
    "date_this_week_start": """
        DATEADD(WEEK, DATEDIFF(WEEK, 0, GETDATE()), 0)
    """,
}
```

---

### 3.3 🟡 크로스 DB 조인 성능

#### 리스크 설명
두 DB에서 대량 데이터를 조회 후 메모리 내 조인 시 성능 저하 및 메모리 부족 발생 가능.

#### 완화 전략

| 전략 | 설명 | 효과 |
|------|------|------|
| 필터 푸시다운 | 조인 전 각 DB에서 WHERE 조건 적용 | 전송 데이터 감소 |
| 컬럼 프로젝션 | 필요한 컬럼만 SELECT | 메모리 사용 감소 |
| 페이지네이션 | 결과 row 제한 (기본 1000) | OOM 방지 |
| 인덱스 활용 | 조인 키에 인덱스 보장 | 쿼리 속도 향상 |
| 캐싱 | 자주 사용되는 조인 결과 캐싱 | 반복 조회 최적화 |

#### 구현 예시

```python
async def cross_db_join(
    mariadb_query: str,
    mssql_query: str,
    join_key: tuple[str, str],
    max_rows: int = 1000
) -> pd.DataFrame:
    # 병렬 조회
    mariadb_result, mssql_result = await asyncio.gather(
        query_mariadb(f"{mariadb_query} LIMIT {max_rows}"),
        query_mssql(f"SELECT TOP {max_rows} * FROM ({mssql_query}) t")
    )

    # 메모리 조인
    return pd.merge(
        pd.DataFrame(mariadb_result),
        pd.DataFrame(mssql_result),
        left_on=join_key[0],
        right_on=join_key[1],
        how='inner'
    )
```

---

### 3.4 🟡 LLM API 비용 최적화

#### 리스크 설명
GPT-4 등 고비용 모델 과다 사용 시 월 예산 초과 가능.

#### Multi-LLM 전략

```yaml
LLM Tier 구성:
  Primary (복잡한 분석):
    model: gpt-4-turbo / claude-3.5-sonnet
    cost: ~$0.03/1K tokens
    use_case: 크로스 DB 분석, 복잡한 SQL 생성

  Fallback (단순 질의):
    model: gpt-3.5-turbo / gemini-1.5-pro
    cost: ~$0.002/1K tokens
    use_case: 단일 DB 질의, 장애 시 대체

  Budget (전처리):
    model: gemini-1.5-flash
    cost: ~$0.0001/1K tokens
    use_case: 의도 분류, 키워드 추출, 간단한 포맷팅
```

#### 비용 최적화 기법

| 기법 | 설명 | 절감 효과 |
|------|------|----------|
| 질의 분류 | 복잡도에 따라 LLM 티어 선택 | 50-70% |
| 응답 캐싱 | 동일 질의 결과 캐싱 (TTL: 5분) | 30-40% |
| 프롬프트 최적화 | 불필요한 컨텍스트 제거 | 10-20% |
| 배치 처리 | 유사 질의 일괄 처리 | 20-30% |

---

### 3.5 🟢 GA4 API 할당량

#### 리스크 설명
GA4 Data API 무료 할당량 (10,000 requests/day) 초과 시 서비스 중단.

#### 완화 전략

| 전략 | 설명 |
|------|------|
| 적극적 캐싱 | GA4 응답 캐싱 (TTL: 15-30분) |
| 배치 조회 | 여러 지표를 한 번의 API 호출로 |
| 할당량 모니터링 | 사용량 80% 도달 시 알림 |
| 폴백 전략 | 할당량 초과 시 BigQuery Export 활용 |

---

### 3.6 🔴 보안 취약점 (SQL Injection)

#### 리스크 설명
사용자 입력이 SQL에 직접 주입되어 보안 사고 발생 가능.

#### 방어 체계

```
┌─────────────────────────────────────────────────────────────────────┐
│                        보안 방어 체계                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 입력 검증                                                       │
│  ├── 자연어 입력 길이 제한 (MAX: 1000자)                            │
│  ├── 특수문자 필터링 (SQL 예약어 이스케이프)                        │
│  └── 입력 정규화 (공백, 개행 처리)                                  │
│                                                                     │
│  2. SQL 파라미터화                                                  │
│  ├── 모든 값은 파라미터 바인딩 사용                                 │
│  └── 문자열 연결 금지                                               │
│                                                                     │
│  3. DB 권한 제한                                                    │
│  ├── Read-Only 전용 계정 사용                                       │
│  ├── 특정 테이블/뷰만 접근 허용                                     │
│  └── 민감 테이블 접근 차단                                          │
│                                                                     │
│  4. 결과 마스킹                                                     │
│  ├── 비밀번호 필드 자동 마스킹                                      │
│  ├── 주민번호/전화번호 부분 마스킹                                  │
│  └── 민감 컬럼 조회 시 경고                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. 리스크 모니터링

### 4.1 모니터링 대시보드 지표

| 지표 | 임계값 | 알림 조건 |
|------|--------|----------|
| SQL 오류율 | ≤1% | >2% 시 알림 |
| 평균 응답 시간 | ≤5초 | >10초 시 알림 |
| LLM API 비용 | 예산 80% | 80% 도달 시 알림 |
| GA4 API 사용량 | 8,000/일 | 80% 도달 시 알림 |
| 보안 이벤트 | 0건 | 1건 이상 시 즉시 알림 |

### 4.2 정기 점검 항목

| 주기 | 점검 항목 |
|------|----------|
| 일간 | API 비용, 오류 로그, 응답 시간 |
| 주간 | SQL 검증 실패 패턴 분석, 사용자 피드백 |
| 월간 | 보안 감사, 성능 리포트, 비용 최적화 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-29 | 초기 리스크 평가 문서 작성 |
