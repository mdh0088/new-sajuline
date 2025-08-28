# 사주라인 데이터베이스 로그인 정보

> 📅 **생성일**: 2025-07-01  
> 🔧 **스키마 버전**: new-main-database-schema.md 기반  
> 🐳 **환경**: Docker PostgreSQL 15 + pgAdmin

---

## 🗄️ 데이터베이스 접속 정보

### PostgreSQL 연결 정보
```
Host: localhost
Port: 5432
Database: sajuline_db
Username: sajuline_user
Password: sajuline_password123!
```

### 연결 URL (개발용)
```
postgresql://sajuline_user:sajuline_password123!@localhost:5432/sajuline_db
```

---

## 🌐 pgAdmin 웹 인터페이스

### 접속 정보
- **URL**: http://localhost:8080
- **로그인 이메일**: admin@sajuline.com
- **비밀번호**: admin123!

### pgAdmin에서 서버 추가 방법
1. pgAdmin 접속 후 "Add New Server" 클릭
2. **General 탭**:
   - Name: `Sajuline Local`
3. **Connection 탭**:
   - Host name/address: `sajuline-postgres`
   - Port: `5432`
   - Maintenance database: `sajuline_db`
   - Username: `sajuline_user`
   - Password: `sajuline_password123!`

---

## 👥 테스트 계정 정보

### 🔧 관리자 계정

#### 시스템 관리자
- **ID**: admin
- **이메일**: admin@sajuline.com
- **비밀번호**: admin123!
- **권한**: SUPER (최고관리자)
- **부서**: IT

#### CS 매니저
- **ID**: cs_manager
- **이메일**: cs@sajuline.com
- **비밀번호**: admin123!
- **권한**: MANAGER (매니저)
- **부서**: 고객서비스

### 👤 일반 사용자 계정

#### 테스트 사용자
- **사용자 ID**: testuser001
- **이메일**: test@example.com
- **비밀번호**: admin123!
- **닉네임**: 테스트사용자
- **전화번호**: 01012345678
- **가입유형**: EMAIL
- **등급**: WHITE (기본)

### 👩‍🏫 상담사 계정

#### 테스트 상담사
- **닉네임**: 운세마스터
- **상담사 코드**: CS_2025_0001
- **이메일**: counselor@example.com
- **비밀번호**: admin123!
- **이름**: 김운세
- **전화번호**: 01087654321
- **경력**: 20년
- **전문분야**: ["사주", "운세", "궁합"]
- **승인상태**: APPROVED (승인완료)

#### 상담 요금 정보
- **채팅 상담**: 200원/분
- **음성 상담**: 400원/분
- **화상 상담**: 600원/분

#### 근무 시간
- **평일** (월-금): 09:00 - 18:00
- **주말**: 휴무

---

## 🚀 Docker 컨테이너 관리

### 기본 명령어
```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 데이터까지 완전 삭제 후 중지
docker-compose down -v

# 컨테이너 상태 확인
docker-compose ps

# PostgreSQL 로그 확인
docker-compose logs postgres

# pgAdmin 로그 확인
docker-compose logs pgadmin

# 실시간 로그 모니터링
docker-compose logs -f postgres
```

### 데이터베이스 재초기화
```bash
# 모든 데이터 삭제 후 재시작
docker-compose down -v
docker-compose up -d
```

---

## 📊 데이터베이스 스키마 정보

### 생성된 도메인별 테이블 수
- **User Domain**: 3개 테이블
- **Counselor Domain**: 3개 테이블  
- **AI Domain**: 4개 테이블
- **Consultation Domain**: 4개 테이블
- **Payment Domain**: 4개 테이블
- **Community Domain**: 5개 테이블
- **System Domain**: 6개 테이블
- **Log Domain**: 4개 테이블

### 주요 특징
- ✅ Natural Key 활용 (user_id, nickname 등)
- ✅ JSONB 타입으로 유연한 데이터 저장
- ✅ 파티셔닝 적용 (로그 테이블)
- ✅ GIN 인덱스로 전문 검색 지원
- ✅ 트리거로 자동 updated_at 관리
- ✅ 시퀀스로 비즈니스 코드 자동 생성

---

## 🛠️ 개발 시 유용한 정보

### 샘플 데이터 확인
```sql
-- 생성된 테이블 목록
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 't_%'
ORDER BY table_name;

-- 테스트 사용자 정보
SELECT * FROM t_user WHERE user_id = 'testuser001';

-- 테스트 상담사 정보
SELECT * FROM t_counselor WHERE nickname = '운세마스터';

-- 시스템 설정 확인
SELECT * FROM t_system_config ORDER BY config_key;

-- 등급 정보 확인
SELECT * FROM t_grade ORDER BY grade_level;
```

### 포인트 상품 정보
| 상품명 | 포인트 | 가격 | 보너스 |
|--------|--------|------|--------|
| 1,000 포인트 | 1,000P | 1,000원 | 0P |
| 5,000 포인트 | 5,000P | 5,000원 | 250P |
| 10,000 포인트 | 10,000P | 10,000원 | 700P |
| 20,000 포인트 | 20,000P | 20,000원 | 1,500P |
| 50,000 포인트 | 50,000P | 50,000원 | 5,000P |
| 100,000 포인트 | 100,000P | 100,000원 | 12,000P |

---

## ⚠️ 보안 주의사항

### 운영 환경 배포 전 필수 변경사항
1. **데이터베이스 비밀번호 변경**
   - 현재: `sajuline_password123!`
   - → 강력한 랜덤 비밀번호로 변경

2. **관리자 계정 비밀번호 변경**
   - 현재: `admin123!`
   - → 복잡한 비밀번호로 변경

3. **테스트 계정 삭제**
   - testuser001, 운세마스터 계정 제거
   - 또는 비밀번호 변경

4. **pgAdmin 접속 정보 변경**
   - 이메일 및 비밀번호 변경
   - 필요시 pgAdmin 비활성화

### 환경별 설정
```bash
# 개발 환경
export DB_HOST=localhost
export DB_USER=sajuline_user
export DB_PASSWORD=sajuline_password123!

# 운영 환경에서는 반드시 환경변수로 관리
export DB_PASSWORD=${SECURE_DB_PASSWORD}
```

---

## 📝 문제 해결

### 자주 발생하는 문제

#### 1. 컨테이너 접속 불가
```bash
# Docker 데몬 상태 확인
docker ps

# 포트 사용 확인
netstat -an | findstr 5432
netstat -an | findstr 8080
```

#### 2. 초기화 스크립트 오류
```bash
# 로그에서 오류 확인
docker-compose logs postgres | findstr ERROR

# 완전 재초기화
docker-compose down -v
docker-compose up -d
```

#### 3. pgAdmin 접속 불가
- 브라우저 캐시 삭제
- 컨테이너 재시작: `docker-compose restart pgadmin`

---

## 📞 지원 정보

- **스키마 문서**: `project-docs/new-main-database-schema.md`
- **Docker 설정**: `docker-compose.yml`
- **초기화 스크립트**: `init-db/` 폴더
- **백업 스크립트**: `init-db-backup/` 폴더

---

**마지막 업데이트**: 2025-07-01  
**작성자**: AI Assistant  
**버전**: v1.0 