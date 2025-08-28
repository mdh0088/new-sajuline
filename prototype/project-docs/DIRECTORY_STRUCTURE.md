# 사주라인 프로토 - 디렉토리 구조

## 📁 프로젝트 개요
사주라인(Sajuline) 리뉴얼 프로젝트의 디렉토리 구조 및 파일 설명

---

## 🗂️ 루트 디렉토리 구조

```
sajuline-proto/
├── 📁 codebase/                    # UI/UX 프로토타입 HTML 파일들
├── 📁 init-db/                     # 데이터베이스 초기화 스크립트
├── 📁 init-db-backup/              # 데이터베이스 백업 스크립트
├── 📁 project-docs/                # 프로젝트 문서화
├── 📄 DATABASE-LOGIN-INFO.md       # 데이터베이스 로그인 정보
├── 📄 docker-compose.yml           # Docker 컨테이너 설정
├── 📄 README-DATABASE.md           # 데이터베이스 관련 README
├── 📄 README.md                    # 프로젝트 메인 README
└── 📄 DIRECTORY_STRUCTURE.md       # 이 문서
```

---

## 📂 상세 디렉토리 분석

### 🎨 `/codebase` - UI/UX 프로토타입
프론트엔드 개발을 위한 사전 제작된 HTML 파일들이 포함되어 있습니다.

```
codebase/
├── 🔮 ai_cs2.html                  # AI 상담 페이지 (버전 2)
├── 🔮 ai-fortune-complete.html     # AI 운세 완료 페이지
├── 💬 chat_list.html               # 채팅 목록 페이지
├── 💬 chat-cs-page.html            # 채팅 상담 페이지
├── 💬 chatting.html                # 채팅 인터페이스
├── 📋 cs_log.html                  # 상담 로그 페이지
├── 📄 detail.html                  # 상세 페이지
├── 🎉 event_detail.html            # 이벤트 상세 페이지
├── 🎉 event.html                   # 이벤트 페이지
├── ⭐ favorite.html                # 즐겨찾기 페이지
├── 📝 inquiry-detail.html          # 문의 상세 페이지
├── 📝 inquiry-list.html            # 문의 목록 페이지
├── 📝 inquiry-write.html           # 문의 작성 페이지
├── 🔑 login-page.html              # 로그인 페이지
├── 🏠 main.html                    # 메인 페이지
├── 🎁 member_benefit.html          # 회원 혜택 페이지
├── 👤 mypage.html                  # 마이페이지
├── 📢 notice_detail.html           # 공지사항 상세 페이지
├── 📢 notice.html                  # 공지사항 페이지
├── 💰 point_guide.html             # 포인트 가이드 페이지
├── 💰 point_log.html               # 포인트 로그 페이지
├── 💰 point.html                   # 포인트 페이지
├── 📜 privacy.html                 # 개인정보 처리방침
├── 📜 provision.html               # 이용약관
├── ⚡ quick-cs-page.html           # 빠른 상담 페이지
├── ⭐ review-page.html             # 리뷰 페이지
├── 🔍 search-page.html             # 검색 페이지
├── 👥 signup-page_v2.html          # 회원가입 페이지 (버전 2)
└── 👥 signup-page.html             # 회원가입 페이지
```

### 🗄️ `/init-db` - 데이터베이스 초기화 스크립트
PostgreSQL 데이터베이스 구조를 생성하는 SQL 스크립트들입니다.

```
init-db/
├── 01-create-extensions.sql        # PostgreSQL 확장 기능 설치
├── 02-create-functions.sql         # 공통 함수 생성
├── 03-create-tables-users.sql      # 사용자 관련 테이블
├── 04-create-tables-counselors.sql # 상담사 관련 테이블
├── 05-create-tables-ai.sql         # AI 서비스 관련 테이블
├── 06-create-tables-consultations.sql # 상담 관련 테이블
├── 07-create-tables-payments.sql   # 결제 관련 테이블
├── 08-create-tables-community.sql  # 커뮤니티 관련 테이블
├── 09-create-tables-system.sql     # 시스템 관리 테이블
├── 10-create-tables-logs.sql       # 로그 관련 테이블
├── 11-create-partitions.sql        # 테이블 파티셔닝 설정
└── 99-insert-initial-data.sql      # 초기 데이터 삽입
```

### 💾 `/init-db-backup` - 백업 스크립트
데이터베이스 백업용 스크립트 모음입니다.

```
init-db-backup/
├── 01-create-extensions.sql        # 확장 기능 백업
├── 02-create-types.sql             # 커스텀 타입 정의
├── 03-create-tables-users.sql      # 사용자 테이블 백업
├── 04-create-tables-counselors-ai.sql # 상담사/AI 테이블 백업
├── 05-create-tables-consultations-points.sql # 상담/포인트 테이블 백업
├── 06-create-tables-reviews-admin-logs.sql # 리뷰/관리자/로그 테이블 백업
└── 99-insert-initial-data.sql      # 초기 데이터 백업
```

### 📚 `/project-docs` - 프로젝트 문서
프로젝트 관련 모든 문서화 파일들이 위치합니다.

```
project-docs/
├── 📊 ars-database-schema.md       # ARS 데이터베이스 스키마
├── 🔄 business-process.md          # 비즈니스 프로세스 정의
├── 📝 CODE_GUIDLINE.md             # 코딩 가이드라인
├── 🔄 data-migration-generator.md  # 데이터 마이그레이션 가이드
├── 📊 main-database-schema.md      # 메인 데이터베이스 스키마 (기존)
├── 📊 new-main-database-schema-v2.md # 새로운 메인 DB 스키마 v2
├── 📊 new-main-database-schema.md  # 새로운 메인 데이터베이스 스키마
├── 📋 PRD.md                       # 제품 요구사항 정의서
├── 🏗️ system-architecture.md       # 시스템 아키텍처
└── 🛠️ TRD.md                       # 기술 요구사항 정의서
```

---

## 🔧 설정 파일

### 📄 `docker-compose.yml`
- Docker 컨테이너 환경 설정
- PostgreSQL, Redis, 백엔드 서비스 등을 포함한 개발 환경 구성

### 📄 `DATABASE-LOGIN-INFO.md`
- 개발/운영 환경별 데이터베이스 접속 정보
- 보안상 민감한 정보이므로 .gitignore 대상

---

## 📖 README 파일

### 📄 `README.md`
- 프로젝트 메인 README
- 프로젝트 개요, 설치 방법, 사용법 등

### 📄 `README-DATABASE.md`
- 데이터베이스 관련 전용 README
- 스키마 구조, 마이그레이션 가이드 등

---

## 🎯 프로젝트 구조의 특징

### ✅ 장점
1. **모듈화된 구조**: 각 기능별로 명확히 분리된 디렉토리
2. **문서화 중심**: 체계적인 문서 관리로 개발 생산성 향상
3. **프로토타입 기반**: 사전 제작된 HTML로 개발 방향성 명확화
4. **점진적 데이터베이스 구조**: 기존 → 신규 스키마로의 체계적 마이그레이션

### 📋 권장 사항
1. **Frontend**: `codebase/` 의 HTML 파일들을 React 컴포넌트로 변환
2. **Backend**: `init-db/` 스크립트를 기반으로 FastAPI 백엔드 구현
3. **Documentation**: `project-docs/` 의 문서들을 지속적으로 업데이트
4. **Database**: 점진적으로 `new-main-database-schema.md` 기반으로 마이그레이션

---

## 🚀 다음 단계

1. **Frontend 개발**: Next.js 15 + TypeScript 환경 구성
2. **Backend 개발**: FastAPI + SQLModel 환경 구성  
3. **Database 설정**: PostgreSQL 15+ 및 Redis 컨테이너 구성
4. **CI/CD**: GitHub Actions 기반 배포 파이프라인 구축

---

*이 문서는 프로젝트 구조 변경 시 지속적으로 업데이트됩니다.* 