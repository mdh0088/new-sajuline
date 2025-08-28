-- 상담사 테이블에 is_authorized 컬럼 추가
-- 생성일: 2025-07-24
-- 목적: 상담사 승인 상태 관리

-- is_authorized 컬럼 추가
ALTER TABLE t_counselor 
ADD COLUMN is_authorized BOOLEAN DEFAULT FALSE;

-- 기존 데이터에 대한 기본값 설정
-- counselor_status가 'ACTIVE'인 경우 승인된 것으로 간주
UPDATE t_counselor 
SET is_authorized = TRUE 
WHERE counselor_status = 'ACTIVE';

-- 인덱스 추가 (승인된 상담사 조회 성능 향상)
CREATE INDEX idx_counselor_authorized ON t_counselor(is_authorized) WHERE is_authorized = TRUE;

-- 코멘트 추가
COMMENT ON COLUMN t_counselor.is_authorized IS '상담사 승인 여부 (TRUE: 승인됨, FALSE: 승인 대기)';