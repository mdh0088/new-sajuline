# 🚀 개발 환경 빠른 시작 가이드

## 시작하기

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요:

```bash
./start-dev.sh
```

이 스크립트는 자동으로:
1. ✅ Docker 서비스 시작 (Backend API, MariaDB, Redis)
2. ✅ Frontend 개발 서버 시작 (http://localhost:3000)

## 종료하기

```bash
# Frontend 종료: Ctrl+C (터미널에서)

# Docker 서비스 종료:
./stop-dev.sh
```

## 접속 주소

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Admin Backend**: http://localhost:8001
- **Admin Frontend**: http://localhost:8088

## 주요 설정 파일

- `frontend/.env` - 프론트엔드 환경 변수
  - CDN: `https://cdn.sajuline.com/dev-upload/`
  - Proxy: `http://localhost:8000`

## 수동 시작 (필요시)

### Backend (Docker)
```bash
cd infra
docker-compose up -d
```

### Frontend
```bash
cd frontend
npm run dev
```

### Admin Backend (선택사항)
```bash
cd admin-backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

### Admin Frontend (선택사항)
```bash
cd admin-front
npm run dev
```

## 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 포트 사용 확인
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :8001  # Admin Backend
lsof -i :8088  # Admin Frontend

# 프로세스 종료
kill -9 [PID]
```

### Docker 서비스 재시작
```bash
cd infra
docker-compose down
docker-compose up -d
```

### Frontend 캐시 삭제
```bash
cd frontend
rm -rf .nuxt node_modules/.vite
npm run dev
```

## 주요 변경 사항 (로컬 환경 설정)

1. ✅ `.env` 파일 생성 (CDN 및 프록시 설정)
2. ✅ 프로필 아바타 크기 확대 (240px × 200px)
3. ✅ 상담사 specialty 라벨 변경
   - "타로마스터" → "전화타로"
   - "사주마스터" → "전화사주"
   - "운세마스터" → "전화신점"

---

💡 **팁**: 첫 실행 시 Docker 이미지 다운로드로 시간이 걸릴 수 있습니다.
