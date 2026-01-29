# AI 관리자 어시스턴트 - 제약사항 및 비즈니스 규칙

> **문서 버전**: 1.0.0
> **최종 수정**: 2026-01-29
> **상태**: 설계 단계

---

## 1. 기술적 제약사항

### 1.1 Constraint Map 개요

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🚧 CONSTRAINT MAP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔴 CRITICAL                                                                │
│  • 데이터 진실의 원천 (Truth Source) 규칙                                   │
│  • 읽기 전용 (SELECT만 허용)                                                │
│                                                                             │
│  🟠 HIGH                                                                    │
│  • EUC-KR 인코딩 (MSSQL 레거시 데이터)                                      │
│  • MSSQL 2005 SQL 문법 제한                                                 │
│                                                                             │
│  🟡 MEDIUM                                                                  │
│  • Async/Sync 혼합 처리                                                     │
│  • 크로스 DB 조인 성능                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 🔴 CRITICAL: 데이터 진실의 원천 (Truth Source)

| 데이터 유형 | 진실의 원천 | 테이블 | 비고 |
|------------|------------|--------|------|
| **상담사 실시간 상태** | MSSQL | `tm60_member.m_state` | MariaDB는 실시간 아님 |
| **상담 로그/시간/포인트** | MSSQL | `tm60_chatlog` | 핵심 데이터 |
| **매출/결제** | MariaDB | `t_payment` | |
| **유저 프로필** | MariaDB | `t_user` | |
| **상담사 프로필** | MariaDB | `t_counselor` | 상태 제외 |

#### 상담사 상태 코드 (tm60_member.m_state)

| 코드 | 의미 | 설명 |
|------|------|------|
| `1` | 대기중 | 상담 가능 상태 |
| `2` | 상담중 | 현재 통화 중 |
| `3` | 부재중 | 오프라인/휴식 |

---

### 1.3 🟠 HIGH: EUC-KR 인코딩 (MSSQL 레거시)

**영향받는 필드:**
- `tm60_users.u_kname` - 유저 한글 이름
- `tm60_member.m_name` - 상담사 실명
- `tm60_member.m_nickname` - 상담사 닉네임

**해결 방안:**
```python
# pymssql 연결 시 charset 설정
connect_args = {
    "tds_version": "7.0",  # MSSQL 2005 호환
    "charset": "euc-kr",
    "login_timeout": 30,
    "timeout": 30
}
```

---

### 1.4 🟠 HIGH: MSSQL 2005 SQL 문법 제한

#### 지원되지 않는 문법

| 문법 | 대체 방안 |
|------|----------|
| `OFFSET ... FETCH` | `TOP N` 사용 |
| `CTE (WITH 절)` | 서브쿼리로 대체 |
| 일부 윈도우 함수 | 서브쿼리/자체 조인 |
| `TRY_CAST` | `CAST` + 에러 핸들링 |

#### 날짜 처리 패턴 (MSSQL 2005 호환)

```sql
-- 이번 달 시작
DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)

-- 이번 달 끝
DATEADD(SECOND, -1, DATEADD(DAY, 1, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0) - 1))

-- 오늘 시작
DATEADD(DAY, DATEDIFF(DAY, 0, GETDATE()), 0)

-- 이번 주 시작 (월요일)
DATEADD(WEEK, DATEDIFF(WEEK, 0, GETDATE()), 0)
```

---

### 1.5 🟡 MEDIUM: Async/Sync 혼합 처리

| DB | 연결 방식 | 드라이버 |
|----|----------|----------|
| MariaDB | **비동기** | `aiomysql` |
| MSSQL 2005 | **동기** | `pymssql` |

**해결 방안:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

async def query_mssql(query: str):
    """동기 MSSQL 쿼리를 비동기로 래핑"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, sync_mssql_query, query)
```

---

## 2. tm60_chatlog 테이블 상세

### 2.1 핵심 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `m_code` | VARCHAR(3) | 상담사 코드 (조인 키) |
| `u_id` | VARCHAR(50) | 유저 ID (조인 키) |
| `chatstart` | DATETIME | 상담 시작 시간 |
| `chatend` | DATETIME | 상담 종료 시간 |
| `chattm` | INT | **상담 시간 (초 단위)** ★핵심★ |

### 2.2 상담시간 계산 쿼리 (MSSQL 2005 호환)

```sql
-- 특정 상담사의 이번 달 총 상담시간 계산
SELECT
    CAST(FLOOR(SUM(chattm) / 3600) AS VARCHAR(10)) + ':' +
    RIGHT('0' + CAST((SUM(chattm) % 3600) / 60 AS VARCHAR(2)), 2) + ':' +
    RIGHT('0' + CAST(SUM(chattm) % 60 AS VARCHAR(2)), 2) AS total_time
FROM
    tm60_chatlog
WHERE
    m_code = @counselor_code
    AND chatstart >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
    AND chatend <= DATEADD(SECOND, -1, DATEADD(DAY, 1,
        DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0) - 1));
```

### 2.3 상담시간 변환 공식

```
chattm (초) → 시:분:초 변환

시간(hour) = FLOOR(chattm / 3600)
분(minute) = (chattm % 3600) / 60
초(second) = chattm % 60

예: 5765초 → 1:36:05
```

---

## 3. 크로스 DB 조인 키

### 3.1 조인 매핑

```
┌─────────────── MariaDB ───────────────┐     ┌─────────────── MSSQL ───────────────┐
│                                       │     │                                     │
│  t_counselor.counselor_code ◄─────────┼─────┼──► tm60_member.m_code               │
│                                       │     │                                     │
│  t_user.user_id ◄─────────────────────┼─────┼──► tm60_users.u_id                  │
│                                       │     │                                     │
│                                       │     │  tm60_chatlog.m_code (상담사)       │
│                                       │     │  tm60_chatlog.u_id (유저)           │
└───────────────────────────────────────┘     └─────────────────────────────────────┘
```

### 3.2 크로스 조인 예시 (pandas)

```python
import pandas as pd

# MariaDB에서 상담사 정보 조회
counselors_df = pd.DataFrame(mariadb_result)

# MSSQL에서 상담 로그 조회
chatlogs_df = pd.DataFrame(mssql_result)

# 메모리 내 조인
merged_df = pd.merge(
    counselors_df,
    chatlogs_df,
    left_on='counselor_code',
    right_on='m_code',
    how='inner'
)
```

---

## 4. 비즈니스 규칙

### 4.1 데이터 소스 라우팅 규칙

| 질의 키워드 | 데이터 소스 | 테이블 |
|------------|------------|--------|
| 매출, 결제, 충전 | MariaDB | `t_payment` |
| 유저 정보, 프로필 | MariaDB | `t_user` |
| 상담사 프로필, 등급 | MariaDB | `t_counselor` |
| **상담사 상태 (실시간)** | **MSSQL** | `tm60_member.m_state` |
| 상담 시간, 상담 로그 | MSSQL | `tm60_chatlog` |
| 포인트 사용 내역 | MSSQL | `tm60_chatlog` |
| 상담사별 성과 분석 | 크로스 조인 | MariaDB + MSSQL |

### 4.2 결제 상태 코드

| 코드 | 의미 | 집계 포함 |
|------|------|----------|
| `SUCCESS` | 결제 완료 | ✅ 포함 |
| `PENDING` | 결제 대기 | ❌ 제외 |
| `FAILED` | 결제 실패 | ❌ 제외 |
| `CANCELLED` | 결제 취소 | ❌ 제외 |

### 4.3 기본 날짜 범위 규칙

| 표현 | 범위 |
|------|------|
| "오늘" | 오늘 00:00:00 ~ 23:59:59 |
| "어제" | 어제 00:00:00 ~ 23:59:59 |
| "이번 주" | 이번 주 월요일 ~ 오늘 |
| "이번 달" | 이번 달 1일 ~ 오늘 |
| "지난 달" | 지난 달 1일 ~ 말일 |
| **범위 미지정** | **최근 7일 (기본값)** |

### 4.4 집계 기본값 규칙

| 항목 | 기본값 |
|------|--------|
| TOP N 미지정 | 상위 10개 |
| 금액 단위 | 원(₩), 천 단위 콤마 |
| 상담시간 단위 | chattm 초 → 시:분:초 변환 |
| 정렬 미지정 | 최신순 (날짜 내림차순) |

### 4.5 후속 분석 제안 규칙

| 조회 결과 | 자동 제안 |
|----------|----------|
| 매출 감소 감지 | "어떤 상담사 매출이 감소했는지 볼까요?" |
| 상담시간 이상치 | "평균 대비 상담시간이 긴/짧은 상담사 확인할까요?" |
| 특정 유저 조회 | "이 유저의 상담 이력/결제 패턴 볼까요?" |
| 기간 데이터 조회 | "전주/전월 대비 비교할까요?" |
| 상담사 성과 조회 | "시간당 매출 효율을 계산할까요?" |

---

## 5. 보안 규칙

### 5.1 금지 규칙 (필수)

```
🔴 절대 금지:
├── SELECT 외 모든 SQL 문 (INSERT, UPDATE, DELETE)
├── DDL 문 (CREATE, DROP, ALTER, TRUNCATE)
├── 비밀번호 필드 조회 (password_hash, m_passwd 등)
├── 시스템 테이블 조회 (sys.*, information_schema.*)
└── UNION을 이용한 다른 테이블 접근 시도
```

### 5.2 SQL 화이트리스트 검증

```python
ALLOWED_KEYWORDS = {'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER', 'BY',
                    'GROUP', 'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
                    'ON', 'AS', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'TOP',
                    'DISTINCT', 'BETWEEN', 'IN', 'LIKE', 'IS', 'NULL', 'NOT',
                    'CAST', 'CONVERT', 'DATEADD', 'DATEDIFF', 'GETDATE',
                    'FLOOR', 'RIGHT', 'ISNULL', 'COALESCE'}

BLOCKED_KEYWORDS = {'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
                    'TRUNCATE', 'EXEC', 'EXECUTE', 'XP_', 'SP_', 'GRANT',
                    'REVOKE', 'DENY', 'SHUTDOWN', 'BACKUP', 'RESTORE'}

BLOCKED_FIELDS = {'password_hash', 'password', 'm_passwd', 'u_passwd',
                  'secret_key', 'api_key', 'token'}
```

---

## 6. LLM 환경변수 설정

### 6.1 .env 추가 설정

```bash
# =============================================================================
# AI Assistant 설정
# =============================================================================

# LLM 제공자 선택: openai | gemini | claude
AI_LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview

# Google Gemini
GOOGLE_API_KEY=AIzaxxxxx
GEMINI_MODEL=gemini-1.5-pro

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# 공통 LLM 설정
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=4096
AI_TIMEOUT=60

# RAG 설정
AI_EMBEDDING_MODEL=text-embedding-3-small
AI_VECTOR_DB_PATH=./data/vectordb

# 보안 설정
AI_MAX_QUERY_LENGTH=1000
AI_RATE_LIMIT_PER_MINUTE=30
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-29 | 초기 제약사항 문서 작성 |
