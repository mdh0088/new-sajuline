#!/bin/bash
# 사주라인 로컬 개발 환경 종료 스크립트

echo "🛑 사주라인 개발 환경을 종료합니다..."
echo ""

# 프로젝트 루트 디렉토리로 이동
cd "$(dirname "$0")"

# Docker 서비스 종료
echo "📦 Docker 서비스 종료 중..."
cd infra
docker-compose down
if [ $? -eq 0 ]; then
    echo "✅ Docker 서비스가 종료되었습니다."
else
    echo "❌ Docker 서비스 종료에 실패했습니다."
fi
cd ..

echo ""
echo "✨ 개발 환경이 종료되었습니다."
echo "   Frontend(npm)는 Ctrl+C로 별도로 종료하세요."
