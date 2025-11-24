#!/bin/bash
# 사주라인 로컬 개발 환경 시작 스크립트

echo "🚀 사주라인 개발 환경을 시작합니다..."
echo ""

# 프로젝트 루트 디렉토리로 이동
cd "$(dirname "$0")"

# 1. Docker 서비스 시작 (Backend, MariaDB, Redis 등)
echo "📦 Docker 서비스 시작 중..."
cd infra
docker-compose up -d
if [ $? -eq 0 ]; then
    echo "✅ Docker 서비스가 시작되었습니다."
else
    echo "❌ Docker 서비스 시작에 실패했습니다."
    exit 1
fi
cd ..

# Docker 서비스가 완전히 시작될 때까지 대기
echo "⏳ Backend 서비스가 준비될 때까지 대기 중..."
sleep 5

# 2. Frontend 개발 서버 시작
echo ""
echo "🎨 Frontend 개발 서버 시작 중..."
cd frontend
echo "   - URL: http://localhost:3000"
echo "   - 중지하려면 Ctrl+C를 누르세요"
echo ""
npm run dev
