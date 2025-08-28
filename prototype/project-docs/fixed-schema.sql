-- =====================================================
-- 사주라인 리뉴얼 PostgreSQL 최종 스키마 (수정됨)
-- Version: Final v3.0 Fixed
-- Date: 2025-01-01
-- =====================================================

-- =====================================================
-- 0. 필수 확장 기능 및 함수
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 업데이트 타임스탬프 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 비즈니스 코드 생성용 시퀀스들
CREATE SEQUENCE IF NOT EXISTS booking_code_seq;
CREATE SEQUENCE IF NOT EXISTS session_code_seq;
CREATE SEQUENCE IF NOT EXISTS order_seq;
CREATE SEQUENCE IF NOT EXISTS report_seq;
CREATE SEQUENCE IF NOT EXISTS inquiry_seq;

-- =====================================================
-- 1. User Domain (사용자 관리)
-- =====================================================

-- 1.1 사용자 기본 정보
CREATE TABLE t_user (
    user_id VARCHAR(100) PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    phone VARCHAR(15) NOT NULL UNIQUE,
    nickname VARCHAR(100) NOT NULL UNIQUE,
    join_type VARCHAR(20) NOT NULL DEFAULT 'EMAIL',
    user_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    grade_code VARCHAR(20) NOT NULL DEFAULT 'WHITE',
    point_balance INT NOT NULL DEFAULT 0,
    mileage_balance INT NOT NULL DEFAULT 0,
    profile_image_url VARCHAR(500),
    birth_datetime TIMESTAMPTZ,
    is_lunar_birth BOOLEAN DEFAULT FALSE,
    gender VARCHAR(10),
    fcm_token VARCHAR(255),
    is_marketing_agreed BOOLEAN DEFAULT FALSE,
    terms_agreed_at TIMESTAMPTZ NOT NULL,
    privacy_agreed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMPTZ,
    withdrawn_at TIMESTAMPTZ
);

-- 1.2 사용자 선호도
CREATE TABLE t_user_preference (
    user_id VARCHAR(100) PRIMARY KEY REFERENCES t_user(user_id) ON DELETE CASCADE,
    prefer_categories JSONB DEFAULT '[]'::JSONB,
    prefer_counselor_styles JSONB DEFAULT '[]'::JSONB,
    prefer_time_slots JSONB DEFAULT '[]'::JSONB,
    ai_usage_level VARCHAR(20) DEFAULT 'BEGINNER',
    notification_settings JSONB DEFAULT '{
        "daily_fortune": true,
        "marketing": false,
        "consultation_reminder": true
    }'::JSONB,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 사용자 활동 로그 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_user_activity_log (
    activity_seq BIGSERIAL,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    activity_detail JSONB,
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_seq, created_at)
) PARTITION BY RANGE (created_at);

-- =====================================================
-- 2. Counselor Domain (상담사 관리)
-- =====================================================

-- 2.1 상담사 정보
CREATE TABLE t_counselor (
    nickname VARCHAR(100) PRIMARY KEY,
    counselor_code VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    profile_image_url VARCHAR(500),
    introduction_short TEXT,
    introduction_long TEXT,
    greeting_message TEXT,
    specialties JSONB DEFAULT '[]'::JSONB,
    keywords JSONB DEFAULT '[]'::JSONB,
    consultation_styles JSONB DEFAULT '[]'::JSONB,
    experience_years INT DEFAULT 0,
    career_detail TEXT,
    certificates JSONB DEFAULT '[]'::JSONB,
    counselor_status VARCHAR(20) NOT NULL DEFAULT 'REVIEWING',
    online_status VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
    grade VARCHAR(20) DEFAULT 'BRONZE',
    rating_avg NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    consultation_count INT DEFAULT 0,
    approval_status VARCHAR(20) DEFAULT 'PENDING',
    approved_at TIMESTAMPTZ,
    applied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMPTZ
);

-- 2.2 상담사 근무 시간
CREATE TABLE t_counselor_schedule (
    counselor_nickname VARCHAR(100) NOT NULL REFERENCES t_counselor(nickname) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL,
    time_slot_start TIME NOT NULL,
    time_slot_end TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (counselor_nickname, day_of_week, time_slot_start)
);

-- 2.3 상담사 가격 정책
CREATE TABLE t_counselor_pricing (
    counselor_nickname VARCHAR(100) PRIMARY KEY REFERENCES t_counselor(nickname) ON DELETE CASCADE,
    chat_price_per_min INT NOT NULL DEFAULT 1000,
    voice_price_per_min INT NOT NULL DEFAULT 2000,
    video_price_per_min INT NOT NULL DEFAULT 3000,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. AI Domain (AI 서비스)
-- =====================================================

-- 3.1 AI 운세 분석
CREATE TABLE t_ai_fortune (
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    fortune_type VARCHAR(20) NOT NULL,
    target_date DATE NOT NULL,
    fortune_data JSONB NOT NULL,
    ai_model_version VARCHAR(20) NOT NULL,
    processing_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, fortune_type, target_date)
);

-- 3.2 AI 채팅 상담
CREATE TABLE t_ai_consultation (
    consultation_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    session_title VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    message_count INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    ai_model_version VARCHAR(20) NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB
);

-- 3.3 AI 채팅 메시지
CREATE TABLE t_ai_message (
    message_seq BIGSERIAL PRIMARY KEY,
    consultation_seq BIGINT NOT NULL REFERENCES t_ai_consultation(consultation_seq) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens_used INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3.4 AI 서비스 사용 로그 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_ai_usage_log (
    usage_seq BIGSERIAL,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    service_type VARCHAR(50) NOT NULL,
    request_data JSONB,
    response_data JSONB,
    ai_model_version VARCHAR(20),
    processing_time_ms INT,
    tokens_used INT DEFAULT 0,
    point_used INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usage_seq, created_at)
) PARTITION BY RANGE (created_at);

-- =====================================================
-- 4. Consultation Domain (상담 서비스)
-- =====================================================

-- 4.1 상담 예약
CREATE TABLE t_consultation_booking (
    booking_seq BIGSERIAL PRIMARY KEY,
    booking_code VARCHAR(20) UNIQUE DEFAULT 
        ('BK' || TO_CHAR(CURRENT_DATE, 'YYMMDD') || LPAD(nextval('booking_code_seq')::TEXT, 6, '0')),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_nickname VARCHAR(100) NOT NULL REFERENCES t_counselor(nickname),
    booking_datetime TIMESTAMPTZ NOT NULL,
    duration_minutes INT NOT NULL DEFAULT 30,
    consultation_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    cancel_reason TEXT,
    cancelled_at TIMESTAMPTZ,
    cancelled_by VARCHAR(20),
    is_reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4.2 상담 세션
CREATE TABLE t_consultation_session (
    session_seq BIGSERIAL PRIMARY KEY,
    session_code VARCHAR(20) UNIQUE DEFAULT 
        ('SE' || TO_CHAR(CURRENT_DATE, 'YYMMDD') || LPAD(nextval('session_code_seq')::TEXT, 6, '0')),
    booking_seq BIGINT REFERENCES t_consultation_booking(booking_seq),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_nickname VARCHAR(100) NOT NULL REFERENCES t_counselor(nickname),
    consultation_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INT DEFAULT 0,
    total_point_used INT DEFAULT 0,
    user_rating SMALLINT,
    user_review TEXT,
    counselor_memo TEXT,
    session_summary JSONB,
    started_year INT,
    started_month INT,
    started_day INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4.3 채팅 메시지 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_chat_message (
    message_seq BIGSERIAL,
    session_seq BIGINT NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    sender_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'TEXT',
    content TEXT,
    file_info JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_seq, created_at)
) PARTITION BY RANGE (created_at);

-- 4.4 상담 대기열
CREATE TABLE t_consultation_queue (
    queue_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_nickname VARCHAR(100) NOT NULL REFERENCES t_counselor(nickname),
    priority INT DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    queued_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    notified_at TIMESTAMPTZ,
    expired_at TIMESTAMPTZ,
    connected_at TIMESTAMPTZ,
    CONSTRAINT uk_user_counselor_queue UNIQUE (user_id, counselor_nickname, status)
);

-- =====================================================
-- 5. Payment Domain (결제/포인트)
-- =====================================================

-- 5.1 포인트 상품
CREATE TABLE t_point_product (
    product_code VARCHAR(30) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    point_amount INT NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    bonus_point INT DEFAULT 0,
    discount_rate NUMERIC(5,2) DEFAULT 0,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    product_tags JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5.2 결제 내역
CREATE TABLE t_payment (
    payment_seq BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(20) UNIQUE DEFAULT 
        ('ORD' || TO_CHAR(CURRENT_DATE, 'YYMMDD') || LPAD(nextval('order_seq')::TEXT, 6, '0')),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    payment_type VARCHAR(30) NOT NULL,
    product_code VARCHAR(30) REFERENCES t_point_product(product_code),
    amount NUMERIC(12,2) NOT NULL,
    point_amount INT DEFAULT 0,
    mileage_used INT DEFAULT 0,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    pg_provider VARCHAR(20),
    pg_tid VARCHAR(100),
    pg_response JSONB,
    paid_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancel_reason TEXT,
    refund_amount NUMERIC(12,2),
    refunded_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::JSONB,
    paid_year INT,
    paid_month INT,
    paid_day INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5.3 포인트 이력 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_point_log (
    point_log_seq BIGSERIAL,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    transaction_type VARCHAR(30) NOT NULL,
    point_amount INT NOT NULL,
    balance_after INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(100),
    description TEXT,
    expires_at TIMESTAMPTZ,
    created_year INT,
    created_month INT,
    created_day INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (point_log_seq, created_at)
) PARTITION BY RANGE (created_at);

-- 5.4 마일리지 이력
CREATE TABLE t_mileage_log (
    mileage_log_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    transaction_type VARCHAR(20) NOT NULL,
    mileage_amount INT NOT NULL,
    balance_after INT NOT NULL,
    earn_rate NUMERIC(5,2),
    reference_type VARCHAR(50),
    reference_id VARCHAR(100),
    description TEXT,
    expires_at TIMESTAMPTZ,
    created_year INT,
    created_month INT,
    created_day INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. Community Domain (커뮤니티)
-- =====================================================

-- 6.1 상담 후기
CREATE TABLE t_review (
    review_seq BIGSERIAL PRIMARY KEY,
    session_seq BIGINT NOT NULL UNIQUE REFERENCES t_consultation_session(session_seq),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_nickname VARCHAR(100) NOT NULL REFERENCES t_counselor(nickname),
    rating SMALLINT NOT NULL,
    content TEXT,
    counselor_reply TEXT,
    is_best BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,
    like_count INT DEFAULT 0,
    tags JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    counselor_replied_at TIMESTAMPTZ
);

-- 6.2 후기 좋아요
CREATE TABLE t_review_like (
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    review_seq BIGINT NOT NULL REFERENCES t_review(review_seq) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, review_seq)
);

-- 6.3 신고
CREATE TABLE t_report (
    report_seq BIGSERIAL PRIMARY KEY,
    report_no VARCHAR(20) UNIQUE DEFAULT 
        ('RPT' || TO_CHAR(CURRENT_DATE, 'YYMMDD') || LPAD(nextval('report_seq')::TEXT, 6, '0')),
    reporter_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    report_type VARCHAR(30) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    reason_type VARCHAR(30) NOT NULL,
    reason_detail TEXT,
    evidence_urls JSONB DEFAULT '[]'::JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    admin_id VARCHAR(100),
    admin_note TEXT,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6.4 FAQ
CREATE TABLE t_faq (
    faq_seq BIGSERIAL PRIMARY KEY,
    category VARCHAR(30) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::JSONB,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6.5 1:1 문의
CREATE TABLE t_inquiry (
    inquiry_seq BIGSERIAL PRIMARY KEY,
    inquiry_no VARCHAR(20) UNIQUE DEFAULT 
        ('INQ' || TO_CHAR(CURRENT_DATE, 'YYMMDD') || LPAD(nextval('inquiry_seq')::TEXT, 6, '0')),
    user_id VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]'::JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    admin_id VARCHAR(100),
    admin_reply TEXT,
    answered_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. System Domain (시스템 관리)
-- =====================================================

-- 7.1 관리자
CREATE TABLE t_admin (
    admin_id VARCHAR(100) PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'CS',
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSONB DEFAULT '{}'::JSONB,
    last_login_at TIMESTAMPTZ,
    last_login_ip INET,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7.2 배너
CREATE TABLE t_banner (
    banner_code VARCHAR(30) PRIMARY KEY,
    banner_name VARCHAR(100) NOT NULL,
    banner_type VARCHAR(20) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    mobile_image_url VARCHAR(500),
    link_url VARCHAR(500),
    link_target VARCHAR(10) DEFAULT 'SELF',
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    click_count INT DEFAULT 0,
    impression_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7.3 공지사항
CREATE TABLE t_notice (
    notice_seq BIGSERIAL PRIMARY KEY,
    category VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_important BOOLEAN DEFAULT FALSE,
    is_popup BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    admin_id VARCHAR(100) NOT NULL REFERENCES t_admin(admin_id),
    attachments JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7.4 이벤트
CREATE TABLE t_event (
    event_code VARCHAR(30) PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    description TEXT,
    terms TEXT,
    banner_image_url VARCHAR(500),
    reward_type VARCHAR(30) NOT NULL,
    reward_value INT NOT NULL,
    max_participants INT,
    current_participants INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7.5 시스템 설정
CREATE TABLE t_system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'STRING',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- 7.6 등급 정의
CREATE TABLE t_grade (
    grade_code VARCHAR(20) PRIMARY KEY,
    grade_name VARCHAR(50) NOT NULL,
    grade_level INT NOT NULL UNIQUE,
    min_purchase_amount INT NOT NULL,
    point_earn_rate NUMERIC(5,2) NOT NULL,
    discount_rate NUMERIC(5,2) DEFAULT 0,
    benefits JSONB DEFAULT '{}'::JSONB,
    grade_image_url VARCHAR(500),
    grade_color VARCHAR(7),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. Notification Domain (알림)
-- =====================================================

-- 8.1 알림 템플릿
CREATE TABLE t_notification_template (
    template_code VARCHAR(50) PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_type VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    content_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::JSONB,
    button_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8.2 알림 발송 이력 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_notification_log (
    notification_seq BIGSERIAL,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    template_code VARCHAR(50) REFERENCES t_notification_template(template_code),
    title VARCHAR(200),
    content TEXT NOT NULL,
    variables JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    provider_response JSONB,
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    failed_reason TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_seq, created_at)
) PARTITION BY RANGE (created_at);

-- 8.3 알림 대기열
CREATE TABLE t_notification_queue (
    queue_seq BIGSERIAL PRIMARY KEY,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id VARCHAR(100) NOT NULL,
    notification_type VARCHAR(30) NOT NULL,
    priority INT DEFAULT 0,
    payload JSONB NOT NULL,
    scheduled_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8.4 사용자 알림 설정
CREATE TABLE t_user_notification_setting (
    user_id VARCHAR(100) PRIMARY KEY REFERENCES t_user(user_id) ON DELETE CASCADE,
    kakao_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    night_time_enabled BOOLEAN DEFAULT FALSE,
    notification_types JSONB DEFAULT '{
        "consultation_start": true,
        "consultation_reminder": true,
        "payment_complete": true,
        "point_expire": true,
        "daily_fortune": true,
        "event_info": true,
        "marketing": false
    }'::JSONB,
    quiet_time_start TIME DEFAULT '22:00',
    quiet_time_end TIME DEFAULT '08:00',
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8.5 상담사 알림 설정
CREATE TABLE t_counselor_notification_setting (
    counselor_nickname VARCHAR(100) PRIMARY KEY REFERENCES t_counselor(nickname) ON DELETE CASCADE,
    consultation_request BOOLEAN DEFAULT TRUE,
    queue_notification BOOLEAN DEFAULT TRUE,
    review_notification BOOLEAN DEFAULT TRUE,
    daily_summary BOOLEAN DEFAULT TRUE,
    channels JSONB DEFAULT '{
        "kakao": true,
        "sms": true,
        "email": false,
        "push": true
    }'::JSONB,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8.6 푸시 토큰 관리
CREATE TABLE t_push_token (
    token_id BIGSERIAL PRIMARY KEY,
    user_type VARCHAR(20) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    push_token VARCHAR(500) NOT NULL,
    device_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_push_token UNIQUE (push_token)
);

-- =====================================================
-- 9. Log Domain (로그 관리)
-- =====================================================

-- 9.1 이벤트 참여 로그
CREATE TABLE t_event_participation_log (
    participation_seq BIGSERIAL PRIMARY KEY,
    event_code VARCHAR(30) NOT NULL REFERENCES t_event(event_code),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    reward_type VARCHAR(50),
    reward_value INT,
    participation_data JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_event_user UNIQUE (event_code, user_id)
);

-- 9.2 배치 실행 로그
CREATE TABLE t_batch_execution_log (
    execution_seq BIGSERIAL PRIMARY KEY,
    batch_name VARCHAR(100) NOT NULL,
    batch_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    total_processed INT DEFAULT 0,
    success_count INT DEFAULT 0,
    fail_count INT DEFAULT 0,
    error_details JSONB,
    execution_params JSONB
);

-- 9.3 검색 로그 (파티션 키 포함 PRIMARY KEY)
CREATE TABLE t_search_log (
    search_seq BIGSERIAL,
    user_id VARCHAR(100),
    search_type VARCHAR(30) NOT NULL,
    keyword VARCHAR(200) NOT NULL,
    search_filters JSONB,
    result_count INT DEFAULT 0,
    selected_item_id VARCHAR(100),
    selected_position INT,
    search_duration_ms INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (search_seq, created_at)
) PARTITION BY RANGE (created_at);

-- 9.4 등급 변경 로그
CREATE TABLE t_grade_change_log (
    change_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    grade_before VARCHAR(20) NOT NULL,
    grade_after VARCHAR(20) NOT NULL,
    purchase_amount INT NOT NULL,
    calculation_period TSRANGE,
    change_reason VARCHAR(50) NOT NULL,
    admin_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 10. Additional Tables (추가 테이블)
-- =====================================================

-- 10.1 기획전 (레거시 보존)
CREATE TABLE t_exhibition (
    exhibition_code VARCHAR(30) PRIMARY KEY,
    exhibition_name VARCHAR(100) NOT NULL,
    description TEXT,
    banner_image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    legacy_idx INT
);

-- 10.2 더미 리뷰 (마케팅용)
CREATE TABLE t_review_dummy (
    dummy_seq BIGSERIAL PRIMARY KEY,
    user_nickname VARCHAR(100),
    counselor_nickname VARCHAR(100) REFERENCES t_counselor(nickname),
    chat_duration TIME,
    content TEXT,
    counselor_reply TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    legacy_idx INT
);

-- =====================================================
-- 11. Indexes and Triggers
-- =====================================================

-- User indexes
CREATE INDEX idx_user_email ON t_user(email);
CREATE INDEX idx_user_phone ON t_user(phone);
CREATE INDEX idx_user_nickname ON t_user(nickname);
CREATE INDEX idx_user_grade ON t_user(grade_code) WHERE user_status = 'ACTIVE';
CREATE INDEX idx_user_created_at ON t_user(created_at);

-- Counselor indexes
CREATE INDEX idx_counselor_code ON t_counselor(counselor_code);
CREATE INDEX idx_counselor_status ON t_counselor(counselor_status, online_status) 
    WHERE approval_status = 'APPROVED';
CREATE INDEX idx_counselor_rating ON t_counselor(rating_avg DESC, rating_count DESC)
    WHERE counselor_status = 'ACTIVE';
CREATE INDEX idx_counselor_specialties ON t_counselor USING GIN (specialties);
CREATE INDEX idx_counselor_keywords ON t_counselor USING GIN (keywords);

-- Other key indexes
CREATE INDEX idx_booking_user ON t_consultation_booking(user_id, status, booking_datetime);
CREATE INDEX idx_session_user ON t_consultation_session(user_id, status, created_at DESC);
CREATE INDEX idx_payment_user ON t_payment(user_id, payment_status, created_at DESC);

-- Update triggers
CREATE TRIGGER user_updated_at BEFORE UPDATE ON t_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER counselor_updated_at BEFORE UPDATE ON t_counselor
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 12. Initial System Configurations
-- =====================================================

INSERT INTO t_system_config (config_key, config_value, config_type, description) VALUES
('migration.completed_at', CURRENT_TIMESTAMP::TEXT, 'STRING', '마이그레이션 완료 시각'),
('migration.source_system', 'MariaDB', 'STRING', '마이그레이션 소스 시스템'),
('system.maintenance_mode', 'false', 'BOOLEAN', '시스템 점검 모드'),
('ai.default_model', 'gpt-4', 'STRING', 'AI 기본 모델'),
('chat.max_duration_minutes', '60', 'NUMBER', '채팅 최대 시간(분)'),
('point.expire_days', '365', 'NUMBER', '포인트 만료 일수'),
('notification.kakao.sender_key', 'YOUR_SENDER_KEY', 'STRING', '카카오 알림톡 발신 키'),
('notification.sms.sender_number', '1588-0000', 'STRING', 'SMS 발신번호'),
('notification.batch.size', '100', 'NUMBER', '알림 배치 처리 크기'),
('notification.retry.max_count', '3', 'NUMBER', '알림 최대 재시도 횟수'),
('notification.retry.delay_seconds', '300', 'NUMBER', '알림 재시도 대기 시간(초)')
ON CONFLICT (config_key) DO NOTHING;

-- =====================================================
-- 13. Create Initial Partitions for Current Month
-- =====================================================

-- 2025년 7월 파티션 생성
CREATE TABLE t_user_activity_log_2025_07 PARTITION OF t_user_activity_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE t_ai_usage_log_2025_07 PARTITION OF t_ai_usage_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE t_chat_message_2025_07 PARTITION OF t_chat_message
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE t_point_log_2025_07 PARTITION OF t_point_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE t_search_log_2025_07 PARTITION OF t_search_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE t_notification_log_2025_07 PARTITION OF t_notification_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');