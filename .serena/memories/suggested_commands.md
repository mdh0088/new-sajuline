# 개발 명령어 가이드

## 프로젝트 구조
```
sajuline-new/
├── backend/          # FastAPI 백엔드
├── frontend/         # Nuxt.js 프론트엔드  
├── infra/           # Docker Compose 설정
└── prototype/       # 기존 프로토타입 참고용
```

## Backend 명령어 (Python/FastAPI)

### 환경 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -e .
pip install -e ".[dev]"   # 개발 의존성 포함
```

### 개발 서버
```bash
# 개발 서버 실행 (auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 또는 스크립트로 실행
python -m src.main
```

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 되돌리기
alembic downgrade -1
```

### 코드 품질 (작업 완료 후 필수 실행)
```bash
# 코드 포매팅
black src/
isort src/

# 린팅
flake8 src/
mypy src/

# 테스트 실행
pytest
pytest --cov=src tests/  # 커버리지 포함
```

### Docker 실행
```bash
# Docker 이미지 빌드
docker build -t sajuline-backend .

# Docker 컨테이너 실행
docker run -p 8000:8000 sajuline-backend
```

## Frontend 명령어 (Nuxt.js/TypeScript)

### 환경 설정
```bash
cd frontend
npm install
# 또는
yarn install
```

### 개발 서버
```bash
# 개발 서버 실행 (http://localhost:3000)
npm run dev
# 또는
yarn dev

# SSR 빌드 후 서버 실행
npm run build && npm run start
```

### 코드 품질 (작업 완료 후 필수 실행)
```bash
# 린팅
npm run lint
npm run lint:fix    # 자동 수정

# 포매팅
npm run format
npm run format:check

# 타입 체크
npm run type-check
```

### 빌드 및 배포
```bash
# 프로덕션 빌드
npm run build

# 정적 사이트 생성
npm run generate

# 프리뷰 (빌드 결과 확인)
npm run preview
```

### Docker 실행
```bash
# Docker 이미지 빌드
docker build -t sajuline-frontend .

# Docker 컨테이너 실행
docker run -p 3000:3000 sajuline-frontend
```

## 인프라 명령어 (Docker Compose)

### 전체 환경 구성
```bash
cd infra

# 개발 환경 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d mariadb redis

# 로그 확인
docker-compose logs -f [service-name]

# 컨테이너 상태 확인
docker-compose ps

# 환경 종료
docker-compose down

# 볼륨까지 삭제하여 완전 정리
docker-compose down -v
```

### 데이터베이스 관리
```bash
# MariaDB 접속
docker-compose exec mariadb mysql -u sajuline -p sajuline

# Redis 접속  
docker-compose exec redis redis-cli

# 데이터베이스 백업
docker-compose exec mariadb mysqldump -u sajuline -p sajuline > backup.sql

# 데이터베이스 복원
cat backup.sql | docker-compose exec -T mariadb mysql -u sajuline -p sajuline
```

## 통합 개발 워크플로

### 1. 전체 환경 시작
```bash
# 1단계: 인프라 서비스 시작
cd infra && docker-compose up -d

# 2단계: 백엔드 개발 서버 시작
cd ../backend && uvicorn src.main:app --reload

# 3단계: 프론트엔드 개발 서버 시작  
cd ../frontend && npm run dev
```

### 2. 작업 완료 후 체크리스트
```bash
# Backend 체크
cd backend
black src/ && isort src/     # 코드 포매팅
flake8 src/                  # 린팅 체크
mypy src/                    # 타입 체크
pytest                       # 테스트 실행

# Frontend 체크
cd frontend  
npm run lint:fix             # 린팅 및 자동 수정
npm run format              # 코드 포매팅
npm run type-check          # 타입 체크
npm run build               # 빌드 확인
```

### 3. Git 워크플로
```bash
# 변경사항 확인
git status
git diff

# 단계별 커밋 (Conventional Commits)
git add .
git commit -m "feat(auth): add OAuth login functionality"

# 푸시 전 최종 확인
git log --oneline -5
git push origin feature/oauth-login
```

## 환경 변수 관리

### Backend (.env.development)
```bash
# 데이터베이스
DATABASE_URL=mysql+aiomysql://sajuline:sajuline123@localhost:3306/sajuline
REDIS_URL=redis://localhost:6379/0

# 보안
JWT_SECRET_KEY=your-secret-key
AES_MASTER_KEY=your-aes-key

# 외부 서비스
OPENAI_API_KEY=your-openai-key
KAKAO_CLIENT_ID=your-kakao-id
NAVER_CLIENT_ID=your-naver-id
```

### Frontend (.env.development)
```bash
# API 엔드포인트
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# 소셜 로그인
NUXT_PUBLIC_KAKAO_CLIENT_ID=your-kakao-id
NUXT_PUBLIC_NAVER_CLIENT_ID=your-naver-id
```

## 헬스체크 및 모니터링

### API 헬스체크
```bash
# Backend 헬스체크
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI

# Frontend 헬스체크  
curl http://localhost:3000/health
```

### 로그 모니터링
```bash
# Docker 로그
docker-compose logs -f backend
docker-compose logs -f frontend

# 개발 중 실시간 로그
tail -f logs/app.log           # Backend
```

## 디버깅 도구

### Backend 디버깅
```bash
# IPython으로 디버깅
pip install ipython
# 코드에 breakpoint() 추가 후 실행

# Pytest 디버깅
pytest -vvs tests/test_specific.py::test_function --pdb
```

### Frontend 디버깅
```bash
# Vue DevTools (브라우저 확장)
# 또는 Nuxt DevTools
npx nuxi@latest devtools enable
```

## 성능 최적화

### Backend 성능 확인
```bash
# API 응답시간 측정
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health

# 부하 테스트 (간단)
ab -n 1000 -c 10 http://localhost:8000/api/v1/health
```

### Frontend 성능 확인
```bash
# 번들 분석
npm run build -- --analyze

# Lighthouse CI
npx lhci autorun
```