# Backend DI 리팩토링 계획서

> **문서 버전**: 1.2 (2026-01-27)
> **상태**: 검토 대기

## Executive Summary

### 문제 요약
- **16개 API 파일**에 **97개 이상의 DI 함수**가 분산 정의됨
- **40개 이상의 중복 정의** 발견 (동일 함수가 여러 파일에 존재)
- **5개 서비스**에서 의존성 버전 불일치로 인한 **잠재적 런타임 오류** 발견
- **MSSQL 세션 누수 위험**이 있는 패턴이 5개 파일에서 사용 중

### 해결 방안
- FastAPI 네이티브 `Depends()` + `Annotated` 타입 alias 패턴 채택
- 중앙화된 `dependencies.py` 모듈 생성
- 서비스별 **표준 의존성 정의** 확립

### 예상 효과
- **~700줄 코드 제거**, **~350줄 순감소**
- 6개 Critical/High 버그 수정
- 유지보수성 대폭 향상

### 위험 요소 (반드시 확인)
| 위험도 | 항목 | 영향 |
|-------|------|------|
| 🔴 Critical | MSSQL 세션 누수 | 커넥션 풀 고갈 |
| 🔴 Critical | UserService/GradeService 불일치 | 기능 불완전 |
| 🟠 High | Sync/Async 경계 위반 | 이벤트 루프 블로킹 |

---

## 목차
1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조](#2-목표-구조)
3. [마이그레이션 단계](#3-마이그레이션-단계)
4. [상세 작업 내용](#4-상세-작업-내용)
5. [테스트 전략](#5-테스트-전략)
6. [롤백 계획](#6-롤백-계획)
7. [예상 효과](#7-예상-효과)

---

## 1. 현재 상태 분석

### 1.1 파일 현황

| 구분 | 파일 수 | 위치 |
|-----|--------|-----|
| API 파일 | 16개 | `backend/src/api/v1/*.py` |
| Repository | 21개 | `backend/src/repositories/*.py` (+ ars/ 하위) |
| Service | 25개 | `backend/src/services/*.py` (+ ars/ 하위) |
| Core | 3개 | `backend/src/core/*.py` |

### 1.2 중복 DI 함수 현황 (정밀 분석 결과)

**총 DI 함수 정의**: 97개 이상
**중복 정의**: 40개 이상

| DI 함수 | 정의된 파일 수 | 파일 목록 |
|--------|--------------|----------|
| `get_user_repository()` | 4개 | user_api, payment_api, counselor_api, inquiry_api |
| `get_auth_service()` | 6개 | auth_api, user_api, payment_api, counselor_api, exhibition_api, grade_api |
| `get_notification_repository()` | 5개 | notification_api, user_api, payment_api, counselor_api, inquiry_api |
| `get_notification_service()` | 5개 | notification_api, user_api, payment_api, counselor_api, inquiry_api |
| `get_counselor_repository()` | 4개 | counselor_api, user_api, payment_api, counselor_application_api |
| `get_tm60_users_service()` | 5개 | user_api, payment_api, counselor_api, exhibition_api, consultation_review_api |
| `get_grade_repository()` | 4개 | grade_api, user_api, payment_api, counselor_api |
| `get_point_transaction_repository()` | 3개 | user_api, payment_api, mileage_api |
| `get_tm60_users_repository()` | 4개 | user_api, payment_api, counselor_api, exhibition_api |

### 1.2.1 API 파일별 DI 함수 수

| API 파일 | DI 함수 수 | 복잡도 |
|---------|----------|-------|
| user_api.py | 23개 | 🔴 최고 |
| counselor_api.py | 15개 | 🟠 높음 |
| payment_api.py | 11개 | 🟠 높음 |
| consultation_review_api.py | 10개 | 🟡 중간 |
| inquiry_api.py | 9개 | 🟡 중간 |
| auth_api.py | 8개 | 🟡 중간 |
| counselor_application_api.py | 7개 | 🟡 중간 |
| grade_api.py | 5개 | 🟢 낮음 |
| mileage_api.py | 5개 | 🟢 낮음 |
| exhibition_api.py | 4개 | 🟢 낮음 |
| notice_api.py | 2개 | 🟢 낮음 |
| banner_api.py | 2개 | 🟢 낮음 |
| promotion_api.py | 2개 | 🟢 낮음 |
| point_product_api.py | 2개 | 🟢 낮음 |

**총 중복 코드량**: ~650줄 이상

### 1.3 발견된 문제점

#### A. 동일 파일 내 중복 정의 (버그)
```python
# user_api.py - 라인 190-193
def get_tm60_chatlog_repository():
    for mssql_session in get_db_mssql():
        return Tm60ChatlogRepository(mssql_session)

# user_api.py - 라인 230-232 (동일 함수 중복!)
def get_tm60_chatlog_repository():
    for mssql_session in get_db_mssql():
        return Tm60ChatlogRepository(mssql_session)
```

#### B. 동일 서비스의 다른 구성
```python
# user_api.py - 전체 의존성 체인 사용
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
    event_service: EventService = Depends(get_event_service),
    activity_log_service: UserActivityLogService = Depends(get_user_activity_log_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> UserService:
    return UserService(user_repo, counselor_repo, auth_service, ...)

# payment_api.py - 단순화된 버전 (불일치!)
def get_user_service(db: AsyncSession = Depends(get_db_maria)) -> UserService:
    return UserService(UserRepository(db), CounselorRepository(db), AuthService())
```

#### C. 비표준 MSSQL 세션 패턴
```python
# for loop을 사용한 generator 소비 (비표준)
def get_tm60_users_service():
    for mssql_session in get_db_mssql():
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)
```

#### D. 네이밍 불일치
```python
# banner_api.py - 제네릭 이름
def get_repo(...) -> BannerRepository:
def get_service(...) -> BannerService:

# grade_api.py - 명시적 이름
def get_grade_repository(...) -> GradeRepository:
def get_grade_service(...) -> GradeService:
```

#### E. GradeService 버전 불일치 (신규 발견)
```python
# grade_api.py - 3개 의존성
def get_grade_service(
    grade_repo: GradeRepository = Depends(get_grade_repository),
    grade_change_log_repo: GradeChangeLogRepository = Depends(get_grade_change_log_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> GradeService:
    return GradeService(grade_repo, grade_change_log_repo, auth_service)

# user_api.py - 1개 의존성만 (불완전!)
def get_grade_service(
    grade_repo: GradeRepository = Depends(get_grade_repository)
) -> GradeService:
    return GradeService(grade_repo)  # 🚨 grade_change_log_repo, auth_service = None
```

#### F. CounselorApplicationService 버전 불일치 (신규 발견)
```python
# counselor_application_api.py - 표준 DI 패턴
def get_counselor_application_service(
    repo: CounselorApplicationRepository = Depends(get_counselor_application_repository)
) -> CounselorApplicationService:
    return CounselorApplicationService(repo)

# counselor_api.py - 직접 세션 전달 패턴 (비표준)
def get_counselor_application_service(
    db: AsyncSession = Depends(get_db_maria)
) -> CounselorApplicationService:
    return CounselorApplicationService(CounselorApplicationRepository(db))
```

#### G. CounselorStatusService 비표준 팩토리 패턴 (신규 발견)
```python
# counselor_api.py - 세션을 직접 전달하는 특이한 패턴
def get_counselor_status_service(
    db: AsyncSession = Depends(get_db_maria)
) -> CounselorStatusService:
    return CounselorStatusService(db)  # Repository가 아닌 session 직접 전달
```

#### H. Repository에서 직접 Commit/Rollback (Anti-Pattern, 신규 발견)
```python
# tm60_member_repository.py (lines 58, 60, 78, 80, 98, 100)
def _sync_update_member(self):
    try:
        self.mssql_session.flush()
        self.mssql_session.commit()   # 🚨 Repository에서 직접 commit
    except Exception:
        self.mssql_session.rollback()  # 🚨 Repository에서 직접 rollback
        raise

# tm60_users_repository.py (line 76, 78)
def _sync_update_user_points(self):
    self.mssql_session.flush()
    self.mssql_session.commit()  # 🚨 서비스 레이어의 트랜잭션 제어 불가
```

#### I. Sync 메서드를 Async 컨텍스트에서 잘못 호출 (신규 발견)
```python
# counselor_service.py (line 241, 247)
async def get_counselor_list(...):
    counselors = self.tm60_member_repository.get_all()  # 🚨 sync 호출 (await 없음)
    # ...
    self.tm60_member_repository.update_status(...)  # 🚨 sync 호출 (await 없음)

# 올바른 패턴:
async def get_counselor_list(...):
    counselors = await asyncio.to_thread(self.tm60_member_repository.get_all)
```

### 1.4 현재 데이터베이스 구조

```python
# MariaDB (비동기) - 주 데이터베이스
async def get_db_maria() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# MSSQL (동기) - 외부 ARS 시스템
def get_db_mssql() -> Generator[Session, None, None]:
    db = MSSQLSessionLocal()
    yield db
```

---

## 1.5 위험 요소 분석 (Critical Review)

### 🔴 Critical: MSSQL 세션 생명주기 문제

현재 MSSQL 서비스 DI 패턴에 **심각한 세션 누수 위험**이 있습니다.

#### 문제 코드
```python
# payment_api.py, user_api.py, counselor_api.py 등에서 사용
def get_tm60_users_service():
    for mssql_session in get_db_mssql():  # generator 순회
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)  # 🚨 첫 번째 yield 후 즉시 return
```

#### 왜 문제인가?
```python
# database.py의 get_db_mssql()
def get_db_mssql() -> Generator[Session, None, None]:
    db = MSSQLSessionLocal()
    try:
        yield db
        db.commit()  # 🚨 for loop에서 return하면 여기 도달 안 함
    except Exception:
        db.rollback()
    finally:
        db.close()  # 🚨 for loop에서 return하면 finally 실행 안 됨!
```

- `for` 루프에서 `return`하면 generator가 완전히 소비되지 않음
- `finally` 블록의 `db.close()`가 **호출되지 않을 수 있음**
- 결과: **DB 커넥션 풀 고갈** 가능성

#### 현재 동작하는 이유 (우연)
- Repository 메서드 내에서 직접 `commit()`/`close()` 호출
- Python GC가 generator 정리 시 finally 실행
- 하지만 **보장되지 않음**

#### 리팩토링 시 해결 방안
```python
# dependencies.py에서 올바른 패턴
def get_tm60_users_service(
    mssql_session: Session = Depends(get_db_mssql)  # FastAPI가 생명주기 관리
) -> Tm60UsersService:
    repo = Tm60UsersRepository(mssql_session)
    return Tm60UsersService(repo)
```

---

### 🔴 Critical: UserService 버전 불일치

#### 문제 상황
```python
# user_api.py - 전체 기능 (6개 의존성)
def get_user_service(
    user_repo, counselor_repo, auth_service,
    event_service,           # 이벤트 포인트 지급
    activity_log_service,    # 활동 로그 기록
    tm60_users_service       # ARS 시스템 연동
) -> UserService:
    return UserService(...)

# payment_api.py - 축소 버전 (3개 의존성만)
def get_user_service(db: AsyncSession = Depends(get_db_maria)) -> UserService:
    return UserService(UserRepository(db), CounselorRepository(db), AuthService())
    # 🚨 event_service, activity_log_service, tm60_users_service = None
```

#### 영향받는 기능
| 메서드 | user_api 버전 | payment_api 버전 |
|--------|--------------|-----------------|
| `signup()` 이벤트 포인트 | ✅ 동작 | ❌ 실패 (event_service=None) |
| `login()` 활동 로그 | ✅ 기록 | ❌ 누락 (activity_log_service=None) |
| ARS 시스템 연동 | ✅ 동작 | ❌ 실패 (tm60_users_service=None) |

#### 리팩토링 시 해결 방안
- **하나의 표준 `get_user_service()` 정의** (user_api.py 버전 채택)
- payment_api.py가 이를 import하여 사용
- 모든 API 파일에서 동일한 UserService 구성 보장

---

### 🟠 High: PointTransactionService 의존성 불일치

#### 문제 코드
```python
# user_api.py - Repository 1개만 주입
def get_point_transaction_service(
    point_transaction_repo: PointTransactionRepository = Depends(...)
) -> PointTransactionService:
    return PointTransactionService(point_transaction_repo)  # user_repo, grade_repo = None

# payment_api.py - Repository 3개 주입 (마일리지 적립 필요)
def get_point_transaction_service(
    point_transaction_repo: PointTransactionRepository = Depends(...),
    user_repo: UserRepository = Depends(...),
    grade_repo: GradeRepository = Depends(...)
) -> PointTransactionService:
    return PointTransactionService(point_transaction_repo, user_repo, grade_repo)
```

#### 영향
- `earn_mileage_from_payment()` 호출 시:
  - payment_api → ✅ 정상 동작
  - user_api → ❌ `ValueError` 발생 (user_repo, grade_repo가 None)

#### 리팩토링 시 해결 방안
- **payment_api.py 버전을 표준으로 채택** (3개 Repository 주입)
- 마일리지 적립이 필요 없는 경우에도 안전하게 동작

---

### 🟠 High: 결제 콜백의 트랜잭션 경계 문제

#### 현재 구조 (payment_api.py `/point_callback`)
```python
@router.post("/point_callback")
async def payment_callback(
    payment_service: PaymentService = Depends(get_payment_service),      # MariaDB 세션 A
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service),  # MSSQL 세션
    point_transaction_service: PointTransactionService = Depends(...),   # MariaDB 세션 B (?)
    user_repo: UserRepository = Depends(get_user_repository),            # MariaDB 세션 C (?)
    ...
):
```

#### 문제점
1. **각 서비스가 독립적인 세션을 가질 수 있음** (FastAPI DI 캐싱 미보장 시)
2. **부분 실패 시 일관성 문제**:
   - `payment_service.update_payment()` 성공
   - `tm60_users_service.update_user_points()` 성공
   - `point_transaction_service.earn_mileage_from_payment()` 실패
   - → 마일리지만 적립 안 됨 (허용된 동작이지만 로그 확인 필요)

3. **Repository 레벨 commit**:
   ```python
   # tm60_users_repository.py
   def _sync_update_user_points():
       self.mssql_session.flush()
       self.mssql_session.commit()  # 🚨 Repository에서 직접 commit
   ```
   - 서비스 레이어에서 트랜잭션 제어 불가
   - 현재 동작은 하지만 아키텍처적으로 비권장

#### 리팩토링 시 고려사항
- **현재 동작 유지** (마일리지 실패해도 결제는 성공 처리)
- 리팩토링 후에도 **동일한 동작 보장** 필요
- 트랜잭션 경계 변경은 **별도 작업으로 분리** 권장

---

### 🟡 Medium: 계획서의 잘못된 세션 래핑

#### 계획서 Step 2-2의 문제
```python
# ❌ 불필요한 래핑 (계획서 원안)
async def get_maria_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_maria():
        yield session

MariaSessionDep = Annotated[AsyncSession, Depends(get_maria_session)]

# ✅ 올바른 방법 - 직접 사용
MariaSessionDep = Annotated[AsyncSession, Depends(get_db_maria)]
```

#### MSSQL 세션도 마찬가지
```python
# ❌ 문제가 있는 패턴 (계획서 원안)
def get_mssql_session() -> Generator[Session, None, None]:
    for session in get_db_mssql():
        yield session  # 동일한 세션 누수 위험

# ✅ 올바른 방법 - 직접 사용
MssqlSessionDep = Annotated[Session, Depends(get_db_mssql)]
```

---

### 🟡 Medium: Annotated 타입과 Depends 동작 차이

#### FastAPI의 Depends 캐싱
```python
# 같은 request 내에서 get_db_maria()는 1번만 호출됨
@router.get("/")
async def endpoint(
    user_service: UserServiceDep,      # get_db_maria() 호출
    payment_service: PaymentServiceDep  # 캐시된 세션 재사용
):
```

#### 주의사항
- `Annotated` 타입 alias 사용 시에도 **동일한 캐싱 동작** 유지됨
- 단, **동일한 Depends 함수**를 참조해야 함
- 리팩토링 후 모든 서비스가 **동일한 세션을 공유**하도록 의존성 체인 확인 필요

---

### 🔴 Critical: GradeService 버전 불일치 (신규)

#### 문제 상황
```python
# grade_api.py - 전체 기능 (3개 의존성)
def get_grade_service(
    grade_repo, grade_change_log_repo, auth_service
) -> GradeService:
    return GradeService(grade_repo, grade_change_log_repo, auth_service)

# user_api.py - 축소 버전 (1개 의존성만)
def get_grade_service(grade_repo) -> GradeService:
    return GradeService(grade_repo)  # 🚨 grade_change_log_repo, auth_service = None
```

#### 영향받는 기능
| 메서드 | grade_api 버전 | user_api 버전 |
|--------|---------------|--------------|
| `update_grade()` 로그 기록 | ✅ 동작 | ❌ 실패 (grade_change_log_repo=None) |
| 관리자 권한 확인 | ✅ 동작 | ❌ 실패 (auth_service=None) |

#### 리팩토링 시 해결 방안
- **grade_api.py 버전을 표준으로 채택** (3개 의존성)
- 모든 API 파일에서 동일한 GradeService 구성 보장

---

### 🟠 High: Repository 레벨 Commit/Rollback (신규)

#### 문제 코드
```python
# tm60_member_repository.py - 6개 위치에서 직접 commit/rollback
def _sync_update_member(self):
    try:
        self.mssql_session.flush()
        self.mssql_session.commit()   # lines 58, 78, 98
    except Exception:
        self.mssql_session.rollback()  # lines 60, 80, 100
        raise

# tm60_users_repository.py - 2개 위치
def _sync_update_user_points(self):
    self.mssql_session.commit()  # lines 76, 78
```

#### 왜 문제인가?
- 서비스 레이어에서 **트랜잭션 경계 제어 불가**
- 여러 Repository 작업을 **원자적으로 처리 불가**
- database.py의 `get_db_mssql()` 제네레이터의 commit/rollback과 **중복 실행**

#### 리팩토링 시 고려사항
- 현재 동작은 유지 (MSSQL 작업이 독립적)
- **향후 개선**: Repository에서 commit 제거, Service 레이어에서 트랜잭션 관리
- 이번 DI 리팩토링에서는 **현상 유지** (별도 작업으로 분리)

---

### 🟠 High: Sync/Async 경계 위반 (신규)

#### 문제 코드
```python
# counselor_service.py (lines 241, 247)
async def get_counselor_list(self, ...):
    # 🚨 sync 메서드를 async 함수 내에서 await 없이 호출
    counselors = self.tm60_member_repository.get_all()  # BLOCKING!
    # ...
    self.tm60_member_repository.update_status(...)      # BLOCKING!
```

#### 왜 문제인가?
- **이벤트 루프 블로킹**: DB I/O 동안 다른 요청 처리 불가
- **타임아웃 위험**: 동시 요청 시 응답 지연
- 현재 트래픽이 적어서 문제가 드러나지 않음

#### 올바른 패턴
```python
async def get_counselor_list(self, ...):
    counselors = await asyncio.to_thread(self.tm60_member_repository.get_all)
    # ...
    await asyncio.to_thread(self.tm60_member_repository.update_status, ...)
```

#### 리팩토링 시 고려사항
- **tm60_users_repository.py**는 이미 `asyncio.to_thread()` 사용 중 (올바른 패턴)
- **tm60_member_repository.py** 호출부는 수정 필요
- 이번 DI 리팩토링과 **함께 수정** 권장

---

### 🟡 Medium: CounselorStatusService 비표준 패턴 (신규)

#### 문제 코드
```python
# counselor_api.py
def get_counselor_status_service(db: AsyncSession = Depends(get_db_maria)):
    return CounselorStatusService(db)  # 세션을 직접 전달
```

#### 왜 문제인가?
- 다른 서비스들은 **Repository를 주입**받는 패턴
- 일관성 없는 아키텍처
- 내부에서 Repository를 직접 생성하면 테스트 어려움

#### 리팩토링 시 해결 방안
- 표준 패턴으로 변경 또는 현상 유지 (영향 적음)

---

### 위험 요소 요약 (업데이트)

| 위험도 | 문제 | 영향 | 해결 필요 시점 |
|-------|------|------|--------------|
| 🔴 Critical | MSSQL 세션 누수 패턴 | 커넥션 풀 고갈 | Step 2 |
| 🔴 Critical | UserService 버전 불일치 | 기능 불완전 | Step 2 |
| 🔴 Critical | GradeService 버전 불일치 | 등급 변경 로그 누락 | Step 2 |
| 🟠 High | PointTransactionService 불일치 | 마일리지 오류 | Step 2 |
| 🟠 High | 결제 콜백 트랜잭션 경계 | 일관성 위험 | 리팩토링 후 별도 |
| 🟠 High | Repository 레벨 commit | 트랜잭션 제어 불가 | 리팩토링 후 별도 |
| 🟠 High | Sync/Async 경계 위반 | 이벤트 루프 블로킹 | Step 5와 함께 |
| 🟡 Medium | 세션 래핑 불필요 | 복잡성 증가 | Step 2 |
| 🟡 Medium | Depends 캐싱 이해 | 잠재적 버그 | 테스트로 검증 |
| 🟡 Medium | CounselorStatusService 비표준 | 일관성 부족 | 선택적 |
| 🟡 Medium | CounselorApplicationService 불일치 | 잠재적 버그 | Step 2 |

---

## 1.6 문제 코드 위치 참조 (Quick Reference)

### 🔴 Critical Issues - 반드시 수정

| 문제 | 파일 | 라인 | 설명 |
|-----|------|-----|------|
| 중복 함수 정의 | user_api.py | 190-193, 230-232 | `get_tm60_chatlog_repository()` 2번 정의 |
| MSSQL 세션 누수 | user_api.py | 170-172 | `for mssql_session in get_db_mssql()` 패턴 |
| MSSQL 세션 누수 | payment_api.py | 48-50 | `for mssql_session in get_db_mssql()` 패턴 |
| MSSQL 세션 누수 | counselor_api.py | 112-115 | `for mssql_session in get_db_mssql()` 패턴 |
| MSSQL 세션 누수 | consultation_review_api.py | 35-38 | `for mssql_session in get_db_mssql()` 패턴 |
| MSSQL 세션 누수 | exhibition_api.py | 26-28 | `for mssql_session in get_db_mssql()` 패턴 |
| UserService 불일치 | payment_api.py | 62-63 | 3개 의존성만 (표준: 6개) |
| GradeService 불일치 | user_api.py | 확인필요 | 1개 의존성만 (표준: 3개) |

### 🟠 High Priority Issues

| 문제 | 파일 | 라인 | 설명 |
|-----|------|-----|------|
| Repo 직접 commit | tm60_member_repository.py | 58, 60 | `_sync_update_member()` 내 commit/rollback |
| Repo 직접 commit | tm60_member_repository.py | 78, 80 | `_sync_update_member_status()` 내 commit/rollback |
| Repo 직접 commit | tm60_member_repository.py | 98, 100 | 또 다른 메서드 내 commit/rollback |
| Repo 직접 commit | tm60_users_repository.py | 76, 78 | `_sync_update_user_points()` 내 commit |
| Sync/Async 위반 | counselor_service.py | 241 | `get_all()` sync 호출 (await 없음) |
| Sync/Async 위반 | counselor_service.py | 247 | `update_status()` sync 호출 (await 없음) |

### 📊 중복 DI 함수 위치 매트릭스

```
get_user_repository()
├── user_api.py
├── payment_api.py
├── counselor_api.py
└── inquiry_api.py

get_auth_service()
├── auth_api.py
├── user_api.py
├── payment_api.py
├── counselor_api.py
├── exhibition_api.py
└── grade_api.py

get_notification_service()
├── notification_api.py
├── user_api.py
├── payment_api.py
├── counselor_api.py
└── inquiry_api.py

get_tm60_users_service()
├── user_api.py
├── payment_api.py
├── counselor_api.py
├── exhibition_api.py
└── consultation_review_api.py

get_counselor_repository()
├── counselor_api.py
├── user_api.py
├── payment_api.py
└── counselor_application_api.py
```

---

## 2. 목표 구조

### 2.1 디렉토리 구조 변경

```
backend/src/
├── core/
│   ├── database.py          # 기존 유지
│   ├── redis.py             # 기존 유지
│   └── dependencies.py      # 🆕 신규 생성 - 중앙화된 DI
├── api/v1/
│   ├── user_api.py          # DI 함수 제거, import 변경
│   ├── payment_api.py       # DI 함수 제거, import 변경
│   └── ...                  # 모든 API 파일 동일 적용
└── ...
```

### 2.2 dependencies.py 구조

```python
# backend/src/core/dependencies.py

"""
중앙화된 의존성 주입 모듈
- 모든 Repository/Service DI 함수를 한 곳에서 관리
- Annotated 타입 alias로 깔끔한 endpoint 작성 지원
"""

from typing import Annotated, AsyncGenerator, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# ==================== Database Sessions ====================
# MariaDB (Async)
MariaSessionDep = Annotated[AsyncSession, Depends(get_db_maria)]

# MSSQL (Sync)
MssqlSessionDep = Annotated[Session, Depends(get_db_mssql)]

# ==================== Repositories ====================
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
CounselorRepositoryDep = Annotated[CounselorRepository, Depends(get_counselor_repository)]
# ... 17개 Repository

# ==================== Services ====================
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
# ... 21개 Service
```

### 2.3 리팩토링 후 API 파일 예시

```python
# backend/src/api/v1/user_api.py (리팩토링 후)

from fastapi import APIRouter, Query
from src.core.dependencies import (
    UserServiceDep,
    NotificationServiceDep,
    InquiryServiceDep,
    # ... 필요한 의존성만 import
)
from src.services.auth_service import get_current_user, TokenPayload
from src.schemas.user_schema import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

# ========== DI 함수 정의 완전 제거 ==========

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserServiceDep  # Annotated 타입으로 깔끔하게
):
    return await user_service.get_user(user_id)
```

---

## 3. 마이그레이션 단계

### 전체 단계 개요

| Step | 작업 내용 | 예상 영향 범위 | 위험도 |
|------|----------|--------------|-------|
| 1 | 즉시 버그 수정 | user_api.py | 🟢 낮음 |
| 2 | dependencies.py 생성 | 신규 파일 | 🟢 낮음 |
| 3 | 간단한 API 마이그레이션 (2개) | notice, banner | 🟢 낮음 |
| 4 | 중간 복잡도 API 마이그레이션 (6개) | grade, event 등 | 🟡 중간 |
| 5 | 복잡한 API 마이그레이션 (7개) | user, payment 등 | 🟠 높음 |
| 6 | 테스트 및 검증 | 전체 | 🟢 낮음 |
| 7 | 정리 및 문서화 | 전체 | 🟢 낮음 |

---

## 4. 상세 작업 내용

### Step 1: 즉시 버그 수정 (우선순위: 긴급)

**목표**: 동일 파일 내 중복 함수 정의 제거

**작업 파일**: `backend/src/api/v1/user_api.py`

**작업 내용**:
- [ ] 라인 230-232의 중복 `get_tm60_chatlog_repository()` 함수 삭제
- [ ] 기능 테스트 수행

**예상 변경량**: 3줄 삭제

---

### Step 2: dependencies.py 생성 (우선순위: 높음)

**목표**: 중앙화된 의존성 모듈 생성

**작업 파일**: `backend/src/core/dependencies.py` (신규)

**작업 내용**:

#### 2-1. 파일 생성 및 기본 구조
```python
"""
중앙화된 의존성 주입 모듈

모든 Repository/Service DI 함수와 Annotated 타입 alias를 관리합니다.
각 API 파일에서는 이 모듈에서 필요한 의존성만 import하여 사용합니다.
"""
from typing import Annotated, AsyncGenerator, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
```

#### 2-2. Database Session 의존성 (수정됨)
```python
from src.core.database import get_db_maria, get_db_mssql

# ✅ 올바른 방법: 기존 함수를 직접 Depends로 사용
# FastAPI가 generator 생명주기를 자동 관리함

# MariaDB Async Session - 래핑 없이 직접 사용
MariaSessionDep = Annotated[AsyncSession, Depends(get_db_maria)]

# MSSQL Sync Session - 래핑 없이 직접 사용
MssqlSessionDep = Annotated[Session, Depends(get_db_mssql)]
```

**중요**: `for loop`으로 generator를 소비하는 패턴은 **절대 사용하지 않음**.
FastAPI의 `Depends()`가 generator의 생명주기(yield → finally)를 올바르게 관리함.

#### 2-3. Repository 의존성 (17개)

**MariaDB Repositories**:
- [ ] `get_user_repository()` → `UserRepositoryDep`
- [ ] `get_counselor_repository()` → `CounselorRepositoryDep`
- [ ] `get_notification_repository()` → `NotificationRepositoryDep`
- [ ] `get_notification_wait_repository()` → `NotificationWaitRepositoryDep`
- [ ] `get_payment_repository()` → `PaymentRepositoryDep`
- [ ] `get_point_product_repository()` → `PointProductRepositoryDep`
- [ ] `get_point_transaction_repository()` → `PointTransactionRepositoryDep`
- [ ] `get_grade_repository()` → `GradeRepositoryDep`
- [ ] `get_event_repository()` → `EventRepositoryDep`
- [ ] `get_banner_repository()` → `BannerRepositoryDep`
- [ ] `get_notice_repository()` → `NoticeRepositoryDep`
- [ ] `get_inquiry_repository()` → `InquiryRepositoryDep`
- [ ] `get_consultation_review_repository()` → `ConsultationReviewRepositoryDep`
- [ ] `get_user_bookmark_repository()` → `UserBookmarkRepositoryDep`
- [ ] `get_user_activity_log_repository()` → `UserActivityLogRepositoryDep`
- [ ] `get_counselor_application_repository()` → `CounselorApplicationRepositoryDep`
- [ ] `get_mileage_repository()` → `MileageRepositoryDep`

**MSSQL Repositories (ARS)**:
- [ ] `get_tm60_users_repository()` → `Tm60UsersRepositoryDep`
- [ ] `get_tm60_member_repository()` → `Tm60MemberRepositoryDep`
- [ ] `get_tm60_chatlog_repository()` → `Tm60ChatlogRepositoryDep`
- [ ] `get_tm60_mobile_repository()` → `Tm60MobileRepositoryDep`

#### 2-4. Service 의존성 (21개)

**Stateless Services**:
- [ ] `get_auth_service()` → `AuthServiceDep`

**Simple Services (Repository 1개 의존)**:
- [ ] `get_notification_service()` → `NotificationServiceDep`
- [ ] `get_banner_service()` → `BannerServiceDep`
- [ ] `get_notice_service()` → `NoticeServiceDep`
- [ ] `get_grade_service()` → `GradeServiceDep`
- [ ] `get_consultation_review_service()` → `ConsultationReviewServiceDep`
- [ ] `get_user_bookmark_service()` → `UserBookmarkServiceDep`
- [ ] `get_user_activity_log_service()` → `UserActivityLogServiceDep`
- [ ] `get_counselor_application_service()` → `CounselorApplicationServiceDep`
- [ ] `get_mileage_service()` → `MileageServiceDep`
- [ ] `get_phone_verification_service()` → `PhoneVerificationServiceDep`

**Complex Services (다중 의존성)**:
- [ ] `get_user_service()` → `UserServiceDep`
- [ ] `get_counselor_service()` → `CounselorServiceDep`
- [ ] `get_payment_service()` → `PaymentServiceDep`
- [ ] `get_point_product_service()` → `PointProductServiceDep`
- [ ] `get_point_transaction_service()` → `PointTransactionServiceDep`
- [ ] `get_event_service()` → `EventServiceDep`
- [ ] `get_inquiry_service()` → `InquiryServiceDep`
- [ ] `get_notification_wait_service()` → `NotificationWaitServiceDep`
- [ ] `get_social_auth_service()` → `SocialAuthServiceDep`

**MSSQL Services (ARS)**:
- [ ] `get_tm60_users_service()` → `Tm60UsersServiceDep`
- [ ] `get_tm60_member_service()` → `Tm60MemberServiceDep`
- [ ] `get_tm60_chatlog_service()` → `Tm60ChatlogServiceDep`
- [ ] `get_tm60_mobile_service()` → `Tm60MobileServiceDep`

---

### Step 3: 간단한 API 마이그레이션 (파일럿)

**목표**: 2개의 간단한 API 파일로 패턴 검증

**대상 파일**:
1. `backend/src/api/v1/notice_api.py` (DI 함수 2개)
2. `backend/src/api/v1/banner_api.py` (DI 함수 2개)

**작업 내용**:
- [ ] 기존 DI 함수 삭제
- [ ] `from src.core.dependencies import ...` 추가
- [ ] 엔드포인트의 `Depends()` 를 `Annotated` 타입으로 교체
- [ ] 기능 테스트 수행

**예시 변경**:
```python
# Before (notice_api.py)
def get_notice_repository(db: AsyncSession = Depends(get_db_maria)) -> NoticeRepository:
    return NoticeRepository(db)

def get_notice_service(repo: NoticeRepository = Depends(get_notice_repository)) -> NoticeService:
    return NoticeService(repo)

@router.get("/")
async def get_notices(service: NoticeService = Depends(get_notice_service)):
    ...

# After
from src.core.dependencies import NoticeServiceDep

@router.get("/")
async def get_notices(service: NoticeServiceDep):
    ...
```

---

### Step 4: 중간 복잡도 API 마이그레이션

**목표**: 8개의 중간 복잡도 API 파일 마이그레이션

**대상 파일** (DI 함수 4-10개):

| 파일 | DI 함수 수 | 특이사항 |
|-----|----------|---------|
| `consultation_review_api.py` | 10개 | MSSQL 세션 누수 패턴 수정 필요 |
| `inquiry_api.py` | 9개 | notification_service 중복 |
| `auth_api.py` | 8개 | 기본 인증 로직 |
| `counselor_application_api.py` | 7개 | CounselorApplicationService 표준화 |
| `grade_api.py` | 5개 | GradeService 표준 버전 |
| `mileage_api.py` | 5개 | point_transaction 관련 |
| `exhibition_api.py` | 4개 | MSSQL 세션 누수 패턴 수정 필요 |
| `promotion_api.py` | 2개 | 단순 |

**작업 순서**:
- [ ] 각 파일의 DI 함수 분석
- [ ] dependencies.py에 누락된 의존성 추가
- [ ] MSSQL 세션 패턴 수정 (consultation_review_api, exhibition_api)
- [ ] API 파일 리팩토링
- [ ] 개별 테스트

---

### Step 5: 복잡한 API 마이그레이션

**목표**: 7개의 복잡한 API 파일 마이그레이션

**대상 파일** (DI 함수 7개 이상):
1. `user_api.py` (23개 DI 함수) - **최고 복잡도**
2. `payment_api.py` (11개 DI 함수)
3. `counselor_api.py` (14개 DI 함수)
4. `counselor_application_api.py`
5. `auth_api.py`
6. `social_auth_api.py`
7. `phone_verification_api.py`

**특별 주의사항**:

#### A. UserService 표준화 (Critical)
- `user_api.py`의 `get_user_service()` 정의를 **표준**으로 채택 (6개 의존성)
- `payment_api.py`의 단순화된 버전은 **반드시 표준 버전으로 교체**
- 그렇지 않으면 이벤트 포인트, 활동 로그, ARS 연동 기능 누락

#### B. PointTransactionService 표준화 (High)
- `payment_api.py`의 3개 Repository 주입 버전을 **표준**으로 채택
- 마일리지 적립 기능이 모든 API에서 정상 동작하도록 보장

#### C. GradeService 표준화 (Critical) - 신규
- `grade_api.py`의 `get_grade_service()` 정의를 **표준**으로 채택 (3개 의존성)
- `user_api.py`의 축소 버전은 **반드시 표준 버전으로 교체**
- 그렇지 않으면 등급 변경 로그 기록 및 관리자 권한 확인 기능 누락

#### D. MSSQL 서비스 패턴 통일 (Critical)
```python
# ❌ 기존 패턴 (세션 누수 위험) - 5개 파일에서 발견
def get_tm60_users_service():
    for mssql_session in get_db_mssql():
        return Tm60UsersService(Tm60UsersRepository(mssql_session))

# ✅ 올바른 패턴 (FastAPI가 세션 생명주기 관리)
def get_tm60_users_service(
    mssql_session: Session = Depends(get_db_mssql)
) -> Tm60UsersService:
    return Tm60UsersService(Tm60UsersRepository(mssql_session))
```

#### E. Sync/Async 경계 수정 (High) - 신규
`counselor_service.py`에서 sync 메서드를 async 컨텍스트에서 호출하는 문제 수정:
```python
# ❌ 현재 코드 (line 241, 247) - 이벤트 루프 블로킹
counselors = self.tm60_member_repository.get_all()

# ✅ 수정 코드
counselors = await asyncio.to_thread(self.tm60_member_repository.get_all)
```

#### F. CounselorApplicationService 패턴 통일 (Medium) - 신규
- `counselor_application_api.py` 패턴을 표준으로 채택
- `counselor_api.py`의 직접 세션 전달 패턴 수정

#### G. 결제 콜백 테스트 필수 (Critical)
- `/point_callback` 엔드포인트는 **실제 결제 처리**
- 리팩토링 후 반드시 **통합 테스트** 수행:
  - 결제 성공 → 포인트 충전 → 마일리지 적립 전체 플로우
  - 각 단계 실패 시 적절한 에러 처리 확인
  - DB 상태 일관성 검증

#### H. 서비스별 표준 의존성 정의 (Step 2에서 적용)

| 서비스 | 표준 정의 출처 | 의존성 |
|--------|--------------|--------|
| UserService | user_api.py | user_repo, counselor_repo, auth_service, event_service, activity_log_service, tm60_users_service |
| GradeService | grade_api.py | grade_repo, grade_change_log_repo, auth_service |
| PointTransactionService | payment_api.py | point_transaction_repo, user_repo, grade_repo |
| CounselorApplicationService | counselor_application_api.py | counselor_application_repo |
| CounselorService | counselor_api.py | counselor_repo, notification_repo, tm60_member_repo, user_repo |

---

### Step 6: 테스트 및 검증

**목표**: 전체 기능 검증

**테스트 항목**:
- [ ] 단위 테스트 전체 실행
- [ ] API 엔드포인트 수동 테스트
- [ ] 의존성 순환 참조 검증
- [ ] 타입 체크 (mypy)
- [ ] 린트 검사 (flake8, black)

**검증 명령어**:
```bash
cd backend
pytest tests/ -v
mypy src/
flake8 src/
black --check src/
```

---

### Step 7: 정리 및 문서화

**목표**: 코드 정리 및 가이드 작성

**작업 내용**:
- [ ] 사용되지 않는 import 제거
- [ ] 코드 포매팅 (black, isort)
- [ ] dependencies.py 주석 보강
- [ ] CLAUDE.md 업데이트 (DI 패턴 가이드 추가)
- [ ] 본 문서를 COMPLETED로 마킹

---

## 5. 테스트 전략

### 5.1 단계별 테스트

| Step | 테스트 방법 |
|------|-----------|
| Step 1 | 해당 엔드포인트 호출 테스트 |
| Step 2 | import 테스트 (syntax error 확인) |
| Step 3-5 | 각 API 엔드포인트 기능 테스트 |
| Step 6 | 전체 통합 테스트 |

### 5.2 테스트 체크리스트

```bash
# 각 Step 완료 후 실행
cd backend

# 1. 서버 시작 확인
uvicorn src.main:app --reload --port 8000

# 2. 헬스체크
curl http://localhost:8000/health

# 3. Swagger UI 확인
# http://localhost:8000/docs 접속

# 4. 타입 체크
mypy src/

# 5. 린트
flake8 src/
```

### 5.3 결제 로직 필수 테스트 (Critical)

리팩토링 후 **결제 관련 기능 검증 필수**:

#### A. 결제 요청 테스트 (`/payment/request`)
```bash
# 테스트 시나리오
1. 로그인 사용자로 결제 요청
2. UserService가 user 정보 정상 조회하는지 확인
3. PaymentService가 PENDING 상태로 결제 생성하는지 확인
```

#### B. 결제 콜백 테스트 (`/payment/point_callback`)
```bash
# 테스트 시나리오 - 전체 성공 플로우
1. PENDING 상태 결제에 대해 콜백 호출
2. payment_service.update_payment() → SUCCESS 업데이트
3. tm60_users_service.update_user_points() → 포인트 충전 (MSSQL)
4. point_transaction_service.earn_mileage_from_payment() → 마일리지 적립 (MariaDB)
5. notification_service.user_charge_confirm_alert() → 알림톡 발송

# 부분 실패 시나리오 (기존 동작 유지 확인)
- 마일리지 적립 실패 시: 결제는 SUCCESS, 포인트는 충전됨
- 알림톡 실패 시: 결제는 SUCCESS, 포인트는 충전됨
```

#### C. MSSQL 세션 누수 테스트
```bash
# 다수의 동시 요청으로 커넥션 풀 테스트
# pool_size=5 환경에서 10개 동시 요청 테스트
# 타임아웃 없이 정상 처리되어야 함
```

#### D. DB 일관성 검증
```bash
# 결제 성공 후 확인 항목
- MariaDB: payments 테이블 → status='SUCCESS'
- MariaDB: point_transactions 테이블 → 마일리지 적립 내역
- MSSQL: tm60_users 테이블 → u_point 증가
```

---

### 5.4 롤백 트리거 조건

- 서버 시작 실패
- 2개 이상의 엔드포인트 오류
- 타입 체크 오류 10개 이상
- **결제 콜백 테스트 실패** (Critical)
- **MSSQL 커넥션 풀 고갈 발생**

---

## 6. 롤백 계획

### 6.1 Git 브랜치 전략

```bash
# 작업 시작 전
git checkout -b refactor/di-centralization

# 각 Step 완료 시 커밋
git commit -m "refactor(di): Step N - 작업 내용"

# 문제 발생 시 롤백
git checkout main
git branch -D refactor/di-centralization
```

### 6.2 단계별 롤백

| Step | 롤백 방법 |
|------|----------|
| Step 1 | `git checkout -- backend/src/api/v1/user_api.py` |
| Step 2 | `rm backend/src/core/dependencies.py` |
| Step 3-5 | 해당 API 파일 `git checkout` |

---

## 7. 예상 효과

### 7.1 코드 감소량 (정밀 분석 결과)

| 항목 | Before | After | 감소량 |
|-----|--------|-------|-------|
| user_api.py DI 코드 | ~180줄 (23개 함수) | 0줄 | -180줄 |
| counselor_api.py DI 코드 | ~120줄 (15개 함수) | 0줄 | -120줄 |
| payment_api.py DI 코드 | ~85줄 (11개 함수) | 0줄 | -85줄 |
| consultation_review_api.py | ~75줄 (10개 함수) | 0줄 | -75줄 |
| inquiry_api.py | ~70줄 (9개 함수) | 0줄 | -70줄 |
| auth_api.py | ~60줄 (8개 함수) | 0줄 | -60줄 |
| 기타 8개 API 파일 | ~110줄 | 0줄 | -110줄 |
| **총 제거 코드** | **~700줄** | - | **-700줄** |
| dependencies.py | 0줄 | ~350줄 | +350줄 |
| **순 감소** | - | - | **~350줄** |

### 7.1.1 버그 수정 효과

| 수정 항목 | 영향 |
|----------|------|
| 중복 함수 정의 제거 | 잠재적 런타임 오류 방지 |
| MSSQL 세션 누수 수정 | 커넥션 풀 고갈 방지 |
| UserService 통일 | 이벤트 포인트/활동 로그 기능 정상화 |
| GradeService 통일 | 등급 변경 로그 기록 정상화 |
| PointTransactionService 통일 | 마일리지 적립 기능 정상화 |
| Sync/Async 경계 수정 | 이벤트 루프 블로킹 방지 |

### 7.2 유지보수 개선

| 항목 | Before | After |
|-----|--------|-------|
| 새 서비스 추가 시 수정 파일 | 사용하는 모든 API 파일 | dependencies.py 1개 |
| DI 함수 변경 시 | 15개 파일 검토 필요 | 1개 파일만 수정 |
| 의존성 그래프 파악 | 각 파일 분석 필요 | dependencies.py에서 확인 |
| 테스트 모킹 | 파일별 fixture | `app.dependency_overrides` |

### 7.3 코드 품질 개선

- 중복 코드 제거로 **DRY 원칙** 준수
- 일관된 네이밍 컨벤션
- 의존성 불일치 문제 해결
- 타입 안정성 향상 (Annotated)

---

## 변경 이력

| 날짜 | 버전 | 작성자 | 내용 |
|-----|------|-------|-----|
| 2026-01-27 | 1.0 | Claude | 초안 작성 |
| 2026-01-27 | 1.1 | Claude | 위험 요소 분석 추가 (섹션 1.5) |
| 2026-01-27 | 1.1 | Claude | MSSQL 세션 누수 문제 식별 및 해결책 추가 |
| 2026-01-27 | 1.1 | Claude | UserService/PointTransactionService 버전 불일치 문제 추가 |
| 2026-01-27 | 1.1 | Claude | 결제 로직 필수 테스트 항목 추가 (섹션 5.3) |
| 2026-01-27 | 1.1 | Claude | Step 2, Step 5 세부 내용 수정 |
| 2026-01-27 | 1.2 | Claude | **전체 백엔드 정밀 분석 결과 반영** |
| 2026-01-27 | 1.2 | Claude | 섹션 1.1: 파일 현황 업데이트 (16개 API, 21개 Repo, 25개 Service) |
| 2026-01-27 | 1.2 | Claude | 섹션 1.2: 정확한 DI 함수 현황 (97개 정의, 40개+ 중복) |
| 2026-01-27 | 1.2 | Claude | 섹션 1.2.1: API 파일별 DI 함수 수 매트릭스 추가 |
| 2026-01-27 | 1.2 | Claude | 섹션 1.3: 신규 문제 발견 (E~I 항목 추가) |
| 2026-01-27 | 1.2 | Claude | - GradeService 버전 불일치 |
| 2026-01-27 | 1.2 | Claude | - CounselorApplicationService 버전 불일치 |
| 2026-01-27 | 1.2 | Claude | - CounselorStatusService 비표준 패턴 |
| 2026-01-27 | 1.2 | Claude | - Repository 레벨 commit/rollback (Anti-Pattern) |
| 2026-01-27 | 1.2 | Claude | - Sync/Async 경계 위반 (counselor_service.py) |
| 2026-01-27 | 1.2 | Claude | 섹션 1.5: 위험 요소 3개 추가 (GradeService, Repo commit, Sync/Async) |
| 2026-01-27 | 1.2 | Claude | 섹션 1.5: 위험 요소 요약 테이블 업데이트 (11개 항목) |
| 2026-01-27 | 1.2 | Claude | Step 5: 서비스별 표준 의존성 정의 테이블 추가 |
| 2026-01-27 | 1.2 | Claude | Step 5: Sync/Async 경계 수정 항목 추가 |

---

## 승인

- [ ] 계획 검토 완료
- [ ] 작업 시작 승인
