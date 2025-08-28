-- KCP 본인인증 핵심 정보만 저장 (CI/DI 중심)

CREATE TABLE IF NOT EXISTS simplified_phone_verifications (
    id SERIAL PRIMARY KEY,
    
    -- 인증 기본 정보
    phone_no VARCHAR(11) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    birth_date VARCHAR(8) NOT NULL, -- YYYYMMDD
    
    -- KCP 핵심 데이터
    ci VARCHAR(200) NOT NULL UNIQUE,
    di VARCHAR(200) NOT NULL,
    
    -- KCP 인증 결과
    cert_no VARCHAR(100),
    res_cd VARCHAR(10) NOT NULL DEFAULT '0000',
    
    -- 추적 정보
    is_verified BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_sph_phone ON simplified_phone_verifications(phone_no);
CREATE INDEX idx_sph_ci ON simplified_phone_verifications(ci);
CREATE INDEX idx_sph_di ON simplified_phone_verifications(di);
CREATE INDEX idx_sph_created ON simplified_phone_verifications(created_at);

-- 권한 설정
GRANT SELECT, INSERT, UPDATE ON simplified_phone_verifications TO sajuline_user;

