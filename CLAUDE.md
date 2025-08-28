<c2c-rules>
- @c2c-rules/_root.md
</c2c-rules>

# 사주라인 리뉴얼 프로젝트 - Claude Code 가이드

## 프로젝트 개요

**사주라인 리뉴얼 MVP**: AI와 전문가의 하이브리드 사주 상담 플랫폼
- 기존 sajuline.com의 현대화된 모바일 퍼스트 서비스
- Nuxt 3 + FastAPI + Docker Compose 기반 단순 아키텍처
- AI 운세, 실시간 채팅 상담, 투명한 포인트 시스템 제공

## 아키텍처 구조

```
sajuline-new/
├── backend/          # FastAPI 백엔드 (Python 3.11)
├── frontend/         # Nuxt.js 프론트엔드 (Vue 3 + TypeScript)
├── infra/           # Docker Compose 인프라 설정
├── c2c-rules/       # 개발 가이드라인 및 PRD/TRD
└── prototype/       # 기존 프로토타입 (참고용)
```

## 핵심 기술 스택

### Frontend
- **Nuxt 3.17+** (SSR/CSR 하이브리드)
- **TypeScript 5.6+** + **Vue 3.5+**
- **Tailwind CSS 3.4+** (모바일 퍼스트)
- **Pinia** (상태 관리)

### Backend  
- **FastAPI 0.110+** + **Python 3.11**
- **SQLAlchemy 2.0** + **Alembic** (MariaDB 10.6)
- **Redis 7** (세션, 캐시, 실시간)
- **python-socketio** (WebSocket 채팅)
- **OpenAI API** (AI 운세 분석)

### Infrastructure
- **Docker Compose** (개발/스테이징 일원화)
- **MariaDB** (주 데이터), **MSSQL 2005** (외부 연동)
- **AWS S3** (파일 저장), **Sentry** (에러 추적)

## 개발 환경 설정

### 전체 환경 시작
```bash
# 1. 인프라 서비스 시작
cd infra && docker-compose up -d

# 2. 백엔드 개발 서버
cd ../backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# 3. 프론트엔드 개발 서버
cd ../frontend
npm install && npm run dev
```

### 환경 변수 설정
- **Backend**: `.env.development` (DB, Redis, API 키)
- **Frontend**: `.env.development` (API URL, 소셜 로그인)
- **Docker**: 환경변수는 파일 마운트 방식 사용

## 필수 개발 명령어

### 작업 완료 후 품질 검사 (필수)
```bash
# Backend 품질 검사
cd backend
black src/ && isort src/     # 포매팅
flake8 src/ && mypy src/     # 린팅 + 타입 체크
pytest --cov=src tests/     # 테스트 + 커버리지

# Frontend 품질 검사  
cd frontend
npm run lint:fix             # 린팅 자동 수정
npm run format              # 포매팅
npm run type-check          # 타입 체크
npm run build               # 빌드 확인
```

### 데이터베이스 관리
```bash
cd backend
# 마이그레이션 생성
alembic revision --autogenerate -m "description"
# 마이그레이션 적용
alembic upgrade head
```

### Docker 관리
```bash
cd infra
# 전체 환경 시작/종료
docker-compose up -d / docker-compose down
# 로그 확인
docker-compose logs -f [service-name]
```

## 코드 스타일 가이드

### Python (Backend)
- **포매팅**: Black (88자), isort
- **네이밍**: snake_case (함수/변수), PascalCase (클래스)
- **타입 힌팅**: 필수 (mypy strict 모드)
- **도메인 중심 구조**: auth, user, counselor, chat 등

### TypeScript (Frontend)  
- **네이밍**: camelCase (함수/변수), PascalCase (컴포넌트)
- **Vue**: Composition API + `<script setup>` 패턴
- **타입**: interface는 I 접두사

### Git 커밋 컨벤션
```
<type>(<scope>): <description>

예시:
feat(auth): add OAuth2 Google login
fix(chat): resolve WebSocket disconnection issue
docs(api): update authentication endpoints
```

## 성능 목표 & 모니터링

### 성능 지표
- **API 응답**: p95 300ms 이하
- **AI 응답**: 3초 이내  
- **채팅 RTT**: 200ms 이하
- **웹 성능**: LCP 2.5s, CLS 0.1 이하

### 헬스체크
```bash
# API 상태 확인
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI

# 프론트엔드 확인
curl http://localhost:3000/health
```

## 보안 가이드라인

### 핵심 원칙
- **모든 사용자 입력 검증** (Pydantic 스키마)
- **JWT 인증**: HttpOnly 쿠키 + CSRF 토큰
- **데이터 암호화**: AES-256-GCM (PII), Argon2id (비밀번호)
- **API 보안**: CORS 설정, 레이트 리밋
- **환경 변수**: 민감 정보 코드 노출 금지

## 도메인별 주요 기능

### 1. 인증 (Auth)
- 이메일/비밀번호, Kakao/Naver 소셜 로그인
- KCP 본인확인 연동
- JWT 기반 세션 관리

### 2. AI 운세 서비스  
- OpenAI API 연동 (3초 SLA)
- 일/주/월 운세 분석
- 개인화 추천 시스템

### 3. 실시간 채팅
- Socket.IO 기반 WebSocket
- 상담사 매칭 및 예약
- 메시지 암호화 저장

### 4. 포인트 시스템
- Payletter 결제 연동
- 투명한 차감/적립 시스템
- 이중 장부로 정합성 보장

## 배포 및 운영

### 환경별 설정
- **Development**: Docker Compose 로컬 환경
- **Staging**: 동일 구성으로 검증
- **Production**: AWS ECS/Fargate 고려

### 모니터링
- **Sentry**: 에러 추적 및 성능 모니터링
- **Google Analytics 4**: 사용자 행동 분석
- **구조화 로깅**: JSON 형태, 요청 ID 상관관계

## 테스트 전략

### 백엔드
- **단위 테스트**: 서비스/리포지토리 로직
- **통합 테스트**: OAuth, 결제 웹훅
- **E2E 테스트**: 핵심 플로우 (가입→충전→상담)

### 프론트엔드
- **컴포넌트 테스트**: Vue 컴포넌트
- **E2E 테스트**: 사용자 여정 검증

## 외부 연동 서비스

### 필수 연동
- **OpenAI**: AI 운세 분석 엔진
- **KCP**: 휴대폰 본인확인
- **Payletter**: 포인트 충전 결제
- **Kakao/Naver**: 소셜 로그인
- **AWS S3**: 파일 저장

### 데이터베이스 연동
- **MariaDB**: 주 데이터 저장소
- **MSSQL 2005**: 외부 상담사 시스템 (읽기 전용)
- **Redis**: 캐시, 세션, 실시간 데이터

## 개발 가이드라인 참고

### 문서 위치: `c2c-rules/rules/`
- **vooster__prd.md**: 제품 요구사항 문서
- **vooster__architecture.md**: 기술 아키텍처 가이드
- **vooster__clean-code.md**: 클린 코드 원칙
- **vooster__git-commit-message.md**: 커밋 메시지 규칙

## 문제 해결

### 일반적인 이슈
1. **포트 충돌**: 8000(Backend), 3000(Frontend), 3306(MariaDB), 6379(Redis)
2. **의존성 문제**: `pip install -e ".[dev]"` 또는 `npm install` 재실행
3. **DB 마이그레이션**: Alembic 상태 확인 및 수동 적용
4. **Docker 문제**: `docker-compose down -v`로 완전 정리 후 재시작

### 로그 위치
- **Backend**: 터미널 출력 + `logs/` 디렉터리
- **Frontend**: 브라우저 콘솔 + 터미널 출력  
- **Docker**: `docker-compose logs -f [service]`

## 개발팀 협업

### 브랜치 전략
- `main`: 프로덕션 준비 코드
- `develop`: 개발 통합
- `feature/*`: 기능 개발
- `hotfix/*`: 긴급 수정

### 코드 리뷰 체크포인트
- [ ] 품질 검사 도구 모두 통과
- [ ] 테스트 커버리지 확보
- [ ] 성능/보안 고려사항 확인
- [ ] API 문서 업데이트
- [ ] 적절한 커밋 메시지

---

**MVP 목표**: 4주 내 Core 기능 완성 → 8주 Enhanced Features → 지속적 개선
**핵심 가치**: 단순함, 안정성, 사용자 경험, 확장 가능성