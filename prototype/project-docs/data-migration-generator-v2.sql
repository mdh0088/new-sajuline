-- =====================================================
-- MariaDB → PostgreSQL 최종 마이그레이션 쿼리
-- Version: Final v3.0
-- Date: 2025-01-01
-- =====================================================

-- =====================================================
-- PART 1: User Domain (사용자 관련)
-- =====================================================

-- 1.1 사용자 기본 정보 (TBL_USER → t_user)
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
    'FALSE, ',  -- is_marketing_agreed
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

-- 1.2 사용자 선호도 (신규 테이블, 기본값으로 생성)
SELECT CONCAT(
    'INSERT INTO t_user_preference (user_id) VALUES (''', USER_ID, ''');'
) AS insert_query
FROM TBL_USER
WHERE USER_STATUS != '3' AND USER_ID IS NOT NULL;

-- 1.3 사용자 로그인 이력 (TBL_LOG_USER_LOGIN → t_user_activity_log)
SELECT CONCAT(
    'INSERT INTO t_user_activity_log (user_id, activity_type, activity_detail, ip_address, user_agent, device_type, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX LIMIT 1), 
    '''), ',
    '''LOGIN'', ',
    '''{"type": "', IFNULL(TYPE, 'common'), '", "os": "', REPLACE(IFNULL(OS, 'Unknown'), '"', '\\"'), '"}'', ',
    CASE 
        WHEN IP REGEXP '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' 
        THEN CONCAT('''', IP, '''::inet')
        ELSE 'NULL'
    END, ', ',
    '''', IFNULL(OS, 'Unknown'), ''', ',
    '''PC'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_LOG_USER_LOGIN l
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = l.USER_IDX)
  AND REGIST_DATE >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
ORDER BY REGIST_DATE DESC
LIMIT 10000;

-- 1.4 탈퇴 유저 정보 (TBL_USER_EX → t_user_activity_log)
SELECT CONCAT(
    'INSERT INTO t_user_activity_log (user_id, activity_type, activity_detail, created_at) VALUES (',
    '''WITHDRAWN_', USER_IDX, ''', ',
    '''WITHDRAWAL'', ',
    '''{"original_user_id": "', IFNULL(USER_ID, ''), 
    '", "nickname": "', IFNULL(REPLACE(NICK_NAME, '"', '\\"'), ''), 
    '", "phone": "', IFNULL(PHONE, ''), 
    '", "email": "', IFNULL(EMAIL, ''), '"}'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_USER_EX;

-- =====================================================
-- PART 2: Counselor Domain (상담사 관련)
-- =====================================================

-- 2.1 상담사 정보 (TBL_CS → t_counselor)
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

-- 2.2 상담사 가격 정책 (TBL_CS → t_counselor_pricing)
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

-- =====================================================
-- PART 3: Payment Domain (결제/포인트)
-- =====================================================

-- 3.1 포인트 상품 (TBL_PRODUCT → t_point_product)
SELECT CONCAT(
    'INSERT INTO t_point_product (product_code, product_name, point_amount, price, bonus_point, discount_rate, display_order, is_active, valid_from, valid_until, created_at) VALUES (',
    '''PNT_', LPAD(IDX, 6, '0'), ''', ',
    '''', REPLACE(PRODUCT_NAME, '''', ''''''), ''', ',
    PRODUCT_VALUE, ', ',
    PRODUCT_VALUE, ', ',
    ROUND(PRODUCT_VALUE * SAVE_VALUE / 100), ', ',
    DISCOUNT_VALUE, ', ',
    IFNULL(ORD, 0), ', ',
    CASE IS_USE WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(START_DT, '%Y-%m-%d %H:%i:%s'), ''''), '''2025-01-01'''), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(END_DT, '%Y-%m-%d %H:%i:%s'), ''''), '''2030-12-31'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_PRODUCT;

-- 3.2 마일리지 상품 (TBL_MILEAGE_PRODUCT → t_point_product)
SELECT CONCAT(
    'INSERT INTO t_point_product (product_code, product_name, point_amount, price, bonus_point, display_order, is_active, description, created_at) VALUES (',
    '''MLP_', LPAD(M_PRODUCT_IDX, 6, '0'), ''', ',
    '''', REPLACE(M_PRODUCT_NAME, '''', ''''''), ''', ',
    CHARGE_POINT, ', ',
    M_PRODUCT_VALUE, ', ',
    '0, ',
    IFNULL(ORD, 0), ', ',
    CASE IS_USE WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    IFNULL(CONCAT('''', REPLACE(DESCRIPTION, '''', ''''''), ''''), '''마일리지 상품'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_MILEAGE_PRODUCT;

-- 3.3 결제 내역 (TBL_USER_TRADE → t_payment)
SELECT CONCAT(
    'INSERT INTO t_payment (order_no, user_id, payment_type, amount, point_amount, mileage_used, payment_method, payment_status, pg_provider, pg_tid, pg_response, paid_at, cancelled_at, cancel_reason, refund_amount, created_at) VALUES (',
    '''', ORDER_NO, ''', ',
    '(SELECT user_id FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''POINT_CHARGE'', ',
    IFNULL(AMOUNT, 0), ', ',
    IFNULL(USER_POINT, 0), ', ',
    '0, ',
    CASE 
        WHEN PGCODE = 'card' THEN '''CARD'''
        WHEN PGCODE = 'bank' THEN '''BANK_TRANSFER'''
        WHEN PGCODE = 'kakao' THEN '''KAKAO_PAY'''
        ELSE '''CARD'''
    END, ', ',
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
    CASE
        WHEN PAY_TYPE = 'CANCEL' AND CANCEL_DATE IS NOT NULL
        THEN CONCAT('''', CANCEL_DATE, '''')
        ELSE 'NULL'
    END, ', ',
    'NULL, ',
    IFNULL(CANCEL_AMOUNT, '0'), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_USER_TRADE t
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID)
  AND ORDER_NO IS NOT NULL;

-- 3.4 포인트 이력 (TBL_USER_POINT_HIST → t_point_log)
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

-- 3.5 마일리지 적립 이력 (TBL_MILEAGE_SAVE → t_mileage_log)
SELECT CONCAT(
    'INSERT INTO t_mileage_log (user_id, transaction_type, mileage_amount, balance_after, reference_type, reference_id, description, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''EARN'', ',
    ABS(AMOUNT), ', ',
    '(SELECT mileage_balance FROM t_user WHERE user_id = ''', USER_ID, '''), ',
    '''', SOURCE_TYPE, ''', ',
    '''', IFNULL(SOURCE_ID, 'LEGACY'), ''', ',
    IFNULL(CONCAT('''', REPLACE(REASON, '''', ''''''), ''''), '''마이그레이션'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_MILEAGE_SAVE;

-- 3.6 마일리지 사용 이력 (TBL_MILEAGE_USAGE → t_mileage_log)
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

-- 3.7 마일리지 잔액 업데이트 (TBL_MILEAGE_BALANCE → t_user)
SELECT CONCAT(
    'UPDATE t_user SET mileage_balance = ', AVAILABLE_MILEAGE, 
    ' WHERE user_id = ''', USER_ID, ''';'
) AS update_query
FROM TBL_MILEAGE_BALANCE
WHERE EXISTS (SELECT 1 FROM t_user WHERE user_id = TBL_MILEAGE_BALANCE.USER_ID);

-- =====================================================
-- PART 4: Consultation Domain (상담 관련)
-- =====================================================

-- 4.1 카카오 알림 대기자 (TBL_KAKAO_ALARM_WAIT_LIST → t_consultation_queue)
SELECT CONCAT(
    'INSERT INTO t_consultation_queue (user_id, counselor_nickname, priority, status, queued_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = w.USER_IDX LIMIT 1), 
    '''), ',
    '''', (SELECT NICK_NAME FROM TBL_CS WHERE IDX = w.CS_IDX LIMIT 1), ''', ',
    '0, ',
    '''WAITING'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_KAKAO_ALARM_WAIT_LIST w
WHERE USER_IDX IS NOT NULL 
  AND CS_IDX IS NOT NULL
  AND EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = w.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = w.CS_IDX);

-- =====================================================
-- PART 5: Community Domain (커뮤니티)
-- =====================================================

-- 5.1 상담 세션 생성 - 리뷰를 위한 더미 (TBL_CS_REVIEW)
SELECT CONCAT(
    'INSERT INTO t_consultation_session (user_id, counselor_nickname, consultation_type, status, total_point_used, user_rating, user_review, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX LIMIT 1), 
    '''), ',
    '''', (SELECT NICK_NAME FROM TBL_CS WHERE IDX = r.CS_IDX LIMIT 1), ''', ',
    '''CHAT'', ',
    '''COMPLETED'', ',
    '0, ',
    '5, ',
    IFNULL(CONCAT('''', REPLACE(r.USER_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    '''', DATE_FORMAT(r.USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_REVIEW r
WHERE r.SHOW_YN = 'Y'
  AND EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = r.CS_IDX);

-- 5.2 리뷰 (TBL_CS_REVIEW → t_review)
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

-- 5.3 리뷰 좋아요 (TBL_CS_REVIEW_LIKE → t_review_like)
SELECT CONCAT(
    'INSERT INTO t_review_like (user_id, review_seq, created_at) ',
    'SELECT ',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX LIMIT 1), 
    '''), ',
    '(SELECT review_seq FROM t_review r ',
    'JOIN t_consultation_session s ON r.session_seq = s.session_seq ',
    'WHERE s.user_id = (SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER u2 WHERE u2.IDX = (SELECT USER_IDX FROM TBL_CS_REVIEW WHERE IDX = l.REVIEW_IDX) LIMIT 1), 
    ''') ',
    'AND s.counselor_nickname = ''', 
    (SELECT NICK_NAME FROM TBL_CS c WHERE c.IDX = (SELECT CS_IDX FROM TBL_CS_REVIEW WHERE IDX = l.REVIEW_IDX) LIMIT 1), 
    ''' ORDER BY s.created_at DESC LIMIT 1), ',
    '''', DATE_FORMAT(l.REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''' ',
    'WHERE EXISTS (SELECT 1 FROM t_review r2 ',
    'JOIN t_consultation_session s2 ON r2.session_seq = s2.session_seq ',
    'WHERE s2.user_id = (SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER u3 WHERE u3.IDX = (SELECT USER_IDX FROM TBL_CS_REVIEW WHERE IDX = l.REVIEW_IDX) LIMIT 1), 
    '''));'
) AS insert_query
FROM TBL_CS_REVIEW_LIKE l
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = l.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS_REVIEW r WHERE r.IDX = l.REVIEW_IDX);

-- 5.4 더미 리뷰 (TBL_CS_REVIEW_DUMY → t_review_dummy)
SELECT CONCAT(
    'INSERT INTO t_review_dummy (user_nickname, counselor_nickname, chat_duration, content, counselor_reply, created_at, legacy_idx) VALUES (',
    IFNULL(CONCAT('''', REPLACE(USER_ID, '''', ''''''), ''''), '''익명'''), ', ',
    '''', (SELECT NICK_NAME FROM TBL_CS WHERE IDX = d.CS_IDX LIMIT 1), ''', ',
    IFNULL(CONCAT('''', CHAT_TIME, ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', REPLACE(USER_CONT, '''', ''''''), ''''), '''좋은 상담이었습니다'''), ', ',
    IFNULL(CONCAT('''', REPLACE(CS_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    '''', IFNULL(DATE_FORMAT(USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    IDX,
    ');'
) AS insert_query
FROM TBL_CS_REVIEW_DUMY d
WHERE EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = d.CS_IDX)
LIMIT 1000;

-- 5.5 신고 (TBL_CS_REPORT → t_report)
SELECT CONCAT(
    'INSERT INTO t_report (reporter_id, report_type, target_id, reason_type, reason_detail, status, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX LIMIT 1), 
    '''), ',
    '''REVIEW'', ',
    '''REVIEW_', REVIEW_IDX, ''', ',
    CASE TYPE
        WHEN 1 THEN '''SPAM'''
        WHEN 2 THEN '''PRIVACY'''
        WHEN 3 THEN '''ILLEGAL'''
        WHEN 4 THEN '''ABUSE'''
        WHEN 5 THEN '''ABUSE'''
        ELSE '''OTHER'''
    END, ', ',
    IFNULL(CONCAT('''', REPLACE(CONT, '''', ''''''), ''''), '''신고 내용'''), ', ',
    '''PENDING'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_REPORT r
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX);

-- 5.6 유저 문의 (TBL_ADMIN_FAQ → t_inquiry)
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

-- 5.7 상담사 문의 (TBL_CS_ADMIN_FAQ → t_inquiry)
SELECT CONCAT(
    'INSERT INTO t_inquiry (user_id, category, title, content, status, admin_id, admin_reply, answered_at, created_at) VALUES (',
    '''CS_', (SELECT CODE FROM TBL_CS WHERE IDX = f.CS_IDX LIMIT 1), ''', ',
    '''COUNSELOR'', ',
    '''상담사 문의사항'', ',
    IFNULL(CONCAT('''', REPLACE(CS_CONT, '''', ''''''), ''''), '''문의 내용'''), ', ',
    CASE 
        WHEN ADMIN_CONT IS NOT NULL THEN '''ANSWERED'''
        ELSE '''PENDING'''
    END, ', ',
    '''admin'', ',
    IFNULL(CONCAT('''', REPLACE(ADMIN_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(ADMIN_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    '''', DATE_FORMAT(CS_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_ADMIN_FAQ f
WHERE EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = f.CS_IDX);

-- 5.8 상담사-유저 FAQ (TBL_CS_FAQ → t_inquiry)
SELECT CONCAT(
    'INSERT INTO t_inquiry (user_id, category, title, content, status, admin_id, admin_reply, answered_at, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = f.USER_IDX LIMIT 1), 
    '''), ',
    '''CONSULTATION'', ',
    '''상담 문의'', ',
    IFNULL(CONCAT('''', REPLACE(USER_CONT, '''', ''''''), ''''), '''문의 내용'''), ', ',
    CASE 
        WHEN CS_CONT IS NOT NULL THEN '''ANSWERED'''
        ELSE '''PENDING'''
    END, ', ',
    '''CS_', (SELECT CODE FROM TBL_CS WHERE IDX = f.CS_IDX LIMIT 1), ''', ',
    IFNULL(CONCAT('''', REPLACE(CS_CONT, '''', ''''''), ''''), 'NULL'), ', ',
    IFNULL(CONCAT('''', DATE_FORMAT(CS_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    '''', DATE_FORMAT(USER_REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_CS_FAQ f
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = f.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = f.CS_IDX);

-- =====================================================
-- PART 6: System Domain (시스템)
-- =====================================================

-- 6.1 관리자 (TBL_MANAGER → t_admin)
SELECT CONCAT(
    'INSERT INTO t_admin (admin_id, email, password_hash, name, role, department, is_active, permissions, last_login_at, created_at) VALUES (',
    '''ADM_', LPAD(MANAGER_SEQ, 6, '0'), ''', ',
    '''', REPLACE(MANAGER_ID, '''', ''''''), '@sajuline.com'', ',
    '''', REPLACE(PASSWORD, '''', ''''''), ''', ',
    '''', REPLACE(NAME, '''', ''''''), ''', ',
    CASE AUTH
        WHEN 'SUPER' THEN '''SUPER'''
        WHEN 'ADMIN' THEN '''MANAGER'''
        ELSE '''CS'''
    END, ', ',
    '''운영팀'', ',
    CASE ACTIVE_YN WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '''{}''::jsonb, ',
    IFNULL(CONCAT('''', DATE_FORMAT(LAST_LOGIN, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    '''', IFNULL(DATE_FORMAT(REG_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), '''',
    ');'
) AS insert_query
FROM TBL_MANAGER;

-- 6.2 배너 (TBL_BANNER → t_banner)
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

-- 6.3 팝업 (TBL_POPUP → t_banner)
SELECT CONCAT(
    'INSERT INTO t_banner (banner_code, banner_name, banner_type, image_url, link_url, link_target, display_order, is_active, valid_from, valid_until, created_at) VALUES (',
    '''POP_LEGACY_', POPUP_IDX, ''', ',
    IFNULL(CONCAT('''', REPLACE(POPUP_NM, '''', ''''''), ''''), '''팝업'''), ', ',
    '''POPUP'', ',
    IFNULL(CONCAT('''', REPLACE(POPUP_IMG, '''', ''''''), ''''), '''/default.jpg'''), ', ',
    IFNULL(CONCAT('''', REPLACE(RANDING_URL, '''', ''''''), ''''), 'NULL'), ', ',
    '''', IFNULL(TARGET, 'SELF'), ''', ',
    IFNULL(ORD, 0), ', ',
    CASE SHOW_YN WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '''', IFNULL(DATE_FORMAT(START_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(END_DATE, '%Y-%m-%d %H:%i:%s'), DATE_ADD(NOW(), INTERVAL 1 YEAR)), ''', ',
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), '''',
    ');'
) AS insert_query
FROM TBL_POPUP;

-- 6.4 공지사항 (TBL_CS_NOTICE → t_notice)
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

-- 6.5 이벤트 (TBL_EVENT → t_event)
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

-- 6.6 등급 (TBL_GRADE → t_grade)
SELECT CONCAT(
    'INSERT INTO t_grade (grade_code, grade_name, grade_level, min_purchase_amount, point_earn_rate, discount_rate, benefits, grade_image_url, description, is_active, created_at) VALUES (',
    '''', GRADE, ''', ',
    '''', GRADE_NM, ''', ',
    CASE GRADE
        WHEN 'WHITE' THEN '1'
        WHEN 'SILVER' THEN '2'
        WHEN 'GOLD' THEN '3'
        WHEN 'PLATINUM' THEN '4'
        ELSE '5'
    END, ', ',
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

-- 6.7 기획전 (TBL_EXHIBITION → t_exhibition)
SELECT CONCAT(
    'INSERT INTO t_exhibition (exhibition_code, exhibition_name, description, banner_image_url, is_active, valid_from, valid_until, created_at, legacy_idx) VALUES (',
    '''EXH_LEGACY_', EXHIBITION_IDX, ''', ',
    IFNULL(CONCAT('''', REPLACE(EXHIBITION_NM, '''', ''''''), ''''), '''기획전'''), ', ',
    '''레거시 기획전 데이터'', ',
    IFNULL(CONCAT('''', REPLACE(BANNER_IMG, '''', ''''''), ''''), 'NULL'), ', ',
    CASE SHOW_YN WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END, ', ',
    '''', IFNULL(DATE_FORMAT(START_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    '''', IFNULL(DATE_FORMAT(END_DATE, '%Y-%m-%d %H:%i:%s'), DATE_ADD(NOW(), INTERVAL 1 MONTH)), ''', ',
    '''', IFNULL(DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    EXHIBITION_IDX,
    ');'
) AS insert_query
FROM TBL_EXHIBITION;

-- 6.8 기획전 리뷰 - 더미 세션 생성 (TBL_EXHIBITION_REPLY)
SELECT CONCAT(
    'INSERT INTO t_consultation_session (user_id, counselor_nickname, consultation_type, status, total_point_used, user_rating, user_review, created_at) VALUES (',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX LIMIT 1), 
    '''), ',
    '''SYSTEM_BOT'', ',
    '''CHAT'', ',
    '''COMPLETED'', ',
    '0, ',
    '5, ',
    IFNULL(CONCAT('''기획전 참여 후기: ', REPLACE(r.USER_CONT, '''', ''''''), ''''), '''기획전 참여'''), ', ',
    '''', DATE_FORMAT(r.REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_EXHIBITION_REPLY r
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX);

-- =====================================================
-- PART 7: Notification Domain (알림)
-- =====================================================

-- 7.1 카카오 알림 템플릿 (TBL_KAKAO_ALARM_TEMPLATE → t_system_config)
SELECT CONCAT(
    'INSERT INTO t_system_config (config_key, config_value, config_type, description, is_active, is_public) VALUES (',
    '''kakao.template.', CODE, ''', ',
    '''{"name": "', REPLACE(NAME, '"', '\\"'), 
    '", "content": "', REPLACE(REPLACE(CONTENT, '"', '\\"'), CHAR(10), '\\n'), 
    '", "pc_link": "', IFNULL(PC_LINK, ''), 
    '", "mo_link": "', IFNULL(MO_LINK, ''), '"}'', ',
    '''JSON'', ',
    '''카카오 알림 템플릿: ', REPLACE(NAME, '''', ''''''), ''', ',
    'TRUE, ',
    'FALSE',
    ');'
) AS insert_query
FROM TBL_KAKAO_ALARM_TEMPLATE;

-- 7.2 카카오 알림 이력 (TBL_KAKAO_ALARM_HISTORY → t_user_activity_log)
SELECT CONCAT(
    'INSERT INTO t_user_activity_log (user_id, activity_type, activity_detail, created_at) VALUES (',
    CASE 
        WHEN USER_TYPE = 'USER' AND USER_IDX IS NOT NULL THEN 
            CONCAT('(SELECT user_id FROM t_user WHERE user_id = ''', 
                (SELECT USER_ID FROM TBL_USER WHERE IDX = h.USER_IDX LIMIT 1), ''')')
        WHEN USER_TYPE = 'CS' AND USER_IDX IS NOT NULL THEN 
            CONCAT('''CS_', (SELECT CODE FROM TBL_CS WHERE IDX = h.USER_IDX LIMIT 1), '''')
        ELSE '''SYSTEM'''
    END, ', ',
    '''NOTIFICATION'', ',
    '''{"type": "KAKAO", "template_code": "', IFNULL(CODE, ''), 
    '", "message": "', REPLACE(REPLACE(SEND_CONT, '"', '\\"'), CHAR(10), '\\n'), 
    '", "result_code": ', IFNULL(RESULT_CODE, 0), 
    ', "transaction_no": "', IFNULL(NO, ''), '"}'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_KAKAO_ALARM_HISTORY h
WHERE (USER_TYPE = 'USER' AND EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = h.USER_IDX))
   OR (USER_TYPE = 'CS' AND EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = h.USER_IDX))
   OR USER_TYPE NOT IN ('USER', 'CS');

-- =====================================================
-- PART 8: Log Domain (로그)
-- =====================================================

-- 8.1 일일 접속 로그 (TBL_LOG_DAILY → t_user_activity_log)
SELECT CONCAT(
    'INSERT INTO t_user_activity_log (user_id, activity_type, activity_detail, ip_address, user_agent, device_type, created_at) VALUES (',
    '''GUEST_', DATE_FORMAT(REGIST_DATE, '%Y%m%d'), '_', LPAD(IDX, 10, '0'), ''', ',
    '''VIEW'', ',
    '''{"url": "', REPLACE(URL, '"', '\\"'), '"}'', ',
    CASE 
        WHEN IP REGEXP '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' 
        THEN CONCAT('''', IP, '''::inet')
        ELSE 'NULL'
    END, ', ',
    IFNULL(CONCAT('''', REPLACE(USER_AGENT, '''', ''''''), ''''), '''Unknown'''), ', ',
    IFNULL(CONCAT('''', DEVICE_TYPE, ''''), '''PC'''), ', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_LOG_DAILY
WHERE REGIST_DATE >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
ORDER BY REGIST_DATE DESC
LIMIT 10000;

-- 8.2 검색 로그 (TBL_LOG_SEARCH → t_search_log)
SELECT CONCAT(
    'INSERT INTO t_search_log (user_id, search_type, keyword, result_count, created_at) VALUES (',
    CASE 
        WHEN USER_IDX IS NOT NULL THEN 
            CONCAT('(SELECT user_id FROM t_user WHERE user_id = ''', 
                (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX LIMIT 1), ''')')
        ELSE 'NULL'
    END, ', ',
    CASE USER_TYPE
        WHEN 'USER' THEN '''GENERAL'''
        WHEN 'CS' THEN '''COUNSELOR'''
        ELSE '''GENERAL'''
    END, ', ',
    '''', REPLACE(KEYWORD, '''', ''''''), ''', ',
    '0, ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_LOG_SEARCH l
WHERE KEYWORD IS NOT NULL AND USER_IDX != 0;

-- 8.3 이벤트 참여 로그 (TBL_EVENT_LOG → t_event_participation_log)
SELECT CONCAT(
    'INSERT INTO t_event_participation_log (event_code, user_id, reward_type, reward_value, participation_data, created_at) VALUES (',
    '''EVT_LEGACY_', EVENT_IDX, ''', ',
    '(SELECT user_id FROM t_user WHERE user_id = ''', 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX LIMIT 1), 
    '''), ',
    '''POINT'', ',
    IFNULL(POINT, 0), ', ',
    '''{"info": "', REPLACE(REPLACE(INFO, '"', '\\"'), '''', ''''''), '"}'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_EVENT_LOG l
WHERE EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = l.USER_IDX)
  AND EXISTS (SELECT 1 FROM TBL_EVENT e WHERE e.IDX = l.EVENT_IDX);

-- 8.4 배치 실행 로그 (TBL_BATCH → t_batch_execution_log)
SELECT CONCAT(
    'INSERT INTO t_batch_execution_log (batch_name, batch_type, status, started_at, ended_at, total_processed, success_count, fail_count, execution_params) VALUES (',
    '''', REPLACE(ACTIVE_BATCH_NM, '''', ''''''), ''', ',
    CASE 
        WHEN BATCH_TYPE = 'AUTO' THEN '''GRADE'''
        WHEN BATCH_TYPE = 'MANUAL' THEN '''GRADE'''
        ELSE '''STATISTICS'''
    END, ', ',
    CASE STATUS
        WHEN 'COMPLETE' THEN '''SUCCESS'''
        WHEN 'FAILED' THEN '''FAILED'''
        WHEN 'RUNNING' THEN '''RUNNING'''
        ELSE '''SUCCESS'''
    END, ', ',
    '''', IFNULL(DATE_FORMAT(EXEC_START_DATE, '%Y-%m-%d %H:%i:%s'), NOW()), ''', ',
    IFNULL(CONCAT('''', DATE_FORMAT(EXEC_END_DATE, '%Y-%m-%d %H:%i:%s'), ''''), 'NULL'), ', ',
    IFNULL(TOTAL_COUNT, 0), ', ',
    IFNULL(SUCCESS_COUNT, 0), ', ',
    '0, ',
    '''{"target_date": "', TARGET_DATE, '", "type": "', BATCH_TYPE, '"}'', ',
    ');'
) AS insert_query
FROM TBL_BATCH;

-- 8.5 등급 변경 이력 (TBL_GRADE_HISTORY → t_grade_change_log)
SELECT CONCAT(
    'INSERT INTO t_grade_change_log (user_id, grade_before, grade_after, purchase_amount, calculation_period, change_reason, created_at) VALUES (',
    '''', USER_ID, ''', ',
    '''WHITE'', ',
    '''', IFNULL(GRADE, 'WHITE'), ''', ',
    IFNULL(PURCHASE_AMOUNT, 0), ', ',
    '''[', DATE_FORMAT(DATE_SUB(REGIST_DATE, INTERVAL 1 MONTH), '%Y-%m-%d'), ',', 
    DATE_FORMAT(REGIST_DATE, '%Y-%m-%d'), ')''::tsrange, ',
    '''MONTHLY_BATCH'', ',
    '''', DATE_FORMAT(REGIST_DATE, '%Y-%m-%d %H:%i:%s'), '''',
    ');'
) AS insert_query
FROM TBL_GRADE_HISTORY
WHERE PROCESS_STATUS = 'SUCCESS';

-- =====================================================
-- PART 9: Config Domain (설정)
-- =====================================================

-- 9.1 등급 배치 설정 (TBL_GRADE_BATCH_CONFIG → t_system_config)
SELECT CONCAT(
    'INSERT INTO t_system_config (config_key, config_value, config_type, description, is_active) VALUES (',
    '''grade.batch.config'', ',
    '''{"period_month": ', PERIOD_MONTH, 
    ', "period_day": ', PERIOD_DAY, 
    ', "is_use": "', IS_USE, '"}'', ',
    '''JSON'', ',
    '''등급 배치 설정'', ',
    CASE IS_USE WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END,
    ');'
) AS insert_query
FROM TBL_GRADE_BATCH_CONFIG
LIMIT 1;

-- 9.2 멤버십 배치 설정 (TBL_MEMBERSHIP_BATCH_CONFIG → t_system_config)
SELECT CONCAT(
    'INSERT INTO t_system_config (config_key, config_value, config_type, description, is_active) VALUES (',
    '''membership.batch.config'', ',
    '''{"period_month": ', PERIOD_MONTH, 
    ', "period_day": ', PERIOD_DAY, 
    ', "is_use": "', IS_USE, '"}'', ',
    '''JSON'', ',
    '''멤버십 배치 설정'', ',
    CASE IS_USE WHEN 'Y' THEN 'TRUE' ELSE 'FALSE' END,
    ');'
) AS insert_query
FROM TBL_MEMBERSHIP_BATCH_CONFIG
LIMIT 1;

-- 9.3 마일리지 설정 (TBL_MILEAGE_CONFIG → t_system_config)
SELECT CONCAT(
    'INSERT INTO t_system_config (config_key, config_value, config_type, description, is_active) VALUES (',
    '''mileage.', CONFIG_KEY, ''', ',
    '''', CONFIG_VALUE, ''', ',
    '''STRING'', ',
    IFNULL(CONCAT('''', REPLACE(DESCRIPTION, '''', ''''''), ''''), '''마일리지 설정'''), ', ',
    'TRUE',
    ');'
) AS insert_query
FROM TBL_MILEAGE_CONFIG;

-- =====================================================
-- PART 10: 후처리 쿼리
-- =====================================================

-- 10.1 사용자 포인트 잔액 재계산
SELECT 'UPDATE t_user u SET point_balance = COALESCE((
    SELECT SUM(CASE 
        WHEN transaction_type IN (''CHARGE'', ''BONUS'', ''EVENT'', ''REFUND'') THEN point_amount
        ELSE -point_amount
    END)
    FROM t_point_log
    WHERE user_id = u.user_id
), 0);' AS update_query;

-- 10.2 상담사 통계 정보 업데이트
SELECT 'UPDATE t_counselor c SET 
    rating_avg = COALESCE((SELECT AVG(rating)::NUMERIC(3,2) FROM t_review WHERE counselor_nickname = c.nickname AND is_visible = TRUE), 0),
    rating_count = COALESCE((SELECT COUNT(*) FROM t_review WHERE counselor_nickname = c.nickname AND is_visible = TRUE), 0),
    consultation_count = COALESCE((SELECT COUNT(*) FROM t_consultation_session WHERE counselor_nickname = c.nickname AND status = ''COMPLETED''), 0);' 
AS update_query;

-- 10.3 시퀀스 재설정
SELECT 'SELECT reset_all_sequences();' AS execute_query;

-- 10.4 카카오 템플릿 마이그레이션
SELECT 'SELECT migrate_kakao_templates();' AS execute_query;

-- 10.5 데이터 정합성 체크
SELECT 'SELECT * FROM check_data_integrity();' AS execute_query;

-- 10.6 통계 정보 갱신
SELECT 'ANALYZE;' AS execute_query;