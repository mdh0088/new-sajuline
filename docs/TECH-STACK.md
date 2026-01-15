# 사주라인 기술 스택

## 개요

사주라인 프로젝트의 전체 기술 스택을 정리한 문서입니다.

---

## Frontend (사용자 웹)

### 핵심 프레임워크
| 기술 | 버전 | 용도 |
|------|------|------|
| Nuxt | 4.0.3 | SSR/CSR 하이브리드 프레임워크 |
| Vue | 3.5.13 | UI 컴포넌트 프레임워크 |
| TypeScript | 5.6+ | 정적 타입 시스템 |

### UI/스타일링
| 기술 | 버전 | 용도 |
|------|------|------|
| Tailwind CSS | 3.4.17 | 유틸리티 기반 CSS |
| Element Plus | 2.9.7 | UI 컴포넌트 라이브러리 |
| SCSS | - | 커스텀 스타일링 |

### 상태 관리 & 데이터
| 기술 | 버전 | 용도 |
|------|------|------|
| Pinia | 3.0.1 | 상태 관리 |
| TanStack Query | 5.66.0 | 서버 상태 관리 |
| VueUse | 13.0.0 | Vue 유틸리티 컴포저블 |

### 주요 라이브러리
| 기술 | 버전 | 용도 |
|------|------|------|
| Socket.IO Client | 4.8.1 | 실시간 채팅 |
| Swiper | 11.2.1 | 슬라이더/캐러셀 |
| Day.js | 1.11.13 | 날짜 처리 |
| Lottie-web | 5.12.2 | 애니메이션 |

### SEO & 분석
| 기술 | 용도 |
|------|------|
| @nuxtjs/sitemap | 사이트맵 생성 |
| nuxt-gtag | Google Analytics 4 |
| nuxt-schema-org | 구조화된 데이터 |

### 개발 도구
| 기술 | 용도 |
|------|------|
| ESLint | 코드 린팅 |
| Prettier | 코드 포매팅 |
| Vue DevTools | 디버깅 |

---

## Admin-Frontend (관리자 웹)

### 핵심 프레임워크
| 기술 | 버전 | 용도 |
|------|------|------|
| Vue | 3.5.13 | UI 컴포넌트 프레임워크 |
| Vite | 5.2.0 | 빌드 도구 |
| TypeScript | 5.6+ | 정적 타입 시스템 |
| Vue Router | 4.5.0 | SPA 라우팅 |

### UI/스타일링
| 기술 | 버전 | 용도 |
|------|------|------|
| Bootstrap | 5.3.3 | CSS 프레임워크 |
| Element Plus | 2.9.3 | UI 컴포넌트 라이브러리 |
| SCSS | - | 커스텀 스타일링 |
| Feather Icons | - | 아이콘 |

### 상태 관리
| 기술 | 버전 | 용도 |
|------|------|------|
| Pinia | 3.0.1 | 상태 관리 |
| pinia-plugin-persistedstate | 4.2.0 | 상태 영속화 |

### 차트 & 시각화
| 기술 | 버전 | 용도 |
|------|------|------|
| amCharts 5 | 5.10.9 | 데이터 시각화 |
| ApexCharts | 4.3.0 | 차트 라이브러리 |

### 에디터 & 도구
| 기술 | 버전 | 용도 |
|------|------|------|
| TinyMCE | 7.6.1 | 리치 텍스트 에디터 |
| DropZone | 6.0.0-beta.2 | 파일 업로드 |
| XLSX | 0.18.5 | 엑셀 처리 |

### 개발 도구
| 기술 | 용도 |
|------|------|
| ESLint | 코드 린팅 |
| Prettier | 코드 포매팅 |
| unplugin-auto-import | 자동 임포트 |
| unplugin-vue-components | 컴포넌트 자동 등록 |

---

## Backend (사용자 API)

### 핵심 프레임워크
| 기술 | 버전 | 용도 |
|------|------|------|
| FastAPI | 0.110.0 | 웹 프레임워크 |
| Python | 3.11+ | 런타임 |
| Uvicorn | - | ASGI 서버 |
| Gunicorn | - | 프로세스 관리자 |

### 데이터베이스
| 기술 | 버전 | 용도 |
|------|------|------|
| SQLAlchemy | 2.0+ | ORM |
| Alembic | - | DB 마이그레이션 |
| aiomysql | - | 비동기 MySQL 드라이버 |
| pymssql | - | MSSQL 연결 (ARS) |

### 인증 & 보안
| 기술 | 용도 |
|------|------|
| PyJWT | JWT 토큰 |
| python-jose | JWT 처리 |
| passlib[argon2] | 비밀번호 해싱 |
| httpx | HTTP 클라이언트 (OAuth) |

### AI & 챗봇
| 기술 | 버전 | 용도 |
|------|------|------|
| OpenAI | 1.62+ | AI 운세 분석 |
| LangChain | - | LLM 오케스트레이션 |

### 실시간 통신
| 기술 | 버전 | 용도 |
|------|------|------|
| python-socketio | 5.12.1 | WebSocket 서버 |
| Redis | 5.2.1 | 세션/캐시/Pub-Sub |

### 캐싱 & 성능
| 기술 | 용도 |
|------|------|
| Redis | 세션 저장, 캐싱 |
| slowapi | Rate Limiting |

### 결제 연동
| 기술 | 용도 |
|------|------|
| Payletter | 결제 PG |
| 웹훅 처리 | 결제 상태 동기화 |

### 모니터링
| 기술 | 용도 |
|------|------|
| Sentry | 에러 추적 |
| structlog | 구조화된 로깅 |

### 개발 도구
| 기술 | 용도 |
|------|------|
| Black | 코드 포매팅 |
| isort | import 정렬 |
| Flake8 | 린팅 |
| mypy | 타입 체크 |
| pytest | 테스트 |

---

## Admin-Backend (관리자 API)

### 핵심 프레임워크
| 기술 | 버전 | 용도 |
|------|------|------|
| FastAPI | 0.110.0 | 웹 프레임워크 |
| Python | 3.11+ | 런타임 |
| Uvicorn | - | ASGI 서버 |
| Gunicorn | - | 프로세스 관리자 |

### 데이터베이스
| 기술 | 용도 |
|------|------|
| SQLAlchemy 2.0 | ORM |
| Alembic | DB 마이그레이션 |
| aiomysql | 비동기 MySQL |
| pymssql | MSSQL (ARS 연동) |

### 데이터 처리
| 기술 | 용도 |
|------|------|
| Pandas | 데이터 분석 |
| OpenPyXL | 엑셀 파일 처리 |

### 인증 & 보안
| 기술 | 용도 |
|------|------|
| PyJWT | JWT 토큰 |
| python-jose | JWT 처리 |
| passlib[argon2] | 비밀번호 해싱 |

### 모니터링
| 기술 | 용도 |
|------|------|
| Sentry | 에러 추적 |

---

## 인프라 & DevOps

### 클라우드 (AWS)
| 서비스 | 용도 |
|--------|------|
| EC2 | 애플리케이션 서버 |
| VPC | 네트워크 격리 |
| ALB | 로드 밸런싱 |
| S3 | 파일 스토리지 |
| CloudFront | CDN |
| Lambda | 이미지 리사이징 |
| Route 53 | DNS 관리 |

### 데이터베이스
| 기술 | 버전 | 용도 |
|------|------|------|
| MariaDB | 10.6 | 주 데이터베이스 |
| MSSQL | 2005 | 레거시 ARS 연동 |
| Redis | 7.0 | 캐시/세션/실시간 |

### 웹 서버
| 기술 | 용도 |
|------|------|
| Nginx | 리버스 프록시, 정적 파일 |

### 프로세스 관리
| 기술 | 용도 |
|------|------|
| PM2 | Node.js/Python 프로세스 관리 |

### CI/CD
| 기술 | 용도 |
|------|------|
| GitHub Actions | CI/CD 파이프라인 |
| Self-hosted Runner | 배포 실행 |

### 패키지 관리
| 기술 | 용도 |
|------|------|
| npm | Node.js 패키지 |
| uv | Python 패키지 (빠른 설치) |

---

## 외부 서비스 연동

| 서비스 | 용도 |
|--------|------|
| OpenAI API | AI 운세 분석 |
| Kakao OAuth | 소셜 로그인 |
| Naver OAuth | 소셜 로그인 |
| KCP | 휴대폰 본인확인 |
| Payletter | 결제 PG |
| Sentry | 에러 모니터링 |
| Google Analytics | 사용자 분석 |

---

## 버전 호환성 매트릭스

### Node.js 환경
```
Node.js: 20.x LTS
npm: 10.x
```

### Python 환경
```
Python: 3.11+
uv: latest
```

### 데이터베이스 호환성
```
MariaDB: 10.6+
Redis: 7.0+
MSSQL: 2005 (레거시, 읽기 전용)
```
