# 사주라인 통합 개발 환경

Docker Compose 기반의 사주라인 전체 스택 개발 환경입니다.

## 🏗️ 서비스 구성

### 핵심 서비스
- **Frontend** (Nuxt.js 3): `http://localhost:3000`
- **Backend** (FastAPI): `http://localhost:8000`
- **PostgreSQL** (15-alpine): `localhost:5432`
- **Redis** (7.2-alpine): `localhost:6379`

### 개발 도구 (선택사항)
- **pgAdmin**: `http://localhost:5050` (admin@sajuline.com / admin123)
- **Redis Commander**: `http://localhost:8081` (admin / admin123)

### 모니터링 도구 (선택사항)
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001` (admin / admin123)

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일을 열어서 필요한 값들 수정 (특히 OPENAI_API_KEY)
```

### 2. 전체 스택 실행

```bash
# 기본 서비스만 실행 (프론트엔드, 백엔드, DB, Redis)
docker-compose up -d

# 모든 서비스 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 개발 도구 포함 실행

```bash
# 개발 도구 포함 실행 (pgAdmin, Redis Commander)
docker-compose --profile dev-tools up -d

# 모니터링 도구 포함 실행
docker-compose --profile monitoring up -d

# 모든 프로필 포함 실행
docker-compose --profile dev-tools --profile monitoring up -d
```

### 4. 서비스 상태 확인

```bash
# 모든 컨테이너 상태 확인
docker-compose ps

# 헬스체크 상태 확인
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000/health

# 데이터베이스 연결 테스트
docker-compose exec postgres psql -U sajuline -d sajuline -c "SELECT version();"

# Redis 연결 테스트
docker-compose exec redis redis-cli ping
```

## 🛠️ 개발 워크플로우

### 코드 변경 사항 적용

프론트엔드와 백엔드 모두 볼륨 마운트로 실시간 반영됩니다:

- **Frontend**: 코드 변경 시 자동 HMR (Hot Module Replacement)
- **Backend**: 코드 변경 시 자동 리로드 (`--reload` 옵션 활성화)

### 데이터베이스 초기화

```bash
# 데이터베이스 컨테이너 재시작으로 초기화
docker-compose down postgres
docker-compose up -d postgres

# 또는 볼륨까지 삭제하여 완전 초기화
docker-compose down -v
docker-compose up -d
```

### 개별 서비스 관리

```bash
# 특정 서비스만 재시작
docker-compose restart backend
docker-compose restart frontend

# 특정 서비스만 빌드 및 재시작
docker-compose up -d --build backend

# 서비스 스케일링
docker-compose up -d --scale backend=2
```

## 📊 모니터링 및 로그

### 로그 확인

```bash
# 실시간 로그 확인
docker-compose logs -f --tail=100

# 특정 시간 이후 로그
docker-compose logs --since=2024-01-01T00:00:00

# 에러 로그만 필터링
docker-compose logs | grep ERROR
```

### 메트릭 확인

1. **Prometheus**: http://localhost:9090
   - 메트릭 수집 및 쿼리
   - 알림 규칙 설정

2. **Grafana**: http://localhost:3001
   - 시각화 대시보드
   - 알림 설정

### 리소스 사용량

```bash
# 컨테이너별 리소스 사용량
docker stats

# 디스크 사용량
docker system df

# 네트워크 정보
docker network ls
docker network inspect sajuline_sajuline-network
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인 (Windows)
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

#### 2. 컨테이너 빌드 실패
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 모든 이미지 삭제 후 재빌드
docker-compose down --rmi all
docker-compose up -d --build
```

#### 3. 데이터베이스 연결 실패
```bash
# 데이터베이스 컨테이너 로그 확인
docker-compose logs postgres

# 네트워크 연결 확인
docker-compose exec backend ping postgres
```

#### 4. Redis 연결 실패
```bash
# Redis 설정 확인
docker-compose exec redis redis-cli config get "*"

# Redis 로그 확인
docker-compose logs redis
```

### 성능 최적화

#### 개발 환경 최적화
```bash
# 불필요한 서비스 제외
docker-compose up frontend backend postgres redis

# 리소스 제한 설정 (docker-compose.override.yml)
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  postgres:
    mem_limit: 512m
    cpus: 0.5
  redis:
    mem_limit: 256m
    cpus: 0.3
EOF
```

## 📁 파일 구조

```
infra/
├── docker-compose.yml          # 메인 Compose 파일
├── env.example                 # 환경 변수 템플릿
├── redis.conf                  # Redis 설정
├── data/                       # 데이터 저장소
│   ├── postgres/               # PostgreSQL 데이터
│   └── redis/                  # Redis 데이터
├── init-db/                    # DB 초기화 스크립트
├── monitoring/                 # 모니터링 설정
│   ├── prometheus.yml
│   └── grafana/
├── nginx/                      # Nginx 설정 (프로덕션)
└── README.md                   # 이 파일
```

## 🔐 보안 주의사항

### 개발 환경
- 기본 패스워드는 개발용이므로 프로덕션에서 변경 필수
- Redis는 패스워드 없이 설정됨 (프로덕션에서 설정 필요)

### 프로덕션 배포 시
- 모든 기본 패스워드 변경
- SSL/TLS 인증서 설정
- 방화벽 규칙 적용
- 정기적인 보안 업데이트

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. **로그 확인**: `docker-compose logs -f`
2. **컨테이너 상태**: `docker-compose ps`
3. **네트워크 연결**: `docker network inspect sajuline_sajuline-network`
4. **디스크 공간**: `df -h` 또는 `docker system df`

추가 도움이 필요하면 개발팀에 문의해주세요. 