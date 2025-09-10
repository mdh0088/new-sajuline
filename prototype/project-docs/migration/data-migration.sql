-- =====================================================
-- 사주라인 데이터 마이그레이션 스크립트
-- Version: 1.0
-- Date: 2025-01-01
-- 
-- 주의사항:
-- 1. 트랜잭션 단위로 실행
-- 2. 외래키 제약조건은 마이그레이션 완료 후 활성화
-- 3. 대용량 데이터는 배치 처리 권장
-- =====================================================

-- 외래키 체크 비활성화
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- Phase 1: 사용자 도메인 마이그레이션
-- =====================================================

-- 1.1 사용자 정보 마이그레이션 (USER_ID를 그대로 PK로 사용)
INSERT INTO t_user (
    user_id,  -- USER_ID를 직접 PK로 사용
    email,
    password_hash,
    nickname,
    phone,
    join_type,
    social_provider,
    social_id,
    user_status,
    grade_code,
    created_at,
    updated_at,
    last_login_at
)
SELECT 
    USER_ID,  -- USER_ID를 그대로 PK로 사용
    EMAIL,
    -- 비밀번호 해시 처리 (평문 비밀번호 임시 해시화)
    CASE 
        WHEN PASSWORD LIKE '$2%' THEN PASSWORD  -- 이미 bcrypt 해시된 경우
        ELSE CONCAT('$2b$12$TEMP', SHA2(CONCAT(PASSWORD, USER_ID), 256))  -- 임시 해시 (나중에 재설정 필요)
    END,
    NICK_NAME,
    PHONE,
    CASE 
        WHEN JOIN_TYPE = 'common' THEN 'COMMON'
        WHEN JOIN_TYPE = 'kakao' THEN 'KAKAO'
        WHEN JOIN_TYPE = 'naver' THEN 'NAVER'
        ELSE 'COMMON'
    END,
    CASE 
        WHEN JOIN_TYPE = 'kakao' THEN 'KAKAO'
        WHEN JOIN_TYPE = 'naver' THEN 'NAVER'
        ELSE NULL
    END,
    CASE 
        WHEN JOIN_TYPE IN ('kakao', 'naver') THEN USER_ID
        ELSE NULL
    END,
    CASE USER_STATUS
        WHEN '1' THEN 'ACTIVE'
        WHEN '2' THEN 'DORMANT'
        WHEN '3' THEN 'WITHDRAWN'
        ELSE 'ACTIVE'
    END,
    IFNULL(GRADE, 'WHITE'),
    REGIST_DATE,
    UPDATE_DATE,
    LAST_LOGIN
FROM TBL_USER

-- 1.2 포인트/마일리지 잔액 마이그레이션
INSERT INTO t_user_point_balance (
    user_id,
    point_balance,
    mileage_balance,
    total_earned_point,
    total_used_point,
    total_earned_mileage,
    total_used_mileage,
    updated_at
)
SELECT 
    u.USER_ID,  -- USER_ID를 직접 사용
    0, -- 외부 시스템에서 동기화 필요
    IFNULL(u.MILEAGE, 0),  -- TBL_USER의 MILEAGE 필드 우선 사용
    0, -- 계산 필요
    0, -- 계산 필요
    IFNULL((SELECT SUM(AMOUNT) FROM TBL_MILEAGE_SAVE WHERE USER_ID = u.USER_ID), 0),
    IFNULL((SELECT SUM(USE_AMOUNT) FROM TBL_MILEAGE_USAGE WHERE USER_ID = u.USER_ID), 0),
    NOW()
FROM TBL_USER u;

-- TBL_MILEAGE_BALANCE 테이블에 데이터가 있는 경우만 업데이트 (현재는 비어있음)
UPDATE t_user_point_balance pb
JOIN TBL_MILEAGE_BALANCE mb ON mb.USER_ID = pb.user_id
SET pb.mileage_balance = mb.AVAILABLE_MILEAGE
WHERE mb.AVAILABLE_MILEAGE IS NOT NULL;

-- =====================================================
-- Phase 2: 상담사 도메인 마이그레이션
-- =====================================================

-- 2.1 승인된 상담사 마이그레이션 (EMAIL을 PK로 사용)

INSERT INTO t_counselor (
    counselor_id,  -- EMAIL을 PK로 사용
    counselor_code,
    password_hash,
    name,
    nickname,
    phone,
    profile_image_url,
    introduction_short,
    greeting_message,
    career_info,
    counselor_status,
    grade,
    rating_avg,
    rating_count,
    consultation_count,
    consultation_time_total,
    after_amount,
    before_amount,
    is_new,
    is_out,
    is_show,
    approved_at,
    created_at,
    updated_at,
    last_login_at,
    specialty_types,
    keywords
)
SELECT 
    EMAIL,  -- EMAIL을 PK로 사용 (counselor_id = EMAIL)
    CODE,
    PASSWORD,
    NAME,
    NICK_NAME,
    PHONE,
    IMG,
    SHORT_INFO,
    GREETING,
    CAREER,
    CASE STATUS
        WHEN '1' THEN 'WAITING'
        WHEN '2' THEN 'CONSULTING'
        WHEN '3' THEN 'ABSENT'
        ELSE 'WAITING'
    END,
    IFNULL(GRADE, 'BRONZE'),
    0.00, -- 평점 계산 필요
    0,    -- 평점 개수 계산 필요
    0,    -- 상담 횟수 계산 필요
    0,    -- 총 상담 시간(분)
    IFNULL(AFTER_AMOUNT, 1000),
    IFNULL(BEFORE_AMOUNT, 1000),
    CASE WHEN NEW_YN = 'Y' THEN 1 ELSE 0 END,
    CASE WHEN OUT_YN = 'Y' THEN 1 ELSE 0 END,
    CASE WHEN SHOW_YN = 'Y' THEN 1 ELSE 0 END,
    CS_DATE,
    IFNULL(CS_DATE, RECRUIT_DATE),
    UPDATE_DATE,
    LAST_LOGIN,
    CONCAT('[',
        CASE WHEN TYPE LIKE '%1%' THEN '"TARO",' ELSE '' END,
        CASE WHEN TYPE LIKE '%2%' THEN '"FORTUNE",' ELSE '' END,
        CASE WHEN TYPE LIKE '%3%' THEN '"EASY",' ELSE '' END,
        CASE WHEN TYPE LIKE '%4%' THEN '"SAJU",' ELSE '' END,
        '""'
    , ']'),
    CS_KEYWORD
FROM TBL_CS
WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL AND PASSWORD !='';

-- 2.2 상담사 신청 정보 마이그레이션 (미승인)
INSERT INTO t_counselor_application (
    application_id,
    name,
    nickname,
    email,
    phone,
    address,
    specialty_types,
    keywords,
    selected_image_url,
    application_status,
    created_at,
    updated_at,
    specialty_types,
    keywords
)
SELECT 
    IDX,
    NAME,
    NICK_NAME,
    EMAIL,
    PHONE,
    ADDRESS,
    CONCAT('[',
        CASE WHEN TYPE LIKE '%1%' THEN '"TARO",' ELSE '' END,
        CASE WHEN TYPE LIKE '%2%' THEN '"FORTUNE",' ELSE '' END,
        CASE WHEN TYPE LIKE '%3%' THEN '"EASY",' ELSE '' END,
        CASE WHEN TYPE LIKE '%4%' THEN '"SAJU",' ELSE '' END,
        '""'
    , ']'),
    CS_KEYWORD,
    IMG,
    CASE 
        WHEN APPROVAL_YN = 'N' THEN 'PENDING'
        WHEN APPROVAL_YN = 'Y' THEN 'APPROVED'
        ELSE 'PENDING'
    END,
    RECRUIT_DATE,
    UPDATE_DATE
FROM TBL_CS
WHERE APPROVAL_YN = 'N' OR OUT_YN = 'Y';

-- 2.3 상담사 신청 이미지 마이그레이션
INSERT INTO t_counselor_application_image (application_id, image_url, image_order, is_selected, uploaded_at)
SELECT IDX, IMG1, 1, CASE WHEN IMG = IMG1 THEN 1 ELSE 0 END, RECRUIT_DATE
FROM TBL_CS WHERE IMG1 IS NOT NULL AND IMG1 != '' AND (APPROVAL_YN = 'N' OR OUT_YN = 'Y')
UNION ALL
SELECT IDX, IMG2, 2, CASE WHEN IMG = IMG2 THEN 1 ELSE 0 END, RECRUIT_DATE
FROM TBL_CS WHERE IMG2 IS NOT NULL AND IMG2 != '' AND (APPROVAL_YN = 'N' OR OUT_YN = 'Y')
UNION ALL
SELECT IDX, IMG3, 3, CASE WHEN IMG = IMG3 THEN 1 ELSE 0 END, RECRUIT_DATE
FROM TBL_CS WHERE IMG3 IS NOT NULL AND IMG3 != '' AND (APPROVAL_YN = 'N' OR OUT_YN = 'Y')
UNION ALL
SELECT IDX, IMG4, 4, CASE WHEN IMG = IMG4 THEN 1 ELSE 0 END, RECRUIT_DATE
FROM TBL_CS WHERE IMG4 IS NOT NULL AND IMG4 != '' AND (APPROVAL_YN = 'N' OR OUT_YN = 'Y')
UNION ALL
SELECT IDX, IMG5, 5, CASE WHEN IMG = IMG5 THEN 1 ELSE 0 END, RECRUIT_DATE
FROM TBL_CS WHERE IMG5 IS NOT NULL AND IMG5 != '' AND (APPROVAL_YN = 'N' OR OUT_YN = 'Y');

-- 2.4 상담사 전문분야 마이그레이션
INSERT INTO t_counselor_specialty (counselor_id, specialty_code, is_main, created_at)
SELECT EMAIL, 'TARO', 0, NOW() FROM TBL_CS WHERE TARO_YN = 'Y' AND APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL
UNION ALL
SELECT EMAIL, 'SAJU', 0, NOW() FROM TBL_CS WHERE LUCK_YN = 'Y' AND APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL
UNION ALL
SELECT EMAIL, 'FORTUNE', 0, NOW() FROM TBL_CS WHERE FORTUNE_YN = 'Y' AND APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL
UNION ALL
SELECT EMAIL, 'EASY', 0, NOW() FROM TBL_CS WHERE EASY_YN = 'Y' AND APPROVAL_YN = 'Y' AND OUT_YN = 'N' AND EMAIL IS NOT NULL;

-- 첫 번째 전문분야를 대표로 설정
UPDATE t_counselor_specialty cs1
SET is_main = 1
WHERE cs1.counselor_id IN (
    SELECT counselor_id FROM (
        SELECT counselor_id, MIN(specialty_code) as first_specialty
        FROM t_counselor_specialty
        GROUP BY counselor_id
    ) t
) AND cs1.specialty_code = (
    SELECT MIN(specialty_code) 
    FROM t_counselor_specialty cs2 
    WHERE cs2.counselor_id = cs1.counselor_id
);

-- =====================================================
-- Phase 3: 상담 및 후기 마이그레이션
-- =====================================================

-- 3.1 상담 후기 마이그레이션
-- CHATLOG_IDX '1391' 값 중복 있음 삭제 처리 후 마이그레이션 할 것
INSERT INTO t_consultation_review (
    review_id,
    session_id,
    user_id,  -- USER의 USER_ID로 참조
    counselor_id,  -- COUNSELOR의 EMAIL로 참조
    rating,
    content,
    counselor_reply,
    is_best,
    is_visible,
    like_count,
    created_at,
    updated_at,
    counselor_replied_at
)
SELECT 
    r.IDX,
    r.CHATLOG_IDX, -- 세션 ID는 나중에 매핑 필요
    (SELECT USER_ID FROM TBL_USER WHERE IDX = r.USER_IDX),  -- USER_ID로 매핑
    (SELECT EMAIL FROM TBL_CS WHERE IDX = r.CS_IDX),  -- EMAIL로 매핑
    5, -- 기본 평점 (실제 평점이 없으므로)
    r.USER_CONT,
    r.CS_CONT,
    CASE WHEN r.BEST_YN = 'Y' THEN 1 ELSE 0 END,
    CASE WHEN r.SHOW_YN = 'Y' THEN 1 ELSE 0 END,
    IFNULL((SELECT COUNT(*) FROM TBL_CS_REVIEW_LIKE WHERE REVIEW_IDX = r.IDX), 0),
    r.USER_REGIST_DATE,
    IFNULL(r.CS_UPDATE_DATE, r.CS_REGIST_DATE),
    r.CS_REGIST_DATE
FROM TBL_CS_REVIEW r;

-- 3.2 후기 좋아요 마이그레이션
-- 데이터 없음 마이그레이션 안해도 됨
INSERT INTO t_review_like (user_id, review_id, created_at)
SELECT 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX),  -- USER_ID로 매핑
    l.REVIEW_IDX, 
    l.REGIST_DATE
FROM TBL_CS_REVIEW_LIKE l
WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = l.USER_IDX);

-- 3.3 신고 마이그레이션
-- 데이터 없음 마이그레이션 안해도 됨
INSERT INTO t_report (
    report_id,
    report_code,
    reporter_id,  -- USER의 USER_ID로 참조
    reporter_type,
    target_type,
    target_id,
    reason_type,
    reason_detail,
    report_status,
    created_at
)
SELECT 
    IDX,
    CONCAT('RPT', LPAD(IDX, 8, '0')),
    (SELECT USER_ID FROM TBL_USER WHERE IDX = rp.USER_IDX),  -- USER_ID로 매핑
    'USER',
    'REVIEW',
    REVIEW_IDX,
    CASE TYPE
        WHEN 1 THEN 'COMMERCIAL'
        WHEN 2 THEN 'PRIVACY'
        WHEN 3 THEN 'ILLEGAL'
        WHEN 4 THEN 'ADULT'
        WHEN 5 THEN 'ABUSE'
        WHEN 6 THEN 'OTHER'
        ELSE 'OTHER'
    END,
    CONT,
    'PENDING',
    rp.REGIST_DATE
FROM TBL_CS_REPORT rp
WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = rp.USER_IDX);

-- 3.4 더미 후기 마이그레이션
INSERT INTO t_review_dummy (
    dummy_id,
    user_nickname,
    counselor_id,  -- COUNSELOR의 EMAIL로 참조
    consultation_duration,
    content,
    counselor_reply,
    created_at
)
SELECT 
    IDX,
    USER_ID,
    (SELECT EMAIL FROM TBL_CS WHERE IDX = d.CS_IDX),  -- EMAIL로 매핑
    TIME_TO_SEC(CHAT_TIME) / 60, -- 분 단위로 변환
    USER_CONT,
    d.CS_CONT,
    IFNULL(d.USER_REGIST_DATE, d.REGIST_DATE)
FROM TBL_CS_REVIEW_DUMY d
WHERE EXISTS (SELECT 1 FROM TBL_CS WHERE IDX = d.CS_IDX);

-- =====================================================
-- Phase 4: 결제 및 포인트 마이그레이션
-- =====================================================

-- 4.1 포인트 상품 마이그레이션
INSERT INTO t_point_product (
    product_id,
    product_code,
    product_name,
    point_amount,
    price,
    bonus_point,
    discount_rate,
    is_active,
    display_order,
    valid_from,
    valid_until,
    created_at,
    updated_at
)
SELECT 
    IDX,
    CONCAT('POINT_', IDX),
    PRODUCT_NAME,
    PRODUCT_VALUE,
    PRODUCT_VALUE - (PRODUCT_VALUE * DISCOUNT_VALUE / 100),
    SAVE_VALUE,
    DISCOUNT_VALUE,
    CASE WHEN IS_USE = 'Y' THEN 1 ELSE 0 END,
    ORD,
    START_DT,
    END_DT,
    REGIST_DATE,
    UPDATE_DATE
FROM TBL_PRODUCT;

-- 4.2 결제 내역 마이그레이션 (참조 무결성 처리)
INSERT INTO t_payment (
    payment_id,
    order_no,
    user_id,  -- USER의 USER_ID로 직접 매핑
    product_id,
    payment_type,
    amount,
    point_amount,
    bonus_point,
    payment_method,
    payment_status,
    pg_provider,
    pg_tid,
    cid,
    pay_info,
    tax_amount,
    domestic_flag,
    paid_at,
    cancelled_at,
    cancel_reason,
    refund_amount,
    created_at,
    updated_at
)
SELECT 
    t.IDX,
    t.ORDER_NO,
    t.USER_ID,  -- USER_ID를 그대로 사용 (외래키 참조)
    (SELECT product_id FROM t_point_product WHERE product_name = t.PRODUCT_NAME LIMIT 1),
    'POINT_CHARGE',
    IFNULL(CAST(t.AMOUNT AS DECIMAL(12,2)),0),
    t.USER_POINT,
    0, -- 보너스 포인트 계산 필요
    t.PGCODE,
    CASE t.PAY_TYPE
        WHEN 'SUCCESS' THEN 'SUCCESS'
        WHEN 'CANCEL' THEN 'CANCELLED'
        WHEN 'HOLD' THEN 'PENDING'
        WHEN 'FAIL' THEN 'FAILED'
        ELSE 'PENDING'
    END,
    CASE 
        WHEN t.PGCODE LIKE '%KAKAO%' THEN 'KAKAO'
        WHEN t.PGCODE LIKE '%CARD%' THEN 'CARD'
        ELSE 'OTHER'
    END,
    t.TID,
    t.CID,
    t.PAY_INFO,
    t.TAX_AMOUNT,
    t.DOMESTIC_FLAG,
    CASE WHEN t.PAY_TYPE = 'SUCCESS' THEN t.REGIST_DATE ELSE NULL END,
    t.CANCEL_DATE,
    NULL,
    CAST(t.CANCEL_AMOUNT AS DECIMAL(12,2)),
    t.REGIST_DATE,
    t.UPDATE_DATE
FROM TBL_USER_TRADE t
WHERE t.ORDER_NO IS NOT NULL  -- 주문번호가 있는 경우만 마이그레이션
  AND t.USER_ID IS NOT NULL
  AND EXISTS (SELECT 1 FROM TBL_USER WHERE USER_ID = t.USER_ID);  -- 존재하는 사용자만

-- 4.3 포인트 거래 내역 마이그레이션
-- 포인트 충전/사용 내역
INSERT INTO t_point_transaction (
    user_id,  -- USER의 USER_ID로 직접 매핑
    transaction_type,
    currency_type,
    amount,
    balance_after,
    reference_type,
    reference_id,
    description,
    created_at
)
SELECT 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = h.USER_IDX),  -- USER_ID로 매핑
    CASE 
        WHEN h.POINT_ACTION LIKE '%지급%' THEN 'CHARGE'
        WHEN h.POINT_ACTION LIKE '%차감%' THEN 'USE'
        ELSE 'USE'
    END,
    'POINT',
    h.ACTIVE_POINT,
    h.USER_POINT,
    'MANUAL',
    h.IDX,
    h.REASON,
    h.REGIST_DATE
FROM TBL_USER_POINT_HIST h
WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = h.USER_IDX);

-- 마일리지 적립 내역
INSERT INTO t_point_transaction (
    user_id,
    transaction_type,
    currency_type,
    amount,
    balance_after,
    reference_type,
    reference_id,
    description,
    earn_rate,
    expires_at,
    created_at
)
SELECT 
    u.user_id,
    'EARN',
    ms.SOURCE_TYPE,
    ms.AMOUNT,
    (SELECT mileage_balance FROM t_user_point_balance WHERE user_id = u.user_id),
    ms.SOURCE_TYPE,
    ms.SOURCE_ID,
    ms.REASON,
    ms.SAVE_RATE,
    STR_TO_DATE(ms.EXPIRE_DATE, '%Y-%m-%d'),
    ms.REGIST_DATE
FROM TBL_MILEAGE_SAVE ms
INNER JOIN t_user u ON u.user_id = ms.USER_ID  -- 매핑된 사용자만 처리
WHERE ms.USER_ID IS NOT NULL;

-- 마일리지 사용 내역
INSERT INTO t_point_transaction (
    user_id,
    transaction_type,
    currency_type,
    amount,
    balance_after,
    reference_type,
    reference_id,
    description,
    created_at
)
SELECT 
    u.user_id,
    'USE',
    mu.SOURCE_TYPE,
    -mu.USE_AMOUNT, -- 음수로 저장
    (SELECT mileage_balance FROM t_user_point_balance WHERE user_id = u.user_id),
    mu.SOURCE_TYPE,
    mu.SOURCE_ID,
    mu.REASON,
    mu.USE_DATE
FROM TBL_MILEAGE_USAGE mu
INNER JOIN t_user u ON u.user_id = mu.USER_ID  -- 매핑된 사용자만 처리
WHERE mu.USER_ID IS NOT NULL;

-- =====================================================
-- Phase 5: 관리자 및 시스템 마이그레이션
-- =====================================================

-- 5.1 관리자 계정 마이그레이션
INSERT INTO t_admin (
    admin_id,
    login_id,
    password_hash,
    name,
    email,
    phone,
    role,
    is_active,
    last_login_at,
    created_at,
    updated_at
)
SELECT 
    MANAGER_SEQ,
    MANAGER_ID,
    PASSWORD, -- 주의: 해시 처리 필요
    NAME,
    CONCAT(MANAGER_ID, '@sajuline.com'), -- 이메일 생성
    PHONE,
    CASE AUTH
        WHEN 'SUPER' THEN 'SUPER'
        WHEN 'ADMIN' THEN 'ADMIN'
        ELSE 'CS'
    END,
    CASE WHEN ACTIVE_YN = 'Y' THEN 1 ELSE 0 END,
    LAST_LOGIN,
    REG_DATE,
    UPT_DATE
FROM TBL_MANAGER;

-- 5.2 등급 정의 마이그레이션
INSERT INTO t_grade (
    grade_code,
    grade_name,
    grade_level,
    min_purchase_amount,
    point_earn_rate,
    discount_rate,
    grade_image_url,
    description,
    is_active,
    created_at,
    updated_at
)
SELECT 
    GRADE,
    GRADE_NM,
    CASE GRADE
        WHEN 'WHITE' THEN 1
        WHEN 'BRONZE' THEN 2
        WHEN 'SILVER' THEN 3
        WHEN 'GOLD' THEN 4
        WHEN 'VIP' THEN 5
        WHEN 'VIP+' THEN 6
        WHEN 'VVIP' THEN 7
        ELSE 1
    END,
    PURCHASE_AMOUNT,
    SAVE_VALUE,
    DISCOUNT_VALUE,
    GRADE_IMG,
    DESCRIPTION,
    1,
    REGIST_DATE,
    UPDATE_DATE
FROM TBL_GRADE;

-- 5.3 등급 배치 설정 마이그레이션
INSERT INTO t_grade_batch_config (
    period_month,
    period_day,
    is_active,
    updated_at
)
SELECT 
    PERIOD_MONTH,
    PERIOD_DAY,
    CASE WHEN IS_USE = 'Y' THEN 1 ELSE 0 END,
    UPDATE_DATE
FROM TBL_GRADE_BATCH_CONFIG
LIMIT 1;

-- 5.4 마일리지 설정 마이그레이션
INSERT INTO t_mileage_config (config_key, config_value, description, updated_at)
SELECT CONFIG_KEY, CONFIG_VALUE, DESCRIPTION, UPDATE_DATE
FROM TBL_MILEAGE_CONFIG;

-- =====================================================
-- Phase 6: 알림 및 콘텐츠 마이그레이션
-- =====================================================

-- 6.1 알림 템플릿 마이그레이션
INSERT INTO t_notification_template (
    template_id,
    template_code,
    template_name,
    channel,
    content_template,
    button_info,
    is_active,
    created_at
)
SELECT 
    IDX,
    CODE,
    NAME,
    'KAKAO',
    CONTENT,
    JSON_OBJECT('pc_link', PC_LINK, 'mo_link', MO_LINK),
    1,
    NOW()
FROM TBL_KAKAO_ALARM_TEMPLATE;

-- 6.2 알림 발송 로그 마이그레이션
INSERT INTO t_notification_log (
    recipient_type,
    recipient_id,  -- USER의 USER_ID 또는 COUNSELOR의 EMAIL로 매핑
    channel,
    template_id,
    content,
    send_status,
    provider_response,
    sent_at,
    created_at
)
SELECT 
    k.USER_TYPE,
    CASE 
        WHEN k.USER_TYPE = 'USER' THEN (SELECT USER_ID FROM TBL_USER WHERE IDX = k.USER_IDX)
        WHEN k.USER_TYPE = 'CS' THEN (SELECT EMAIL FROM TBL_CS WHERE IDX = k.USER_IDX)
        ELSE k.USER_IDX
    END,
    'KAKAO',
    (SELECT template_id FROM t_notification_template WHERE template_code = k.CODE LIMIT 1),
    k.SEND_CONT,
    CASE WHEN k.RESULT_CODE = 0 THEN 'SUCCESS' ELSE 'FAILED' END,
    JSON_OBJECT('transaction_no', k.NO, 'result_code', k.RESULT_CODE),
    k.REGIST_DATE,
    k.REGIST_DATE
FROM TBL_KAKAO_ALARM_HISTORY k
WHERE (k.USER_TYPE = 'USER' AND EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = k.USER_IDX))
   OR (k.USER_TYPE = 'CS' AND EXISTS (SELECT 1 FROM TBL_CS WHERE IDX = k.USER_IDX));

-- 6.3 공지사항 마이그레이션
INSERT INTO t_notice (
    notice_id,
    notice_type,
    title,
    content,
    target_audience,
    is_important,
    is_active,
    attachments,
    created_by,
    created_at,
    updated_at
)
SELECT 
    IDX,
    'GENERAL',
    TITLE,
    CONT,
    'COUNSELOR',
    0,
    1,
    CASE WHEN ATTACH_FILE IS NOT NULL 
        THEN JSON_ARRAY(JSON_OBJECT('url', ATTACH_FILE))
        ELSE NULL 
    END,
    2,
    REGIST_DATE,
    UPDASTE_DATE
FROM TBL_CS_NOTICE;

-- 6.4 FAQ 마이그레이션 (실제 FAQ만)
-- 관리자 FAQ를 t_faq로
INSERT INTO t_faq (
    category,
    target_audience,
    question,
    answer,
    display_order,
    is_active,
    created_at
)
SELECT 
    'GENERAL',
    CASE USER_TYPE
        WHEN 'USER' THEN 'USER'
        WHEN 'CS' THEN 'COUNSELOR'
        ELSE 'ALL'
    END,
    USER_TITLE,
    ADMIN_CONT,
    0,
    1,
    USER_REGIST_DATE
FROM TBL_ADMIN_FAQ
WHERE ADMIN_CONT IS NOT NULL;

-- 6.5 1:1 문의 마이그레이션
-- 상담사 문의

INSERT INTO t_inquiry
(
	inquirer_type, inquirer_id, counselor_id, category, title, content, is_read, reply_content, answered_at,created_at
)
SELECT
	'COUNSELOR' AS inquirer_type,
	(SELECT EMAIL FROM TBL_CS WHERE IDX = T1.CS_IDX ) AS inquirer_id,
	NULL AS counselor_id,
	'CS_TO_ADMIN' AS category,
	NULL AS title,
	T1.CS_CONT AS content,
	1 AS is_read,
	T1.ADMIN_CONT  AS reply_content,
	T1.ADMIN_REGIST_DATE AS answered_at,
	T1.CS_REGIST_DATE AS created_at
FROM TBL_CS_ADMIN_FAQ  T1 WHERE
	(SELECT EMAIL FROM TBL_CS WHERE IDX = T1.CS_IDX ) IS NOT NULL;

INSERT INTO t_inquiry
(
	inquirer_type, inquirer_id, counselor_id, category, title, content, is_read, reply_content, answered_at,created_at
)
SELECT
	'USER' AS inquirer_type,
	(SELECT USER_ID FROM TBL_USER WHERE IDX = T1.USER_IDX ) AS inquirer_id,
	(SELECT EMAIL FROM TBL_CS WHERE IDX = T1.CS_IDX ) AS counselor_id,
	'USER_TO_CS' AS category,
	NULL AS title,
	T1.USER_CONT AS content,
	1 as is_read,
	T1.CS_CONT AS reply_content,
	T1.CS_REGIST_DATE AS created_at,
	T1.USER_REGIST_DATE AS updated_at
FROM TBL_CS_FAQ T1;

-- INSERT INTO t_inquiry (
--     inquiry_code,
--     inquirer_type,
--     inquirer_id,  -- COUNSELOR의 EMAIL로 매핑
--     category,
--     title,
--     content,
--     attachments,
--     inquiry_status,
--     admin_id,
--     admin_reply,
--     answered_at,
--     created_at
-- )
-- SELECT 
--     CONCAT('INQ_CS_', f.IDX),
--     'COUNSELOR',
--     (SELECT EMAIL FROM TBL_CS WHERE IDX = f.CS_IDX),  -- EMAIL로 매핑
--     'GENERAL',
--     CONCAT('상담사 문의 #', f.IDX),
--     f.CS_CONT,
--     CASE WHEN f.ATTACH_FILE IS NOT NULL 
--         THEN JSON_ARRAY(JSON_OBJECT('url', f.ATTACH_FILE))
--         ELSE NULL 
--     END,
--     CASE WHEN f.ADMIN_CONT IS NOT NULL THEN 'ANSWERED' ELSE 'PENDING' END,
--     f.ADMIN_IDX,
--     f.ADMIN_CONT,
--     f.ADMIN_REGIST_DATE,
--     f.CS_REGIST_DATE
-- FROM TBL_CS_ADMIN_FAQ f
-- WHERE EXISTS (SELECT 1 FROM TBL_CS WHERE IDX = f.CS_IDX);

-- 사용자 문의
-- INSERT INTO t_inquiry (
--     inquiry_code,
--     inquirer_type,
--     inquirer_id,  -- USER의 USER_ID로 매핑
--     category,
--     title,
--     content,
--     inquiry_status,
--     created_at
-- )
-- SELECT 
--     CONCAT('INQ_USER_', q.IDX),
--     'USER',
--     (SELECT USER_ID FROM TBL_USER WHERE IDX = q.USER_IDX),  -- USER_ID로 매핑
--     'GENERAL',
--     CONCAT('사용자 문의 #', q.IDX),
--     q.USER_CONT,
--     CASE WHEN q.CS_CONT IS NOT NULL THEN 'ANSWERED' ELSE 'PENDING' END,
--     q.USER_REGIST_DATE
-- FROM TBL_CS_FAQ q
-- WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = q.USER_IDX);

-- 6.6 배너 마이그레이션
INSERT INTO t_banner (
    banner_id,
    banner_code,
    banner_name,
    banner_type,
    image_url,
    link_url,
    link_target,
    display_order,
    is_active,
    valid_from,
    valid_until,
    created_at,
    updated_at
)
SELECT 
    BANNER_IDX,
    CONCAT('BNR_', BANNER_IDX),
    BANNER_NM,
    'MAIN',
    BANNER_IMG,
    RANDING_URL,
    TARGET,
    ORD,
    CASE WHEN SHOW_YN = 'Y' THEN 1 ELSE 0 END,
    START_DATE,
    END_DATE,
    REGIST_DATE,
    UPDATE_DATE
FROM TBL_BANNER;

-- 팝업을 배너로 통합
INSERT INTO t_banner (
    banner_id,
    banner_code,
    banner_name,
    banner_type,
    image_url,
    link_url,
    link_target,
    display_order,
    is_active,
    valid_from,
    valid_until,
    created_at,
    updated_at
)
SELECT 
    POPUP_IDX + 1000, -- ID 충돌 방지
    CONCAT('POP_', POPUP_IDX),
    POPUP_NM,
    'POPUP',
    POPUP_IMG,
    RANDING_URL,
    TARGET,
    ORD,
    CASE WHEN SHOW_YN = 'Y' THEN 1 ELSE 0 END,
    START_DATE,
    END_DATE,
    REGIST_DATE,
    UPDATE_DATE
FROM TBL_POPUP;

-- 6.7 이벤트 마이그레이션
INSERT INTO t_event (
    event_id,
    event_code,
    event_name,
    event_type,
    description,
    reward_type,
    reward_value,
    is_active,
    valid_from,
    valid_until,
    created_at
)
SELECT 
    IDX,
    CONCAT('EVT_', IDX),
    NAME,
    'POINT',
    INFO,
    'POINT',
    IFNULL(CAST(POINT AS UNSIGNED),0),
    CASE WHEN USE_YN = 'Y' THEN 1 ELSE 0 END,
    START_DATE,
    END_DATE,
    NOW()
FROM TBL_EVENT;

-- =====================================================
-- Phase 7: 로그 마이그레이션
-- =====================================================

-- 7.1 사용자 활동 로그 마이그레이션 (로그인)
-- 오픈 할 때만 마이그레이션 할 것
INSERT INTO t_user_activity_log (
    user_id,  -- USER의 USER_ID로 매핑
    user_type,
    activity_type,
    activity_detail,
    ip_address,
    user_agent,
    device_type,
    created_at
)
SELECT 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = l.USER_IDX),  -- USER_ID로 매핑
    'USER',
    'LOGIN',
    JSON_OBJECT('login_type', l.TYPE),
    l.IP,
    l.OS,
    CASE 
        WHEN l.OS LIKE '%Mobile%' THEN 'MOBILE'
        WHEN l.OS LIKE '%Tablet%' THEN 'TABLET'
        ELSE 'DESKTOP'
    END,
    l.REGIST_DATE
FROM TBL_LOG_USER_LOGIN l
WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = l.USER_IDX);

-- 7.2 검색 로그 마이그레이션
INSERT INTO t_search_log (
    user_id,  -- USER의 USER_ID로 매핑
    user_type,
    search_type,
    keyword,
    created_at
)
SELECT 
    (SELECT USER_ID FROM TBL_USER WHERE IDX = s.USER_IDX),  -- USER_ID로 매핑
    IFNULL(s.USER_TYPE, 'GUEST'),
    'GENERAL',
    s.KEYWORD,
    s.REGIST_DATE
FROM TBL_LOG_SEARCH s
WHERE s.USER_IDX IS NULL OR EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = s.USER_IDX);

-- 7.3 이벤트 참여 로그 마이그레이션
INSERT INTO t_event_participation_log (
    event_id,
    user_id,  -- USER의 USER_ID로 매핑
    reward_type,
    reward_value,
    created_at
)
SELECT 
    e.EVENT_IDX,
    (SELECT USER_ID FROM TBL_USER WHERE IDX = e.USER_IDX),  -- USER_ID로 매핑
    'POINT',
    CAST(e.POINT AS UNSIGNED),
    e.REGIST_DATE
FROM TBL_EVENT_LOG e
WHERE EXISTS (SELECT 1 FROM TBL_USER WHERE IDX = e.USER_IDX);

-- 7.4 등급 변경 로그 마이그레이션
-- 이건 좀 이상함 봐야할 듯
INSERT INTO t_grade_change_log (
    user_id,  -- USER의 USER_ID로 직접 매핑
    grade_before,
    grade_after,
    purchase_amount,
    change_reason,
    created_at
)
SELECT 
    gh.USER_ID,  -- USER_ID를 그대로 사용
    'WHITE', -- 이전 등급 알 수 없음
    gh.GRADE,
    gh.PURCHASE_AMOUNT,
    CASE gh.PROCESS_STATUS 
        WHEN 'SUCCESS' THEN 'AUTO_BATCH'
        ELSE 'MANUAL'
    END,
    gh.REGIST_DATE
FROM TBL_GRADE_HISTORY gh
WHERE gh.PROCESS_STATUS = 'SUCCESS'
  AND EXISTS (SELECT 1 FROM TBL_USER WHERE USER_ID = gh.USER_ID);

-- 7.5 배치 실행 로그 마이그레이션
INSERT INTO t_batch_execution_log (
    batch_name,
    batch_type,
    execution_status,
    started_at,
    ended_at,
    total_processed,
    success_count,
    fail_count,
    error_details
)
SELECT 
    ACTIVE_BATCH_NM,
    BATCH_TYPE,
    STATUS,
    EXEC_START_DATE,
    EXEC_END_DATE,
    TOTAL_COUNT,
    SUCCESS_COUNT,
    TOTAL_COUNT - SUCCESS_COUNT,
    CASE WHEN ERROR_MSG IS NOT NULL 
        THEN JSON_OBJECT('error', ERROR_MSG)
        ELSE NULL 
    END
FROM TBL_BATCH;

-- =====================================================
-- Phase 8: 평점 및 통계 업데이트
-- =====================================================

-- 상담사 평점 업데이트
UPDATE t_counselor c
SET 
    rating_avg = (
        SELECT AVG(rating) 
        FROM t_consultation_review 
        WHERE counselor_id = c.counselor_id AND is_visible = 1
    ),
    rating_count = (
        SELECT COUNT(*) 
        FROM t_consultation_review 
        WHERE counselor_id = c.counselor_id AND is_visible = 1
    ),
    consultation_count = (
        SELECT COUNT(*) 
        FROM t_consultation_session 
        WHERE counselor_id = c.counselor_id AND session_status = 'COMPLETED'
    );

-- 후기 좋아요 수 업데이트
UPDATE t_consultation_review r
SET like_count = (
    SELECT COUNT(*) 
    FROM t_review_like 
    WHERE review_id = r.review_id
);

-- =====================================================
-- Phase 9: 데이터 정합성 검증
-- =====================================================

-- 사용자 수 확인
SELECT 'Users' as entity, 
    (SELECT COUNT(*) FROM TBL_USER) as old_count,
    (SELECT COUNT(*) FROM t_user) as new_count;

-- 상담사 수 확인
SELECT 'Counselors' as entity,
    (SELECT COUNT(*) FROM TBL_CS WHERE APPROVAL_YN = 'Y' AND OUT_YN = 'N') as old_count,
    (SELECT COUNT(*) FROM t_counselor) as new_count;

-- 결제 내역 확인
SELECT 'Payments' as entity,
    (SELECT COUNT(*) FROM TBL_USER_TRADE) as old_count,
    (SELECT COUNT(*) FROM t_payment) as new_count;

-- 후기 수 확인
SELECT 'Reviews' as entity,
    (SELECT COUNT(*) FROM TBL_CS_REVIEW) as old_count,
    (SELECT COUNT(*) FROM t_consultation_review) as new_count;

-- =====================================================
-- Phase 10: 외래키 활성화 및 완료
-- =====================================================

-- 외래키 체크 활성화
SET FOREIGN_KEY_CHECKS = 1;

-- 마이그레이션 완료 기록
INSERT INTO t_system_config (config_key, config_value, config_type, description, updated_at)
VALUES ('migration.completed_at', NOW(), 'DATETIME', '마이그레이션 완료 시각', NOW())
ON DUPLICATE KEY UPDATE 
    config_value = NOW(),
    updated_at = NOW();

-- =====================================================
-- 끝
-- =====================================================

-- == 2025-09-05 추가 데이터 마이그레이션 ==
INSERT INTO t_user_bookmark
(
	user_id, counselor_id, created_at
)
SELECT
	user_id,
	counselor_id,
	created_at
FROM (
SELECT
	(SELECT USER_ID FROM TBL_USER WHERE IDX = TUB.USER_IDX ) AS user_id,
	(SELECT EMAIL FROM TBL_CS WHERE IDX = TUB.CS_IDX ) AS counselor_id,
	TUB.REGIST_DATE AS created_at
FROM TBL_USER_BOOKMARK TUB
) T1 WHERE
	user_id is not null
	and T1.counselor_id is not null;




