-- =====================================================
-- 마이그레이션 사후 검증 스크립트
-- Version: 1.0
-- Date: 2025-01-01
-- 
-- 목적: 마이그레이션 완료 후 데이터 정합성 검증
-- =====================================================

-- =====================================================
-- 1. 데이터 건수 비교
-- =====================================================
SELECT '=== 데이터 건수 비교 ===' as title;

-- 사용자 수 비교
SELECT 
    'Users' as entity,
    (SELECT COUNT(*) FROM TBL_USER) as old_count,
    (SELECT COUNT(*) FROM t_user) as new_count,
    (SELECT COUNT(*) FROM TBL_USER) - (SELECT COUNT(*) FROM t_user) as diff;

-- 상담사 수 비교
SELECT 
    'Counselors' as entity,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL) as old_count,
    (SELECT COUNT(*) FROM t_counselor) as new_count,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL) - (SELECT COUNT(*) FROM t_counselor) as diff;

-- 결제 수 비교
SELECT 
    'Payments' as entity,
    (SELECT COUNT(*) FROM TBL_USER_TRADE WHERE USER_ID IS NOT NULL AND EXISTS (SELECT 1 FROM TBL_USER WHERE USER_ID = TBL_USER_TRADE.USER_ID)) as old_count,
    (SELECT COUNT(*) FROM t_payment) as new_count,
    (SELECT COUNT(*) FROM TBL_USER_TRADE WHERE USER_ID IS NOT NULL AND EXISTS (SELECT 1 FROM TBL_USER WHERE USER_ID = TBL_USER_TRADE.USER_ID)) - (SELECT COUNT(*) FROM t_payment) as diff;

-- =====================================================
-- 2. PK 유니크 검증
-- =====================================================
SELECT '=== PK 유니크 검증 ===' as title;

-- t_user PK 중복 체크
SELECT 'Duplicate user_id in t_user' as check_type, COUNT(*) as count
FROM (
    SELECT user_id, COUNT(*) as cnt
    FROM t_user
    GROUP BY user_id
    HAVING COUNT(*) > 1
) t;

-- t_counselor PK 중복 체크
SELECT 'Duplicate counselor_id in t_counselor' as check_type, COUNT(*) as count
FROM (
    SELECT counselor_id, COUNT(*) as cnt
    FROM t_counselor
    GROUP BY counselor_id
    HAVING COUNT(*) > 1
) t;

-- =====================================================
-- 3. 외래키 무결성 검증
-- =====================================================
SELECT '=== 외래키 무결성 검증 ===' as title;

-- t_user_point_balance FK 체크
SELECT 'Orphan records in t_user_point_balance' as check_type, COUNT(*) as count
FROM t_user_point_balance pb
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = pb.user_id);

-- t_payment FK 체크
SELECT 'Orphan records in t_payment' as check_type, COUNT(*) as count
FROM t_payment p
WHERE p.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = p.user_id);

-- t_consultation_review FK 체크
SELECT 'Orphan user records in t_consultation_review' as check_type, COUNT(*) as count
FROM t_consultation_review r
WHERE r.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = r.user_id);

SELECT 'Orphan counselor records in t_consultation_review' as check_type, COUNT(*) as count
FROM t_consultation_review r
WHERE r.counselor_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM t_counselor c WHERE c.counselor_id = r.counselor_id);

-- t_point_transaction FK 체크
SELECT 'Orphan records in t_point_transaction' as check_type, COUNT(*) as count
FROM t_point_transaction pt
WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = pt.user_id);

-- =====================================================
-- 4. 데이터 변환 검증
-- =====================================================
SELECT '=== 데이터 변환 검증 ===' as title;

-- 비밀번호 해시 검증
SELECT 'Users with plain text passwords' as check_type, COUNT(*) as count
FROM t_user
WHERE password_hash IS NOT NULL 
  AND password_hash NOT LIKE '$2%';

-- 사용자 상태 변환 검증
SELECT 'Invalid user_status values' as check_type, COUNT(*) as count
FROM t_user
WHERE user_status NOT IN ('ACTIVE', 'DORMANT', 'WITHDRAWN');

-- 상담사 상태 변환 검증
SELECT 'Invalid counselor_status values' as check_type, COUNT(*) as count
FROM t_counselor
WHERE counselor_status NOT IN ('WAITING', 'CONSULTING', 'ABSENT');

-- =====================================================
-- 5. 샘플 데이터 검증
-- =====================================================
SELECT '=== 샘플 데이터 검증 ===' as title;

-- 사용자 샘플
SELECT 'User sample:' as description;
SELECT user_id, email, nickname, user_status, grade_code
FROM t_user
LIMIT 5;

-- 상담사 샘플
SELECT 'Counselor sample:' as description;
SELECT counselor_id, counselor_code, nickname, counselor_status, grade
FROM t_counselor
LIMIT 5;

-- 결제 샘플
SELECT 'Payment sample:' as description;
SELECT payment_id, order_no, user_id, amount, payment_status
FROM t_payment
WHERE payment_status = 'SUCCESS'
LIMIT 5;

-- =====================================================
-- 6. 포인트/마일리지 잔액 검증
-- =====================================================
SELECT '=== 포인트/마일리지 잔액 검증 ===' as title;

-- 마일리지 잔액 비교
SELECT 
    'Mileage balance check' as check_type,
    COUNT(*) as total_users,
    SUM(CASE WHEN ABS(o.MILEAGE - n.mileage_balance) > 0 THEN 1 ELSE 0 END) as diff_count,
    SUM(ABS(o.MILEAGE - n.mileage_balance)) as total_diff
FROM TBL_USER o
JOIN t_user_point_balance n ON o.USER_ID = n.user_id;

-- =====================================================
-- 7. 최종 검증 결과
-- =====================================================
SELECT '=== 최종 검증 결과 ===' as title;

SELECT 
    CASE 
        WHEN (
            -- PK 중복 체크
            SELECT COUNT(*) FROM (
                SELECT user_id FROM t_user GROUP BY user_id HAVING COUNT(*) > 1
            ) t1
        ) = 0
        AND (
            SELECT COUNT(*) FROM (
                SELECT counselor_id FROM t_counselor GROUP BY counselor_id HAVING COUNT(*) > 1
            ) t2
        ) = 0
        AND (
            -- FK 무결성 체크
            SELECT COUNT(*) FROM t_payment p
            WHERE p.user_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = p.user_id)
        ) = 0
        AND (
            SELECT COUNT(*) FROM t_point_transaction pt
            WHERE NOT EXISTS (SELECT 1 FROM t_user u WHERE u.user_id = pt.user_id)
        ) = 0
        THEN '✅ SUCCESS - 마이그레이션 성공'
        ELSE '❌ FAILED - 데이터 무결성 문제 발견'
    END as validation_result,
    (
        SELECT COUNT(*) FROM t_user
    ) as migrated_users,
    (
        SELECT COUNT(*) FROM t_counselor
    ) as migrated_counselors,
    (
        SELECT COUNT(*) FROM t_payment
    ) as migrated_payments,
    (
        SELECT COUNT(*) FROM t_point_transaction
    ) as migrated_transactions;

-- =====================================================
-- 8. 문제 데이터 상세 (있는 경우)
-- =====================================================
SELECT '=== 문제 데이터 상세 ===' as title;

-- 누락된 사용자 확인
SELECT 'Missing users:' as description;
SELECT u.USER_ID, u.EMAIL, u.NICK_NAME
FROM TBL_USER u
WHERE NOT EXISTS (SELECT 1 FROM t_user nu WHERE nu.user_id = u.USER_ID)
LIMIT 10;

-- 누락된 상담사 확인
SELECT 'Missing counselors:' as description;
SELECT c.EMAIL, c.CODE, c.NAME
FROM TBL_CS c
WHERE c.APPROVAL_YN = 'Y' AND c.OUT_YN = 'N' AND c.EMAIL IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM t_counselor nc WHERE nc.counselor_id = c.EMAIL)
LIMIT 10;

-- =====================================================
-- 끝
-- =====================================================