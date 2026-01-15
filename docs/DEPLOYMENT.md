# 사주라인 배포 가이드

## 개요

사주라인 프로젝트의 배포 프로세스를 정리한 문서입니다.

---

## 배포 환경

| 환경 | 용도 | URL |
|------|------|-----|
| Development | 로컬 개발 | localhost |
| Staging | 테스트 | staging.sajuline.com |
| Production | 운영 | sajuline.com |

---

## CI/CD 파이프라인

### GitHub Actions 워크플로우

#### 1. 사용자 서비스 배포 (deploy-all.yml)
```yaml
트리거: workflow_dispatch (수동)
입력값:
  - deploy_frontend: boolean
  - deploy_backend: boolean
  - environment: dev | prod

실행 단계:
  1. 환경 변수 설정
  2. Self-hosted Runner 체크아웃
  3. 조건부 Frontend/Backend 배포
```

#### 2. 관리자 서비스 배포 (deploy-admin-all.yml)
```yaml
트리거: workflow_dispatch (수동)
입력값:
  - deploy_admin_front: boolean
  - deploy_admin_backend: boolean
  - environment: dev | prod

실행 단계:
  1. 환경 변수 설정
  2. Self-hosted Runner 체크아웃
  3. 조건부 Admin-Front/Admin-Backend 배포
```

---

## 프로세스 관리 (PM2)

### Frontend (Nuxt SSR)
```javascript
// ecosystem.production.config.js
{
  name: 'sajuline-front',
  script: './.output/server/index.mjs',
  instances: 'max',
  exec_mode: 'cluster',
  env: {
    NODE_ENV: 'production',
    PORT: 3100,
    NITRO_PORT: 3100
  }
}
```

### Admin-Frontend (Vue Static)
```javascript
// ecosystem.production.config.js
{
  name: 'sajuline-admin-front',
  script: 'serve',
  args: '-s dist -l 3300',
  env: {
    PM2_SERVE_PATH: './dist',
    PM2_SERVE_PORT: 3300,
    PM2_SERVE_SPA: 'true'
  }
}
```

### Backend (FastAPI)
```javascript
// ecosystem.production.config.js
{
  name: 'sajuline-backend',
  script: 'gunicorn',
  args: '-w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8000',
  interpreter: 'python3',
  env: {
    ENV: 'production'
  }
}
```

### Admin-Backend (FastAPI)
```javascript
// ecosystem.production.config.js
{
  name: 'sajuline-admin-backend',
  script: 'gunicorn',
  args: '-w 2 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8001',
  interpreter: 'python3',
  env: {
    ENV: 'production'
  }
}
```

---

## 배포 스크립트

### Frontend 배포 (deploy.production.sh)
```bash
#!/bin/bash

# 저장소 업데이트
git fetch origin
git checkout main
git pull origin main

# 의존성 설치 및 빌드
npm ci
npm run build

# PM2 재시작
pm2 reload ecosystem.production.config.js --env production
```

### Backend 배포 (deploy.production.sh)
```bash
#!/bin/bash

# 저장소 업데이트
git fetch origin
git checkout main
git pull origin main

# Python 의존성 설치
uv sync

# 기존 포트 프로세스 정리
fuser -k 8000/tcp 2>/dev/null || true

# 마이그레이션 실행
alembic upgrade head

# PM2 재시작
pm2 reload ecosystem.production.config.js --env production
```

### Admin-Frontend 배포 (deploy.production.sh)
```bash
#!/bin/bash

# 저장소 업데이트
git fetch origin
git checkout main
git pull origin main

# 의존성 설치 및 빌드
npm ci
npm run build

# PM2 재시작
pm2 reload ecosystem.production.config.js --env production
```

### Admin-Backend 배포 (deploy.production.sh)
```bash
#!/bin/bash

# 저장소 업데이트
git fetch origin
git checkout main
git pull origin main

# Python 의존성 설치
uv sync

# 기존 포트 프로세스 정리
fuser -k 8001/tcp 2>/dev/null || true

# 마이그레이션 실행
alembic upgrade head

# PM2 재시작
pm2 reload ecosystem.production.config.js --env production
```

---

## Nginx 설정

### 사용자 서비스 (sajuline.com)
```nginx
server {
    listen 80;
    server_name sajuline.com www.sajuline.com;

    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # SQL Injection 방어
    if ($query_string ~* "union.*select|select.*from|insert.*into") {
        return 403;
    }

    # Nuxt SSR 프록시
    location / {
        proxy_pass http://127.0.0.1:3100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API 프록시
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket 프록시
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Rate Limiting
    limit_req zone=api burst=20 nodelay;
}
```

### 관리자 서비스 (admin.sajuline.com)
```nginx
server {
    listen 80;
    server_name admin.sajuline.com;

    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 정적 파일 서빙
    root /var/www/admin-front/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Admin API 프록시
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 환경 변수

### Frontend (.env.production)
```bash
NUXT_PUBLIC_API_URL=https://api.sajuline.com
NUXT_PUBLIC_SOCKET_URL=https://api.sajuline.com
NUXT_PUBLIC_KAKAO_CLIENT_ID=xxx
NUXT_PUBLIC_NAVER_CLIENT_ID=xxx
NUXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

### Backend (.env.production)
```bash
# 데이터베이스
DATABASE_URL=mysql+aiomysql://user:pass@db-host:3306/sajuline
MSSQL_HOST=mssql-host
MSSQL_USER=xxx
MSSQL_PASSWORD=xxx

# Redis
REDIS_URL=redis://redis-host:6379/0

# JWT
JWT_SECRET_KEY=xxx
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# 외부 서비스
OPENAI_API_KEY=xxx
SENTRY_DSN=xxx
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=sajuline-uploads

# 결제
PAYLETTER_API_KEY=xxx
PAYLETTER_SECRET_KEY=xxx
```

### Admin-Backend (.env.production)
```bash
# 데이터베이스
DATABASE_URL=mysql+aiomysql://user:pass@db-host:3306/sajuline_admin
MSSQL_HOST=mssql-host

# JWT
JWT_SECRET_KEY=xxx
ADMIN_JWT_SECRET_KEY=xxx

# 모니터링
SENTRY_DSN=xxx
```

---

## 배포 체크리스트

### 배포 전
- [ ] 코드 리뷰 완료
- [ ] 테스트 통과 확인
- [ ] 환경 변수 설정 확인
- [ ] 마이그레이션 스크립트 준비
- [ ] 롤백 계획 수립

### 배포 중
- [ ] GitHub Actions 워크플로우 실행
- [ ] 배포 로그 모니터링
- [ ] PM2 상태 확인
- [ ] Nginx 설정 리로드 (필요시)

### 배포 후
- [ ] 헬스체크 확인
- [ ] 주요 기능 테스트
- [ ] 에러 로그 확인 (Sentry)
- [ ] 성능 지표 모니터링
- [ ] 사용자 피드백 수집

---

## 롤백 절차

### PM2 롤백
```bash
# 이전 버전으로 롤백
pm2 reload ecosystem.production.config.js --env production

# 특정 커밋으로 롤백
git checkout <commit-hash>
npm ci && npm run build
pm2 reload ecosystem.production.config.js
```

### 데이터베이스 롤백
```bash
# 마이그레이션 롤백
cd backend
alembic downgrade -1
```

### 긴급 롤백
```bash
# 서비스 중지
pm2 stop all

# 이전 안정 버전으로 체크아웃
git checkout tags/v1.0.0

# 재빌드 및 재시작
./deploy.production.sh
```

---

## 모니터링

### PM2 모니터링
```bash
# 상태 확인
pm2 status

# 로그 확인
pm2 logs

# 메트릭 확인
pm2 monit
```

### 헬스체크
```bash
# Frontend
curl -f http://localhost:3100/health

# Backend
curl -f http://localhost:8000/health

# Admin-Frontend
curl -f http://localhost:3300/health

# Admin-Backend
curl -f http://localhost:8001/health
```

### 로그 위치
```
/var/log/nginx/access.log
/var/log/nginx/error.log
~/.pm2/logs/sajuline-front-*.log
~/.pm2/logs/sajuline-backend-*.log
```

---

## 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :3100
lsof -i :8000

# 포트 강제 해제
fuser -k 3100/tcp
fuser -k 8000/tcp
```

### PM2 문제
```bash
# PM2 재시작
pm2 kill
pm2 start ecosystem.production.config.js

# PM2 업데이트
pm2 update
```

### Nginx 문제
```bash
# 설정 테스트
nginx -t

# 설정 리로드
sudo systemctl reload nginx

# 로그 확인
tail -f /var/log/nginx/error.log
```
