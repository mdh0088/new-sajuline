-- 사주라인 리뉴얼 프로젝트 초기 데이터베이스 스키마
-- PostgreSQL 15+ 기준
-- 생성일: 2025-07-07
-- 마지막 업데이트: 2025-07-24 (자동 업데이트 - database-schema-management 규칙 적용)

-- 필수 확장 기능
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 업데이트 타임스탬프 자동 갱신
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 1. User Domain
-- =====================================================

CREATE TABLE t_user (
    user_id VARCHAR(100) PRIMARY KEY, -- 사용자 정의 ID (email 기반 등)
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    phone VARCHAR(15) NOT NULL UNIQUE,
    nickname VARCHAR(50) NOT NULL UNIQUE,
    join_type VARCHAR(20) NOT NULL DEFAULT 'EMAIL',
    user_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    is_premium BOOLEAN DEFAULT FALSE,
    point_balance INT NOT NULL DEFAULT 0,
    profile_image_url VARCHAR(500),
    birth_date DATE,
    gender CHAR(1),
    fcm_token VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON t_user(email);
CREATE INDEX idx_user_status ON t_user(user_status) WHERE user_status = 'ACTIVE';

CREATE TRIGGER user_updated_at BEFORE UPDATE ON t_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 2. Counselor Domain
-- =====================================================

CREATE TABLE t_counselor (
    counselor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    counselor_nickname VARCHAR(100) NOT NULL UNIQUE, -- 사용자에게 보이는 닉네임
    counselor_code VARCHAR(20) NOT NULL UNIQUE, -- CS_2025_0001 형식
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    profile_image_url VARCHAR(500),
    introduction TEXT,
    specialties TEXT[],
    price_per_minute INT NOT NULL DEFAULT 1000,
    counselor_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    is_online BOOLEAN DEFAULT FALSE,
    rating_avg NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    is_authorized BOOLEAN DEFAULT FALSE, -- 상담사 승인 여부
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_counselor_status ON t_counselor(counselor_status, is_online);
CREATE INDEX idx_counselor_nickname ON t_counselor(counselor_nickname);
CREATE INDEX idx_counselor_authorized ON t_counselor(is_authorized) WHERE is_authorized = TRUE;

CREATE TRIGGER counselor_updated_at BEFORE UPDATE ON t_counselor
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 3. Consultation Domain
-- =====================================================

CREATE TABLE t_consultation_session (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_id UUID NOT NULL REFERENCES t_counselor(counselor_id),
    consultation_type VARCHAR(20) NOT NULL DEFAULT 'CHAT',
    status VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_minutes INT DEFAULT 0,
    total_points_used INT DEFAULT 0,
    user_rating SMALLINT CHECK (user_rating >= 1 AND user_rating <= 5),
    user_review TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_user ON t_consultation_session(user_id, created_at DESC);
CREATE INDEX idx_session_counselor ON t_consultation_session(counselor_id, created_at DESC);

CREATE TRIGGER session_updated_at BEFORE UPDATE ON t_consultation_session
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 채팅 메시지
CREATE TABLE t_chat_message (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES t_consultation_session(session_id),
    sender_type VARCHAR(20) NOT NULL, -- USER, COUNSELOR, SYSTEM
    sender_id VARCHAR(100) NOT NULL, -- user_id 또는 counselor_id
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_session ON t_chat_message(session_id, created_at);

-- =====================================================
-- 4. Payment Domain (중복 방지 강화)
-- =====================================================

-- 포인트 상품
CREATE TABLE t_point_product (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name VARCHAR(100) NOT NULL,
    point_amount INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    bonus_point INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER point_product_updated_at BEFORE UPDATE ON t_point_product
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 결제 내역 (중복 방지 강화)
CREATE TABLE t_payment (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no VARCHAR(50) UNIQUE NOT NULL, -- YYYYMMDDHHmmssSSS + user_id 해시 일부
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    product_id UUID REFERENCES t_point_product(product_id),
    amount NUMERIC(10,2) NOT NULL,
    point_amount INT NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    pg_provider VARCHAR(20) NOT NULL,
    pg_tid VARCHAR(100),
    pg_approval_no VARCHAR(100),
    idempotency_key VARCHAR(100) NOT NULL, -- 멱등성 키 (중복 방지)
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    -- 중복 결제 방지
    CONSTRAINT uk_payment_idempotency UNIQUE (user_id, idempotency_key),
    CONSTRAINT uk_payment_pg UNIQUE (pg_provider, pg_tid)
);

CREATE INDEX idx_payment_user ON t_payment(user_id, created_at DESC);
CREATE INDEX idx_payment_order_no ON t_payment(order_no);

CREATE TRIGGER payment_updated_at BEFORE UPDATE ON t_payment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 주문번호 생성 함수 (충돌 방지)
CREATE OR REPLACE FUNCTION generate_order_no(p_user_id VARCHAR) 
RETURNS VARCHAR AS $$
DECLARE
    time_part VARCHAR;
    user_hash VARCHAR;
    final_order_no VARCHAR;
BEGIN
    -- 밀리초까지 포함
    time_part := TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS');
    -- user_id의 해시값 일부 (6자리)
    user_hash := SUBSTRING(MD5(p_user_id), 1, 6);
    final_order_no := time_part || '_' || user_hash;
    
    RETURN final_order_no;
END;
$$ LANGUAGE plpgsql;

-- 포인트 이력
CREATE TABLE t_point_log (
    point_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    transaction_type VARCHAR(20) NOT NULL, -- CHARGE, USE, REFUND
    point_amount INT NOT NULL,
    balance_after INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id UUID, -- payment_id 또는 session_id
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_point_log_user ON t_point_log(user_id, created_at DESC);

-- =====================================================
-- 5. Community Domain
-- =====================================================

CREATE TABLE t_review (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL UNIQUE REFERENCES t_consultation_session(session_id),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    counselor_id UUID NOT NULL REFERENCES t_counselor(counselor_id),
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_review_counselor ON t_review(counselor_id, created_at DESC)
    WHERE is_visible = TRUE;

CREATE TRIGGER review_updated_at BEFORE UPDATE ON t_review
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 6. System Domain
-- =====================================================

CREATE TABLE t_admin (
    admin_id VARCHAR(100) PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'CS',
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE t_system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE t_notice (
    notice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_important BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    admin_id VARCHAR(100) NOT NULL REFERENCES t_admin(admin_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE t_faq (
    faq_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(30) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. 초기 데이터 삽입
-- =====================================================

-- 시스템 관리자 계정
INSERT INTO t_admin (admin_id, email, password_hash, name, role) VALUES
('admin', 'admin@sajuline.com', '$2b$12$8xJKhcO0lGJ.u5zGwRXfce5TJQ5XBx37LIgI6eMxBHDJvUm2kzgQu', '시스템관리자', 'SUPER');

-- 시스템 설정
INSERT INTO t_system_config (config_key, config_value, description) VALUES
('maintenance_mode', 'false', '유지보수 모드'),
('point_exchange_rate', '100', '1포인트당 원화 환율'),
('free_ai_daily_limit', '3', '일일 무료 AI 운세 횟수'),
('consultation_commission_rate', '0.3', '상담 수수료율 (30%)'),
('min_withdrawal_amount', '10000', '최소 출금 금액');

-- 포인트 상품
INSERT INTO t_point_product (product_name, point_amount, price, bonus_point, display_order) VALUES
('1,000 포인트', 1000, 1100.00, 0, 1),
('5,000 포인트', 5000, 5300.00, 200, 2),
('10,000 포인트', 10000, 10500.00, 500, 3),
('30,000 포인트', 30000, 31000.00, 2000, 4),
('50,000 포인트', 50000, 50000.00, 5000, 5),
('100,000 포인트', 100000, 95000.00, 15000, 6);

-- FAQ 초기 데이터
INSERT INTO t_faq (category, question, answer, display_order) VALUES
('이용안내', '사주라인은 어떤 서비스인가요?', '사주라인은 AI 기술과 전문 상담사를 통해 사주, 운세 상담을 제공하는 온라인 플랫폼입니다.', 1),
('포인트', '포인트는 어떻게 충전하나요?', '마이페이지에서 포인트 충전 메뉴를 통해 신용카드, 계좌이체 등으로 충전할 수 있습니다.', 2),
('상담', '상담사는 어떻게 선택하나요?', '상담사 목록에서 전문 분야, 평점, 후기 등을 확인하고 선택할 수 있습니다.', 3),
('환불', '포인트 환불이 가능한가요?', '미사용 포인트에 한해 구매일로부터 7일 이내 환불이 가능합니다.', 4);

-- 코멘트 추가
COMMENT ON TABLE t_user IS '사용자 정보';
COMMENT ON TABLE t_counselor IS '상담사 정보';
COMMENT ON TABLE t_consultation_session IS '상담 세션';
COMMENT ON TABLE t_chat_message IS '채팅 메시지';
COMMENT ON TABLE t_payment IS '결제 내역';
COMMENT ON TABLE t_point_product IS '포인트 상품';
COMMENT ON TABLE t_point_log IS '포인트 이력';
COMMENT ON TABLE t_review IS '상담 후기';
COMMENT ON TABLE t_admin IS '관리자';
COMMENT ON TABLE t_system_config IS '시스템 설정';
COMMENT ON TABLE t_notice IS '공지사항';
COMMENT ON TABLE t_faq IS '자주 묻는 질문'; 