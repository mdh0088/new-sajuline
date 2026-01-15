# 사주라인 프로젝트 문서 인덱스

## 개요

사주라인은 AI와 전문가의 하이브리드 사주 상담 플랫폼입니다. 이 문서는 프로젝트의 전체 문서를 정리한 인덱스입니다.

---

## 📁 프로젝트 구조

```
new-sajuline/
├── frontend/        # Nuxt 4 사용자 웹 (SSR)
├── admin-front/     # Vue 3 관리자 웹 (SPA)
├── backend/         # FastAPI 사용자 API
├── admin-backend/   # FastAPI 관리자 API
└── docs/            # 프로젝트 문서
```

---

## 📚 핵심 문서

### 아키텍처 & 설계
| 문서 | 설명 |
|------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 시스템 아키텍처 개요 |
| [TECH-STACK.md](./TECH-STACK.md) | 기술 스택 상세 |
| [DATA-MODELS.md](./DATA-MODELS.md) | 데이터베이스 모델 |
| [API-REFERENCE.md](./API-REFERENCE.md) | API 엔드포인트 레퍼런스 |

### 운영 & 배포
| 문서 | 설명 |
|------|------|
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 배포 가이드 |
| [../CLAUDE.md](../CLAUDE.md) | 개발 가이드 (Claude Code) |

---

## 🔧 기존 프로젝트 문서

### 프론트엔드 가이드
| 문서 | 설명 |
|------|------|
| [../FRONT_README.md](../FRONT_README.md) | 프론트엔드 개요 |
| [../FRONT_PAGE_README.md](../FRONT_PAGE_README.md) | 페이지 구조 |
| [../FRONT_FUNCTION_README.md](../FRONT_FUNCTION_README.md) | 기능 가이드 |
| [../FRONT_DIRECTORT_README.md](../FRONT_DIRECTORT_README.md) | 디렉토리 구조 |

### 배포 가이드
| 문서 | 설명 |
|------|------|
| [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) | 일반 배포 가이드 |
| [../ADMIN_AWS_DEPLOYMENT_GUIDE.md](../ADMIN_AWS_DEPLOYMENT_GUIDE.md) | 관리자 AWS 배포 |

### 비즈니스 문서
| 문서 | 설명 |
|------|------|
| [../VIRTUAL_ACCOUNT_PAYMENT_PROCESS.md](../VIRTUAL_ACCOUNT_PAYMENT_PROCESS.md) | 가상계좌 결제 프로세스 |
| [../USER_WITHDRAWAL_IMPACT_ANALYSIS.md](../USER_WITHDRAWAL_IMPACT_ANALYSIS.md) | 회원 탈퇴 영향 분석 |

---

## 🏗️ 프로젝트 파트별 구조

### Frontend (Nuxt 4 + Vue 3)
```
frontend/
├── app/
│   ├── components/     # Vue 컴포넌트
│   ├── composables/    # Vue 컴포저블
│   └── assets/         # 정적 자산
├── pages/              # 라우트 페이지
├── stores/             # Pinia 스토어
├── server/             # Nuxt 서버 API
└── nuxt.config.ts      # Nuxt 설정
```

### Admin-Frontend (Vue 3 + Vite)
```
admin-front/
├── src/
│   ├── views/          # 페이지 뷰
│   ├── components/     # Vue 컴포넌트
│   ├── api/            # API 클라이언트
│   ├── stores/         # Pinia 스토어
│   └── router/         # Vue Router
├── public/             # 정적 파일
└── vite.config.ts      # Vite 설정
```

### Backend (FastAPI + Python)
```
backend/
├── src/
│   ├── api/v1/         # API 라우터
│   ├── models/         # SQLAlchemy 모델
│   ├── schemas/        # Pydantic 스키마
│   ├── services/       # 비즈니스 로직
│   ├── repositories/   # 데이터 접근 계층
│   └── common/         # 공통 유틸리티
├── alembic/            # DB 마이그레이션
└── pyproject.toml      # Python 의존성
```

### Admin-Backend (FastAPI + Python)
```
admin-backend/
├── src/
│   ├── api/v1/         # API 라우터
│   ├── models/         # SQLAlchemy 모델
│   ├── schemas/        # Pydantic 스키마
│   ├── services/       # 비즈니스 로직
│   └── repositories/   # 데이터 접근 계층
├── alembic/            # DB 마이그레이션
└── pyproject.toml      # Python 의존성
```

---

## 🌐 AWS 인프라 구성

| 서비스 | 용도 |
|--------|------|
| Route 53 | DNS 관리 |
| CloudFront | CDN, SSL 종료 |
| ALB | 로드 밸런싱 |
| EC2 (VPC) | 애플리케이션/DB 서버 |
| S3 | 파일 스토리지 |
| Lambda | 이미지 리사이징 |
| Redis | 세션/캐시 |

### VPC 구성
- **Public Subnet**: Bastion Host (t3.micro) + Redis
- **Private Subnet**: App Server (t2.small), DB Server (t2.small)

---

## 🔗 외부 서비스 연동

| 서비스 | 용도 |
|--------|------|
| OpenAI API | AI 운세 분석 |
| Kakao OAuth | 소셜 로그인 |
| Naver OAuth | 소셜 로그인 |
| KCP | 휴대폰 본인확인 |
| Payletter | 결제 PG |
| Sentry | 에러 모니터링 |
| Google Analytics 4 | 사용자 분석 |

---

## 📊 주요 성능 지표

| 지표 | 목표 |
|------|------|
| API 응답시간 | p95 < 300ms |
| AI 응답시간 | < 3초 |
| 채팅 RTT | < 200ms |
| LCP | < 2.5초 |
| CLS | < 0.1 |

---

## 🚀 빠른 시작

### 개발 환경 설정
```bash
# 백엔드
cd backend
uv sync
uvicorn src.main:app --reload

# 프론트엔드
cd frontend
npm install
npm run dev

# 관리자 백엔드
cd admin-backend
uv sync
uvicorn src.main:app --reload --port 8001

# 관리자 프론트엔드
cd admin-front
npm install
npm run dev
```

### 프로덕션 배포
```bash
# GitHub Actions 워크플로우 사용
# deploy-all.yml (사용자 서비스)
# deploy-admin-all.yml (관리자 서비스)
```

---

## 📝 문서 업데이트 기록

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-01-15 | 1.0.0 | 초기 문서 생성 (Deep Scan) |

---

## 📞 연락처

- **프로젝트 저장소**: GitHub (private)
- **문서 관리**: BMAD Analyst Workflow
