-- =====================================================
-- 마이그레이션 검증 쿼리
-- Version: 1.0
-- Date: 2025-01-01
-- 
-- 목적: 데이터 마이그레이션 후 정합성 검증
-- =====================================================

-- =====================================================
-- 1. 데이터 건수 검증
-- =====================================================

-- 1.1 전체 건수 비교
SELECT '=== 전체 데이터 건수 비교 ===' as title;

SELECT 
    'Users' as entity,
    (SELECT COUNT(*) FROM TBL_USER) as old_count,
    (SELECT COUNT(*) FROM t_user) as new_count,
    (SELECT COUNT(*) FROM TBL_USER) - (SELECT COUNT(*) FROM t_user) as diff
UNION ALL
SELECT 
    'Active Users' as entity,
    (SELECT COUNT(*) FROM TBL_USER WHERE USER_STATUS = '1') as old_count,
    (SELECT COUNT(*) FROM t_user WHERE user_status = 'ACTIVE') as new_count,
    (SELECT COUNT(*) FROM TBL_USER WHERE USER_STATUS = '1') - 
    (SELECT COUNT(*) FROM t_user WHERE user_status = 'ACTIVE') as diff
UNION ALL
SELECT 
    'Counselors (Approved)' as entity,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N') as old_count,
    (SELECT COUNT(*) FROM t_counselor) as new_count,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N') - 
    (SELECT COUNT(*) FROM t_counselor) as diff
UNION ALL
SELECT 
    'Counselor Applications' as entity,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'N' OR OUT_YN = 'Y') as old_count,
    (SELECT COUNT(*) FROM t_counselor_application) as new_count,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'N' OR OUT_YN = 'Y') - 
    (SELECT COUNT(*) FROM t_counselor_application) as diff
UNION ALL
SELECT 
    'Reviews' as entity,
    (SELECT COUNT(*) FROM TBL_CS_REVIEW) as old_count,
    (SELECT COUNT(*) FROM t_consultation_review) as new_count,
    (SELECT COUNT(*) FROM TBL_CS_REVIEW) - (SELECT COUNT(*) FROM t_consultation_review) as diff
UNION ALL
SELECT 
    'Payments' as entity,
    (SELECT COUNT(*) FROM TBL_USER_TRADE) as old_count,
    (SELECT COUNT(*) FROM t_payment) as new_count,
    (SELECT COUNT(*) FROM TBL_USER_TRADE) - (SELECT COUNT(*) FROM t_payment) as diff
UNION ALL
SELECT 
    'Notices' as entity,
    (SELECT COUNT(*) FROM TBL_CS_NOTICE) as old_count,
    (SELECT COUNT(*) FROM t_notice WHERE target_audience = 'COUNSELOR') as new_count,
    (SELECT COUNT(*) FROM TBL_CS_NOTICE) - 
    (SELECT COUNT(*) FROM t_notice WHERE target_audience = 'COUNSELOR') as diff;

-- 1.2 포인트/마일리지 거래 건수 검증
SELECT '=== 포인트/마일리지 거래 건수 ===' as title;

SELECT 
    'Point History' as entity,
    (SELECT COUNT(*) FROM TBL_USER_POINT_HIST) as old_count,
    (SELECT COUNT(*) FROM t_point_transaction WHERE currency_type = 'POINT') as new_count
UNION ALL
SELECT 
    'Mileage Save' as entity,
    (SELECT COUNT(*) FROM TBL_MILEAGE_SAVE) as old_count,
    (SELECT COUNT(*) FROM t_point_transaction WHERE currency_type = 'MILEAGE' AND transaction_type = 'EARN') as new_count
UNION ALL
SELECT 
    'Mileage Usage' as entity,
    (SELECT COUNT(*) FROM TBL_MILEAGE_USAGE) as old_count,
    (SELECT COUNT(*) FROM t_point_transaction WHERE currency_type = 'MILEAGE' AND transaction_type = 'USE') as new_count;

-- =====================================================
-- 2. 데이터 무결성 검증
-- =====================================================

-- 2.1 사용자 중복 검증
SELECT '=== 중복 데이터 검증 ===' as title;

SELECT 'Duplicate User Login IDs' as check_type, COUNT(*) as count
FROM (
    SELECT login_id, COUNT(*) as cnt
    FROM t_user
    GROUP BY login_id
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT 'Duplicate User Emails' as check_type, COUNT(*) as count
FROM (
    SELECT email, COUNT(*) as cnt
    FROM t_user
    GROUP BY email
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT 'Duplicate User Phones' as check_type, COUNT(*) as count
FROM (
    SELECT phone, COUNT(*) as cnt
    FROM t_user
    GROUP BY phone
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT 'Duplicate Counselor Codes' as check_type, COUNT(*) as count
FROM (
    SELECT counselor_code, COUNT(*) as cnt
    FROM t_counselor
    GROUP BY counselor_code
    HAVING COUNT(*) > 1
) t;

-- 2.2 외래키 무결성 검증
SELECT '=== 외래키 무결성 검증 ===' as title;

SELECT 'User Auth without User' as check_type, COUNT(*) as count
FROM t_user_auth ua
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = ua.user_id)
UNION ALL
SELECT 'Point Balance without User' as check_type, COUNT(*) as count
FROM t_user_point_balance pb
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = pb.user_id)
UNION ALL
SELECT 'Reviews without User' as check_type, COUNT(*) as count
FROM t_consultation_review r
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = r.user_id)
UNION ALL
SELECT 'Reviews without Counselor' as check_type, COUNT(*) as count
FROM t_consultation_review r
WHERE NOT EXISTS (SELECT 1 FROM t_counselor c WHERE c.counselor_id = r.counselor_id)
UNION ALL
SELECT 'Payments without User' as check_type, COUNT(*) as count
FROM t_payment p
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = p.user_id);

-- =====================================================
-- 3. 데이터 변환 검증
-- =====================================================

-- 3.1 상태 변환 검증
SELECT '=== 상태 변환 검증 ===' as title;

-- 사용자 상태
SELECT 
    'User Status Conversion' as check_type,
    old_status,
    new_status,
    count
FROM (
    SELECT 
        o.USER_STATUS as old_status,
        n.user_status as new_status,
        COUNT(*) as count
    FROM TBL_USER o
    JOIN t_user n ON o.IDX = n.user_id
    GROUP BY o.USER_STATUS, n.user_status
) t;

-- 상담사 상태
SELECT 
    'Counselor Status Conversion' as check_type,
    old_status,
    new_status,
    count
FROM (
    SELECT 
        o.STATUS as old_status,
        n.counselor_status as new_status,
        COUNT(*) as count
    FROM TBL_CS o
    JOIN t_counselor n ON o.IDX = n.counselor_id
    WHERE o.APPROVAL_YN = 'Y' AND o.OUT_YN = 'N'
    GROUP BY o.STATUS, n.counselor_status
) t;

-- 3.2 금액 데이터 검증
SELECT '=== 금액 데이터 검증 ===' as title;

-- 마일리지 잔액 비교
SELECT 
    'Mileage Balance Check' as check_type,
    COUNT(*) as total_users,
    SUM(CASE WHEN ABS(o.MILEAGE - n.mileage_balance) > 0 THEN 1 ELSE 0 END) as diff_count,
    SUM(ABS(o.MILEAGE - n.mileage_balance)) as total_diff
FROM TBL_USER o
JOIN t_user u ON o.IDX = u.user_id
JOIN t_user_point_balance n ON u.user_id = n.user_id;

-- 결제 금액 비교
SELECT 
    'Payment Amount Check' as check_type,
    COUNT(*) as total_payments,
    SUM(CASE WHEN ABS(CAST(o.AMOUNT AS DECIMAL) - n.amount) > 0.01 THEN 1 ELSE 0 END) as diff_count
FROM TBL_USER_TRADE o
JOIN t_payment n ON o.IDX = n.payment_id;

-- =====================================================
-- 4. 핵심 비즈니스 데이터 검증
-- =====================================================

-- 4.1 상담사 전문분야 검증
SELECT '=== 상담사 전문분야 검증 ===' as title;

SELECT 
    'Counselor Specialties' as check_type,
    old_count,
    new_count,
    old_count - new_count as diff
FROM (
    SELECT 
        (SELECT SUM(
            CASE WHEN TARO_YN = 'Y' THEN 1 ELSE 0 END +
            CASE WHEN LUCK_YN = 'Y' THEN 1 ELSE 0 END +
            CASE WHEN FORTUNE_YN = 'Y' THEN 1 ELSE 0 END +
            CASE WHEN EASY_YN = 'Y' THEN 1 ELSE 0 END
        ) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N') as old_count,
        (SELECT COUNT(*) FROM t_counselor_specialty) as new_count
) t;

-- 4.2 포인트 거래 합계 검증
SELECT '=== 포인트 거래 합계 검증 ===' as title;

-- 사용자별 포인트 합계
SELECT 
    'Point Transaction Total' as check_type,
    COUNT(*) as user_count,
    SUM(ABS(old_total - new_total)) as total_diff
FROM (
    SELECT 
        o.USER_IDX,
        SUM(o.ACTIVE_POINT) as old_total,
        IFNULL((
            SELECT SUM(amount) 
            FROM t_point_transaction 
            WHERE user_id = o.USER_IDX AND currency_type = 'POINT'
        ), 0) as new_total
    FROM TBL_USER_POINT_HIST o
    GROUP BY o.USER_IDX
) t
WHERE ABS(old_total - new_total) > 0;

-- =====================================================
-- 5. 데이터 품질 검증
-- =====================================================

-- 5.1 필수 필드 NULL 검증
SELECT '=== 필수 필드 NULL 검증 ===' as title;

SELECT 'Users with NULL email' as check_type, COUNT(*) as count
FROM t_user WHERE email IS NULL
UNION ALL
SELECT 'Users with NULL login_id' as check_type, COUNT(*) as count
FROM t_user WHERE login_id IS NULL
UNION ALL
SELECT 'Counselors with NULL code' as check_type, COUNT(*) as count
FROM t_counselor WHERE counselor_code IS NULL
UNION ALL
SELECT 'Payments with NULL order_no' as check_type, COUNT(*) as count
FROM t_payment WHERE order_no IS NULL;

-- 5.2 날짜 데이터 검증
SELECT '=== 날짜 데이터 검증 ===' as title;

SELECT 'Future dated records' as check_type, entity, COUNT(*) as count
FROM (
    SELECT 'User' as entity FROM t_user WHERE created_at > NOW()
    UNION ALL
    SELECT 'Counselor' as entity FROM t_counselor WHERE created_at > NOW()
    UNION ALL
    SELECT 'Payment' as entity FROM t_payment WHERE created_at > NOW()
    UNION ALL
    SELECT 'Review' as entity FROM t_consultation_review WHERE created_at > NOW()
) t
GROUP BY entity;

-- 5.3 비밀번호 해시 검증
SELECT '=== 비밀번호 보안 검증 ===' as title;

SELECT 
    'Plain text passwords' as check_type,
    COUNT(*) as count
FROM t_user_auth
WHERE password_hash IS NOT NULL 
    AND LENGTH(password_hash) < 30; -- bcrypt 해시는 보통 60자

-- =====================================================
-- 6. 성능 관련 인덱스 검증
-- =====================================================

-- 6.1 인덱스 존재 확인
SELECT '=== 인덱스 검증 ===' as title;

SELECT 
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as columns
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN (
        't_user', 't_counselor', 't_consultation_session',
        't_payment', 't_point_transaction', 't_consultation_review'
    )
    AND INDEX_NAME != 'PRIMARY'
GROUP BY TABLE_NAME, INDEX_NAME
ORDER BY TABLE_NAME, INDEX_NAME;

-- =====================================================
-- 7. 샘플 데이터 비교
-- =====================================================

-- 7.1 사용자 샘플 비교 (상위 10건)
SELECT '=== 사용자 데이터 샘플 비교 ===' as title;

SELECT 
    'OLD' as source,
    USER_ID as login_id,
    EMAIL as email,
    NICK_NAME as nickname,
    USER_STATUS as status,
    GRADE as grade
FROM TBL_USER
ORDER BY IDX
LIMIT 5
UNION ALL
SELECT 
    'NEW' as source,
    login_id,
    email,
    nickname,
    user_status as status,
    grade_code as grade
FROM t_user
ORDER BY user_id
LIMIT 5;

-- 7.2 결제 샘플 비교
SELECT '=== 결제 데이터 샘플 비교 ===' as title;

SELECT 
    'OLD' as source,
    ORDER_NO as order_no,
    USER_ID as user_id,
    AMOUNT as amount,
    PAY_TYPE as status,
    REGIST_DATE as created_at
FROM TBL_USER_TRADE
WHERE PAY_TYPE = 'SUCCESS'
ORDER BY IDX DESC
LIMIT 5
UNION ALL
SELECT 
    'NEW' as source,
    order_no,
    u.login_id as user_id,
    amount,
    payment_status as status,
    p.created_at
FROM t_payment p
JOIN t_user u ON p.user_id = u.user_id
WHERE payment_status = 'SUCCESS'
ORDER BY payment_id DESC
LIMIT 5;

-- =====================================================
-- 8. 최종 요약
-- =====================================================

SELECT '=== 마이그레이션 검증 요약 ===' as title;

SELECT 
    CASE 
        WHEN (
            SELECT COUNT(*) FROM t_user
        ) = (
            SELECT COUNT(*) FROM TBL_USER
        ) THEN '✓ PASS'
        ELSE '✗ FAIL'
    END as 'User Migration',
    
    CASE 
        WHEN (
            SELECT COUNT(*) FROM t_counselor
        ) = (
            SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N'
        ) THEN '✓ PASS'
        ELSE '✗ FAIL'
    END as 'Counselor Migration',
    
    CASE 
        WHEN (
            SELECT COUNT(*) FROM t_payment
        ) = (
            SELECT COUNT(*) FROM TBL_USER_TRADE
        ) THEN '✓ PASS'
        ELSE '✗ FAIL'
    END as 'Payment Migration',
    
    CASE 
        WHEN (
            SELECT COUNT(*) FROM t_consultation_review
        ) = (
            SELECT COUNT(*) FROM TBL_CS_REVIEW
        ) THEN '✓ PASS'
        ELSE '✗ FAIL'
    END as 'Review Migration';

-- =====================================================
-- 끝
-- =====================================================