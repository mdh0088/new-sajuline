-- =====================================================
-- 사주라인 PostgreSQL 최종 스키마
-- Version: Final Simplified v1.0
-- Date: 2025-01-03
-- 
-- 특징:
-- 1. 구조 단순화 (파티셔닝, AI 도메인, 예약시스템 제거)
-- 2. UUID v7 자동 생성
-- 3. 컬럼별 코멘트 포함
-- 4. 기존 MariaDB 데이터 완벽 호환
-- =====================================================

-- 필수 확장 기능
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- UUID v7 생성 함수 (타임스탬프 기반)
-- =====================================================
CREATE OR REPLACE FUNCTION generate_uuid_v7()
RETURNS UUID AS $$
DECLARE
    timestamp_ms BIGINT;
    random_bytes BYTEA;
    uuid_bytes BYTEA;
BEGIN
    timestamp_ms := EXTRACT(EPOCH FROM clock_timestamp()) * 1000;
    uuid_bytes := int8send(timestamp_ms >> 16)::bytea;
    uuid_bytes := substring(uuid_bytes FROM 3);
    random_bytes := gen_random_bytes(10);
    uuid_bytes := uuid_bytes || random_bytes;
    uuid_bytes := set_byte(uuid_bytes, 6, (get_byte(uuid_bytes, 6) & 15) | 112);
    uuid_bytes := set_byte(uuid_bytes, 8, (get_byte(uuid_bytes, 8) & 63) | 128);
    RETURN encode(uuid_bytes, 'hex')::UUID;
END;
$$ LANGUAGE plpgsql;

-- 업데이트 타임스탬프 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

COMMENT ON TABLE t_user IS '사용자 기본 정보';
COMMENT ON COLUMN t_user.user_id IS '사용자 ID';
COMMENT ON COLUMN t_user.email IS '이메일';
COMMENT ON COLUMN t_user.password_hash IS '비밀번호 해시';
COMMENT ON COLUMN t_user.phone IS '전화번호';
COMMENT ON COLUMN t_user.nickname IS '닉네임';
COMMENT ON COLUMN t_user.join_type IS '가입 유형 (EMAIL, KAKAO, NAVER, GOOGLE)';
COMMENT ON COLUMN t_user.user_status IS '사용자 상태 (ACTIVE:활성, DORMANT:휴면, WITHDRAWN:탈퇴)';
COMMENT ON COLUMN t_user.grade_code IS '등급 코드';
COMMENT ON COLUMN t_user.point_balance IS '포인트 잔액';
COMMENT ON COLUMN t_user.mileage_balance IS '마일리지 잔액';
COMMENT ON COLUMN t_user.profile_image_url IS '프로필 이미지 URL';
COMMENT ON COLUMN t_user.birth_datetime IS '생년월일시';
COMMENT ON COLUMN t_user.is_lunar_birth IS '음력 여부';
COMMENT ON COLUMN t_user.gender IS '성별 (M:남성, F:여성, OTHER:기타)';
COMMENT ON COLUMN t_user.fcm_token IS 'FCM 토큰';
COMMENT ON COLUMN t_user.is_marketing_agreed IS '마케팅 동의 여부';
COMMENT ON COLUMN t_user.terms_agreed_at IS '이용약관 동의 일시';
COMMENT ON COLUMN t_user.privacy_agreed_at IS '개인정보처리방침 동의 일시';
COMMENT ON COLUMN t_user.created_at IS '가입일시';
COMMENT ON COLUMN t_user.updated_at IS '수정일시';
COMMENT ON COLUMN t_user.last_login_at IS '마지막 로그인 일시';
COMMENT ON COLUMN t_user.withdrawn_at IS '탈퇴일시';

CREATE INDEX idx_user_email ON t_user(email);
CREATE INDEX idx_user_phone ON t_user(phone);
CREATE INDEX idx_user_status ON t_user(user_status) WHERE user_status = 'ACTIVE';

CREATE TRIGGER user_updated_at BEFORE UPDATE ON t_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

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

COMMENT ON TABLE t_user_preference IS '사용자 선호도';
COMMENT ON COLUMN t_user_preference.user_id IS '사용자 ID';
COMMENT ON COLUMN t_user_preference.prefer_categories IS '선호 카테고리 (JSON 배열)';
COMMENT ON COLUMN t_user_preference.prefer_counselor_styles IS '선호 상담사 스타일 (JSON 배열)';
COMMENT ON COLUMN t_user_preference.prefer_time_slots IS '선호 시간대 (JSON 배열)';
COMMENT ON COLUMN t_user_preference.ai_usage_level IS 'AI 사용 수준 (BEGINNER:초급, INTERMEDIATE:중급, ADVANCED:고급)';
COMMENT ON COLUMN t_user_preference.notification_settings IS '알림 설정 (JSON 객체)';
COMMENT ON COLUMN t_user_preference.updated_at IS '수정일시';

CREATE TRIGGER user_preference_updated_at BEFORE UPDATE ON t_user_preference
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 1.3 사용자 활동 로그
CREATE TABLE t_user_activity_log (
    activity_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    activity_detail JSONB,
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_user_activity_log IS '사용자 활동 로그';
COMMENT ON COLUMN t_user_activity_log.activity_seq IS '활동 순번';
COMMENT ON COLUMN t_user_activity_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_user_activity_log.activity_type IS '활동 유형 (LOGIN, LOGOUT, VIEW, SEARCH, PURCHASE, CONSULTATION, NOTIFICATION, WITHDRAWAL)';
COMMENT ON COLUMN t_user_activity_log.activity_detail IS '활동 상세 정보 (JSON)';
COMMENT ON COLUMN t_user_activity_log.ip_address IS 'IP 주소';
COMMENT ON COLUMN t_user_activity_log.user_agent IS '유저 에이전트';
COMMENT ON COLUMN t_user_activity_log.device_type IS '디바이스 유형 (PC, MOBILE, TABLET, APP)';
COMMENT ON COLUMN t_user_activity_log.created_at IS '생성일시';

CREATE INDEX idx_user_activity_user ON t_user_activity_log(user_id, created_at DESC);

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

COMMENT ON TABLE t_counselor IS '상담사 정보';
COMMENT ON COLUMN t_counselor.nickname IS '상담사 닉네임 (PK)';
COMMENT ON COLUMN t_counselor.counselor_code IS '상담사 코드 (CS_2024_0001 형식)';
COMMENT ON COLUMN t_counselor.email IS '이메일';
COMMENT ON COLUMN t_counselor.password_hash IS '비밀번호 해시';
COMMENT ON COLUMN t_counselor.name IS '실명';
COMMENT ON COLUMN t_counselor.phone IS '전화번호';
COMMENT ON COLUMN t_counselor.profile_image_url IS '프로필 이미지 URL';
COMMENT ON COLUMN t_counselor.introduction_short IS '짧은 소개';
COMMENT ON COLUMN t_counselor.introduction_long IS '상세 소개';
COMMENT ON COLUMN t_counselor.greeting_message IS '인사말';
COMMENT ON COLUMN t_counselor.specialties IS '전문 분야 (JSON 배열)';
COMMENT ON COLUMN t_counselor.keywords IS '키워드 (JSON 배열)';
COMMENT ON COLUMN t_counselor.consultation_styles IS '상담 스타일 (JSON 배열)';
COMMENT ON COLUMN t_counselor.experience_years IS '경력 년수';
COMMENT ON COLUMN t_counselor.career_detail IS '경력 상세';
COMMENT ON COLUMN t_counselor.certificates IS '자격증 (JSON 배열)';
COMMENT ON COLUMN t_counselor.counselor_status IS '상담사 상태 (ACTIVE:활동중, REST:휴식, REVIEWING:심사중, SUSPENDED:정지)';
COMMENT ON COLUMN t_counselor.online_status IS '온라인 상태 (ONLINE:온라인, OFFLINE:오프라인, BUSY:상담중)';
COMMENT ON COLUMN t_counselor.grade IS '상담사 등급 (BRONZE, SILVER, GOLD, PLATINUM)';
COMMENT ON COLUMN t_counselor.rating_avg IS '평균 평점';
COMMENT ON COLUMN t_counselor.rating_count IS '평점 개수';
COMMENT ON COLUMN t_counselor.consultation_count IS '상담 횟수';
COMMENT ON COLUMN t_counselor.approval_status IS '승인 상태 (PENDING:대기, APPROVED:승인, REJECTED:거절)';
COMMENT ON COLUMN t_counselor.approved_at IS '승인일시';
COMMENT ON COLUMN t_counselor.applied_at IS '신청일시';
COMMENT ON COLUMN t_counselor.created_at IS '등록일시';
COMMENT ON COLUMN t_counselor.updated_at IS '수정일시';
COMMENT ON COLUMN t_counselor.last_login_at IS '마지막 로그인 일시';

CREATE INDEX idx_counselor_status ON t_counselor(counselor_status, online_status) 
    WHERE approval_status = 'APPROVED';

CREATE TRIGGER counselor_updated_at BEFORE UPDATE ON t_counselor
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

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

COMMENT ON TABLE t_counselor_schedule IS '상담사 근무 시간';
COMMENT ON COLUMN t_counselor_schedule.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_counselor_schedule.day_of_week IS '요일 (1:월 ~ 7:일)';
COMMENT ON COLUMN t_counselor_schedule.time_slot_start IS '시작 시간';
COMMENT ON COLUMN t_counselor_schedule.time_slot_end IS '종료 시간';
COMMENT ON COLUMN t_counselor_schedule.is_active IS '활성화 여부';
COMMENT ON COLUMN t_counselor_schedule.created_at IS '등록일시';
COMMENT ON COLUMN t_counselor_schedule.updated_at IS '수정일시';

-- 2.3 상담사 가격 정책
CREATE TABLE t_counselor_pricing (
    counselor_nickname VARCHAR(100) PRIMARY KEY REFERENCES t_counselor(nickname) ON DELETE CASCADE,
    chat_price_per_min INT NOT NULL DEFAULT 1000,
    after_price_per_min INT NOT NULL DEFAULT 1000,
    before_price_per_min INT NOT NULL DEFAULT 1000,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_counselor_pricing IS '상담사 가격 정책';
COMMENT ON COLUMN t_counselor_pricing.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_counselor_pricing.chat_price_per_min IS '채팅 상담 분당 가격';
COMMENT ON COLUMN t_counselor_pricing.after_price_per_min IS '후불 상담 분당 가격';
COMMENT ON COLUMN t_counselor_pricing.before_price_per_min IS '선불 상담 분당 가격';
COMMENT ON COLUMN t_counselor_pricing.updated_at IS '수정일시';

-- =====================================================
-- 3. Consultation Domain (상담 서비스)
-- =====================================================

-- 3.1 상담 세션
CREATE TABLE t_consultation_session (
    session_seq BIGSERIAL PRIMARY KEY,
    session_code VARCHAR(36) UNIQUE DEFAULT generate_uuid_v7()::text,
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_consultation_session IS '상담 세션';
COMMENT ON COLUMN t_consultation_session.session_seq IS '세션 순번';
COMMENT ON COLUMN t_consultation_session.session_code IS '세션 코드 (UUID v7)';
COMMENT ON COLUMN t_consultation_session.user_id IS '사용자 ID';
COMMENT ON COLUMN t_consultation_session.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_consultation_session.consultation_type IS '상담 유형 (CHAT:채팅, VOICE:음성, VIDEO:화상)';
COMMENT ON COLUMN t_consultation_session.status IS '상태 (WAITING:대기, IN_PROGRESS:진행중, COMPLETED:완료, CANCELLED:취소)';
COMMENT ON COLUMN t_consultation_session.started_at IS '시작일시';
COMMENT ON COLUMN t_consultation_session.ended_at IS '종료일시';
COMMENT ON COLUMN t_consultation_session.duration_seconds IS '상담 시간(초)';
COMMENT ON COLUMN t_consultation_session.total_point_used IS '사용 포인트';
COMMENT ON COLUMN t_consultation_session.user_rating IS '사용자 평점 (1~5)';
COMMENT ON COLUMN t_consultation_session.user_review IS '사용자 후기';
COMMENT ON COLUMN t_consultation_session.counselor_memo IS '상담사 메모';
COMMENT ON COLUMN t_consultation_session.session_summary IS '세션 요약 (JSON)';
COMMENT ON COLUMN t_consultation_session.created_at IS '생성일시';
COMMENT ON COLUMN t_consultation_session.updated_at IS '수정일시';

CREATE INDEX idx_session_user ON t_consultation_session(user_id, created_at DESC);
CREATE INDEX idx_session_counselor ON t_consultation_session(counselor_nickname, created_at DESC);

CREATE TRIGGER session_updated_at BEFORE UPDATE ON t_consultation_session
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 3.2 채팅 메시지
CREATE TABLE t_chat_message (
    message_seq BIGSERIAL PRIMARY KEY,
    session_seq BIGINT NOT NULL REFERENCES t_consultation_session(session_seq),
    sender_type VARCHAR(20) NOT NULL,
    sender_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'TEXT',
    content TEXT,
    file_info JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_chat_message IS '채팅 메시지';
COMMENT ON COLUMN t_chat_message.message_seq IS '메시지 순번';
COMMENT ON COLUMN t_chat_message.session_seq IS '세션 순번';
COMMENT ON COLUMN t_chat_message.sender_type IS '발신자 유형 (USER:사용자, COUNSELOR:상담사, SYSTEM:시스템)';
COMMENT ON COLUMN t_chat_message.sender_id IS '발신자 ID';
COMMENT ON COLUMN t_chat_message.message_type IS '메시지 유형 (TEXT:텍스트, IMAGE:이미지, FILE:파일, VOICE:음성, EMOJI:이모지)';
COMMENT ON COLUMN t_chat_message.content IS '메시지 내용';
COMMENT ON COLUMN t_chat_message.file_info IS '파일 정보 (JSON)';
COMMENT ON COLUMN t_chat_message.is_read IS '읽음 여부';
COMMENT ON COLUMN t_chat_message.read_at IS '읽은 시간';
COMMENT ON COLUMN t_chat_message.created_at IS '전송일시';

CREATE INDEX idx_chat_session ON t_chat_message(session_seq, created_at);

-- =====================================================
-- 4. Payment Domain (결제/포인트)
-- =====================================================

-- 4.1 포인트 상품
CREATE TABLE t_point_product (
    product_code VARCHAR(36) PRIMARY KEY DEFAULT generate_uuid_v7()::text,
    product_name VARCHAR(100) NOT NULL,
    point_amount INT NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    bonus_point INT DEFAULT 0,
    discount_rate NUMERIC(5,2) DEFAULT 0,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    start_dt TIMESTAMPTZ,
    end_dt TIMESTAMPTZ,
    product_tags JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_point_product IS '포인트 상품 정보';
COMMENT ON COLUMN t_point_product.product_code IS '상품 코드 (UUID v7)';
COMMENT ON COLUMN t_point_product.product_name IS '상품명';
COMMENT ON COLUMN t_point_product.point_amount IS '포인트 금액';
COMMENT ON COLUMN t_point_product.price IS '판매 가격';
COMMENT ON COLUMN t_point_product.bonus_point IS '보너스 포인트';
COMMENT ON COLUMN t_point_product.discount_rate IS '할인율';
COMMENT ON COLUMN t_point_product.display_order IS '노출 순서';
COMMENT ON COLUMN t_point_product.is_active IS '활성화 여부';
COMMENT ON COLUMN t_point_product.start_dt IS '판매 시작일시';
COMMENT ON COLUMN t_point_product.end_dt IS '판매 종료일시';
COMMENT ON COLUMN t_point_product.product_tags IS '상품 태그 (JSON 배열)';
COMMENT ON COLUMN t_point_product.created_at IS '등록일시';
COMMENT ON COLUMN t_point_product.updated_at IS '수정일시';

CREATE TRIGGER point_product_updated_at BEFORE UPDATE ON t_point_product
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 4.2 결제 내역
CREATE TABLE t_payment (
    payment_seq BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(36) UNIQUE DEFAULT generate_uuid_v7()::text,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    payment_type VARCHAR(30) NOT NULL,
    product_code VARCHAR(36) REFERENCES t_point_product(product_code),
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_payment IS '결제 내역';
COMMENT ON COLUMN t_payment.payment_seq IS '결제 순번';
COMMENT ON COLUMN t_payment.order_no IS '주문 번호 (UUID v7)';
COMMENT ON COLUMN t_payment.user_id IS '사용자 ID';
COMMENT ON COLUMN t_payment.payment_type IS '결제 유형 (POINT_CHARGE:포인트충전, MILEAGE_CHARGE:마일리지충전, MEMBERSHIP:멤버십)';
COMMENT ON COLUMN t_payment.product_code IS '상품 코드';
COMMENT ON COLUMN t_payment.amount IS '결제 금액';
COMMENT ON COLUMN t_payment.point_amount IS '충전 포인트';
COMMENT ON COLUMN t_payment.mileage_used IS '사용 마일리지';
COMMENT ON COLUMN t_payment.payment_method IS '결제 수단 (CARD:카드, BANK_TRANSFER:계좌이체, KAKAO_PAY:카카오페이, NAVER_PAY:네이버페이, TOSS:토스)';
COMMENT ON COLUMN t_payment.payment_status IS '결제 상태 (PENDING:대기, SUCCESS:성공, FAILED:실패, CANCELLED:취소, REFUNDED:환불)';
COMMENT ON COLUMN t_payment.pg_provider IS 'PG사';
COMMENT ON COLUMN t_payment.pg_tid IS 'PG 거래번호';
COMMENT ON COLUMN t_payment.pg_response IS 'PG 응답 (JSON)';
COMMENT ON COLUMN t_payment.paid_at IS '결제일시';
COMMENT ON COLUMN t_payment.cancelled_at IS '취소일시';
COMMENT ON COLUMN t_payment.cancel_reason IS '취소 사유';
COMMENT ON COLUMN t_payment.refund_amount IS '환불 금액';
COMMENT ON COLUMN t_payment.refunded_at IS '환불일시';
COMMENT ON COLUMN t_payment.metadata IS '메타데이터 (JSON)';
COMMENT ON COLUMN t_payment.created_at IS '생성일시';
COMMENT ON COLUMN t_payment.updated_at IS '수정일시';

CREATE INDEX idx_payment_user ON t_payment(user_id, created_at DESC);

CREATE TRIGGER payment_updated_at BEFORE UPDATE ON t_payment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 4.3 포인트 이력
CREATE TABLE t_point_log (
    point_log_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    transaction_type VARCHAR(30) NOT NULL,
    point_amount INT NOT NULL,
    balance_after INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(100),
    description TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_point_log IS '포인트 이력';
COMMENT ON COLUMN t_point_log.point_log_seq IS '로그 순번';
COMMENT ON COLUMN t_point_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_point_log.transaction_type IS '거래 유형 (CHARGE:충전, USE:사용, REFUND:환불, EXPIRE:만료, BONUS:보너스, EVENT:이벤트)';
COMMENT ON COLUMN t_point_log.point_amount IS '포인트 금액';
COMMENT ON COLUMN t_point_log.balance_after IS '거래 후 잔액';
COMMENT ON COLUMN t_point_log.reference_type IS '참조 유형';
COMMENT ON COLUMN t_point_log.reference_id IS '참조 ID';
COMMENT ON COLUMN t_point_log.description IS '설명';
COMMENT ON COLUMN t_point_log.expires_at IS '만료일시';
COMMENT ON COLUMN t_point_log.created_at IS '생성일시';

CREATE INDEX idx_point_log_user ON t_point_log(user_id, created_at DESC);

-- 4.4 마일리지 이력
CREATE TABLE t_mileage_log (
    mileage_log_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    transaction_type VARCHAR(20) NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    mileage_amount INT NOT NULL,
    balance_after INT NOT NULL,
    earn_rate NUMERIC(5,2),
    reference_type VARCHAR(50),
    reference_id VARCHAR(100),
    description TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_mileage_log IS '마일리지 이력';
COMMENT ON COLUMN t_mileage_log.mileage_log_seq IS '로그 순번';
COMMENT ON COLUMN t_mileage_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_mileage_log.transaction_type IS '거래 유형 (EARN:적립, USE:사용, EXPIRE:만료)';
COMMENT ON COLUMN t_mileage_log.source_type IS '소스 유형 (PURCHASE:구매, EVENT:이벤트, GRADE:등급, MANUAL:수동)';
COMMENT ON COLUMN t_mileage_log.mileage_amount IS '마일리지 금액';
COMMENT ON COLUMN t_mileage_log.balance_after IS '거래 후 잔액';
COMMENT ON COLUMN t_mileage_log.earn_rate IS '적립률';
COMMENT ON COLUMN t_mileage_log.reference_type IS '참조 유형';
COMMENT ON COLUMN t_mileage_log.reference_id IS '참조 ID';
COMMENT ON COLUMN t_mileage_log.description IS '설명';
COMMENT ON COLUMN t_mileage_log.expires_at IS '만료일시';
COMMENT ON COLUMN t_mileage_log.created_at IS '생성일시';

CREATE INDEX idx_mileage_log_user ON t_mileage_log(user_id, created_at DESC);

-- =====================================================
-- 5. Community Domain (커뮤니티)
-- =====================================================

-- 5.1 상담 후기
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

COMMENT ON TABLE t_review IS '상담 후기';
COMMENT ON COLUMN t_review.review_seq IS '후기 순번';
COMMENT ON COLUMN t_review.session_seq IS '세션 순번';
COMMENT ON COLUMN t_review.user_id IS '사용자 ID';
COMMENT ON COLUMN t_review.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_review.rating IS '평점 (1~5)';
COMMENT ON COLUMN t_review.content IS '후기 내용';
COMMENT ON COLUMN t_review.counselor_reply IS '상담사 답변';
COMMENT ON COLUMN t_review.is_best IS '베스트 후기 여부';
COMMENT ON COLUMN t_review.is_visible IS '노출 여부';
COMMENT ON COLUMN t_review.like_count IS '좋아요 수';
COMMENT ON COLUMN t_review.tags IS '태그 (JSON 배열)';
COMMENT ON COLUMN t_review.created_at IS '작성일시';
COMMENT ON COLUMN t_review.updated_at IS '수정일시';
COMMENT ON COLUMN t_review.counselor_replied_at IS '상담사 답변일시';

CREATE INDEX idx_review_counselor ON t_review(counselor_nickname, created_at DESC)
    WHERE is_visible = TRUE;

CREATE TRIGGER review_updated_at BEFORE UPDATE ON t_review
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 5.2 후기 좋아요
CREATE TABLE t_review_like (
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    review_seq BIGINT NOT NULL REFERENCES t_review(review_seq) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, review_seq)
);

COMMENT ON TABLE t_review_like IS '후기 좋아요';
COMMENT ON COLUMN t_review_like.user_id IS '사용자 ID';
COMMENT ON COLUMN t_review_like.review_seq IS '후기 순번';
COMMENT ON COLUMN t_review_like.created_at IS '좋아요 일시';

-- 5.3 신고
CREATE TABLE t_report (
    report_seq BIGSERIAL PRIMARY KEY,
    report_no VARCHAR(36) UNIQUE DEFAULT generate_uuid_v7()::text,
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

COMMENT ON TABLE t_report IS '신고';
COMMENT ON COLUMN t_report.report_seq IS '신고 순번';
COMMENT ON COLUMN t_report.report_no IS '신고 번호 (UUID v7)';
COMMENT ON COLUMN t_report.reporter_id IS '신고자 ID';
COMMENT ON COLUMN t_report.report_type IS '신고 유형 (REVIEW:후기, COUNSELOR:상담사, USER:사용자, CHAT:채팅)';
COMMENT ON COLUMN t_report.target_id IS '신고 대상 ID';
COMMENT ON COLUMN t_report.reason_type IS '신고 사유 (SPAM:스팸, PRIVACY:개인정보, ILLEGAL:불법, ABUSE:욕설, FRAUD:사기, OTHER:기타)';
COMMENT ON COLUMN t_report.reason_detail IS '신고 상세 내용';
COMMENT ON COLUMN t_report.evidence_urls IS '증거 URL (JSON 배열)';
COMMENT ON COLUMN t_report.status IS '처리 상태 (PENDING:대기, PROCESSING:처리중, COMPLETED:완료, REJECTED:반려)';
COMMENT ON COLUMN t_report.admin_id IS '처리 관리자 ID';
COMMENT ON COLUMN t_report.admin_note IS '관리자 메모';
COMMENT ON COLUMN t_report.processed_at IS '처리일시';
COMMENT ON COLUMN t_report.created_at IS '신고일시';

-- 5.4 FAQ
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

COMMENT ON TABLE t_faq IS 'FAQ';
COMMENT ON COLUMN t_faq.faq_seq IS 'FAQ 순번';
COMMENT ON COLUMN t_faq.category IS '카테고리 (GENERAL:일반, PAYMENT:결제, CONSULTATION:상담, COUNSELOR:상담사, TECHNICAL:기술)';
COMMENT ON COLUMN t_faq.question IS '질문';
COMMENT ON COLUMN t_faq.answer IS '답변';
COMMENT ON COLUMN t_faq.keywords IS '키워드 (JSON 배열)';
COMMENT ON COLUMN t_faq.display_order IS '노출 순서';
COMMENT ON COLUMN t_faq.is_active IS '활성화 여부';
COMMENT ON COLUMN t_faq.view_count IS '조회수';
COMMENT ON COLUMN t_faq.is_pinned IS '고정 여부';
COMMENT ON COLUMN t_faq.created_at IS '등록일시';
COMMENT ON COLUMN t_faq.updated_at IS '수정일시';

CREATE TRIGGER faq_updated_at BEFORE UPDATE ON t_faq
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 5.5 1:1 문의
CREATE TABLE t_inquiry (
    inquiry_seq BIGSERIAL PRIMARY KEY,
    inquiry_no VARCHAR(36) UNIQUE DEFAULT generate_uuid_v7()::text,
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

COMMENT ON TABLE t_inquiry IS '1:1 문의';
COMMENT ON COLUMN t_inquiry.inquiry_seq IS '문의 순번';
COMMENT ON COLUMN t_inquiry.inquiry_no IS '문의 번호 (UUID v7)';
COMMENT ON COLUMN t_inquiry.user_id IS '사용자 ID';
COMMENT ON COLUMN t_inquiry.category IS '카테고리 (PAYMENT:결제, CONSULTATION:상담, ACCOUNT:계정, BUG:버그, COUNSELOR:상담사, GENERAL:일반, OTHER:기타)';
COMMENT ON COLUMN t_inquiry.title IS '제목';
COMMENT ON COLUMN t_inquiry.content IS '내용';
COMMENT ON COLUMN t_inquiry.attachments IS '첨부파일 (JSON 배열)';
COMMENT ON COLUMN t_inquiry.status IS '상태 (PENDING:대기, IN_PROGRESS:처리중, ANSWERED:답변완료, CLOSED:종료)';
COMMENT ON COLUMN t_inquiry.admin_id IS '담당 관리자 ID';
COMMENT ON COLUMN t_inquiry.admin_reply IS '관리자 답변';
COMMENT ON COLUMN t_inquiry.answered_at IS '답변일시';
COMMENT ON COLUMN t_inquiry.closed_at IS '종료일시';
COMMENT ON COLUMN t_inquiry.created_at IS '문의일시';
COMMENT ON COLUMN t_inquiry.updated_at IS '수정일시';

CREATE INDEX idx_inquiry_user ON t_inquiry(user_id, created_at DESC);

CREATE TRIGGER inquiry_updated_at BEFORE UPDATE ON t_inquiry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 6. System Domain (시스템 관리)
-- =====================================================

-- 6.1 관리자
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

COMMENT ON TABLE t_admin IS '관리자 정보';
COMMENT ON COLUMN t_admin.admin_id IS '관리자 ID';
COMMENT ON COLUMN t_admin.email IS '이메일';
COMMENT ON COLUMN t_admin.password_hash IS '비밀번호 해시';
COMMENT ON COLUMN t_admin.name IS '이름';
COMMENT ON COLUMN t_admin.role IS '권한 (SUPER:최고관리자, MANAGER:매니저, CS:고객응대, VIEWER:조회전용)';
COMMENT ON COLUMN t_admin.department IS '부서';
COMMENT ON COLUMN t_admin.is_active IS '활성화 여부';
COMMENT ON COLUMN t_admin.permissions IS '권한 정보 (JSON)';
COMMENT ON COLUMN t_admin.last_login_at IS '마지막 로그인 일시';
COMMENT ON COLUMN t_admin.last_login_ip IS '마지막 로그인 IP';
COMMENT ON COLUMN t_admin.created_at IS '등록일시';
COMMENT ON COLUMN t_admin.updated_at IS '수정일시';

CREATE TRIGGER admin_updated_at BEFORE UPDATE ON t_admin
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 6.2 배너
CREATE TABLE t_banner (
    banner_code VARCHAR(36) PRIMARY KEY DEFAULT generate_uuid_v7()::text,
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

COMMENT ON TABLE t_banner IS '배너';
COMMENT ON COLUMN t_banner.banner_code IS '배너 코드 (UUID v7)';
COMMENT ON COLUMN t_banner.banner_name IS '배너명';
COMMENT ON COLUMN t_banner.banner_type IS '배너 유형 (MAIN:메인, SUB:서브, EVENT:이벤트, POPUP:팝업)';
COMMENT ON COLUMN t_banner.image_url IS '이미지 URL';
COMMENT ON COLUMN t_banner.mobile_image_url IS '모바일 이미지 URL';
COMMENT ON COLUMN t_banner.link_url IS '링크 URL';
COMMENT ON COLUMN t_banner.link_target IS '링크 타겟 (SELF:현재창, BLANK:새창)';
COMMENT ON COLUMN t_banner.display_order IS '노출 순서';
COMMENT ON COLUMN t_banner.is_active IS '활성화 여부';
COMMENT ON COLUMN t_banner.valid_from IS '시작일시';
COMMENT ON COLUMN t_banner.valid_until IS '종료일시';
COMMENT ON COLUMN t_banner.click_count IS '클릭수';
COMMENT ON COLUMN t_banner.impression_count IS '노출수';
COMMENT ON COLUMN t_banner.created_at IS '등록일시';
COMMENT ON COLUMN t_banner.updated_at IS '수정일시';

CREATE TRIGGER banner_updated_at BEFORE UPDATE ON t_banner
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 6.3 공지사항
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

COMMENT ON TABLE t_notice IS '공지사항';
COMMENT ON COLUMN t_notice.notice_seq IS '공지 순번';
COMMENT ON COLUMN t_notice.category IS '카테고리 (GENERAL:일반, SERVICE:서비스, EVENT:이벤트, MAINTENANCE:점검)';
COMMENT ON COLUMN t_notice.title IS '제목';
COMMENT ON COLUMN t_notice.content IS '내용';
COMMENT ON COLUMN t_notice.is_important IS '중요 공지 여부';
COMMENT ON COLUMN t_notice.is_popup IS '팝업 노출 여부';
COMMENT ON COLUMN t_notice.is_active IS '활성화 여부';
COMMENT ON COLUMN t_notice.view_count IS '조회수';
COMMENT ON COLUMN t_notice.admin_id IS '작성자 ID';
COMMENT ON COLUMN t_notice.attachments IS '첨부파일 (JSON 배열)';
COMMENT ON COLUMN t_notice.created_at IS '등록일시';
COMMENT ON COLUMN t_notice.updated_at IS '수정일시';

CREATE TRIGGER notice_updated_at BEFORE UPDATE ON t_notice
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 6.4 이벤트
CREATE TABLE t_event (
    event_code VARCHAR(36) PRIMARY KEY DEFAULT generate_uuid_v7()::text,
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

COMMENT ON TABLE t_event IS '이벤트';
COMMENT ON COLUMN t_event.event_code IS '이벤트 코드 (UUID v7)';
COMMENT ON COLUMN t_event.event_name IS '이벤트명';
COMMENT ON COLUMN t_event.event_type IS '이벤트 유형 (POINT:포인트, DISCOUNT:할인, COUPON:쿠폰, SPECIAL:특별)';
COMMENT ON COLUMN t_event.description IS '이벤트 설명';
COMMENT ON COLUMN t_event.terms IS '이벤트 약관';
COMMENT ON COLUMN t_event.banner_image_url IS '배너 이미지 URL';
COMMENT ON COLUMN t_event.reward_type IS '보상 유형 (POINT:포인트, MILEAGE:마일리지, DISCOUNT_RATE:할인율, DISCOUNT_AMOUNT:할인금액)';
COMMENT ON COLUMN t_event.reward_value IS '보상 값';
COMMENT ON COLUMN t_event.max_participants IS '최대 참여자 수';
COMMENT ON COLUMN t_event.current_participants IS '현재 참여자 수';
COMMENT ON COLUMN t_event.is_active IS '활성화 여부';
COMMENT ON COLUMN t_event.valid_from IS '시작일시';
COMMENT ON COLUMN t_event.valid_until IS '종료일시';
COMMENT ON COLUMN t_event.metadata IS '메타데이터 (JSON)';
COMMENT ON COLUMN t_event.created_at IS '등록일시';
COMMENT ON COLUMN t_event.updated_at IS '수정일시';

CREATE TRIGGER event_updated_at BEFORE UPDATE ON t_event
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 6.5 시스템 설정
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

COMMENT ON TABLE t_system_config IS '시스템 설정';
COMMENT ON COLUMN t_system_config.config_key IS '설정 키';
COMMENT ON COLUMN t_system_config.config_value IS '설정 값';
COMMENT ON COLUMN t_system_config.config_type IS '설정 타입 (STRING:문자열, NUMBER:숫자, BOOLEAN:불린, JSON:JSON)';
COMMENT ON COLUMN t_system_config.description IS '설명';
COMMENT ON COLUMN t_system_config.is_active IS '활성화 여부';
COMMENT ON COLUMN t_system_config.is_public IS '공개 여부';
COMMENT ON COLUMN t_system_config.updated_at IS '수정일시';
COMMENT ON COLUMN t_system_config.updated_by IS '수정자';

-- 6.6 등급 정의
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

COMMENT ON TABLE t_grade IS '등급 정의';
COMMENT ON COLUMN t_grade.grade_code IS '등급 코드';
COMMENT ON COLUMN t_grade.grade_name IS '등급명';
COMMENT ON COLUMN t_grade.grade_level IS '등급 레벨';
COMMENT ON COLUMN t_grade.min_purchase_amount IS '최소 구매 금액';
COMMENT ON COLUMN t_grade.point_earn_rate IS '포인트 적립률';
COMMENT ON COLUMN t_grade.discount_rate IS '할인율';
COMMENT ON COLUMN t_grade.benefits IS '혜택 정보 (JSON)';
COMMENT ON COLUMN t_grade.grade_image_url IS '등급 이미지 URL';
COMMENT ON COLUMN t_grade.grade_color IS '등급 색상';
COMMENT ON COLUMN t_grade.description IS '등급 설명';
COMMENT ON COLUMN t_grade.is_active IS '활성화 여부';
COMMENT ON COLUMN t_grade.created_at IS '등록일시';
COMMENT ON COLUMN t_grade.updated_at IS '수정일시';

CREATE TRIGGER grade_updated_at BEFORE UPDATE ON t_grade
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- 7. Notification Domain (알림)
-- =====================================================

-- 7.1 알림 템플릿
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

COMMENT ON TABLE t_notification_template IS '알림 템플릿';
COMMENT ON COLUMN t_notification_template.template_code IS '템플릿 코드';
COMMENT ON COLUMN t_notification_template.template_name IS '템플릿명';
COMMENT ON COLUMN t_notification_template.template_type IS '템플릿 유형 (CONSULTATION:상담, PAYMENT:결제, EVENT:이벤트, SYSTEM:시스템)';
COMMENT ON COLUMN t_notification_template.channel IS '채널 (KAKAO:카카오톡, SMS:문자, PUSH:푸시, EMAIL:이메일)';
COMMENT ON COLUMN t_notification_template.content_template IS '내용 템플릿';
COMMENT ON COLUMN t_notification_template.variables IS '변수 목록 (JSON 배열)';
COMMENT ON COLUMN t_notification_template.button_info IS '버튼 정보 (JSON)';
COMMENT ON COLUMN t_notification_template.is_active IS '활성화 여부';
COMMENT ON COLUMN t_notification_template.created_at IS '등록일시';
COMMENT ON COLUMN t_notification_template.updated_at IS '수정일시';

-- 7.2 알림 발송 이력
CREATE TABLE t_notification_log (
    notification_seq BIGSERIAL PRIMARY KEY,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    template_code VARCHAR(50),
    title VARCHAR(200),
    content TEXT NOT NULL,
    variables JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    provider_response JSONB,
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    failed_reason TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_notification_log IS '알림 발송 이력';
COMMENT ON COLUMN t_notification_log.notification_seq IS '알림 순번';
COMMENT ON COLUMN t_notification_log.recipient_type IS '수신자 유형 (USER:사용자, COUNSELOR:상담사, ADMIN:관리자)';
COMMENT ON COLUMN t_notification_log.recipient_id IS '수신자 ID';
COMMENT ON COLUMN t_notification_log.channel IS '채널 (KAKAO:카카오톡, SMS:문자, PUSH:푸시, EMAIL:이메일)';
COMMENT ON COLUMN t_notification_log.template_code IS '템플릿 코드';
COMMENT ON COLUMN t_notification_log.title IS '제목';
COMMENT ON COLUMN t_notification_log.content IS '내용';
COMMENT ON COLUMN t_notification_log.variables IS '변수 값 (JSON)';
COMMENT ON COLUMN t_notification_log.status IS '상태 (PENDING:대기, SENT:발송, READ:읽음, FAILED:실패)';
COMMENT ON COLUMN t_notification_log.provider_response IS '제공자 응답 (JSON)';
COMMENT ON COLUMN t_notification_log.sent_at IS '발송일시';
COMMENT ON COLUMN t_notification_log.read_at IS '읽은일시';
COMMENT ON COLUMN t_notification_log.failed_reason IS '실패 사유';
COMMENT ON COLUMN t_notification_log.retry_count IS '재시도 횟수';
COMMENT ON COLUMN t_notification_log.created_at IS '생성일시';

CREATE INDEX idx_notification_log_recipient ON t_notification_log(recipient_id, created_at DESC);

-- 7.3 사용자 알림 설정
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

COMMENT ON TABLE t_user_notification_setting IS '사용자 알림 설정';
COMMENT ON COLUMN t_user_notification_setting.user_id IS '사용자 ID';
COMMENT ON COLUMN t_user_notification_setting.kakao_enabled IS '카카오톡 알림 허용';
COMMENT ON COLUMN t_user_notification_setting.sms_enabled IS 'SMS 알림 허용';
COMMENT ON COLUMN t_user_notification_setting.email_enabled IS '이메일 알림 허용';
COMMENT ON COLUMN t_user_notification_setting.push_enabled IS '푸시 알림 허용';
COMMENT ON COLUMN t_user_notification_setting.night_time_enabled IS '야간 알림 허용';
COMMENT ON COLUMN t_user_notification_setting.notification_types IS '알림 유형별 설정 (JSON)';
COMMENT ON COLUMN t_user_notification_setting.quiet_time_start IS '방해금지 시작 시간';
COMMENT ON COLUMN t_user_notification_setting.quiet_time_end IS '방해금지 종료 시간';
COMMENT ON COLUMN t_user_notification_setting.updated_at IS '수정일시';

-- 7.4 상담사 알림 설정
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

COMMENT ON TABLE t_counselor_notification_setting IS '상담사 알림 설정';
COMMENT ON COLUMN t_counselor_notification_setting.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_counselor_notification_setting.consultation_request IS '상담 요청 알림';
COMMENT ON COLUMN t_counselor_notification_setting.queue_notification IS '대기열 알림';
COMMENT ON COLUMN t_counselor_notification_setting.review_notification IS '후기 알림';
COMMENT ON COLUMN t_counselor_notification_setting.daily_summary IS '일일 요약 알림';
COMMENT ON COLUMN t_counselor_notification_setting.channels IS '채널별 설정 (JSON)';
COMMENT ON COLUMN t_counselor_notification_setting.updated_at IS '수정일시';

-- =====================================================
-- 8. Log Domain (로그 관리)
-- =====================================================

-- 8.1 이벤트 참여 로그
CREATE TABLE t_event_participation_log (
    participation_seq BIGSERIAL PRIMARY KEY,
    event_code VARCHAR(36) NOT NULL REFERENCES t_event(event_code),
    user_id VARCHAR(100) NOT NULL REFERENCES t_user(user_id),
    reward_type VARCHAR(50),
    reward_value INT,
    participation_data JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_event_user UNIQUE (event_code, user_id)
);

COMMENT ON TABLE t_event_participation_log IS '이벤트 참여 로그';
COMMENT ON COLUMN t_event_participation_log.participation_seq IS '참여 순번';
COMMENT ON COLUMN t_event_participation_log.event_code IS '이벤트 코드';
COMMENT ON COLUMN t_event_participation_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_event_participation_log.reward_type IS '보상 유형';
COMMENT ON COLUMN t_event_participation_log.reward_value IS '보상 값';
COMMENT ON COLUMN t_event_participation_log.participation_data IS '참여 데이터 (JSON)';
COMMENT ON COLUMN t_event_participation_log.created_at IS '참여일시';

-- 8.2 배치 실행 로그
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

COMMENT ON TABLE t_batch_execution_log IS '배치 실행 로그';
COMMENT ON COLUMN t_batch_execution_log.execution_seq IS '실행 순번';
COMMENT ON COLUMN t_batch_execution_log.batch_name IS '배치명';
COMMENT ON COLUMN t_batch_execution_log.batch_type IS '배치 유형 (GRADE:등급, MILEAGE:마일리지, POINT_EXPIRE:포인트만료, STATISTICS:통계)';
COMMENT ON COLUMN t_batch_execution_log.status IS '상태 (RUNNING:실행중, SUCCESS:성공, FAILED:실패)';
COMMENT ON COLUMN t_batch_execution_log.started_at IS '시작일시';
COMMENT ON COLUMN t_batch_execution_log.ended_at IS '종료일시';
COMMENT ON COLUMN t_batch_execution_log.total_processed IS '전체 처리 건수';
COMMENT ON COLUMN t_batch_execution_log.success_count IS '성공 건수';
COMMENT ON COLUMN t_batch_execution_log.fail_count IS '실패 건수';
COMMENT ON COLUMN t_batch_execution_log.error_details IS '에러 상세 (JSON)';
COMMENT ON COLUMN t_batch_execution_log.execution_params IS '실행 파라미터 (JSON)';

-- 8.3 검색 로그
CREATE TABLE t_search_log (
    search_seq BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    search_type VARCHAR(30) NOT NULL,
    keyword VARCHAR(200) NOT NULL,
    search_filters JSONB,
    result_count INT DEFAULT 0,
    selected_item_id VARCHAR(100),
    selected_position INT,
    search_duration_ms INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_search_log IS '검색 로그';
COMMENT ON COLUMN t_search_log.search_seq IS '검색 순번';
COMMENT ON COLUMN t_search_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_search_log.search_type IS '검색 유형 (COUNSELOR:상담사, FAQ:FAQ, GENERAL:일반)';
COMMENT ON COLUMN t_search_log.keyword IS '검색어';
COMMENT ON COLUMN t_search_log.search_filters IS '검색 필터 (JSON)';
COMMENT ON COLUMN t_search_log.result_count IS '검색 결과 수';
COMMENT ON COLUMN t_search_log.selected_item_id IS '선택한 항목 ID';
COMMENT ON COLUMN t_search_log.selected_position IS '선택한 항목 위치';
COMMENT ON COLUMN t_search_log.search_duration_ms IS '검색 소요 시간(ms)';
COMMENT ON COLUMN t_search_log.created_at IS '검색일시';

-- 8.4 등급 변경 로그
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

COMMENT ON TABLE t_grade_change_log IS '등급 변경 로그';
COMMENT ON COLUMN t_grade_change_log.change_seq IS '변경 순번';
COMMENT ON COLUMN t_grade_change_log.user_id IS '사용자 ID';
COMMENT ON COLUMN t_grade_change_log.grade_before IS '변경 전 등급';
COMMENT ON COLUMN t_grade_change_log.grade_after IS '변경 후 등급';
COMMENT ON COLUMN t_grade_change_log.purchase_amount IS '구매 금액';
COMMENT ON COLUMN t_grade_change_log.calculation_period IS '계산 기간';
COMMENT ON COLUMN t_grade_change_log.change_reason IS '변경 사유 (MONTHLY_BATCH:월정산, MANUAL:수동, PROMOTION:프로모션)';
COMMENT ON COLUMN t_grade_change_log.admin_id IS '처리 관리자 ID';
COMMENT ON COLUMN t_grade_change_log.created_at IS '변경일시';

-- =====================================================
-- 9. Additional Tables (추가 테이블)
-- =====================================================

-- 9.1 기획전 (레거시 보존)
CREATE TABLE t_exhibition (
    exhibition_code VARCHAR(36) PRIMARY KEY DEFAULT generate_uuid_v7()::text,
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

COMMENT ON TABLE t_exhibition IS '기획전 (레거시 데이터 보존)';
COMMENT ON COLUMN t_exhibition.exhibition_code IS '기획전 코드 (UUID v7)';
COMMENT ON COLUMN t_exhibition.exhibition_name IS '기획전명';
COMMENT ON COLUMN t_exhibition.description IS '설명';
COMMENT ON COLUMN t_exhibition.banner_image_url IS '배너 이미지 URL';
COMMENT ON COLUMN t_exhibition.is_active IS '활성화 여부';
COMMENT ON COLUMN t_exhibition.valid_from IS '시작일시';
COMMENT ON COLUMN t_exhibition.valid_until IS '종료일시';
COMMENT ON COLUMN t_exhibition.created_at IS '등록일시';
COMMENT ON COLUMN t_exhibition.updated_at IS '수정일시';
COMMENT ON COLUMN t_exhibition.legacy_idx IS '레거시 IDX';

CREATE TRIGGER exhibition_updated_at BEFORE UPDATE ON t_exhibition
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 9.2 더미 리뷰 (마케팅용)
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

COMMENT ON TABLE t_review_dummy IS '더미 리뷰 (마케팅용)';
COMMENT ON COLUMN t_review_dummy.dummy_seq IS '더미 순번';
COMMENT ON COLUMN t_review_dummy.user_nickname IS '사용자 닉네임';
COMMENT ON COLUMN t_review_dummy.counselor_nickname IS '상담사 닉네임';
COMMENT ON COLUMN t_review_dummy.chat_duration IS '채팅 시간';
COMMENT ON COLUMN t_review_dummy.content IS '리뷰 내용';
COMMENT ON COLUMN t_review_dummy.counselor_reply IS '상담사 답변';
COMMENT ON COLUMN t_review_dummy.created_at IS '생성일시';
COMMENT ON COLUMN t_review_dummy.legacy_idx IS '레거시 IDX';

-- =====================================================
-- 10. 설정 관련 테이블
-- =====================================================

-- 10.1 카카오 알림 템플릿
CREATE TABLE t_kakao_alarm_template (
    template_idx SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    pc_link VARCHAR(255),
    mo_link VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_kakao_alarm_template IS '카카오 알림 템플릿';
COMMENT ON COLUMN t_kakao_alarm_template.template_idx IS '템플릿 순번';
COMMENT ON COLUMN t_kakao_alarm_template.code IS '템플릿 코드';
COMMENT ON COLUMN t_kakao_alarm_template.name IS '템플릿명';
COMMENT ON COLUMN t_kakao_alarm_template.content IS '템플릿 내용';
COMMENT ON COLUMN t_kakao_alarm_template.pc_link IS 'PC 링크';
COMMENT ON COLUMN t_kakao_alarm_template.mo_link IS '모바일 링크';
COMMENT ON COLUMN t_kakao_alarm_template.is_active IS '활성화 여부';
COMMENT ON COLUMN t_kakao_alarm_template.created_at IS '등록일시';
COMMENT ON COLUMN t_kakao_alarm_template.updated_at IS '수정일시';

-- 10.2 등급 배치 설정
CREATE TABLE t_grade_batch_config (
    config_idx SERIAL PRIMARY KEY,
    period_month INT NOT NULL DEFAULT 1,
    period_day INT NOT NULL DEFAULT 1,
    is_use BOOLEAN DEFAULT TRUE,
    update_user VARCHAR(100),
    update_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_grade_batch_config IS '등급 배치 관리 설정';
COMMENT ON COLUMN t_grade_batch_config.config_idx IS '설정 순번';
COMMENT ON COLUMN t_grade_batch_config.period_month IS '등급 조정 주기(월)';
COMMENT ON COLUMN t_grade_batch_config.period_day IS '수행일(일)';
COMMENT ON COLUMN t_grade_batch_config.is_use IS '활성화 여부';
COMMENT ON COLUMN t_grade_batch_config.update_user IS '수정자';
COMMENT ON COLUMN t_grade_batch_config.update_date IS '수정일시';
COMMENT ON COLUMN t_grade_batch_config.created_at IS '생성일시';
COMMENT ON COLUMN t_grade_batch_config.updated_at IS '수정일시';

-- 10.3 멤버십 배치 설정
CREATE TABLE t_membership_batch_config (
    config_idx SERIAL PRIMARY KEY,
    period_month INT NOT NULL DEFAULT 1,
    period_day INT NOT NULL DEFAULT 1,
    is_use BOOLEAN DEFAULT TRUE,
    update_user VARCHAR(100),
    update_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_membership_batch_config IS '멤버십 배치 관리 설정';
COMMENT ON COLUMN t_membership_batch_config.config_idx IS '설정 순번';
COMMENT ON COLUMN t_membership_batch_config.period_month IS '등급 조정 주기(월)';
COMMENT ON COLUMN t_membership_batch_config.period_day IS '수행일(일)';
COMMENT ON COLUMN t_membership_batch_config.is_use IS '활성화 여부';
COMMENT ON COLUMN t_membership_batch_config.update_user IS '수정자';
COMMENT ON COLUMN t_membership_batch_config.update_date IS '수정일시';
COMMENT ON COLUMN t_membership_batch_config.created_at IS '생성일시';
COMMENT ON COLUMN t_membership_batch_config.updated_at IS '수정일시';

-- 10.4 마일리지 설정
CREATE TABLE t_mileage_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(50) UNIQUE NOT NULL,
    config_value VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    regist_user VARCHAR(100),
    regist_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    update_user VARCHAR(100),
    update_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_mileage_config IS '마일리지 설정';
COMMENT ON COLUMN t_mileage_config.config_id IS '설정 ID';
COMMENT ON COLUMN t_mileage_config.config_key IS '설정 키';
COMMENT ON COLUMN t_mileage_config.config_value IS '설정 값';
COMMENT ON COLUMN t_mileage_config.description IS '설명';
COMMENT ON COLUMN t_mileage_config.regist_user IS '등록자';
COMMENT ON COLUMN t_mileage_config.regist_date IS '등록일시';
COMMENT ON COLUMN t_mileage_config.update_user IS '수정자';
COMMENT ON COLUMN t_mileage_config.update_date IS '수정일시';
COMMENT ON COLUMN t_mileage_config.created_at IS '생성일시';
COMMENT ON COLUMN t_mileage_config.updated_at IS '수정일시';

-- =====================================================
-- 11. 기본 데이터 입력
-- =====================================================

-- 기본 등급 데이터
INSERT INTO t_grade (grade_code, grade_name, grade_level, min_purchase_amount, point_earn_rate, discount_rate) VALUES
('WHITE', '화이트', 1, 0, 0, 0),
('SILVER', '실버', 2, 100000, 1, 0),
('GOLD', '골드', 3, 300000, 2, 0),
('VIP', 'VIP', 4, 500000, 3, 0),
('VVIP', 'VVIP', 5, 1000000, 5, 0);

-- 기본 시스템 설정
INSERT INTO t_system_config (config_key, config_value, config_type, description) VALUES
('system.maintenance_mode', 'false', 'BOOLEAN', '시스템 점검 모드'),
('chat.max_duration_minutes', '60', 'NUMBER', '채팅 최대 시간(분)'),
('point.expire_days', '365', 'NUMBER', '포인트 만료 일수'),
('notification.kakao.sender_key', 'YOUR_SENDER_KEY', 'STRING', '카카오 알림톡 발신 키'),
('notification.sms.sender_number', '1588-0000', 'STRING', 'SMS 발신번호')
ON CONFLICT (config_key) DO NOTHING;