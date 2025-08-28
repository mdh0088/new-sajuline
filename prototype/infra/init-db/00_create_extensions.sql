-- PostgreSQL 확장 기능 설치
-- Docker 컨테이너 초기화 시 자동 실행

-- UUID 생성 기능
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 암호화 기능
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 통계 및 모니터링 기능 (옵션)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- JSON 쿼리 최적화 (옵션)
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 텍스트 검색 향상 (옵션)
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; 