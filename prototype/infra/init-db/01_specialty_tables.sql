-- 전문분야 마스터 테이블 (UUID 기반)
CREATE TABLE IF NOT EXISTS t_specialty (
    specialty_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialty_code VARCHAR(20) NOT NULL UNIQUE,
    specialty_name VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 상담사-전문분야 매핑 테이블
CREATE TABLE IF NOT EXISTS t_counselor_specialty (
    counselor_id UUID NOT NULL REFERENCES t_counselor(counselor_id) ON DELETE CASCADE,
    specialty_id UUID NOT NULL REFERENCES t_specialty(specialty_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (counselor_id, specialty_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_specialty_code ON t_specialty(specialty_code);
CREATE INDEX IF NOT EXISTS idx_specialty_active ON t_specialty(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_counselor_specialty_counselor ON t_counselor_specialty(counselor_id);
CREATE INDEX IF NOT EXISTS idx_counselor_specialty_specialty ON t_counselor_specialty(specialty_id);

-- 업데이트 트리거
CREATE TRIGGER specialty_updated_at BEFORE UPDATE ON t_specialty
    FOR EACH ROW EXECUTE FUNCTION update_updated_at(); 