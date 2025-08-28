-- =====================================================
-- 마이그레이션 사전 체크 스크립트
-- Version: 1.0
-- Date: 2025-01-01
-- 
-- 목적: 마이그레이션 실행 전 데이터 무결성 확인
-- =====================================================

-- =====================================================
-- 1. USER 테이블 체크
-- =====================================================
SELECT '=== USER 테이블 체크 ===' as title;

-- USER_ID 중복 체크
SELECT 'Duplicate USER_ID' as check_type, COUNT(*) as count
FROM (
    SELECT USER_ID, COUNT(*) as cnt
    FROM TBL_USER
    GROUP BY USER_ID
    HAVING COUNT(*) > 1
) t;

-- NULL 값 체크
SELECT 'NULL USER_ID' as check_type, COUNT(*) as count FROM TBL_USER WHERE USER_ID IS NULL
UNION ALL
SELECT 'NULL EMAIL' as check_type, COUNT(*) as count FROM TBL_USER WHERE EMAIL IS NULL
UNION ALL
SELECT 'NULL PHONE' as check_type, COUNT(*) as count FROM TBL_USER WHERE PHONE IS NULL;

-- 평문 비밀번호 체크
SELECT 'Plain text passwords' as check_type, COUNT(*) as count
FROM TBL_USER
WHERE PASSWORD IS NOT NULL AND PASSWORD NOT LIKE '$2%';

-- =====================================================
-- 2. COUNSELOR 테이블 체크
-- =====================================================
SELECT '=== COUNSELOR 테이블 체크 ===' as title;

-- EMAIL 중복 체크 (승인된 상담사)
SELECT 'Duplicate counselor EMAIL' as check_type, COUNT(*) as count
FROM (
    SELECT EMAIL, COUNT(*) as cnt
    FROM TBL_CS
    WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL
    GROUP BY EMAIL
    HAVING COUNT(*) > 1
) t;

-- NULL EMAIL 체크 (승인된 상담사)
SELECT 'NULL counselor EMAIL' as check_type, COUNT(*) as count
FROM TBL_CS
WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NULL;

-- =====================================================
-- 3. 참조 무결성 체크
-- =====================================================
SELECT '=== 참조 무결성 체크 ===' as title;

-- USER_TRADE의 USER_ID가 TBL_USER에 존재하는지
SELECT 'USER_TRADE orphan records' as check_type, COUNT(*) as count
FROM TBL_USER_TRADE t
WHERE t.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID);

-- CS_REVIEW의 USER_IDX가 TBL_USER에 존재하는지
SELECT 'CS_REVIEW orphan user records' as check_type, COUNT(*) as count
FROM TBL_CS_REVIEW r
WHERE r.USER_IDX IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.IDX = r.USER_IDX);

-- CS_REVIEW의 CS_IDX가 TBL_CS에 존재하는지
SELECT 'CS_REVIEW orphan counselor records' as check_type, COUNT(*) as count
FROM TBL_CS_REVIEW r
WHERE r.CS_IDX IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_CS c WHERE c.IDX = r.CS_IDX);

-- MILEAGE_SAVE의 USER_ID가 TBL_USER에 존재하는지
SELECT 'MILEAGE_SAVE orphan records' as check_type, COUNT(*) as count
FROM TBL_MILEAGE_SAVE ms
WHERE ms.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = ms.USER_ID);

-- MILEAGE_USAGE의 USER_ID가 TBL_USER에 존재하는지
SELECT 'MILEAGE_USAGE orphan records' as check_type, COUNT(*) as count
FROM TBL_MILEAGE_USAGE mu
WHERE mu.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = mu.USER_ID);

-- =====================================================
-- 4. 데이터 통계
-- =====================================================
SELECT '=== 데이터 통계 ===' as title;

SELECT 'Total users' as metric, COUNT(*) as count FROM TBL_USER
UNION ALL
SELECT 'Active counselors' as metric, COUNT(*) as count FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL
UNION ALL
SELECT 'Pending counselors' as metric, COUNT(*) as count FROM TBL_CS WHERE APPROVAL_YN = 'N'
UNION ALL
SELECT 'Total payments' as metric, COUNT(*) as count FROM TBL_USER_TRADE
UNION ALL
SELECT 'Total reviews' as metric, COUNT(*) as count FROM TBL_CS_REVIEW
UNION ALL
SELECT 'Total mileage saves' as metric, COUNT(*) as count FROM TBL_MILEAGE_SAVE
UNION ALL
SELECT 'Total mileage uses' as metric, COUNT(*) as count FROM TBL_MILEAGE_USAGE;

-- =====================================================
-- 5. 문제 데이터 상세
-- =====================================================
SELECT '=== 문제 데이터 상세 ===' as title;

-- 중복 USER_ID 목록
SELECT 'Duplicate USER_IDs:' as description;
SELECT USER_ID, COUNT(*) as duplicate_count
FROM TBL_USER
GROUP BY USER_ID
HAVING COUNT(*) > 1
LIMIT 10;

-- 참조 무결성이 깨진 결제 내역
SELECT 'Orphan payment records:' as description;
SELECT t.IDX, t.USER_ID, t.AMOUNT, t.REGIST_DATE
FROM TBL_USER_TRADE t
WHERE t.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID)
LIMIT 10;

-- =====================================================
-- 6. 마이그레이션 가능 여부 체크
-- =====================================================
SELECT '=== 마이그레이션 가능 여부 ===' as title;

SELECT 
    CASE 
        WHEN (
            SELECT COUNT(*)
            FROM (
                SELECT USER_ID FROM TBL_USER
                GROUP BY USER_ID
                HAVING COUNT(*) > 1
            ) t
        ) = 0 
        AND (
            SELECT COUNT(*)
            FROM TBL_CS
            WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NULL
        ) = 0
        THEN '✅ READY - 마이그레이션 가능'
        ELSE '❌ NOT READY - 데이터 정리 필요'
    END as migration_status,
    (
        SELECT COUNT(*)
        FROM (
            SELECT USER_ID FROM TBL_USER
            GROUP BY USER_ID
            HAVING COUNT(*) > 1
        ) t
    ) as duplicate_users,
    (
        SELECT COUNT(*)
        FROM TBL_CS
        WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NULL
    ) as counselors_without_email;

-- =====================================================
-- 끝
-- =====================================================