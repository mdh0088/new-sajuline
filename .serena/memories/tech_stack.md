# 기술 스택 (Tech Stack)

## 아키텍처 패턴
- **전체 구조**: Backend(FastAPI) + Frontend(Nuxt.js) + Infra(Docker Compose)
- **배포 방식**: Docker 컨테이너 기반 일원화
- **환경 관리**: .env.development/.env.production 파일 기반 설정

## Frontend (Nuxt.js)
### 핵심 기술
- **프레임워크**: Nuxt 3.17+ (Vue 3 기반)
- **언어**: TypeScript 5.6+
- **스타일링**: Tailwind CSS 3.4+
- **상태관리**: Pinia 3.0+
- **빌드**: Vite 기반

### 주요 라이브러리
```json
{
  "nuxt": "^3.17.6",
  "vue": "^3.5.17",
  "@nuxtjs/tailwindcss": "^6.12.1",
  "@pinia/nuxt": "^0.11.1",
  "crypto-js": "^4.2.0"
}
```

### 개발 도구
- ESLint + Prettier (코드 포매팅)
- TypeScript (타입 체크)
- Vue TSC (Vue 타입 체크)

## Backend (FastAPI)
### 핵심 기술
- **프레임워크**: FastAPI 0.110.0
- **런타임**: Python 3.11
- **서버**: Uvicorn + Gunicorn
- **검증**: Pydantic v2

### 데이터베이스
- **주 DB**: MariaDB 10.6+ (aiomysql 드라이버)
- **외부 연동**: MSSQL 2005 (pymssql)
- **ORM**: SQLAlchemy 2.0 + SQLModel
- **마이그레이션**: Alembic 1.13+

### 캐시 & 세션
- **Redis**: 7.x (세션, 캐시, 레이트리밋)
- **라이브러리**: redis[hiredis], aioredis

### 인증 & 보안
- **JWT**: python-jose[cryptography]
- **비밀번호**: passlib[bcrypt]
- **암호화**: AES-256-GCM (cryptography)

### 실시간 통신
- **WebSocket**: python-socketio 5.11+
- **프로토콜**: Socket.IO

### 외부 연동
- **AI**: OpenAI API 1.14+, langchain
- **HTTP**: httpx, aiohttp
- **결제**: Payletter (웹훅)
- **본인확인**: KCP
- **소셜로그인**: Kakao/Naver OAuth

### 모니터링
- **에러추적**: Sentry SDK
- **로깅**: python-json-logger
- **헬스체크**: /healthz, /readyz

## Infrastructure
### 컨테이너화
- **Docker**: 모든 서비스 컨테이너화
- **오케스트레이션**: Docker Compose
- **서비스**: frontend, backend, mariadb, redis, nginx(선택)

### 데이터베이스 서비스
- **MariaDB 10.6**: 메인 데이터 저장소
- **Redis 7**: 캐시, 세션, 큐
- **MSSQL 2005**: 외부 시스템 연동 (읽기 전용)

### 파일 저장
- **AWS S3**: 프로필 이미지, 채팅 파일
- **CDN**: 정적 자산 전송 최적화

## 개발 환경 설정
### 환경 변수 관리
- **Backend**: .env.development, .env.production
- **Frontend**: .env.development, .env.production  
- **Docker**: 파일 마운트 방식으로 전달

### 코드 품질 도구
#### Backend
- **포매팅**: black, isort
- **린팅**: flake8, mypy
- **테스팅**: pytest, pytest-asyncio, pytest-cov

#### Frontend  
- **린팅**: ESLint (@nuxt/eslint-config)
- **포매팅**: Prettier
- **타입체크**: vue-tsc, TypeScript

## 성능 목표
- **API 응답**: p95 300ms 이하
- **AI 응답**: 3초 이내
- **채팅 RTT**: 200ms 이하
- **웹 성능**: LCP 2.5s 이하, CLS 0.1 이하