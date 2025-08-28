-- 핸드폰 인증 테이블 생성 SQL (독립적으로 실행)
CREATE TABLE IF NOT EXISTS phone_verifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '일련번호',
    session_id VARCHAR(128) UNIQUE NOT NULL COMMENT '세션 ID (KCP)',
    user_id VARCHAR(50) NULL COMMENT '사용자 ID (선택)',
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'EXPIRED') NOT NULL DEFAULT 'PENDING' COMMENT '인증 상태',
    
    -- 사용자 입력 정보
    user_name VARCHAR(50) NOT NULL COMMENT '사용자 이름',
    birth_date VARCHAR(8) NOT NULL COMMENT '생년월일 (YYYYMMDD)',
    phone_number VARCHAR(20) NOT NULL COMMENT '휴대폰 번호',
    carrier ENUM('SKT', 'KTF', 'LGT', 'MVNO') NOT NULL COMMENT '통신사',
    gender CHAR(1) NOT NULL COMMENT '성별 (M/F)',
    local_code VARCHAR(10) NULL COMMENT '지역코드',
    verification_method ENUM('sms', 'pass', 'card') NOT NULL DEFAULT 'sms' COMMENT '인증 방법',
    
    -- KCP 처리 정보
    cert_no VARCHAR(128) NULL COMMENT '인증번호',
    enc_cert_data TEXT NULL COMMENT '암호화된 인증 데이터',
    up_hash VARCHAR(256) NULL COMMENT '요청 해시값',
    dn_hash VARCHAR(256) NULL COMMENT '응답 해시값',
    comm_id VARCHAR(128) NULL COMMENT '통신 ID',
    
    -- 인증 완료 정보
    phone_no VARCHAR(20) NULL COMMENT '인증된 휴대폰 번호',
    verified_name VARCHAR(50) NULL COMMENT '인증된 이름',
    verified_birth VARCHAR(8) NULL COMMENT '인증된 생년월일',
    sex_code CHAR(1) NULL COMMENT '인증된 성별',
    ci VARCHAR(256) NULL COMMENT 'CI (Connecting Information)',
    di VARCHAR(256) NULL COMMENT 'DI (Duplication Information)',
    
    -- 결과 정보
    res_cd VARCHAR(10) NULL COMMENT '결과 코드',
    res_msg TEXT NULL COMMENT '결과 메시지',
    
    -- Additional Data (JSON)
    meta_data JSON NULL COMMENT '추가 메타데이터',
    
    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
    verified_at TIMESTAMP NULL COMMENT '인증 완료일시',
    expires_at TIMESTAMP NULL COMMENT '만료일시',
    
    -- 인덱스
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_phone_number (phone_number),
    INDEX idx_status_created (status, created_at),
    INDEX idx_verified_at (verified_at),
    INDEX idx_expires_at (expires_at),
    INDEX idx_ci (ci),
    INDEX idx_di (di)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='핸드폰 인증 정보';