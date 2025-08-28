# 사주라인 PostgreSQL 데이터베이스 실행 가이드

## 📋 개요
이 가이드는 새롭게 설계된 PostgreSQL 15+ 스키마를 Docker로 실행하는 방법을 안내합니다.

## 🏗️ 스키마 설계 특징
- **Natural Key 사용**: user_id, nickname 등 의미있는 키 활용
- **PostgreSQL 최적화**: JSONB, BOOLEAN, TIMESTAMPTZ, GENERATED COLUMN 사용
- **파티셔닝**: 대용량 로그 테이블에 월별 파티셔닝 적용
- **확장성**: GIN 인덱스, 전문 검색, 차트용 컬럼 제공

## 🚀 실행 방법

### 1. Docker Desktop 실행 확인
```powershell
# Docker 버전 확인
docker --version

# Docker 데몬 상태 확인
docker ps
```

### 2. 컨테이너 실행
```powershell
# 기존 컨테이너 정리 (필요시)
docker-compose down -v

# 새 컨테이너 시작
docker-compose up -d
```

### 3. 접속 정보
- **PostgreSQL**: localhost:5432
  - 데이터베이스: sajuline_db
  - 사용자: sajuline_user
  - 비밀번호: sajuline_password123!

- **pgAdmin**: http://localhost:8080
  - 이메일: admin@sajuline.com
  - 비밀번호: admin123!

## 📊 초기 데이터
다음 테스트 계정들이 자동으로 생성됩니다:

### 관리자 계정
- **시스템 관리자**: admin@sajuline.com / admin123!
- **CS 매니저**: cs@sajuline.com / admin123!

### 테스트 사용자
- **일반 사용자**: test@example.com / admin123!
- **테스트 상담사**: counselor@example.com / admin123!

## 🗂️ 스키마 구조

### Domain 별 테이블 구성
1. **User Domain** (3개 테이블)
   - t_user: 사용자 기본 정보
   - t_user_preference: 사용자 선호도
   - t_user_activity_log: 사용자 활동 로그 (파티션)

2. **Counselor Domain** (3개 테이블)
   - t_counselor: 상담사 정보
   - t_counselor_schedule: 상담사 근무 시간
   - t_counselor_pricing: 상담사 가격 정책

3. **AI Domain** (4개 테이블)
   - t_ai_fortune: AI 운세 분석
   - t_ai_consultation: AI 채팅 상담
   - t_ai_message: AI 채팅 메시지
   - t_ai_usage_log: AI 서비스 사용 로그 (파티션)

4. **Consultation Domain** (4개 테이블)
   - t_consultation_booking: 상담 예약
   - t_consultation_session: 상담 세션
   - t_chat_message: 채팅 메시지 (파티션)
   - t_consultation_queue: 상담 대기열

5. **Payment Domain** (4개 테이블)
   - t_point_product: 포인트 상품
   - t_payment: 결제 내역
   - t_point_log: 포인트 이력 (파티션)
   - t_mileage_log: 마일리지 이력

6. **Community Domain** (5개 테이블)
   - t_review: 상담 후기
   - t_review_like: 후기 좋아요
   - t_report: 신고
   - t_faq: FAQ
   - t_inquiry: 1:1 문의

7. **System Domain** (6개 테이블)
   - t_admin: 관리자
   - t_banner: 배너
   - t_notice: 공지사항
   - t_event: 이벤트
   - t_system_config: 시스템 설정
   - t_grade: 등급 정의

8. **Log Domain** (4개 테이블)
   - t_event_participation_log: 이벤트 참여 로그
   - t_batch_execution_log: 배치 실행 로그
   - t_search_log: 검색 로그 (파티션)
   - t_grade_change_log: 등급 변경 로그

## 🔧 유틸리티 함수
데이터베이스에는 다음 유틸리티 함수들이 포함되어 있습니다:

- `update_updated_at()`: 자동 업데이트 타임스탬프
- `reset_daily_sequences()`: 일일 시퀀스 리셋
- `create_monthly_partitions()`: 월별 파티션 자동 생성
- `drop_old_partitions()`: 오래된 파티션 정리

## 📈 성능 최적화
- **인덱스**: 검색 성능 최적화를 위한 복합 인덱스
- **파티셔닝**: 로그성 테이블의 월별 파티셔닝
- **JSONB**: 인덱싱 가능한 JSON 데이터 저장
- **Generated Column**: 차트용 연/월/일 컬럼 자동 생성

## 🔍 스키마 확인
```sql
-- 전체 테이블 목록 확인
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- 파티션 테이블 확인
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE tablename LIKE '%_log_%' 
ORDER BY tablename;

-- 인덱스 확인
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

## 🚨 문제 해결

### Docker 실행 오류
```powershell
# Docker Desktop 재시작
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 컨테이너 강제 재시작
docker-compose down -v --remove-orphans
docker-compose up -d --force-recreate
```

### 데이터베이스 접속 오류
1. 컨테이너 상태 확인: `docker-compose ps`
2. 로그 확인: `docker-compose logs postgres`
3. 포트 충돌 확인: `netstat -an | findstr :5432`

### 초기화 스크립트 오류
```powershell
# 볼륨 완전 삭제 후 재실행
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

## 📚 참고 문서
- [PostgreSQL 15 공식 문서](https://www.postgresql.org/docs/15/)
- [Docker Compose 가이드](https://docs.docker.com/compose/)
- [pgAdmin 사용법](https://www.pgadmin.org/docs/) 