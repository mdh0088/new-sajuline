# Technology Stack Evaluation

### Project Type: Brownfield

이 프로젝트는 기존 운영 중인 시스템의 현대화 프로젝트입니다. 새로운 starter template 선택이 아닌 **기존 기술 스택 활용**이 적절합니다.

### Established Technology Stack

**Frontend (사용자 웹):**
| 기술 | 버전 | 결정 근거 |
|------|------|----------|
| Nuxt 4 | 4.0.3 | SSR/CSR 하이브리드, SEO 최적화 |
| Vue 3 | 3.5.13 | Composition API, TypeScript 지원 |
| Tailwind CSS | 3.4.17 | 유틸리티 기반, 모바일 퍼스트 |
| Pinia | 3.0.1 | Vue 공식 상태 관리 |
| TanStack Query | 5.66.0 | 서버 상태 캐싱 |
| Socket.IO Client | 4.8.1 | 실시간 채팅 |

**Backend (사용자 API):**
| 기술 | 버전 | 결정 근거 |
|------|------|----------|
| FastAPI | 0.110.0 | 비동기, 자동 문서화, 타입 힌팅 |
| Python | 3.11+ | 성능 개선, 타입 지원 |
| SQLAlchemy 2.0 | 2.0+ | 비동기 ORM |
| OpenAI | 1.62+ | AI 운세 분석 |
| python-socketio | 5.12.1 | WebSocket 서버 |
| Redis | 5.2.1 | 세션/캐시/Pub-Sub |

**Admin Frontend:**
| 기술 | 버전 | 결정 근거 |
|------|------|----------|
| Vue 3 + Vite | 5.2.0 | SPA, 빠른 빌드 |
| Bootstrap 5 | 5.3.3 | 관리자 UI 적합 |
| Element Plus | 2.9.3 | 풍부한 컴포넌트 |

**Admin Backend:**
- FastAPI + Python 3.11 (사용자 API와 동일 스택)
- 별도 인증 체계 (관리자 JWT)

**Infrastructure:**
| 기술 | 용도 |
|------|------|
| AWS (EC2, S3, CloudFront, ALB) | 클라우드 인프라 |
| MariaDB 10.6 | 주 데이터베이스 |
| Redis 7.0 | 캐시/세션/실시간 |
| Nginx | 리버스 프록시 |
| PM2 | 프로세스 관리 |
| GitHub Actions | CI/CD |

### Architectural Decisions Established

**Language & Runtime:**
- Frontend: TypeScript 5.6+ (strict mode)
- Backend: Python 3.11+ (type hints)

**Styling Solution:**
- 사용자 웹: Tailwind CSS + SCSS
- 관리자 웹: Bootstrap 5 + SCSS

**Build Tooling:**
- Frontend: Nuxt 4 (Nitro), Vite
- Backend: uvicorn/gunicorn

**Testing Framework:**
- Frontend: Vitest (예정)
- Backend: pytest

**Code Organization:**
- Frontend: Feature-based (pages/, components/, composables/)
- Backend: Layer-based (api/, services/, repositories/, models/)

**Development Experience:**
- Hot Reload: Nuxt dev, uvicorn --reload
- Debugging: Vue DevTools, Python debugger
- Linting: ESLint + Prettier (FE), Black + isort + Flake8 (BE)

### New Development: AI Fortune Service

MVP 신규 개발 대상인 AI 운세 서비스는 기존 스택 위에 구현:

```
신규 컴포넌트:
├── Frontend
│   └── pages/fortune/          # AI 운세 페이지
│       ├── index.vue           # 메인 진입점
│       └── components/         # 운세 UI 컴포넌트
├── Backend
│   └── src/
│       ├── api/v1/fortune_api.py     # API 엔드포인트
│       ├── services/fortune_service.py # 비즈니스 로직
│       └── services/openai_service.py  # OpenAI 연동
└── Database
    └── fortune_histories      # 운세 기록 테이블
```

---
