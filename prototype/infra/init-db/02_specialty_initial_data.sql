-- 전문분야 초기 데이터 (UUID 기반)
INSERT INTO t_specialty (specialty_id, specialty_code, specialty_name, description, display_order) VALUES
(gen_random_uuid(), 'SAJU', '사주', '사주명리학 기반 운세 상담', 1),
(gen_random_uuid(), 'TAROT', '타로', '타로카드를 이용한 심리 상담', 2),
(gen_random_uuid(), 'PALM', '손금', '손금 해석을 통한 운세 상담', 3),
(gen_random_uuid(), 'FACE', '관상', '관상학 기반 성격 및 운세 분석', 4),
(gen_random_uuid(), 'DREAM', '해몽', '꿈 해석 및 의미 분석', 5),
(gen_random_uuid(), 'NAME', '작명/개명', '이름의 의미와 작명 컨설팅', 6),
(gen_random_uuid(), 'COMPAT', '궁합', '연인/부부 궁합 분석', 7),
(gen_random_uuid(), 'BUSINESS', '사업운', '사업 관련 운세 및 방향 상담', 8),
(gen_random_uuid(), 'LOVE', '연애운', '연애 및 결혼 운세 상담', 9),
(gen_random_uuid(), 'CAREER', '진로/직업', '직업 선택 및 진로 방향 상담', 10); 