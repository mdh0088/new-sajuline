-- =====================================================
-- 사주라인 리뉴얼 MariaDB 개선 스키마
-- Version: 1.0
-- Date: 2025-01-01
-- =====================================================

-- 기존 테이블 삭제 (개발 환경에서만 사용)
-- DROP DATABASE IF EXISTS sajuline_new;
-- CREATE DATABASE sajuline_new CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
-- USE sajuline_new;

-- =====================================================
-- 1. User Domain (사용자 관리)
-- =====================================================

-- 1.1 사용자 정보 (인증 정보 통합)
CREATE TABLE t_user (
    user_id VARCHAR(100) NOT NULL COMMENT '사용자 ID (로그인 ID)',
    email VARCHAR(100) NOT NULL COMMENT '이메일',
    password_hash VARCHAR(255) DEFAULT NULL COMMENT '비밀번호 해시 (소셜로그인은 NULL)',
    nickname VARCHAR(100) NOT NULL COMMENT '닉네임',
    phone VARCHAR(15) NOT NULL COMMENT '전화번호',
    join_type VARCHAR(20) NOT NULL DEFAULT 'COMMON' COMMENT '가입유형: COMMON, KAKAO, NAVER',
    social_provider VARCHAR(20) DEFAULT NULL COMMENT '소셜 제공자: KAKAO, NAVER',
    social_id VARCHAR(255) DEFAULT NULL COMMENT '소셜 고유 ID',
    user_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '상태: ACTIVE, DORMANT, WITHDRAWN',
    grade_code VARCHAR(20) NOT NULL DEFAULT 'WHITE' COMMENT '등급코드',
    profile_image_url VARCHAR(500) DEFAULT NULL COMMENT '프로필 이미지 URL',
    birth_date varchar(30) DEFAULT NULL COMMENT '생년월일',
    gender VARCHAR(10) DEFAULT NULL COMMENT '성별: MALE, FEMALE',
    mileage_point int(11) DEFAULT 0 COMMENT '마일리지 포인트',
    is_marketing_agreed TINYINT(1) DEFAULT 1 COMMENT '마케팅 동의',
    password_changed_at DATETIME DEFAULT NULL COMMENT '비밀번호 변경일시',
    failed_login_count INT(11) DEFAULT 0 COMMENT '로그인 실패 횟수',
    locked_until DATETIME DEFAULT NULL COMMENT '계정 잠금 해제 시간',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    last_login_at DATETIME DEFAULT NULL,
    withdrawn_at DATETIME DEFAULT NULL,
    PRIMARY KEY (user_id),
    KEY idx_user_status (user_status),
    KEY idx_grade_code (grade_code),
    KEY idx_created_at (created_at),
    KEY idx_social_provider_id (social_provider, social_id),
    CONSTRAINT chk_user_status CHECK (user_status IN ('ACTIVE', 'DORMANT', 'WITHDRAWN')),
    CONSTRAINT chk_join_type CHECK (join_type IN ('COMMON', 'KAKAO', 'NAVER'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='사용자 정보';

-- 1.2 포인트/마일리지 잔액 (통합)
CREATE TABLE t_user_point_balance (
    user_id VARCHAR(100) NOT NULL,
    point_balance INT(11) NOT NULL DEFAULT 0 COMMENT '포인트 잔액',
    mileage_balance INT(11) NOT NULL DEFAULT 0 COMMENT '마일리지 잔액',
    total_earned_point INT(11) NOT NULL DEFAULT 0 COMMENT '총 적립 포인트',
    total_used_point INT(11) NOT NULL DEFAULT 0 COMMENT '총 사용 포인트',
    total_earned_mileage INT(11) NOT NULL DEFAULT 0 COMMENT '총 적립 마일리지',
    total_used_mileage INT(11) NOT NULL DEFAULT 0 COMMENT '총 사용 마일리지',
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
    --CONSTRAINT fk_point_balance_user FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='포인트/마일리지 잔액';

-- 1.3 사용자 선호도 설정
CREATE TABLE t_user_preference (
    user_id VARCHAR(100) NOT NULL,
    prefer_fortune_types JSON DEFAULT NULL COMMENT '선호 운세 타입 ["TARO", "SAJU", "FORTUNE", "EASY"]',
    prefer_counselor_styles JSON DEFAULT NULL COMMENT '선호 상담 스타일',
    notification_settings JSON DEFAULT NULL COMMENT '알림 설정',
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
    --CONSTRAINT fk_preference_user FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='사용자 선호도 설정';

-- =====================================================
-- 2. Counselor Domain (상담사 관리)
-- =====================================================

-- 2.1 상담사 정보 (승인된 상담사만)
CREATE TABLE t_counselor (
    counselor_id VARCHAR(100) NOT NULL COMMENT '상담사 ID (로그인 ID = 이메일)',
    counselor_code VARCHAR(50) NOT NULL COMMENT '상담사 고유 코드',
    password_hash VARCHAR(255) NOT NULL COMMENT '비밀번호 해시',
    name VARCHAR(50) NOT NULL COMMENT '실명',
    nickname VARCHAR(100) NOT NULL COMMENT '활동명',
    phone VARCHAR(50) NOT NULL COMMENT '전화번호',
    profile_image_url VARCHAR(500) DEFAULT NULL COMMENT '프로필 이미지',
    introduction_short TEXT DEFAULT NULL COMMENT '짧은 소개',
    greeting_message TEXT DEFAULT NULL COMMENT '인사말',
    career_info TEXT DEFAULT NULL COMMENT '경력사항',
    counselor_status VARCHAR(20) NOT NULL DEFAULT 'WAITING' COMMENT '상태: WAITING, CONSULTING, ABSENT',
    grade VARCHAR(20) DEFAULT 'BRONZE' COMMENT '등급: BRONZE, SILVER, GOLD',
    specialty_types longtext DEFAULT NULL,
    keywords text DEFAULT NULL,
    work_time text DEFAULT NULL COMMENT '업무 시간',
    rating_avg DECIMAL(3,2) DEFAULT 0.00 COMMENT '평균 평점',
    rating_count INT(11) DEFAULT 0 COMMENT '평점 개수',
    consultation_count INT(11) DEFAULT 0 COMMENT '총 상담 횟수',
    consultation_time_total INT(11) DEFAULT 0 COMMENT '총 상담 시간(분)',
    after_amount int(11) DEFAULT 1000 COMMENT '선불 금액',
    before_amount varchar(100) NOT NULL DEFAULT '1000' COMMENT '후분금액',
    is_best tinyint(1) DEFAULT 0 COMMENT '베스트 여부',
    is_new TINYINT(1) DEFAULT 1 COMMENT '신규 상담사 여부',
    is_out TINYINT(1) NOT NULL DEFAULT 0 COMMENT '탈퇴 여부',
    is_show TINYINT(1) NOT NULL DEFAULT 0 COMMENT '노출여부',
    approved_at DATETIME DEFAULT NULL COMMENT '승인일시',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    last_login_at DATETIME DEFAULT NULL,
    withdrawn_at DATETIME DEFAULT NULL,
    PRIMARY KEY (counselor_id),
    UNIQUE KEY uk_counselor_code (counselor_code),
    UNIQUE KEY uk_nickname (nickname),
    UNIQUE KEY uk_phone (phone),
    KEY idx_counselor_status (counselor_status),
    KEY idx_grade (grade),
    KEY idx_rating (rating_avg DESC, rating_count DESC),
    CONSTRAINT chk_counselor_status CHECK (counselor_status IN ('WAITING', 'CONSULTING', 'ABSENT')),
    CONSTRAINT chk_grade CHECK (grade IN ('BRONZE', 'SILVER', 'GOLD'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담사 정보';

-- 2.2 상담사 신청 정보
CREATE TABLE `t_counselor_application` (
  application_id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(50) NOT NULL COMMENT '실명',
  nickname varchar(100) NOT NULL COMMENT '희망 활동명',
  email varchar(100) NOT NULL COMMENT '이메일',
  phone varchar(50) NOT NULL COMMENT '전화번호',
  address varchar(500) DEFAULT NULL COMMENT '주소',
  specialty_types longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT '신청 분야 ["TARO", "SAJU", "FORTUNE", "EASY"]' CHECK (json_valid(`specialty_types`)),
  keywords varchar(500) DEFAULT NULL COMMENT '키워드',
  introduction text DEFAULT NULL COMMENT '자기소개',
  selected_image_url varchar(500) DEFAULT NULL COMMENT '선택된 이미지',
  upload_image1 varchar(500) DEFAULT NULL,
  upload_image2 varchar(500) DEFAULT NULL,
  upload_image3 varchar(500) DEFAULT NULL,
  application_status varchar(20) NOT NULL DEFAULT 'PENDING' COMMENT '상태: PENDING,  APPROVED, REJECTED',
  admin_note text DEFAULT NULL COMMENT '관리자 메모',
  reviewed_by int(11) DEFAULT NULL COMMENT '검토한 관리자',
  reviewed_at datetime DEFAULT NULL COMMENT '검토일시',
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  updated_at datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`application_id`),
  KEY `idx_application_status` (`application_status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=235 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담사 신청 정보';

-- 2.3 상담사 신청 이미지
CREATE TABLE t_counselor_application_image (
    image_id INT(11) NOT NULL AUTO_INCREMENT,
    application_id INT(11) NOT NULL,
    image_url VARCHAR(500) NOT NULL COMMENT '이미지 URL',
    image_order INT(11) NOT NULL COMMENT '이미지 순서',
    is_selected TINYINT(1) DEFAULT 0 COMMENT '선택 여부',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (image_id),
    KEY idx_application_id (application_id)
    --CONSTRAINT fk_app_image_application FOREIGN KEY (application_id) REFERENCES t_counselor_application(application_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담사 신청 이미지';

-- 2.4 상담사 전문분야
CREATE TABLE t_counselor_specialty (
    counselor_id VARCHAR(100) NOT NULL,
    specialty_code VARCHAR(20) NOT NULL COMMENT '전문분야 코드: TARO, SAJU, FORTUNE, EASY',
    is_main TINYINT(1) DEFAULT 0 COMMENT '대표 전문분야 여부',
    experience_years INT(11) DEFAULT 0 COMMENT '경력 연수',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (counselor_id, specialty_code),
    KEY idx_specialty_code (specialty_code)
    --CONSTRAINT fk_specialty_counselor FOREIGN KEY (counselor_id) REFERENCES t_counselor(counselor_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담사 전문분야';

-- 2.5 상담사 근무시간
CREATE TABLE t_counselor_schedule (
    schedule_id INT(11) NOT NULL AUTO_INCREMENT,
    counselor_id VARCHAR(100) NOT NULL,
    day_of_week TINYINT(1) NOT NULL COMMENT '요일 (1=월, 7=일)',
    start_time TIME NOT NULL COMMENT '시작 시간',
    end_time TIME NOT NULL COMMENT '종료 시간',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (schedule_id),
    UNIQUE KEY uk_counselor_day_time (counselor_id, day_of_week, start_time)
    --CONSTRAINT fk_schedule_counselor FOREIGN KEY (counselor_id) REFERENCES t_counselor(counselor_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담사 근무시간';

-- =====================================================
-- 3. Consultation Domain (상담 서비스)
-- =====================================================

-- 3.1 상담 세션
CREATE TABLE t_consultation_session (
    session_id INT(11) NOT NULL AUTO_INCREMENT,
    session_code VARCHAR(50) NOT NULL COMMENT '세션 코드',
    user_id VARCHAR(100) NOT NULL,
    counselor_id VARCHAR(100) NOT NULL,
    consultation_type VARCHAR(20) NOT NULL DEFAULT 'CHAT' COMMENT '상담 유형: CHAT, VOICE, VIDEO',
    session_status VARCHAR(20) NOT NULL DEFAULT 'WAITING' COMMENT '상태: WAITING, IN_PROGRESS, COMPLETED, CANCELLED',
    started_at DATETIME DEFAULT NULL COMMENT '시작 시간',
    ended_at DATETIME DEFAULT NULL COMMENT '종료 시간',
    duration_seconds INT(11) DEFAULT 0 COMMENT '상담 시간(초)',
    point_used INT(11) DEFAULT 0 COMMENT '사용 포인트',
    point_per_minute INT(11) DEFAULT 1000 COMMENT '분당 포인트',
    user_rating TINYINT(1) DEFAULT NULL COMMENT '사용자 평점 (1-5)',
    counselor_memo TEXT DEFAULT NULL COMMENT '상담사 메모',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id),
    UNIQUE KEY uk_session_code (session_code),
    KEY idx_user_id_created (user_id, created_at DESC),
    KEY idx_counselor_id_created (counselor_id, created_at DESC),
    KEY idx_session_status (session_status),
    KEY idx_started_at (started_at)
    --CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES t_user(user_id),
    --CONSTRAINT fk_session_counselor FOREIGN KEY (counselor_id) REFERENCES t_counselor(counselor_id),
    --CONSTRAINT chk_session_status CHECK (session_status IN ('WAITING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담 세션';

-- 3.2 채팅 메시지
CREATE TABLE t_chat_message (
    message_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    session_id INT(11) NOT NULL,
    sender_type VARCHAR(20) NOT NULL COMMENT '발신자 타입: USER, COUNSELOR, SYSTEM',
    sender_id INT(11) NOT NULL COMMENT '발신자 ID',
    message_type VARCHAR(20) DEFAULT 'TEXT' COMMENT '메시지 타입: TEXT, IMAGE, FILE',
    content TEXT DEFAULT NULL COMMENT '메시지 내용',
    file_url VARCHAR(500) DEFAULT NULL COMMENT '파일 URL',
    is_read TINYINT(1) DEFAULT 0 COMMENT '읽음 여부',
    read_at DATETIME DEFAULT NULL COMMENT '읽은 시간',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id),
    KEY idx_session_id_created (session_id, created_at),
    KEY idx_sender (sender_type, sender_id)
    --CONSTRAINT fk_message_session FOREIGN KEY (session_id) REFERENCES t_consultation_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='채팅 메시지';

-- 3.3 상담 대기열
CREATE TABLE t_consultation_queue (
    queue_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) NOT NULL,
    counselor_id VARCHAR(100) NOT NULL,
    priority INT(11) DEFAULT 0 COMMENT '우선순위',
    queue_status VARCHAR(20) NOT NULL DEFAULT 'WAITING' COMMENT '상태: WAITING, NOTIFIED, CONNECTED, EXPIRED',
    queued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notified_at DATETIME DEFAULT NULL,
    connected_at DATETIME DEFAULT NULL,
    expired_at DATETIME DEFAULT NULL,
    PRIMARY KEY (queue_id),
    UNIQUE KEY uk_user_counselor_waiting (user_id, counselor_id, queue_status),
    KEY idx_counselor_status (counselor_id, queue_status),
    KEY idx_queued_at (queued_at)
    --CONSTRAINT fk_queue_user FOREIGN KEY (user_id) REFERENCES t_user(user_id),
    --CONSTRAINT fk_queue_counselor FOREIGN KEY (counselor_id) REFERENCES t_counselor(counselor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담 대기열';

-- =====================================================
-- 4. Review & Report Domain (후기 및 신고)
-- =====================================================

-- 4.1 상담 후기
CREATE TABLE t_consultation_review (
    review_id INT(11) NOT NULL AUTO_INCREMENT,
    session_id INT(11) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    counselor_id VARCHAR(100) NOT NULL,
    rating TINYINT(1) NOT NULL COMMENT '평점 (1-5)',
    content TEXT DEFAULT NULL COMMENT '후기 내용',
    counselor_reply TEXT DEFAULT NULL COMMENT '상담사 답변',
    review_tags longtext DEFAULT NULL COMMENT '리뷰 태그',
    is_best TINYINT(1) DEFAULT 0 COMMENT '베스트 후기',
    is_visible TINYINT(1) DEFAULT 1 COMMENT '공개 여부',
    like_count INT(11) DEFAULT 0 COMMENT '좋아요 수',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    counselor_replied_at DATETIME DEFAULT NULL,
    PRIMARY KEY (review_id),
    UNIQUE KEY uk_session_id (session_id),
    KEY idx_user_id (user_id),
    KEY idx_counselor_id (counselor_id),
    KEY idx_is_best_visible (is_best, is_visible),
    KEY idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='상담 후기';

-- 4.2 후기 좋아요
CREATE TABLE t_review_like (
    user_id VARCHAR(100) NOT NULL,
    review_id INT(11) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, review_id)
    --CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES t_user(user_id),
    --CONSTRAINT fk_like_review FOREIGN KEY (review_id) REFERENCES t_consultation_review(review_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='후기 좋아요';

-- 4.3 신고
CREATE TABLE t_report (
    report_id INT(11) NOT NULL AUTO_INCREMENT,
    report_code VARCHAR(50) NOT NULL COMMENT '신고 코드',
    reporter_id INT(11) NOT NULL COMMENT '신고자 ID',
    reporter_type VARCHAR(20) NOT NULL COMMENT '신고자 타입: USER, COUNSELOR',
    target_type VARCHAR(20) NOT NULL COMMENT '신고 대상 타입: REVIEW, USER, COUNSELOR',
    target_id INT(11) NOT NULL COMMENT '신고 대상 ID',
    reason_type VARCHAR(50) NOT NULL COMMENT '신고 사유',
    reason_detail TEXT DEFAULT NULL COMMENT '상세 사유',
    report_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '처리 상태',
    admin_id INT(11) DEFAULT NULL COMMENT '처리 관리자',
    admin_note TEXT DEFAULT NULL COMMENT '관리자 메모',
    processed_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id),
    UNIQUE KEY uk_report_code (report_code),
    KEY idx_reporter (reporter_type, reporter_id),
    KEY idx_target (target_type, target_id),
    KEY idx_report_status (report_status),
    KEY idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='신고';

-- =====================================================
-- 5. Payment & Point Domain (결제/포인트)
-- =====================================================

-- 5.1 포인트 상품
CREATE TABLE t_point_product (
    product_id INT(11) NOT NULL AUTO_INCREMENT,
    product_code VARCHAR(50) NOT NULL COMMENT '상품 코드',
    product_name VARCHAR(100) NOT NULL COMMENT '상품명',
    point_amount INT(11) NOT NULL COMMENT '포인트 수량',
    price DECIMAL(12,2) NOT NULL COMMENT '가격',
    bonus_point INT(11) DEFAULT 0 COMMENT '보너스 포인트',
    discount_rate DECIMAL(5,2) DEFAULT 0 COMMENT '할인율',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    display_order INT(11) DEFAULT 0 COMMENT '노출 순서',
    valid_from DATETIME DEFAULT NULL COMMENT '판매 시작일',
    valid_until DATETIME DEFAULT NULL COMMENT '판매 종료일',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    UNIQUE KEY uk_product_code (product_code),
    KEY idx_is_active_order (is_active, display_order),
    KEY idx_valid_date (valid_from, valid_until)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='포인트 상품';

-- 5.2 결제 내역
CREATE TABLE `t_payment` (
  payment_id int(11) NOT NULL AUTO_INCREMENT,
  order_no varchar(50) NOT NULL COMMENT '주문번호',
  user_id varchar(100) NOT NULL,
  product_id int(11) DEFAULT NULL,
  payment_type varchar(30) NOT NULL COMMENT '결제 유형: POINT_CHARGE, SUBSCRIPTION',
  amount int(11) NOT NULL COMMENT '결제 금액',
  point_amount int(11) DEFAULT 0 COMMENT '충전 포인트',
  mileage_used int(11) DEFAULT 0 COMMENT '사용 마일리지',
  payment_method varchar(30) NOT NULL COMMENT '결제 수단, pgcode',
  payment_status varchar(20) NOT NULL DEFAULT 'PENDING' COMMENT '결제 상태',
  pg_tid varchar(100) DEFAULT NULL COMMENT 'PG 거래번호',
  cid varchar(100) DEFAULT '' COMMENT 'cid',
  billkey varchar(200) DEFAULT NULL COMMENT '자 동결제 재결제용 키',
  card_info varchar(100) DEFAULT NULL COMMENT '마스킹 카드번호',
  pay_info varchar(100) DEFAULT '' COMMENT '결제정보',
  tax_amount varchar(100) DEFAULT '0' COMMENT '세금',
  install_month varchar(100) DEFAULT NULL,
  pay_hash varchar(100) DEFAULT NULL,
  taxfree_amount varchar(100) DEFAULT NULL,
  nonsettle_amount varchar(100) DEFAULT NULL,
  discount_amount varchar(100) DEFAULT NULL,
  point_use_flag varchar(100) DEFAULT NULL,
  disposable_cup_deposit varchar(100) DEFAULT NULL,
  domestic_flag varchar(100) DEFAULT '' COMMENT '도메스틱 플래그',
  paid_at datetime DEFAULT NULL COMMENT '결제 완료 시간',
  code varchar(100) DEFAULT NULL COMMENT '성공코드',
  result_message text DEFAULT NULL COMMENT '결과 메시지',
  cancel_amount int(11) DEFAULT NULL COMMENT '환불 금액',
  cancelled_at datetime DEFAULT NULL COMMENT '취소 시간',
  account_no varchar(100) DEFAULT NULL,
  account_name varchar(100) DEFAULT NULL,
  account_holder varchar(100) DEFAULT NULL,
  bank_code varchar(100) DEFAULT NULL,
  bank_name varchar(100) DEFAULT NULL,
  expire_date varchar(100) DEFAULT NULL,
  expire_time varchar(100) DEFAULT NULL,
  issue_tid varchar(100) DEFAULT NULL,
  cash_receipt_type varchar(100) DEFAULT NULL,
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  updated_at datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`payment_id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id_status` (`user_id`,`payment_status`),
  KEY `idx_paid_at` (`paid_at`),
  KEY `idx_created_at` (`created_at` DESC),
  KEY `fk_payment_product` (`product_id`)
)  ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='결제 내역';

-- 5.3 포인트/마일리지 거래 내역 (통합)
CREATE TABLE t_point_transaction (
    transaction_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) NOT NULL,
    transaction_type VARCHAR(30) NOT NULL COMMENT '거래 유형: CHARGE, USE, EARN, EXPIRE, CANCEL',
    currency_type VARCHAR(20) NOT NULL COMMENT '통화 유형: POINT, MILEAGE, TRADE',
    amount INT(11) NOT NULL COMMENT '거래 금액 (양수: 증가, 음수: 감소)',
    balance_after INT(11) NOT NULL COMMENT '거래 후 잔액',
    reference_type VARCHAR(50) DEFAULT NULL COMMENT '참조 유형: PAYMENT, CONSULTATION, EVENT, MANUAL',
    reference_id VARCHAR(100) DEFAULT NULL COMMENT '참조 ID',
    description TEXT DEFAULT NULL COMMENT '거래 설명',
    earn_rate DECIMAL(5,2) DEFAULT NULL COMMENT '적립률',
    expires_at DATETIME DEFAULT NULL COMMENT '만료일시',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    KEY idx_user_currency_created (user_id, currency_type, created_at DESC),
    KEY idx_reference (reference_type, reference_id),
    KEY idx_expires_at (expires_at)
    --CONSTRAINT fk_transaction_user FOREIGN KEY (user_id) REFERENCES t_user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='포인트/마일리지 거래 내역';

-- 5.4 외부 포인트 동기화 로그
CREATE TABLE t_external_point_sync (
    sync_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) NOT NULL,
    external_user_id VARCHAR(100) NOT NULL COMMENT '외부 시스템 사용자 ID',
    sync_type VARCHAR(20) NOT NULL COMMENT '동기화 유형: DEDUCT, REFUND',
    point_amount INT(11) NOT NULL COMMENT '포인트 금액',
    session_id INT(11) DEFAULT NULL COMMENT '관련 상담 세션',
    sync_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '동기화 상태',
    external_response TEXT DEFAULT NULL COMMENT '외부 시스템 응답',
    retry_count INT(11) DEFAULT 0 COMMENT '재시도 횟수',
    synced_at DATETIME DEFAULT NULL COMMENT '동기화 완료 시간',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sync_id),
    KEY idx_user_id_status (user_id, sync_status),
    KEY idx_session_id (session_id),
    KEY idx_created_at (created_at)
    --CONSTRAINT fk_sync_user FOREIGN KEY (user_id) REFERENCES t_user(user_id),
    --CONSTRAINT fk_sync_session FOREIGN KEY (session_id) REFERENCES t_consultation_session(session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='외부 포인트 동기화 로그';

-- =====================================================
-- 6. Admin & System Domain (관리자/시스템)
-- =====================================================

-- 6.1 관리자
CREATE TABLE t_admin (
    admin_id INT(11) NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(100) NOT NULL COMMENT '로그인 ID',
    password_hash VARCHAR(255) NOT NULL COMMENT '비밀번호 해시',
    name VARCHAR(50) NOT NULL COMMENT '관리자 이름',
    email VARCHAR(100) NOT NULL COMMENT '이메일',
    phone VARCHAR(20) NOT NULL COMMENT '전화번호',
    role VARCHAR(20) NOT NULL DEFAULT 'CS' COMMENT '권한: SUPER, ADMIN, CS',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    last_login_at DATETIME DEFAULT NULL COMMENT '마지막 로그인',
    last_login_ip VARCHAR(45) DEFAULT NULL COMMENT '마지막 로그인 IP',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (admin_id),
    UNIQUE KEY uk_login_id (login_id),
    UNIQUE KEY uk_email (email),
    KEY idx_role (role),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='관리자';

-- 6.2 시스템 설정
CREATE TABLE t_system_config (
    config_key VARCHAR(100) NOT NULL COMMENT '설정 키',
    config_value TEXT NOT NULL COMMENT '설정 값',
    config_type VARCHAR(20) DEFAULT 'STRING' COMMENT '값 타입: STRING, NUMBER, BOOLEAN, JSON',
    description TEXT DEFAULT NULL COMMENT '설명',
    is_public TINYINT(1) DEFAULT 0 COMMENT '공개 여부',
    updated_by INT(11) DEFAULT NULL COMMENT '수정자',
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='시스템 설정';

-- 6.3 등급 정의
CREATE TABLE t_grade (
    grade_code VARCHAR(20) NOT NULL COMMENT '등급 코드',
    grade_name VARCHAR(50) NOT NULL COMMENT '등급명',
    grade_level INT(11) NOT NULL COMMENT '등급 레벨',
    min_purchase_amount INT(11) NOT NULL COMMENT '최소 구매 금액',
    point_earn_rate DECIMAL(5,2) NOT NULL COMMENT '포인트 적립률',
    discount_rate DECIMAL(5,2) DEFAULT 0 COMMENT '할인율',
    benefits JSON DEFAULT NULL COMMENT '추가 혜택',
    grade_image_url VARCHAR(500) DEFAULT NULL COMMENT '등급 이미지',
    description TEXT DEFAULT NULL COMMENT '등급 설명',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (grade_code),
    UNIQUE KEY uk_grade_level (grade_level),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='등급 정의';

-- =====================================================
-- 7. Notification Domain (알림)
-- =====================================================

-- 7.1 알림 템플릿
CREATE TABLE t_notification_template (
    template_id INT(11) NOT NULL AUTO_INCREMENT,
    template_code VARCHAR(50) NOT NULL COMMENT '템플릿 코드',
    template_name VARCHAR(100) NOT NULL COMMENT '템플릿명',
    channel VARCHAR(20) NOT NULL COMMENT '채널: KAKAO, SMS, EMAIL, PUSH',
    content_template TEXT NOT NULL COMMENT '내용 템플릿',
    variables JSON DEFAULT NULL COMMENT '변수 목록',
    button_info JSON DEFAULT NULL COMMENT '버튼 정보',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (template_id),
    UNIQUE KEY uk_template_code (template_code),
    KEY idx_channel (channel),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='알림 템플릿';

-- 7.2 알림 발송 로그
CREATE TABLE t_notification_log (
    log_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    recipient_type VARCHAR(20) NOT NULL COMMENT '수신자 타입: USER, COUNSELOR',
    recipient_id VARCHAR(100) NOT NULL COMMENT '수신자 ID',
    channel VARCHAR(20) NOT NULL COMMENT '발송 채널',
    template_id INT(11) DEFAULT NULL,
    title VARCHAR(200) DEFAULT NULL COMMENT '제목',
    content TEXT NOT NULL COMMENT '내용',
    variables JSON DEFAULT NULL COMMENT '치환 변수',
    send_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '발송 상태',
    provider_response JSON DEFAULT NULL COMMENT '제공자 응답',
    sent_at DATETIME DEFAULT NULL COMMENT '발송 시간',
    read_at DATETIME DEFAULT NULL COMMENT '읽은 시간',
    failed_reason TEXT DEFAULT NULL COMMENT '실패 사유',
    retry_count INT(11) DEFAULT 0 COMMENT '재시도 횟수',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY idx_recipient (recipient_type, recipient_id),
    KEY idx_send_status (send_status),
    KEY idx_created_at (created_at DESC)
    --CONSTRAINT fk_notification_template FOREIGN KEY (template_id) REFERENCES t_notification_template(template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='알림 발송 로그';

-- =====================================================
-- 8. Content Domain (콘텐츠)
-- =====================================================

-- 8.1 공지사항
CREATE TABLE t_notice (
    notice_id INT(11) NOT NULL AUTO_INCREMENT,
    notice_type VARCHAR(20) NOT NULL DEFAULT 'GENERAL' COMMENT '공지 타입: GENERAL, EVENT, UPDATE',
    title VARCHAR(200) NOT NULL COMMENT '제목',
    content TEXT NOT NULL COMMENT '내용',
    target_audience VARCHAR(20) DEFAULT 'ALL' COMMENT '대상: ALL, USER, COUNSELOR',
    is_important TINYINT(1) DEFAULT 0 COMMENT '중요 공지',
    is_popup TINYINT(1) DEFAULT 0 COMMENT '팝업 표시',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    view_count INT(11) DEFAULT 0 COMMENT '조회수',
    attachments JSON DEFAULT NULL COMMENT '첨부파일',
    created_by INT(11) NOT NULL COMMENT '작성자',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (notice_id),
    KEY idx_type_active (notice_type, is_active),
    KEY idx_target_audience (target_audience),
    KEY idx_created_at (created_at DESC)
    --CONSTRAINT fk_notice_admin FOREIGN KEY (created_by) REFERENCES t_admin(admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='공지사항';

-- 8.2 FAQ
CREATE TABLE t_faq (
    faq_id INT(11) NOT NULL AUTO_INCREMENT,
    category VARCHAR(30) NOT NULL COMMENT '카테고리',
    target_audience VARCHAR(20) DEFAULT 'ALL' COMMENT '대상: ALL, USER, COUNSELOR',
    question TEXT NOT NULL COMMENT '질문',
    answer TEXT NOT NULL COMMENT '답변',
    display_order INT(11) DEFAULT 0 COMMENT '노출 순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    view_count INT(11) DEFAULT 0 COMMENT '조회수',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (faq_id),
    KEY idx_category_active (category, is_active),
    KEY idx_target_audience (target_audience),
    KEY idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='FAQ';

-- 8.3 1:1 문의
-- CREATE TABLE t_inquiry (
--     inquiry_id INT(11) NOT NULL AUTO_INCREMENT,
--     inquiry_code VARCHAR(50) NOT NULL COMMENT '문의 코드',
--     inquirer_type VARCHAR(20) NOT NULL COMMENT '문의자 타입: USER, COUNSELOR, GUEST',
--     inquirer_id VARCHAR(100) DEFAULT NULL COMMENT '문의자 ID (회원인 경우)',
--     inquirer_email VARCHAR(100) DEFAULT NULL COMMENT '문의자 이메일 (비회원)',
--     inquirer_phone VARCHAR(20) DEFAULT NULL COMMENT '문의자 전화번호 (비회원)',
--     category VARCHAR(30) NOT NULL COMMENT '문의 카테고리',
--     title VARCHAR(200) NOT NULL COMMENT '제목',
--     content TEXT NOT NULL COMMENT '내용',
--     attachments JSON DEFAULT NULL COMMENT '첨부파일',
--     inquiry_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '상태',
--     admin_id INT(11) DEFAULT NULL COMMENT '담당 관리자',
--     admin_reply TEXT DEFAULT NULL COMMENT '관리자 답변',
--     answered_at DATETIME DEFAULT NULL COMMENT '답변 시간',
--     created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
--     PRIMARY KEY (inquiry_id),
--     UNIQUE KEY uk_inquiry_code (inquiry_code),
--     KEY idx_inquirer (inquirer_type, inquirer_id),
--     KEY idx_status (inquiry_status),
--     KEY idx_created_at (created_at DESC),
--     CONSTRAINT fk_inquiry_admin FOREIGN KEY (admin_id) REFERENCES t_admin(admin_id)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='1:1 문의';
-- 2025-09-10 수정 버전
CREATE TABLE `t_inquiry` (
  `inquiry_id` int(11) NOT NULL AUTO_INCREMENT,
  `inquirer_type` varchar(20) NOT NULL COMMENT '문의자 타입: USER, COUNSELOR, GUEST',
  `inquirer_id` varchar(100) DEFAULT NULL COMMENT '문의자 ID',
  `counselor_id` varchar(100) DEFAULT NULL COMMENT '문의 상담사 id',
  `category` varchar(30) DEFAULT NULL COMMENT '문의 카테고리',
  `title` varchar(200) DEFAULT NULL COMMENT '제목',
  `content` text NOT NULL COMMENT '내용',
  `is_read` tinyint(1) DEFAULT 0 COMMENT '읽음 상태',
  `reply_content` text DEFAULT NULL COMMENT '관리자 답변',
  `answered_at` datetime DEFAULT NULL COMMENT '답변 시간',
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`inquiry_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3415 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='1:1 문의';

-- 8.4 배너
CREATE TABLE t_banner (
    banner_id INT(11) NOT NULL AUTO_INCREMENT,
    banner_code VARCHAR(50) NOT NULL COMMENT '배너 코드',
    banner_name VARCHAR(100) NOT NULL COMMENT '배너명',
    banner_type VARCHAR(20) NOT NULL DEFAULT 'MAIN' COMMENT '배너 타입: MAIN, SUB, POPUP',
    image_url VARCHAR(500) NOT NULL COMMENT '이미지 URL',
    mobile_image_url VARCHAR(500) DEFAULT NULL COMMENT '모바일 이미지 URL',
    link_url VARCHAR(500) DEFAULT NULL COMMENT '링크 URL',
    link_target VARCHAR(10) DEFAULT 'SELF' COMMENT '링크 타겟: SELF, BLANK',
    display_order INT(11) DEFAULT 0 COMMENT '노출 순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    valid_from DATETIME NOT NULL COMMENT '노출 시작일',
    valid_until DATETIME NOT NULL COMMENT '노출 종료일',
    click_count INT(11) DEFAULT 0 COMMENT '클릭수',
    impression_count INT(11) DEFAULT 0 COMMENT '노출수',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (banner_id),
    UNIQUE KEY uk_banner_code (banner_code),
    KEY idx_type_active (banner_type, is_active),
    KEY idx_valid_date (valid_from, valid_until),
    KEY idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='배너';

-- 8.5 이벤트
CREATE TABLE t_event (
    event_id INT(11) NOT NULL AUTO_INCREMENT,
    event_code VARCHAR(50) NOT NULL COMMENT '이벤트 코드',
    event_name VARCHAR(100) NOT NULL COMMENT '이벤트명',
    event_type VARCHAR(30) NOT NULL COMMENT '이벤트 타입',
    description TEXT DEFAULT NULL COMMENT '설명',
    terms TEXT DEFAULT NULL COMMENT '약관',
    banner_image_url VARCHAR(500) DEFAULT NULL COMMENT '배너 이미지',
    reward_type VARCHAR(30) NOT NULL COMMENT '보상 타입: POINT, MILEAGE, COUPON',
    reward_value INT(11) NOT NULL COMMENT '보상 값',
    max_participants INT(11) DEFAULT NULL COMMENT '최대 참여자수',
    current_participants INT(11) DEFAULT 0 COMMENT '현재 참여자수',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    valid_from DATETIME NOT NULL COMMENT '시작일',
    valid_until DATETIME NOT NULL COMMENT '종료일',
    metadata JSON DEFAULT NULL COMMENT '추가 데이터',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (event_id),
    UNIQUE KEY uk_event_code (event_code),
    KEY idx_type_active (event_type, is_active),
    KEY idx_valid_date (valid_from, valid_until)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='이벤트';

-- =====================================================
-- 9. Log Domain (로그)
-- =====================================================

-- 9.1 사용자 활동 로그
CREATE TABLE t_user_activity_log (
    log_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) DEFAULT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'USER' COMMENT '사용자 타입: USER, COUNSELOR, GUEST',
    activity_type VARCHAR(50) NOT NULL COMMENT '활동 타입',
    activity_detail JSON DEFAULT NULL COMMENT '활동 상세',
    ip_address VARCHAR(45) DEFAULT NULL COMMENT 'IP 주소',
    user_agent TEXT DEFAULT NULL COMMENT 'User Agent',
    device_type VARCHAR(20) DEFAULT NULL COMMENT '기기 타입',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY idx_user_id_created (user_id, created_at DESC),
    KEY idx_activity_type (activity_type),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='사용자 활동 로그';

-- 9.2 검색 로그
CREATE TABLE t_search_log (
    log_id BIGINT(20) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) DEFAULT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'USER' COMMENT '사용자 타입',
    search_type VARCHAR(30) NOT NULL COMMENT '검색 타입',
    keyword VARCHAR(200) NOT NULL COMMENT '검색어',
    search_filters JSON DEFAULT NULL COMMENT '검색 필터',
    result_count INT(11) DEFAULT 0 COMMENT '결과 수',
    selected_item_id VARCHAR(100) DEFAULT NULL COMMENT '선택 항목',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY idx_user_id (user_id),
    KEY idx_keyword (keyword),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='검색 로그';

-- 9.3 이벤트 참여 로그
CREATE TABLE t_event_participation_log (
    log_id INT(11) NOT NULL AUTO_INCREMENT,
    event_id INT(11) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    participation_data JSON DEFAULT NULL COMMENT '참여 데이터',
    reward_type VARCHAR(50) DEFAULT NULL COMMENT '보상 타입',
    reward_value INT(11) DEFAULT NULL COMMENT '보상 값',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    UNIQUE KEY uk_event_user (event_id, user_id),
    KEY idx_user_id (user_id),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='이벤트 참여 로그';

-- 9.4 등급 변경 로그
CREATE TABLE t_grade_change_log (
    log_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(100) NOT NULL,
    grade_before VARCHAR(20) NOT NULL COMMENT '이전 등급',
    grade_after VARCHAR(20) NOT NULL COMMENT '변경 후 등급',
    purchase_amount INT(11) NOT NULL COMMENT '구매 금액',
    change_reason VARCHAR(50) NOT NULL COMMENT '변경 사유',
    admin_id INT(11) DEFAULT NULL COMMENT '처리 관리자',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY idx_user_id (user_id),
    KEY idx_created_at (created_at)
    --CONSTRAINT fk_grade_log_user FOREIGN KEY (user_id) REFERENCES t_user(user_id),
    --CONSTRAINT fk_grade_log_admin FOREIGN KEY (admin_id) REFERENCES t_admin(admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='등급 변경 로그';

-- 9.5 배치 실행 로그
CREATE TABLE t_batch_execution_log (
    log_id INT(11) NOT NULL AUTO_INCREMENT,
    batch_name VARCHAR(100) NOT NULL COMMENT '배치명',
    batch_type VARCHAR(50) NOT NULL COMMENT '배치 타입',
    execution_status VARCHAR(20) NOT NULL COMMENT '실행 상태',
    started_at DATETIME DEFAULT NULL COMMENT '시작 시간',
    ended_at DATETIME DEFAULT NULL COMMENT '종료 시간',
    total_processed INT(11) DEFAULT 0 COMMENT '처리 건수',
    success_count INT(11) DEFAULT 0 COMMENT '성공 건수',
    fail_count INT(11) DEFAULT 0 COMMENT '실패 건수',
    error_details JSON DEFAULT NULL COMMENT '에러 상세',
    execution_params JSON DEFAULT NULL COMMENT '실행 파라미터',
    PRIMARY KEY (log_id),
    KEY idx_batch_name (batch_name),
    KEY idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='배치 실행 로그';

-- =====================================================
-- 10. 배치 및 설정 테이블
-- =====================================================

-- 10.1 등급 배치 설정
CREATE TABLE t_grade_batch_config (
    config_id INT(11) NOT NULL AUTO_INCREMENT,
    period_month INT(11) NOT NULL COMMENT '등급 조정 주기(월)',
    period_day INT(11) NOT NULL COMMENT '실행일',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    last_executed_at DATETIME DEFAULT NULL COMMENT '마지막 실행일',
    updated_by INT(11) DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (config_id)
    --CONSTRAINT fk_grade_config_admin FOREIGN KEY (updated_by) REFERENCES t_admin(admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='등급 배치 설정';

-- 10.2 마일리지 설정
CREATE TABLE t_mileage_config (
    config_key VARCHAR(50) NOT NULL COMMENT '설정 키',
    config_value VARCHAR(255) NOT NULL COMMENT '설정 값',
    description VARCHAR(500) DEFAULT NULL COMMENT '설명',
    updated_by INT(11) DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (config_key)
    --CONSTRAINT fk_mileage_config_admin FOREIGN KEY (updated_by) REFERENCES t_admin(admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='마일리지 설정';

-- =====================================================
-- 11. 더미 데이터 테이블 (마케팅용)
-- =====================================================

-- 11.1 더미 후기
CREATE TABLE t_review_dummy (
    dummy_id INT(11) NOT NULL AUTO_INCREMENT,
    user_nickname VARCHAR(100) DEFAULT NULL COMMENT '사용자 닉네임',
    counselor_id VARCHAR(100) DEFAULT NULL,
    consultation_duration INT(11) DEFAULT NULL COMMENT '상담 시간(분)',
    content TEXT DEFAULT NULL COMMENT '후기 내용',
    counselor_reply TEXT DEFAULT NULL COMMENT '상담사 답변',
    display_order INT(11) DEFAULT 0 COMMENT '노출 순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dummy_id),
    KEY idx_counselor_id (counselor_id),
    KEY idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='더미 후기';

-- =====================================================
-- 12. 초기 데이터 입력
-- =====================================================

-- 등급 초기 데이터
INSERT INTO t_grade (grade_code, grade_name, grade_level, min_purchase_amount, point_earn_rate, discount_rate) VALUES
('WHITE', '화이트', 1, 0, 1.0, 0),
('SILVER', '실버', 2, 100000, 2.0, 5.0),
('GOLD', '골드', 3, 300000, 3.0, 10.0),
('VIP', 'VIP', 4, 500000, 5.0, 15.0);

-- 시스템 설정 초기 데이터
INSERT INTO t_system_config (config_key, config_value, config_type, description) VALUES
('system.maintenance_mode', 'false', 'BOOLEAN', '시스템 점검 모드'),
('point.expire_days', '365', 'NUMBER', '포인트 만료 일수'),
('consultation.max_duration_minutes', '180', 'NUMBER', '최대 상담 시간(분)'),
('consultation.point_per_minute_default', '1000', 'NUMBER', '기본 분당 포인트'),
('notification.kakao.sender_key', '', 'STRING', '카카오 알림톡 발신키'),
('notification.sms.sender_number', '1588-0000', 'STRING', 'SMS 발신번호');

-- 마일리지 설정 초기 데이터
INSERT INTO t_mileage_config (config_key, config_value, description) VALUES
('mileage.expire_days', '365', '마일리지 만료 일수'),
('mileage.min_use_amount', '1000', '최소 사용 금액'),
('mileage.max_use_rate', '100', '최대 사용 비율(%)');

-- 관리자 계정 (비밀번호: admin123 의 bcrypt 해시)
INSERT INTO t_admin (login_id, password_hash, name, email, phone, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQaXscF', 'Super Admin', 'admin@sajuline.com', '010-1234-5678', 'SUPER');



-- == 2025-09-05 추가 스키마 ==



CREATE TABLE `t_user_bookmark` (
  `bookmark_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(100) NOT NULL COMMENT '유저 id',
  `counselor_id` varchar(100) NOT NULL COMMENT '상담사 id',
  `created_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT '등록일',
  PRIMARY KEY (`bookmark_id`),
  KEY `t_user_bookmark_user_id_IDX` (`user_id`) USING BTREE,
  KEY `t_user_bookmark_counselor_id_IDX` (`counselor_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- == 2025-09-30 추가 스키마 ==

CREATE TABLE `t_mileage_product` (
  `mileage_id` int(11) NOT NULL AUTO_INCREMENT,
  `m_product_name` varchar(100) NOT NULL COMMENT '상품명',
  `m_product_value` int(11) NOT NULL COMMENT '상품가격',
  `charge_point` int(11) NOT NULL COMMENT '충전 포인트',
  `m_product_img` varchar(100) DEFAULT NULL,
  `image_url` varchar(100) DEFAULT NULL,
  `valid_from` datetime DEFAULT NULL COMMENT '상품 노출 시작일',
  `valid_until` datetime DEFAULT NULL COMMENT '상품 노출 종료일',
  `ord` int(11) NOT NULL COMMENT '노출 순번',
  `tags` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL COMMENT '상품설명',
  `is_active` tinyint(1) NOT NULL DEFAULT '0' COMMENT '사용유무',
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`mileage_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;