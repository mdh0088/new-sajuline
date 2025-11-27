# GitHub Actions Self-hosted Runner 배포 가이드

AWS EC2 Private 서브넷 환경에서 GitHub Actions Self-hosted Runner를 사용한 배포 가이드입니다.

## 목차
1. [아키텍처 개요](#1-아키텍처-개요)
2. [사전 준비](#2-사전-준비)
3. [GitHub Self-hosted Runner 설치](#3-github-self-hosted-runner-설치)
4. [배포 스크립트 생성](#4-배포-스크립트-생성)
5. [GitHub Actions 워크플로우](#5-github-actions-워크플로우)
6. [배포 테스트](#6-배포-테스트)
7. [Runner 관리](#7-runner-관리)
8. [트러블슈팅](#8-트러블슈팅)

---

## 1. 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS VPC                               │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │  Public Subnet  │    │        Private Subnet            │ │
│  │                 │    │                                   │ │
│  │  ┌───────────┐  │    │  ┌─────────────────────────────┐ │ │
│  │  │  Bastion  │  │    │  │      EC2 Instance           │ │ │
│  │  │  (SSH용)  │──┼────┼──│  - GitHub Actions Runner    │ │ │
│  │  └───────────┘  │    │  │  - Backend (FastAPI)        │ │ │
│  │                 │    │  │  - Frontend (Nuxt.js)       │ │ │
│  └─────────────────┘    │  └─────────────────────────────┘ │ │
│                         └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ NAT Gateway (아웃바운드)
                              ▼
                    ┌─────────────────┐
                    │  GitHub.com     │
                    │  (Runner 연결)  │
                    └─────────────────┘
```

### Self-hosted Runner 동작 방식
1. Runner가 GitHub에 **아웃바운드** 연결 (NAT 통해 가능)
2. GitHub에서 워크플로우 트리거 시 Runner가 작업 수신
3. Runner가 로컬에서 배포 스크립트 실행
4. **인바운드 연결 불필요** → Private 서브넷에서 동작 가능

---

## 2. 사전 준비

### 2.1 서버 요구사항
- OS: Amazon Linux 2 / Ubuntu 20.04+
- CPU: 2 vCPU 이상 권장
- RAM: 4GB 이상 권장
- 디스크: 20GB 이상 여유 공간
- 네트워크: NAT Gateway를 통한 아웃바운드 인터넷 접근

### 2.2 필수 패키지 설치

Bastion을 통해 Private EC2에 SSH 접속 후 실행:

```bash
# Amazon Linux 2 기준
# Git 설치
sudo yum install -y git

# Node.js 20.x 설치
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Python 3.11 설치
sudo amazon-linux-extras install python3.11 -y
# 또는 pyenv 사용

# PM2 전역 설치
sudo npm install -g pm2

# 기타 필수 패키지
sudo yum install -y libicu jq
```

### 2.3 배포 디렉토리 구조 확인

```bash
# 디렉토리 구조
/data/www/new-sajuline/
├── backend/
│   ├── .venv/           # Python 가상환경
│   ├── src/
│   ├── ecosystem.config.js
│   └── logs/
└── frontend/
    ├── node_modules/
    ├── .output/         # Nuxt 빌드 결과
    ├── ecosystem.config.cjs
    └── logs/

# 디렉토리 생성 (없는 경우)
sudo mkdir -p /data/www/new-sajuline/backend/logs
sudo mkdir -p /data/www/new-sajuline/frontend/logs
sudo chown -R ec2-user:ec2-user /data/www/new-sajuline
```

---

## 3. GitHub Self-hosted Runner 설치

### 3.1 GitHub에서 Runner 토큰 발급

1. GitHub 레포지토리로 이동: `https://github.com/mdh0088/new-sajuline`
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Actions** → **Runners** 클릭
4. **New self-hosted runner** 버튼 클릭
5. OS: **Linux**, Architecture: **x64** 선택
6. 화면에 표시되는 토큰을 복사 (유효기간 1시간)

![Runner 설정 화면](https://docs.github.com/assets/cb-12377/images/help/actions/actions-runner-architecture.png)

### 3.2 Runner 설치 (EC2 서버에서 실행)

```bash
# 1. Runner 전용 디렉토리 생성
mkdir -p ~/actions-runner && cd ~/actions-runner

# 2. 최신 Runner 패키지 다운로드
# 버전 확인: https://github.com/actions/runner/releases
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# 3. 압축 해제
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 4. 의존성 설치 (선택사항 - 에러 발생 시)
sudo ./bin/installdependencies.sh
```

### 3.3 Runner 설정

```bash
# GitHub에서 발급받은 토큰으로 설정
# --url: 레포지토리 URL
# --token: GitHub에서 복사한 토큰
# --name: Runner 이름 (구분용)
# --labels: 커스텀 라벨 (워크플로우에서 사용)
# --work: 작업 디렉토리

./config.sh \
  --url https://github.com/mdh0088/new-sajuline \
  --token <YOUR_TOKEN_HERE> \
  --name "sajuline-ec2-runner" \
  --labels "self-hosted,linux,x64,sajuline" \
  --work "_work" \
  --unattended
```

**설정 시 질문 응답 예시** (--unattended 없이 실행 시):
```
Enter the name of the runner group to add this runner to: [press Enter for Default]
→ Enter 키 (기본값 사용)

Enter the name of runner: [press Enter for ip-xxx-xxx-xxx-xxx]
→ sajuline-ec2-runner

Enter any additional labels:
→ sajuline

Enter name of work folder: [press Enter for _work]
→ Enter 키 (기본값 사용)
```

### 3.4 Runner 서비스 등록 (자동 시작 설정)

```bash
# 서비스 설치 (root 권한 필요)
sudo ./svc.sh install

# 서비스 시작
sudo ./svc.sh start

# 서비스 상태 확인
sudo ./svc.sh status
```

### 3.5 Runner 등록 확인

GitHub에서 확인:
1. 레포지토리 → Settings → Actions → Runners
2. 등록한 Runner가 **Idle** 상태로 표시되면 성공

```bash
# 서버에서 상태 확인
cd ~/actions-runner
./run.sh --check
```

---

## 4. 배포 스크립트 생성

### 4.1 Backend 배포 스크립트

```bash
cat << 'EOF' > /data/www/new-sajuline/backend/deploy.sh
#!/bin/bash
set -e

# 변수 설정
APP_DIR="/data/www/new-sajuline/backend"
LOG_FILE="$APP_DIR/logs/deploy.log"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== Backend 배포 시작 =========="

cd "$APP_DIR"

# Git 최신 코드 가져오기
log "Git pull 실행..."
git fetch origin
git reset --hard origin/main
log "Git pull 완료"

# uv로 의존성 설치
log "Python 의존성 설치 (uv)..."
uv sync
log "의존성 설치 완료"

# 데이터베이스 마이그레이션 (필요시 주석 해제)
# log "데이터베이스 마이그레이션..."
# alembic upgrade head

# PM2 프로세스 재시작
log "PM2 재시작..."
if pm2 describe fastapi-sajuline > /dev/null 2>&1; then
    pm2 reload ecosystem.config.js --env production
else
    pm2 start ecosystem.config.js --env production
fi

# PM2 설정 저장 (서버 재부팅 시 자동 시작)
pm2 save

log "========== Backend 배포 완료 =========="
EOF

chmod +x /data/www/new-sajuline/backend/deploy.sh
```

### 4.2 Frontend 배포 스크립트

```bash
cat << 'EOF' > /data/www/new-sajuline/frontend/deploy.sh
#!/bin/bash
set -e

# 변수 설정
APP_DIR="/data/www/new-sajuline/frontend"
LOG_FILE="$APP_DIR/logs/deploy.log"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== Frontend 배포 시작 =========="

cd "$APP_DIR"

# Git 최신 코드 가져오기
log "Git pull 실행..."
git fetch origin
git reset --hard origin/main
log "Git pull 완료"

# Node.js 의존성 설치
log "NPM 의존성 설치..."
npm ci --silent
log "의존성 설치 완료"

# Nuxt 빌드
log "Nuxt 빌드 시작..."
npm run build
log "빌드 완료"

# PM2 프로세스 재시작
log "PM2 재시작..."
if pm2 describe nuxt-sajuline > /dev/null 2>&1; then
    pm2 reload ecosystem.config.cjs --env production
else
    pm2 start ecosystem.config.cjs --env production
fi

# PM2 설정 저장
pm2 save

log "========== Frontend 배포 완료 =========="
EOF

chmod +x /data/www/new-sajuline/frontend/deploy.sh
```

### 4.3 배포 스크립트 테스트

```bash
# Backend 테스트
cd /data/www/new-sajuline/backend
./deploy.sh

# Frontend 테스트
cd /data/www/new-sajuline/frontend
./deploy.sh

# PM2 상태 확인
pm2 status
```

---

## 5. GitHub Actions 워크플로우

### 5.1 Backend 배포 워크플로우

파일: `.github/workflows/deploy-backend.yml`

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        working-directory: backend
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run code quality checks
        working-directory: backend
        run: |
          black --check src/
          isort --check-only src/
          flake8 src/
          mypy src/

  deploy:
    needs: test
    runs-on: [self-hosted, sajuline]
    steps:
      - name: Deploy Backend
        run: |
          cd /data/www/new-sajuline/backend
          ./deploy.sh

      - name: Health Check
        run: |
          sleep 5
          curl -f http://localhost:8000/health || echo "Health check skipped"
```

### 5.2 Frontend 배포 워크플로우

파일: `.github/workflows/deploy-frontend.yml`

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Type check
        working-directory: frontend
        run: npm run type-check

  deploy:
    needs: lint
    runs-on: [self-hosted, sajuline]
    steps:
      - name: Deploy Frontend
        run: |
          cd /data/www/new-sajuline/frontend
          ./deploy.sh

      - name: Health Check
        run: |
          sleep 10
          curl -f http://localhost:3000/ || echo "Health check skipped"
```

### 5.3 전체 배포 워크플로우 (수동)

파일: `.github/workflows/deploy-all.yml`

```yaml
name: Deploy All (Manual)

on:
  workflow_dispatch:
    inputs:
      target:
        description: '배포 대상'
        required: true
        default: 'all'
        type: choice
        options:
          - all
          - backend
          - frontend

jobs:
  deploy-backend:
    if: ${{ github.event.inputs.target == 'all' || github.event.inputs.target == 'backend' }}
    runs-on: [self-hosted, sajuline]
    steps:
      - name: Deploy Backend
        run: |
          cd /data/www/new-sajuline/backend
          ./deploy.sh

      - name: Health Check
        run: |
          sleep 5
          curl -f http://localhost:8000/health || echo "Health check skipped"

  deploy-frontend:
    if: ${{ always() && (github.event.inputs.target == 'all' || github.event.inputs.target == 'frontend') }}
    runs-on: [self-hosted, sajuline]
    needs: [deploy-backend]
    steps:
      - name: Deploy Frontend
        run: |
          cd /data/www/new-sajuline/frontend
          ./deploy.sh

      - name: Health Check
        run: |
          sleep 10
          curl -f http://localhost:3000/ || echo "Health check skipped"
```

---

## 6. 배포 테스트

### 6.1 수동 배포 테스트

1. GitHub 레포지토리 → **Actions** 탭
2. 좌측에서 워크플로우 선택 (예: Deploy Backend)
3. **Run workflow** 버튼 클릭
4. 브랜치 선택 후 **Run workflow** 실행

### 6.2 자동 배포 테스트

```bash
# 로컬에서 코드 수정 후 push
cd backend  # 또는 frontend
echo "# test" >> README.md
git add .
git commit -m "test: trigger deployment"
git push origin main
```

### 6.3 배포 결과 확인

**GitHub에서 확인:**
- Actions 탭에서 워크플로우 실행 상태 확인
- 녹색 체크마크: 성공
- 빨간 X: 실패 (로그 확인)

**서버에서 확인:**
```bash
# PM2 상태
pm2 status
pm2 logs --lines 50

# 배포 로그
tail -f /data/www/new-sajuline/backend/logs/deploy.log
tail -f /data/www/new-sajuline/frontend/logs/deploy.log

# 헬스체크
curl http://localhost:8000/health
curl http://localhost:3000/
```

---

## 7. Runner 관리

### 7.1 Runner 서비스 명령어

```bash
cd ~/actions-runner

# 상태 확인
sudo ./svc.sh status

# 시작
sudo ./svc.sh start

# 중지
sudo ./svc.sh stop

# 재시작
sudo ./svc.sh stop && sudo ./svc.sh start

# 서비스 제거
sudo ./svc.sh uninstall
```

### 7.2 Runner 업데이트

GitHub에서 새 버전 알림이 오면:

```bash
cd ~/actions-runner

# 서비스 중지
sudo ./svc.sh stop

# 새 버전 다운로드
curl -o actions-runner-linux-x64-2.312.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.312.0/actions-runner-linux-x64-2.312.0.tar.gz

# 압축 해제 (기존 파일 덮어쓰기)
tar xzf ./actions-runner-linux-x64-2.312.0.tar.gz

# 서비스 시작
sudo ./svc.sh start
```

### 7.3 Runner 삭제

```bash
cd ~/actions-runner

# 서비스 중지 및 제거
sudo ./svc.sh stop
sudo ./svc.sh uninstall

# GitHub에서 Runner 등록 해제
./config.sh remove --token <TOKEN>

# 또는 GitHub 웹에서 직접 삭제
# Settings → Actions → Runners → 해당 Runner 선택 → Remove
```

### 7.4 여러 Runner 운영 (선택사항)

고가용성을 위해 여러 Runner 운영 가능:

```bash
# 두 번째 Runner 디렉토리
mkdir -p ~/actions-runner-2 && cd ~/actions-runner-2

# 설치 및 설정 (다른 이름으로)
./config.sh \
  --url https://github.com/mdh0088/new-sajuline \
  --token <TOKEN> \
  --name "sajuline-ec2-runner-2" \
  --labels "self-hosted,linux,x64,sajuline"
```

---

## 8. 트러블슈팅

### 8.1 Runner가 Offline 상태

```bash
# 서비스 상태 확인
sudo ./svc.sh status

# 로그 확인
sudo journalctl -u actions.runner.mdh0088-new-sajuline.sajuline-ec2-runner.service -f

# 서비스 재시작
sudo ./svc.sh stop
sudo ./svc.sh start
```

### 8.2 Runner 연결 실패 (네트워크)

```bash
# GitHub 연결 테스트
curl -I https://github.com
curl -I https://api.github.com

# NAT Gateway 확인
curl -I https://www.google.com

# DNS 확인
nslookup github.com
```

### 8.3 권한 오류

```bash
# 배포 디렉토리 권한
sudo chown -R ec2-user:ec2-user /data/www/new-sajuline
chmod -R 755 /data/www/new-sajuline

# 배포 스크립트 실행 권한
chmod +x /data/www/new-sajuline/backend/deploy.sh
chmod +x /data/www/new-sajuline/frontend/deploy.sh
```

### 8.4 PM2 관련 오류

```bash
# PM2 프로세스 확인
pm2 status
pm2 describe fastapi-sajuline

# 에러 로그 확인
pm2 logs fastapi-sajuline --err --lines 100

# PM2 완전 재시작
pm2 delete all
cd /data/www/new-sajuline/backend
pm2 start ecosystem.config.js --env production
cd /data/www/new-sajuline/frontend
pm2 start ecosystem.config.cjs --env production
pm2 save
```

### 8.5 Git 관련 오류

```bash
cd /data/www/new-sajuline/backend

# Git 상태 확인
git status

# 로컬 변경사항 무시하고 강제 pull
git fetch origin
git reset --hard origin/main

# Git 권한 오류 시
git config --global --add safe.directory /data/www/new-sajuline/backend
git config --global --add safe.directory /data/www/new-sajuline/frontend
```

### 8.6 빌드 실패 (Frontend)

```bash
cd /data/www/new-sajuline/frontend

# node_modules 재설치
rm -rf node_modules
rm -rf .output
npm ci

# 메모리 부족 시
export NODE_OPTIONS="--max-old-space-size=2048"
npm run build
```

---

## 부록

### A. 체크리스트

**Runner 설치 전:**
- [ ] EC2 인스턴스에 SSH 접속 가능
- [ ] NAT Gateway를 통한 인터넷 연결 확인
- [ ] Git, Node.js, Python, PM2 설치 완료

**Runner 설치:**
- [ ] GitHub에서 Runner 토큰 발급
- [ ] Runner 다운로드 및 압축 해제
- [ ] config.sh로 설정 완료
- [ ] svc.sh로 서비스 등록 및 시작
- [ ] GitHub에서 Runner 상태 Idle 확인

**배포 설정:**
- [ ] 배포 스크립트 생성 및 실행 권한 부여
- [ ] 배포 스크립트 수동 테스트 성공
- [ ] GitHub Actions 워크플로우 파일 생성
- [ ] 워크플로우 수동 실행 테스트 성공

### B. 유용한 명령어 모음

```bash
# Runner 상태
sudo ./svc.sh status
pm2 status

# 로그 확인
pm2 logs --lines 100
tail -f /data/www/new-sajuline/backend/logs/deploy.log

# 헬스체크
curl http://localhost:8000/health
curl http://localhost:3000/

# 디스크 용량
df -h

# 메모리 사용량
free -m
```

### C. 참고 링크

- [GitHub Self-hosted Runner 공식 문서](https://docs.github.com/en/actions/hosting-your-own-runners)
- [PM2 공식 문서](https://pm2.keymetrics.io/docs/usage/quick-start/)
- [GitHub Actions 워크플로우 문법](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
