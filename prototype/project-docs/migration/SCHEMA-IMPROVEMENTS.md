# DB 스키마 개선사항 - PK 최적화

## 📌 주요 개선사항

### 1. Primary Key 구조 단순화

#### 기존 문제점
- 불필요한 Auto Increment ID와 실제 login ID 분리
- user_id(AUTO_INCREMENT) + login_id(실제 로그인 ID) 이중 구조
- counselor_id(AUTO_INCREMENT) + login_id + email 중복 구조

#### 개선된 구조

**t_user 테이블**
```sql
-- 기존 (복잡한 구조)
user_id INT AUTO_INCREMENT PRIMARY KEY
login_id VARCHAR(100) UNIQUE  -- 실제 로그인 ID

-- 개선 (단순한 구조)  
user_id VARCHAR(100) PRIMARY KEY  -- USER_ID를 그대로 PK로 사용
```

**t_counselor 테이블**
```sql
-- 기존 (복잡한 구조)
counselor_id INT AUTO_INCREMENT PRIMARY KEY
login_id VARCHAR(100) UNIQUE
email VARCHAR(100) UNIQUE

-- 개선 (단순한 구조)
counselor_id VARCHAR(100) PRIMARY KEY  -- EMAIL을 PK로 사용 (로그인 ID = 이메일)
counselor_code VARCHAR(50) UNIQUE  -- 기존 CODE 유지
```

### 2. 데이터 마이그레이션 전략

#### USER 테이블
- TBL_USER.USER_ID → t_user.user_id (PK로 직접 사용)
- 중복 USER_ID 문제 자동 해결 (WithDrawal@ 접두사 16건)
- AUTO_INCREMENT 불필요

#### COUNSELOR 테이블  
- TBL_CS.EMAIL → t_counselor.counselor_id (PK로 사용)
- 상담사는 이메일로 로그인하므로 EMAIL을 PK로 사용
- CODE는 별도 unique key로 유지

### 3. 장점

1. **구조 단순화**
   - 불필요한 중복 제거
   - 명확한 식별자 체계

2. **성능 향상**
   - JOIN 연산 감소
   - 인덱스 효율성 증가

3. **데이터 무결성**
   - PK 자체가 의미있는 값
   - 중복 방지 자동화

4. **유지보수성**
   - 직관적인 구조
   - 마이그레이션 단순화

### 4. 변경된 테이블 목록

| 테이블 | PK 타입 변경 | 설명 |
|--------|------------|------|
| t_user | VARCHAR(100) | USER_ID를 그대로 PK로 사용 |
| t_user_point_balance | VARCHAR(100) | user_id FK |
| t_user_preference | VARCHAR(100) | user_id FK |
| t_counselor | VARCHAR(100) | EMAIL을 PK로 사용 |
| t_counselor_specialty | VARCHAR(100) | counselor_id FK |
| t_counselor_schedule | VARCHAR(100) | counselor_id FK |
| t_consultation_session | VARCHAR(100) | user_id, counselor_id FK |
| t_consultation_queue | VARCHAR(100) | user_id, counselor_id FK |
| t_consultation_review | VARCHAR(100) | user_id, counselor_id FK |
| t_review_like | VARCHAR(100) | user_id FK |
| t_payment | VARCHAR(100) | user_id FK |
| t_point_transaction | VARCHAR(100) | user_id FK |
| t_external_point_sync | VARCHAR(100) | user_id FK |
| t_user_activity_log | VARCHAR(100) | user_id FK |
| t_search_log | VARCHAR(100) | user_id FK |
| t_event_participation_log | VARCHAR(100) | user_id FK |
| t_grade_change_log | VARCHAR(100) | user_id FK |
| t_review_dummy | VARCHAR(100) | counselor_id FK |

### 5. 마이그레이션 스크립트 핵심 변경

```sql
-- USER 마이그레이션 (단순화)
INSERT INTO t_user (user_id, email, ...)
SELECT USER_ID, EMAIL, ...  -- USER_ID를 그대로 PK로 사용
FROM TBL_USER;

-- COUNSELOR 마이그레이션 (이메일을 PK로)
INSERT INTO t_counselor (counselor_id, counselor_code, ...)
SELECT EMAIL, CODE, ...  -- EMAIL을 PK로 사용
FROM TBL_CS
WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL;

-- 참조 무결성 처리
-- 모든 FK 참조는 실제 ID 값으로 직접 매핑
```

### 6. 검증 체크리스트

- [x] PK 중복 제거
- [x] AUTO_INCREMENT 제거 (의미있는 PK 사용)
- [x] 외래키 참조 정합성
- [x] NULL 처리 로직
- [x] 중복 데이터 방지
- [x] 마이그레이션 스크립트 수정

## 결론

기존의 복잡한 이중 구조(AUTO_INCREMENT ID + 실제 ID)를 제거하고,
의미있는 비즈니스 키를 직접 PK로 사용함으로써 구조를 단순화했습니다.

- **사용자**: USER_ID를 그대로 PK로 사용
- **상담사**: EMAIL을 PK로 사용 (로그인 ID = 이메일)

이를 통해 불필요한 JOIN을 줄이고, 데이터 무결성을 강화하며,
전체적인 시스템 성능과 유지보수성을 개선했습니다.