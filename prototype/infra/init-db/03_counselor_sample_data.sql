-- 상담사 샘플 데이터 (counselor_status INT 버전)
-- 비밀번호: password123 (bcrypt 해시)

INSERT INTO t_counselor (
    counselor_id,
    counselor_nickname,
    counselor_code,
    email,
    password_hash,
    name,
    phone,
    introduction,
    price_per_minute,
    counselor_status,
    is_online,
    is_authorized,
    rating_avg,
    rating_count
) VALUES 
-- 승인된 활성 상담사 (대기중)
(
    gen_random_uuid(),
    '별빛상담사',
    '001',
    'counselor001@sajuline.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LdQgUlpLN7.IVY9.y',
    '김상담',
    '01012345001',
    '15년 경력의 전문 사주 상담사입니다.',
    1500,
    1,  -- 대기중
    true,
    true,
    4.8,
    127
),
(
    gen_random_uuid(),
    '달님타로',
    '002',
    'counselor002@sajuline.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LdQgUlpLN7.IVY9.y',
    '이연화',
    '01012345002',
    '타로와 사주를 전문으로 하는 상담사입니다.',
    2000,
    3,  -- 부재중
    false,
    true,
    4.9,
    89
),
(
    gen_random_uuid(),
    '운세박사',
    '003',
    'counselor003@sajuline.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LdQgUlpLN7.IVY9.y',
    '박운세',
    '01012345003',
    '20년 경력의 사주명리학 전문가입니다.',
    2500,
    2,  -- 상담중
    true,
    true,
    4.7,
    203
),
-- 승인 대기 중인 상담사
(
    gen_random_uuid(),
    '신규상담사',
    '004',
    'counselor004@sajuline.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LdQgUlpLN7.IVY9.y',
    '최신규',
    '01012345004',
    '새롭게 시작하는 상담사입니다.',
    1200,
    1,  -- 대기중
    false,
    false,
    0.0,
    0
);

-- 상담사별 전문분야 매핑
INSERT INTO t_counselor_specialty (counselor_id, specialty_id)
SELECT c.counselor_id, s.specialty_id
FROM t_counselor c, t_specialty s
WHERE c.counselor_code = '001' AND s.specialty_code IN ('SAJU', 'TAROT', 'LOVE')

UNION ALL

SELECT c.counselor_id, s.specialty_id
FROM t_counselor c, t_specialty s
WHERE c.counselor_code = '002' AND s.specialty_code IN ('TAROT', 'SAJU', 'CAREER')

UNION ALL

SELECT c.counselor_id, s.specialty_id
FROM t_counselor c, t_specialty s
WHERE c.counselor_code = '003' AND s.specialty_code IN ('SAJU', 'NAME', 'BUSINESS')

UNION ALL

SELECT c.counselor_id, s.specialty_id
FROM t_counselor c, t_specialty s
WHERE c.counselor_code = '004' AND s.specialty_code IN ('TAROT', 'LOVE'); 