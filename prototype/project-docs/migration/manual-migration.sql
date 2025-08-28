-- =====================================================
-- 수동 마이그레이션 스크립트
-- MCP 권한 제한으로 인한 수동 실행용
-- =====================================================

-- 1. 중복 USER_ID 처리
UPDATE TBL_USER 
SET USER_ID = CONCAT(USER_ID, '_', IDX)
WHERE USER_ID IN (
    SELECT USER_ID FROM (
        SELECT USER_ID
        FROM TBL_USER
        GROUP BY USER_ID
        HAVING COUNT(*) > 1
    ) dup
);

-- 2. 빈 닉네임 처리
UPDATE TBL_USER 
SET NICK_NAME = CONCAT('user_', IDX)
WHERE NICK_NAME IS NULL OR NICK_NAME = '';

-- 3. 빈 이메일 처리
UPDATE TBL_USER 
SET EMAIL = CONCAT('temp_', IDX, '@temp.com')
WHERE EMAIL IS NULL OR EMAIL = '';

-- 4. 빈 전화번호 처리
UPDATE TBL_USER 
SET PHONE = CONCAT('010-0000-', LPAD(IDX, 4, '0'))
WHERE PHONE IS NULL OR PHONE = '';

-- 5. 데이터 마이그레이션 실행
-- 이제 data-migration.sql을 실행하세요