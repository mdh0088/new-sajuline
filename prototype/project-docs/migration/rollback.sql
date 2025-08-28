-- =====================================================
-- 마이그레이션 롤백 스크립트
-- Version: 1.0
-- Date: 2025-01-01
-- 
-- 주의사항:
-- 1. 이 스크립트는 비상시에만 사용
-- 2. 실행 전 반드시 백업 확인
-- 3. 신규 테이블의 데이터는 복구되지 않음
-- =====================================================

-- 트랜잭션 시작
START TRANSACTION;

-- 외래키 체크 비활성화
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- Phase 1: 마이그레이션 후 생성된 데이터 백업
-- =====================================================

-- 마이그레이션 이후 신규 생성된 데이터 임시 보관
CREATE TEMPORARY TABLE IF NOT EXISTS tmp_new_users AS
SELECT * FROM t_user 
WHERE user_id > (SELECT MAX(IDX) FROM TBL_USER);

CREATE TEMPORARY TABLE IF NOT EXISTS tmp_new_payments AS
SELECT * FROM t_payment 
WHERE payment_id > (SELECT MAX(IDX) FROM TBL_USER_TRADE);

CREATE TEMPORARY TABLE IF NOT EXISTS tmp_new_reviews AS
SELECT * FROM t_consultation_review 
WHERE review_id > (SELECT MAX(IDX) FROM TBL_CS_REVIEW);

-- =====================================================
-- Phase 2: 신규 테이블 삭제 (의존성 순서 고려)
-- =====================================================

-- 로그 테이블 삭제
DROP TABLE IF EXISTS t_batch_execution_log;
DROP TABLE IF EXISTS t_grade_change_log;
DROP TABLE IF EXISTS t_event_participation_log;
DROP TABLE IF EXISTS t_search_log;
DROP TABLE IF EXISTS t_user_activity_log;

-- 알림 도메인 삭제
DROP TABLE IF EXISTS t_notification_log;
DROP TABLE IF EXISTS t_notification_template;

-- 콘텐츠 도메인 삭제
DROP TABLE IF EXISTS t_event;
DROP TABLE IF EXISTS t_banner;
DROP TABLE IF EXISTS t_inquiry;
DROP TABLE IF EXISTS t_faq;
DROP TABLE IF EXISTS t_notice;

-- 결제/포인트 도메인 삭제
DROP TABLE IF EXISTS t_external_point_sync;
DROP TABLE IF EXISTS t_point_transaction;
DROP TABLE IF EXISTS t_payment;
DROP TABLE IF EXISTS t_point_product;

-- 후기/신고 도메인 삭제
DROP TABLE IF EXISTS t_report;
DROP TABLE IF EXISTS t_review_like;
DROP TABLE IF EXISTS t_consultation_review;
DROP TABLE IF EXISTS t_review_dummy;

-- 상담 도메인 삭제
DROP TABLE IF EXISTS t_consultation_queue;
DROP TABLE IF EXISTS t_chat_message;
DROP TABLE IF EXISTS t_consultation_session;

-- 상담사 도메인 삭제
DROP TABLE IF EXISTS t_counselor_schedule;
DROP TABLE IF EXISTS t_counselor_specialty;
DROP TABLE IF EXISTS t_counselor_application_image;
DROP TABLE IF EXISTS t_counselor_application;
DROP TABLE IF EXISTS t_counselor;

-- 사용자 도메인 삭제
DROP TABLE IF EXISTS t_user_preference;
DROP TABLE IF EXISTS t_user_point_balance;
DROP TABLE IF EXISTS t_user;

-- 시스템 도메인 삭제
DROP TABLE IF EXISTS t_mileage_config;
DROP TABLE IF EXISTS t_grade_batch_config;
DROP TABLE IF EXISTS t_grade;
DROP TABLE IF EXISTS t_system_config;
DROP TABLE IF EXISTS t_admin;

-- 뷰 삭제
DROP VIEW IF EXISTS v_active_counselors;
DROP VIEW IF EXISTS v_user_point_status;

-- =====================================================
-- Phase 3: 기존 테이블 데이터 복원 (필요시)
-- =====================================================

-- 마이그레이션 중 변경된 데이터가 있다면 복원
-- 예: 비밀번호 해시 원복, 상태값 원복 등

-- 사용자 비밀번호 원복 (해시에서 원본으로 - 보안상 권장하지 않음)
-- UPDATE TBL_USER u
-- SET PASSWORD = (
--     SELECT password_original 
--     FROM backup_passwords bp 
--     WHERE bp.user_id = u.IDX
-- )
-- WHERE EXISTS (
--     SELECT 1 FROM backup_passwords bp 
--     WHERE bp.user_id = u.IDX
-- );

-- =====================================================
-- Phase 4: 시퀀스 및 AUTO_INCREMENT 복원
-- =====================================================

-- AUTO_INCREMENT 값 원복 (필요한 경우)
-- ALTER TABLE TBL_USER AUTO_INCREMENT = (이전값);
-- ALTER TABLE TBL_CS AUTO_INCREMENT = (이전값);
-- ALTER TABLE TBL_USER_TRADE AUTO_INCREMENT = (이전값);

-- =====================================================
-- Phase 5: 제약조건 복원
-- =====================================================

-- 외래키 체크 활성화
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- Phase 6: 롤백 검증
-- =====================================================

-- 기존 테이블 확인
SELECT 
    'Rollback Verification' as check_type,
    TABLE_NAME,
    'EXISTS' as status
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN (
        'TBL_USER', 'TBL_CS', 'TBL_USER_TRADE', 
        'TBL_CS_REVIEW', 'TBL_PRODUCT'
    )
ORDER BY TABLE_NAME;

-- 신규 테이블 삭제 확인
SELECT 
    'New Tables Removed' as check_type,
    COUNT(*) as remaining_tables
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME LIKE 't_%';

-- =====================================================
-- Phase 7: 롤백 로그 기록
-- =====================================================

-- 롤백 실행 기록 (시스템 설정 테이블이 남아있다면)
-- INSERT INTO system_rollback_log (
--     rollback_date,
--     rollback_reason,
--     executed_by,
--     status
-- ) VALUES (
--     NOW(),
--     'Migration rollback executed',
--     USER(),
--     'COMPLETED'
-- );

-- =====================================================
-- Phase 8: 커밋 또는 롤백
-- =====================================================

-- 모든 작업이 성공적으로 완료되면 커밋
-- COMMIT;

-- 문제가 발생하면 롤백
-- ROLLBACK;

-- =====================================================
-- 선택적: 신규 데이터 복구 쿼리
-- =====================================================

-- 마이그레이션 이후 생성된 신규 데이터를 복구해야 하는 경우
-- 아래 쿼리를 별도로 실행

/*
-- 신규 사용자 복구
INSERT INTO TBL_USER (
    NICK_NAME, USER_ID, PASSWORD, EMAIL, PHONE,
    USER_STATUS, JOIN_TYPE, GRADE, MILEAGE,
    REGIST_DATE, UPDATE_DATE, LAST_LOGIN
)
SELECT 
    nickname, login_id, '임시비밀번호', email, phone,
    '1', 'common', 'WHITE', 0,
    created_at, updated_at, last_login_at
FROM tmp_new_users;

-- 신규 결제 복구
INSERT INTO TBL_USER_TRADE (
    USER_ID, ORDER_NO, AMOUNT, PAY_TYPE,
    REGIST_DATE
)
SELECT 
    u.login_id, order_no, amount, 
    CASE payment_status 
        WHEN 'SUCCESS' THEN 'SUCCESS'
        ELSE 'FAIL'
    END,
    p.created_at
FROM tmp_new_payments p
JOIN TBL_USER u ON u.IDX = p.user_id;

-- 신규 후기 복구
INSERT INTO TBL_CS_REVIEW (
    USER_IDX, CS_IDX, USER_CONT,
    USER_REGIST_DATE, SHOW_YN
)
SELECT 
    user_id, counselor_id, content,
    created_at, 'Y'
FROM tmp_new_reviews;
*/

-- =====================================================
-- 주의사항 및 추가 작업
-- =====================================================

/*
롤백 후 필요한 추가 작업:

1. 애플리케이션 설정 원복
   - 데이터베이스 연결 설정
   - 엔티티 매핑 원복
   - 쿼리 원복

2. 캐시 초기화
   - Redis 캐시 클리어
   - 애플리케이션 캐시 초기화

3. 외부 시스템 연동 확인
   - MSSQL 포인트 시스템 연동
   - 알림 시스템 연동

4. 백업 확인
   - 롤백 전 풀 백업 권장
   - 마이그레이션 이후 데이터 별도 백업

5. 모니터링
   - 에러 로그 확인
   - 성능 모니터링
   - 사용자 영향도 확인
*/

-- =====================================================
-- 끝
-- =====================================================