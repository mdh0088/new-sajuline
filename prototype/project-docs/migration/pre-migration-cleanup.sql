-- =====================================================
-- 마이그레이션 전 데이터 정리 스크립트
-- Version: 1.0
-- Date: 2025-01-06
-- 
-- 목적: 마이그레이션 전 발견된 데이터 문제 해결
-- =====================================================

-- =====================================================
-- 1. USER_ID 중복 문제 해결
-- =====================================================
-- WithDrawal@ 접두사가 있는 중복 USER_ID를 고유하게 만들기
-- 전략: USER_ID에 IDX를 추가하여 고유성 보장

-- 백업 테이블 생성
CREATE TABLE IF NOT EXISTS TBL_USER_BACKUP AS SELECT * FROM TBL_USER;

-- 중복 USER_ID 업데이트 (IDX를 추가하여 고유하게 만들기)
UPDATE TBL_USER 
SET USER_ID = CONCAT(USER_ID, '_', IDX)
WHERE USER_ID IN (
    SELECT USER_ID FROM (
        SELECT USER_ID, COUNT(*) as cnt
        FROM TBL_USER
        GROUP BY USER_ID
        HAVING COUNT(*) > 1
    ) dup
);

-- 중복 제거 확인
SELECT 'After cleanup - Duplicate USER_ID' as check_type, COUNT(*) as count
FROM (
    SELECT USER_ID, COUNT(*) as cnt
    FROM TBL_USER
    GROUP BY USER_ID
    HAVING COUNT(*) > 1
) t;

-- =====================================================
-- 2. 참조 무결성 문제 해결
-- =====================================================
-- TBL_USER_TRADE의 고아 레코드 처리
-- 전략: 탈퇴한 사용자의 결제 기록은 유지하되, user_id를 NULL로 처리

-- 고아 레코드 백업
CREATE TABLE IF NOT EXISTS TBL_USER_TRADE_ORPHANS AS
SELECT * FROM TBL_USER_TRADE t
WHERE t.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID);

-- 고아 레코드의 USER_ID를 보존하면서 별도 필드에 저장
ALTER TABLE TBL_USER_TRADE ADD COLUMN IF NOT EXISTS ORIGINAL_USER_ID VARCHAR(100) COMMENT '원본 USER_ID (탈퇴 사용자)';

UPDATE TBL_USER_TRADE t
SET ORIGINAL_USER_ID = USER_ID,
    USER_ID = NULL
WHERE t.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID);

-- 처리 결과 확인
SELECT 'After cleanup - USER_TRADE orphan records' as check_type, COUNT(*) as count
FROM TBL_USER_TRADE t
WHERE t.USER_ID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID);

-- =====================================================
-- 3. 평문 비밀번호 임시 해시 처리
-- =====================================================
-- 평문 비밀번호를 임시 bcrypt 해시로 변환
-- 사용자는 로그인 시 비밀번호 재설정 필요

-- 평문 비밀번호 사용자 백업
CREATE TABLE IF NOT EXISTS TBL_USER_PLAIN_PWD AS
SELECT IDX, USER_ID, PASSWORD
FROM TBL_USER
WHERE PASSWORD IS NOT NULL AND PASSWORD NOT LIKE '$2%';

-- 임시 해시 적용 (실제 bcrypt는 애플리케이션에서 처리)
-- 여기서는 표시용으로 TEMP_ 접두사 추가
UPDATE TBL_USER
SET PASSWORD = CONCAT('TEMP_HASH_', SHA2(CONCAT(PASSWORD, USER_ID), 256))
WHERE PASSWORD IS NOT NULL AND PASSWORD NOT LIKE '$2%' AND PASSWORD NOT LIKE 'TEMP_HASH_%';

-- 처리 결과 확인
SELECT 'After cleanup - Plain text passwords' as check_type, COUNT(*) as count
FROM TBL_USER
WHERE PASSWORD IS NOT NULL 
  AND PASSWORD NOT LIKE '$2%' 
  AND PASSWORD NOT LIKE 'TEMP_HASH_%';

-- =====================================================
-- 4. 최종 마이그레이션 가능 여부 확인
-- =====================================================
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
        AND (
            SELECT COUNT(*)
            FROM TBL_USER_TRADE t
            WHERE t.USER_ID IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID)
        ) = 0
        THEN '✅ READY - 마이그레이션 가능'
        ELSE '❌ NOT READY - 추가 데이터 정리 필요'
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
    ) as counselors_without_email,
    (
        SELECT COUNT(*)
        FROM TBL_USER_TRADE t
        WHERE t.USER_ID IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM TBL_USER u WHERE u.USER_ID = t.USER_ID)
    ) as orphan_payments;

-- =====================================================
-- 5. 데이터 정리 요약
-- =====================================================
SELECT '=== 데이터 정리 요약 ===' as title;

SELECT 'Backup tables created' as action, 
       'TBL_USER_BACKUP, TBL_USER_TRADE_ORPHANS, TBL_USER_PLAIN_PWD' as details;

SELECT 'Duplicate USER_IDs fixed' as action,
       CONCAT('Updated ', (SELECT COUNT(*) FROM TBL_USER WHERE USER_ID LIKE '%WithDrawal@%_%'), ' records') as details;

SELECT 'Orphan payments handled' as action,
       CONCAT('Moved ', (SELECT COUNT(*) FROM TBL_USER_TRADE WHERE ORIGINAL_USER_ID IS NOT NULL), ' USER_IDs to ORIGINAL_USER_ID') as details;

SELECT 'Plain passwords marked' as action,
       CONCAT('Marked ', (SELECT COUNT(*) FROM TBL_USER WHERE PASSWORD LIKE 'TEMP_HASH_%'), ' passwords for reset') as details;

-- =====================================================
-- 끝
-- =====================================================