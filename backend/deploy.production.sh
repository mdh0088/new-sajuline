#!/bin/bash
set -e

# 변수 설정
APP_DIR="/data/www/new-sajuline/backend"
LOG_FILE="$APP_DIR/logs/deploy-production.log"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== Backend Production 배포 시작 =========="

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
# uv run alembic upgrade head

# PM2 프로세스 재시작
log "PM2 재시작..."
if pm2 describe fastapi-sajuline > /dev/null 2>&1; then
    log "기존 프로세스 완전 제거..."
    pm2 delete fastapi-sajuline

    # 포트 8000 점유 프로세스 강제 종료
    log "포트 8000 점유 프로세스 확인 및 종료..."
    PORT_PIDS=$(sudo lsof -ti :8000 2>/dev/null || true)
    if [ -n "$PORT_PIDS" ]; then
        log "포트 점유 프로세스 발견: $PORT_PIDS"
        sudo kill -9 $PORT_PIDS || true
        sleep 2
    fi

    # Gunicorn 좀비 프로세스 정리
    log "Gunicorn 좀비 프로세스 정리..."
    pkill -f "gunicorn.*fastapi-sajuline" || true
    sleep 1

    # 포트 해제 최종 확인
    if sudo lsof -i :8000 > /dev/null 2>&1; then
        log "경고: 포트 8000이 여전히 사용 중입니다"
        sudo lsof -i :8000
    else
        log "포트 8000 해제 확인 완료"
    fi
fi

log "프로세스 시작 (Production)..."
pm2 start ecosystem.config.production.js

# PM2 설정 저장 (서버 재부팅 시 자동 시작)
pm2 save

log "========== Backend Production 배포 완료 =========="
