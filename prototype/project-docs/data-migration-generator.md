# 데이터 마이그레이션 쿼리 (MariaDB → PostgreSQL)
## 1. User Domain
### 1.1 사용자 기본 정보 (TBL_USER → T_USER)

```sql
-- T_USER 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_user (user_id, email, password_hash, phone, nickname, join_type, user_status, grade_code, point_balance, mileage_balance, profile_image_url, birth_datetime, is_lunar_birth, gender, fcm_token, is_marketing_agreed, terms_agreed_at, privacy_agreed_at, created_at, updated_at, last_login_at, withdrawn_at) VALUES (',
    '''', USER_ID, ''', ',
    '''', REPLACE(EMAIL, '''', ''''''), ''', ',
    '''', REPLACE(PASSWORD, '''', ''''''), ''', ',
    '''', PHONE, ''', ',
    '''', REPLACE(NICK_NAME, '''', ''''''), ''', ',
    '''', UPPER(IFNULL(JOIN_TYPE, 'EMAIL')), ''', ',
    CASE USER_STATUS 
        WHEN '1' THEN '''ACTIVE'''
        WHEN '2' THEN '''DORMANT'''
        WHEN '3' THEN '''WITHDRAWN'''
        ELSE '''ACTIVE'''
    END, ', ',
    '''', IFNULL(GRADE, 'WHITE'), ''', ',
    '0, ',  -- point_balance (별도 계산 필요)
    IFNULL(MILEAGE, 0), ', ',
    'NULL, ',  -- profile_image_url
    'NULL, ',  -- birth_datetime
    'FALSE, ',  -- is_lunar_birth
    'NULL, ',  -- gender
    'NULL, ',  -- fcm_token
    '''N'' = ''Y'', ',  -- is_marketing_agreed (기본값 FALSE)
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    IFNULL(CONCAT('''', DATE_FORMAT(UPDATE_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(LAST_LOGIN, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    CASE 
        WHEN USER_STATUS = '3' THEN CONCAT('''', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), '''')
        ELSE 'NULL'
    END,
    ');'
) AS insert_query
FROM TBL_USER
WHERE USER_ID IS NOT NULL AND USER_ID != '';

-- T_USER_PREFERENCE 마이그레이션 (신규 테이블, 기본값으로 생성)
SELECT CONCAT(
    'INSERT INTO t_user_preference (user_id) VALUES (''', USER_ID, ''');'
) AS insert_query
FROM TBL_USER
WHERE USER_STATUS != '3' AND USER_ID IS NOT NULL;
```

## 2. Counselor Domain
### 2.1 상담사 정보 (TBL_CS → T_COUNSELOR)
```sql
-- T_COUNSELOR 마이그레이션
SELECT CONCAT(
    'INSERT INTO t_counselor (nickname, counselor_code, email, password_hash, name, phone, profile_image_url, introduction_short, introduction_long, greeting_message, specialties, keywords, consultation_styles, experience_years, career_detail, certificates, counselor_status, online_status, grade, rating_avg, rating_count, consultation_count, approval_status, approved_at, applied_at, created_at, updated_at, last_login_at) VALUES (',
    '''', REPLACE(NICK_NAME, '''', ''''''), ''', ',
    '''', CODE, ''', ',
    '''', REPLACE(EMAIL, '''', ''''''), ''', ',
    '''', REPLACE(IFNULL(PASSWORD,''), '''', ''''''), ''', ',
    '''', REPLACE(NAME, '''', ''''''), ''', ',
    '''', PHONE, ''', ',
    IFNULL(CONCAT('''', REPLACE(IMG, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(SHORT_INFO, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(GREETING, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(GREETING, '''', ''''''), ''''), 'NULL'), ', ',
    '''[',
    CASE WHEN TARO_YN = 'Y' THEN '"타로"' ELSE '' END,
    CASE WHEN TARO_YN = 'Y' AND (LUCK_YN = 'Y' OR FORTUNE_YN = 'Y' OR EASY_YN = 'Y') THEN ',' ELSE '' END,
    CASE WHEN LUCK_YN = 'Y' THEN '"사주"' ELSE '' END,
    CASE WHEN LUCK_YN = 'Y' AND (FORTUNE_YN = 'Y' OR EASY_YN = 'Y') THEN ',' ELSE '' END,
    CASE WHEN FORTUNE_YN = 'Y' THEN '"신점"' ELSE '' END,
    CASE WHEN FORTUNE_YN = 'Y' AND EASY_YN = 'Y' THEN ',' ELSE '' END,
    CASE WHEN EASY_YN = 'Y' THEN '"역학"' ELSE '' END,
    ']''::jsonb, ',
    IFNULL(CONCAT('''["', REPLACE(REPLACE(CS_KEYWORD, ',', '","'), '''', ''''''), '"]''::jsonb'), '''[]''::jsonb'), ', ',
    '''[]''::jsonb, ',  -- consultation_styles
    '0, ',  -- experience_years
    IFNULL(CONCAT('''', REPLACE(CAREER, '''', ''''''), ''''), 'NULL'), ', ',
    '''[]''::jsonb, ',  -- certificates
    CASE STATUS 
        WHEN '1' THEN '''ACTIVE'''
        WHEN '2' THEN '''ACTIVE'''
        WHEN '3' THEN '''REST'''
        ELSE '''REVIEWING'''
    END, ', ',
    CASE STATUS 
        WHEN '1' THEN '''OFFLINE'''
        WHEN '2' THEN '''BUSY'''
        ELSE '''OFFLINE'''
    END, ', ',
    '''', IFNULL(GRADE, 'BRONZE'), ''', ',
    '0.00, ',  -- rating_avg
    '0, ',  -- rating_count
    '0, ',  -- consultation_count
    CASE 
        WHEN APPROVAL_YN = 'Y' THEN '''APPROVED'''
        ELSE '''PENDING'''
    END, ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(CS_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(RECRUIT_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    '''', IFNULL(DATE_FORMAT(CS_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    IFNULL(CONCAT('''', DATE_FORMAT(UPDATE_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(LAST_LOGIN, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'),
    ');'
) AS insert_query
FROM TBL_CS
WHERE OUT_YN = 'N' AND NICK_NAME IS NOT NULL;

-- T_COUNSELOR_PRICING 마이그레이션
SELECT CONCAT(
    'INSERT INTO t_counselor_pricing (counselor_nickname, chat_price_per_min, voice_price_per_min, video_price_per_min) VALUES (',
    '''', REPLACE(NICK_NAME, '''', ''''''), ''', ',
    IFNULL(AFTER_AMOUNT, 1000), ', ',
    IFNULL(BEFORE_AMOUNT * 2, 2000), ', ',
    IFNULL(BEFORE_AMOUNT * 3, 3000),
    ');'
) AS insert_query
FROM TBL_CS
WHERE OUT_YN = 'N' AND APPROVAL_YN = 'Y' AND NICK_NAME IS NOT NULL;
```

## 3. Payment Domain
### 3.1 결제 내역 (TBL_USER_TRADE → T_PAYMENT)
```sql
-- T_PAYMENT 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_payment (order_no, user_id, payment_type, amount, point_amount, mileage_used, payment_method, payment_status, pg_provider, pg_tid, pg_response, paid_at, cancelled_at, cancel_reason, refund_amount, created_at) VALUES (',
    '''', ORDER_NO, ''', ',
    '(SELECT user_id FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''POINT_CHARGE'', ',
    IFNULL(AMOUNT, 0), ', ',
    IFNULL(USER_POINT, 0), ', ',
    '0, ',  -- mileage_used
    ifnull(PGCODE,''), ', ',
    CASE PAY_TYPE
        WHEN 'SUCCESS' THEN '''SUCCESS'''
        WHEN 'CANCEL' THEN '''CANCELLED'''
        WHEN 'FAIL' THEN '''FAILED'''
        ELSE '''PENDING'''
    END, ', ',
    IFNULL(CONCAT('''', PGCODE, ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', TID, ''''), 'NULL'), ', ',
    '''{}''::jsonb, ',
CASE
    WHEN PAY_TYPE = 'SUCCESS' AND TRANSACTION_DATE IS NOT NULL
    THEN CONCAT('''', TRANSACTION_DATE, '''')
    ELSE 'NULL'
END, ', ',

-- cancelled_at  
CASE
    WHEN PAY_TYPE = 'CANCEL' AND CANCEL_DATE IS NOT NULL
    THEN CONCAT('''', CANCEL_DATE, '''')
    ELSE 'NULL'
END, ', ',
    'NULL, ',  -- cancel_reason
    IFNULL(CANCEL_AMOUNT, '0'), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_USER_TRADE t
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID)
  AND ORDER_NO IS NOT NULL;


-- T_POINT_LOG 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_point_log (user_id, transaction_type, point_amount, balance_after, reference_type, reference_id, description, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = h.USER_IDX LIMIT 1), 
    '''), ',
    CASE 
        WHEN POINT_ACTION = '지급' THEN '''CHARGE'''
        WHEN POINT_ACTION = '차감' THEN '''USE'''
        ELSE '''USE'''
    END, ', ',
    ABS(ACTIVE_POINT), ', ',
    IFNULL(USER_POINT, 0), ', ',
    '''MIGRATION'', ',
    '''LEGACY_', USER_IDX, ''', ',
    IFNULL(CONCAT('''', REPLACE(REASON, '''', ''''''), ''''), '''마이그레이션'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_USER_POINT_HIST h
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = h.USER_IDX);

-- T_MILEAGE_LOG 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_mileage_log (user_id, transaction_type, mileage_amount, balance_after, reference_type, reference_id, description, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    SOURCE_TYPE, ', ',
    ABS(AMOUNT), ', ',
    '(SELECT mileage_balance FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''', SOURCE_TYPE, ''', ',
    '''', IFNULL(SOURCE_ID, 'LEGACY'), ''', ',
    IFNULL(CONCAT('''', REPLACE(REASON, '''', ''''''), ''''), '''마이그레이션'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_MILEAGE_SAVE
UNION ALL
SELECT CONCAT(
    'INSERT INTO t_mileage_log (user_id, transaction_type, mileage_amount, balance_after, reference_type, reference_id, description, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''USE'', ',
    ABS(USE_AMOUNT), ', ',
    '(SELECT mileage_balance FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''', SOURCE_TYPE, ''', ',
    '''', IFNULL(SOURCE_ID, 'LEGACY'), ''', ',
    IFNULL(CONCAT('''', REPLACE(REASON, '''', ''''''), ''''), '''마일리지 사용'''), ', ',
    '''', DATE_FORMAT(USE_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_MILEAGE_USAGE;
```

## 4. Community Domain
### 4.1 후기 (TBL_CS_REVIEW → T_REVIEW)
```sql
-- 먼저 상담 세션 생성 (리뷰를 위한 더미 세션)

SELECT CONCAT(
    'INSERT INTO t_consultation_session (user_id, counselor_nickname, consultation_type, status, total_point_used, user_rating, user_review, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX LIMIT 1), 
    '''), ',
    '''', (SELECT NICK_NAME FROM TBL_CS WHERE IDX = r.CS_IDX LIMIT 1), ''', ',
    '''CHAT'', ',
    '''COMPLETED'', ',
    '0, ',
    '5, ',  -- 기본 평점
    IFNULL(CONCAT('''', REPLACE(r.USER_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    '''', DATE_FORMAT(r.USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_REVIEW r
WHERE r.SHOW_YN = 'Y'
  AND EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = r.CS_IDX);

-- T_REVIEW 마이그레이션 (세션 생성 후 실행)
SELECT CONCAT(
    'INSERT INTO t_review (session_seq, user_id, counselor_nickname, rating, content, counselor_reply, is_best, is_visible, like_count, created_at, counselor_replied_at) ',
    'SELECT s.session_seq, s.user_id, s.counselor_nickname, 5, ',
    IFNULL(CONCAT('''', REPLACE(r.USER_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(r.CS_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    CASE WHEN r.BEST_YN = 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    CASE WHEN r.SHOW_YN = 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '0, ',
    '''', DATE_FORMAT(r.USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''', ',
    IFNULL(CONCAT('''', DATE_FORMAT(r.CS_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'),
    ' FROM t_consultation_session s ',
    'WHERE s.user_id = (SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX LIMIT 1), ''') ',
    'AND s.counselor_nickname = ''', 
    (SELECT NICK_NAME FROM TBL_CS WHERE IDX = r.CS_IDX LIMIT 1), ''' ',
    'ORDER BY s.created_at DESC LIMIT 1;'
) AS insert_query
FROM TBL_CS_REVIEW r
WHERE r.SHOW_YN = 'Y'
  AND EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = r.CS_IDX);
```

## 5. System Domain
### 5.1 FAQ (TBL_ADMIN_FAQ → T_INQUIRY)
```sql
-- T_INQUIRY 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_inquiry (user_id, category, title, content, status, admin_id, admin_reply, answered_at, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = f.USER_IDX LIMIT 1), 
    '''), ',
    CASE USER_TYPE
        WHEN 'USER' THEN '''GENERAL'''
        WHEN 'CS' THEN '''CONSULTATION'''
        ELSE '''GENERAL'''
    END, ', ',
    IFNULL(CONCAT('''', REPLACE(USER_TITLE, '''', ''''''), ''''), '''문의사항'''), ', ',
    IFNULL(CONCAT('''', REPLACE(USER_CONT, '''', ''''''), ''''), '''내용 없음'''), ', ',
    CASE 
        WHEN ADMIN_CONT IS NOT NULL THEN '''ANSWERED'''
        ELSE '''PENDING'''
    END, ', ',
    '''admin'', ',
    IFNULL(CONCAT('''', REPLACE(ADMIN_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(ADMIN_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    '''', DATE_FORMAT(USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_ADMIN_FAQ f
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = f.USER_IDX);
```

### 5.2 배너 (TBL_BANNER → T_BANNER)
```sql
-- T_BANNER 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_banner (banner_code, banner_name, banner_type, image_url, link_url, link_target, display_order, is_active, valid_from, valid_until, created_at) VALUES (',
    '''BNR_LEGACY_', BANNER_IDX, ''', ',
    IFNULL(CONCAT('''', REPLACE(BANNER_NM, '''', ''''''), ''''), '''배너'''), ', ',
    '''MAIN'', ',
    IFNULL(CONCAT('''', REPLACE(BANNER_IMG, '''', ''''''), ''''), '''/default.jpg'''), ', ',
    IFNULL(CONCAT('''', REPLACE(RANDING_URL, '''', ''''''), ''''), 'NULL'), ', ',
    '''', IFNULL(TARGET, 'SELF'), ''', ',
    IFNULL(ORD, 0), ', ',
    CASE SHOW_YN WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '''', IFNULL(DATE_FORMAT(START_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(END_DATE, '%Y-%m-%d %H:%i:%s'), DATE_ADD(NOW(), INTERVAL 1 YEAR)), ''', ',
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), '''',
    ');'
) AS insert_query
FROM TBL_BANNER;
```

### 5.3 공지사항 (TBL_CS_NOTICE → T_NOTICE)
```sql
-- T_NOTICE 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_notice (category, title, content, is_important, is_active, admin_id, created_at) VALUES (',
    '''GENERAL'', ',
    IFNULL(CONCAT('''', REPLACE(TITLE, '''', ''''''), ''''), '''공지사항'''), ', ',
    IFNULL(CONCAT('''', REPLACE(CONT, '''', ''''''), ''''), '''내용 없음'''), ', ',
    'FALSE, ',
    'TRUE, ',
    '''admin'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_NOTICE;
```

### 5.4 이벤트 (TBL_EVENT → T_EVENT)
```sql
-- T_EVENT 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_event (event_code, event_name, event_type, description, reward_type, reward_value, is_active, valid_from, valid_until, created_at) VALUES (',
    '''EVT_LEGACY_', IDX, ''', ',
    IFNULL(CONCAT('''', REPLACE(NAME, '''', ''''''), ''''), '''이벤트'''), ', ',
    '''POINT'', ',
    IFNULL(CONCAT('''', REPLACE(INFO, '''', ''''''), ''''), '''이벤트 설명'''), ', ',
    '''POINT'', ',
    IFNULL(POINT, 0), ', ',
    CASE USE_YN WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '''', IFNULL(DATE_FORMAT(START_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(END_DATE, '%Y-%m-%d %H:%i:%s'), DATE_ADD(NOW(), INTERVAL 1 MONTH)), ''', ',
    '''', NOW(), '''',
    ');'
) AS insert_query
FROM TBL_EVENT;
```

### 5.5 등급 (TBL_GRADE → T_GRADE)
```sql
-- T_GRADE 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_grade (grade_code, grade_name, grade_level, min_purchase_amount, point_earn_rate, discount_rate, benefits, grade_image_url, description, is_active, created_at) VALUES (',
    '''', GRADE, ''', ',
    '''', GRADE_NM, ''', ',
    GRADE, ', ',
    PURCHASE_AMOUNT, ', ',
    SAVE_VALUE, ', ',
    DISCOUNT_VALUE, ', ',
    '''{}''::jsonb, ',
    IFNULL(CONCAT('''', REPLACE(GRADE_IMG, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(DESCRIPTION, '''', ''''''), ''''), 'NULL'), ', ',
    'TRUE, ',
    '''', NOW(), '''',
    ');'
) AS insert_query
FROM TBL_GRADE;
```

## 6. Log Domain
### 6.1 검색 로그 (TBL_LOG_SEARCH → T_SEARCH_LOG)
```sql
-- T_SEARCH_LOG 마이그레이션

SELECT CONCAT(
    'INSERT INTO t_search_log (user_id, search_type, keyword, result_count, created_at) VALUES (',
    CASE 
        WHEN USER_IDX IS NOT NULL THEN 
            CONCAT('(SELECT user_id FROM t_user WHERE user_id = ''', 
                (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX LIMIT 1), ''')')
        ELSE 'NULL'
    END, ', ',
    USER_TYPE, ', ',
    '''', REPLACE(KEYWORD, '''', ''''''), ''', ',
    '0, ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_LOG_SEARCH l
WHERE KEYWORD IS NOT NULL AND USER_IDX != 0;
```

## 7. 실행 순서 및 주의사항
```sql
-- 실행 순서
-- 1. 기본 마스터 데이터
--    T_GRADE, T_SYSTEM_CONFIG (수동 입력)

-- 2. 사용자 도메인
--    T_USER → T_USER_PREFERENCE

-- 3. 상담사 도메인
--    T_COUNSELOR → T_COUNSELOR_PRICING

-- 4. 결제 도메인
--    T_POINT_PRODUCT (수동) → T_PAYMENT → T_POINT_LOG → T_MILEAGE_LOG

-- 5. 상담 도메인 (더미 데이터)
--    T_CONSULTATION_SESSION (리뷰용 더미)

-- 6. 커뮤니티 도메인
--    T_REVIEW → T_INQUIRY

-- 7. 시스템 도메인
--    T_ADMIN (수동) → T_BANNER → T_NOTICE → T_EVENT

-- 8. 로그 도메인
--    각종 _LOG 테이블

-- PostgreSQL에서 실행 전 설정
SET client_encoding = 'UTF8';
SET datestyle = 'ISO, YMD';
```

## 주의사항:
- REPLACE(column, '''', '''''') : 작은따옴표 이스케이프 처리
- 날짜 포맷: MariaDB DATE_FORMAT → PostgreSQL 형식
- NULL 처리: IFNULL → PostgreSQL에서는 COALESCE 사용
- JSONB 타입: ::jsonb 캐스팅 필요
- 외래키 참조: 부모 테이블 먼저 마이그레이션




