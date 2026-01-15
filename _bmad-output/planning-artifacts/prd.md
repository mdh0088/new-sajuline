---
stepsCompleted:
  - step-01-init
  - step-01b-continue
  - step-02-discovery
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
inputDocuments:
  - docs/index.md
  - docs/ARCHITECTURE.md
  - docs/TECH-STACK.md
  - docs/API-REFERENCE.md
  - docs/DATA-MODELS.md
  - docs/DEPLOYMENT.md
  - _bmad-output/planning-artifacts/product-brief-new-sajuline-2026-01-15.md
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 6
workflowType: 'prd'
projectType: 'brownfield'
classification:
  projectType: 'Web Application (SaaS)'
  domain: 'Entertainment/Lifestyle'
  complexity: 'Medium'
  projectContext: 'brownfield'
---

# Product Requirements Document - new-sajuline

**Author:** DongDong
**Date:** 2026-01-15
**Version:** 1.0
**Status:** Complete - Ready for Architecture

---

## Executive Summary

**new-sajuline**은 기존 sajuline.com을 현대화한 AI 기반 하이브리드 사주 상담 플랫폼입니다.

### 문제 정의
기존 서비스의 올드한 UI, 느린 속도, 더딘 업데이트로 인한 사용자 이탈 및 젊은 세대 접근성 저하

### 해결 방안
AI 기반 일일/주간/월간/연간 운세 서비스를 통해 낮은 진입장벽과 트렌디한 경험 제공

### MVP 범위
- **핵심 기능**: AI 운세 서비스 (일일/주간/월간/연간)
- **기존 완료**: 모던 UI/UX, 상담 시스템, 회원/결제 시스템
- **기술 스택**: Nuxt 4 + FastAPI + MariaDB + OpenAI API

### 핵심 성공 지표
| 지표 | 목표 |
|------|------|
| AI 운세 응답시간 | < 3초 |
| AI 운세 이용률 | 가입자 30%+ |
| 서비스 가용성 | 99%+ |

### 주요 리스크
- OpenAI API 의존성 → 폴백 응답 준비
- 운세 품질 → 프롬프트 지속 개선

---

## Success Criteria

### User Success

**핵심 성공 순간:**
- AI 운세 결과가 본인 상황과 맞아떨어질 때 "가치 인식"
- 빠르고 간편하게 운세를 확인할 수 있을 때 만족
- 기존 올드한 서비스 대비 현대적이고 트렌디한 경험

**측정 가능한 사용자 성공:**

| 지표 | 목표 | 의미 |
|------|------|------|
| AI 운세 이용률 | 가입자의 30%+ | 새 기능 채택도 |
| 첫 상담 완료율 | 측정 필요 | 신규 가입 → 첫 경험 전환 |
| 재방문율 | 측정 필요 | 서비스 만족도 간접 측정 |

### Business Success

**현재 단계 우선순위** (매출보다 안정성 우선):

| 우선순위 | 성공 기준 | 구체적 목표 |
|----------|-----------|-------------|
| 1순위 | 서비스 안정성 | 99%+ 가용성 유지 |
| 2순위 | 개발 민첩성 | 빠른 개발-테스트-배포 사이클 |
| 3순위 | UX 개선 | 사용자 피드백 반영 속도 |

### Technical Success

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| API 응답시간 | p95 < 300ms | 서버 모니터링 |
| AI 운세 응답시간 | < 3초 | OpenAI API 응답 추적 |
| 페이지 로드 (LCP) | < 2.5초 | Core Web Vitals |
| 서비스 가용성 | 99%+ | 업타임 모니터링 |

### Measurable Outcomes

**MVP 출시 후 성공 판단 기준:**
- ✅ AI 운세 기능이 3초 이내 응답
- ✅ 가입자 30% 이상이 AI 운세 이용
- ✅ 서비스 99% 이상 가용성 유지
- ✅ 사용자 피드백이 긍정적

---

## Product Scope

### MVP - Minimum Viable Product

**AI 운세 서비스** (P0 - 필수):
- 일일 운세 AI 분석
- 주간 운세 AI 분석
- 월간 운세 AI 분석
- 연간 운세 AI 분석

**기술 구현:**
- OpenAI API 연동
- 프롬프트 템플릿 방식
- 로그인 필수 (기존 사주 정보 활용)
- 추가 사용자 입력 없음

**이미 완료된 기능:**
- ✅ 모던 UI/UX 리뉴얼
- ✅ 기존 상담 서비스 (상담사 목록, 예약, 채팅)
- ✅ 회원 시스템 (가입, 로그인, 소셜 로그인)
- ✅ 결제 시스템 (포인트 충전)
- ✅ 관리자 시스템

### Growth Features (Post-MVP)

**Phase 2: 하이브리드 상담**
- 전문 상담사 + AI 보조 상담
- AI가 사전 분석 제공 → 상담사가 심층 상담

### Vision (Future)

**Phase 3: AI 중심 상담**
- 상담사가 사주 데이터/해석 패턴 제공
- AI가 데이터 기반 자동 상담 수행
- 상담사는 복잡한 케이스만 담당

**장기 비전:**
- AI 사주 서비스 시장 선점
- 개인화된 운세 알림 서비스
- 사주 기반 라이프스타일 추천

---

## User Journeys

### Journey 1: 민지의 AI 운세 첫 경험 (Primary User - Success Path)

**페르소나**: 민지, 34세, 직장인 여성, 기혼

**Opening Scene (현재 상황):**
민지는 다음 달 이직 면접을 앞두고 있다. 평소 중요한 결정 전에는 항상 사주를 확인하는 습관이 있다. 오늘도 sajuline.com에 접속했는데, 새로운 "AI 운세" 메뉴가 눈에 띈다.

**Rising Action (여정):**
1. 로그인 후 메인 화면에서 "오늘의 운세" 버튼 클릭
2. 이미 가입 시 입력한 사주 정보가 자동으로 적용됨
3. 약 2-3초의 로딩 후 AI가 분석한 오늘의 운세 결과 표시
4. 일/주/월/연간 탭을 전환하며 다양한 기간의 운세 확인

**Climax (가치 인식 순간):**
AI 운세 결과가 "이번 주 중반에 좋은 소식이 있을 수 있다"고 말하고, 실제로 면접 일정이 그 시기에 잡혀있다. 민지는 "오, 신기하네?" 하며 운세 내용을 더 자세히 읽는다.

**Resolution (결과):**
민지는 AI 운세를 매일 아침 확인하는 습관이 생긴다. 기존 상담사 상담 전에 AI 운세로 대략적인 흐름을 파악하고, 중요한 결정은 여전히 상담사와 상담한다.

---

### Journey 2: 신규 사용자의 첫 AI 운세 (Primary User - Onboarding)

**페르소나**: 수진, 28세, 취업 준비생

**Opening Scene:**
인스타그램에서 친구가 공유한 AI 운세 결과를 보고 호기심에 sajuline.com에 접속했다. 사주에 대해 잘 모르지만, AI가 분석해준다니 재미있을 것 같다.

**Rising Action:**
1. 회원가입 (이메일 또는 카카오/네이버 소셜 로그인)
2. 본인인증 (핸드폰 번호)
3. 사주 정보 입력 (생년월일, 태어난 시간, 성별)
4. 가입 완료 시 10,000P 자동 지급
5. 메인 화면에서 "AI 운세" 클릭

**Climax:**
무료 포인트 없이도 AI 운세를 확인할 수 있다는 것을 알고 기뻐한다. 결과가 본인 상황과 맞아 "신기하다"며 주간 운세도 확인한다.

**Resolution:**
수진은 취업운이 궁금해져서 전문 상담사와의 상담도 시도해본다. 10,000P로 약 5분간 상담 체험 후, 만족하면 포인트 충전을 고려한다.

---

### Journey 3: 상담사의 AI 운세 활용 (Secondary User - Counselor)

**페르소나**: 김선생, 52세, 전문 상담사 (경력 15년)

**Opening Scene:**
김선생은 하루에 10-15건의 상담을 진행한다. 새로운 AI 운세 기능이 추가되었다는 공지를 보고, 상담 준비에 활용할 수 있을지 궁금하다.

**Rising Action:**
1. (현재 MVP에서는 상담사 전용 기능 없음)
2. 고객이 AI 운세를 먼저 확인하고 상담에 들어오는 경우가 늘어남
3. 고객이 "AI 운세에서 이렇게 나왔는데 맞나요?"라고 물어봄

**Climax:**
김선생은 AI 운세가 대략적인 흐름을 잡아주어 상담 진입점이 쉬워졌다고 느낀다. 고객이 이미 기본 정보를 알고 오니 심층 상담에 집중할 수 있다.

**Resolution:**
Phase 2에서 AI가 상담 전 사전 분석을 제공하면 더 효율적인 상담이 가능할 것이라 기대한다.

---

### Journey 4: 관리자의 AI 운세 모니터링 (Admin User)

**페르소나**: DongDong, 개발/총괄 관리자

**Opening Scene:**
AI 운세 기능 출시 후 첫 주, 서비스 상태와 사용자 반응을 모니터링해야 한다.

**Rising Action:**
1. 관리자 페이지에서 AI 운세 이용 통계 확인
2. OpenAI API 응답 시간 및 에러율 확인
3. 사용자 피드백 수집 (문의 게시판, Sentry 에러)
4. 필요 시 프롬프트 템플릿 조정

**Climax:**
AI 응답 시간이 목표(3초) 이내이고, 가입자의 30% 이상이 AI 운세를 이용하는 것을 확인했을 때 MVP 성공을 인식한다.

**Resolution:**
안정적인 운영을 확인하고, Phase 2 개발 계획을 수립한다.

---

### Journey Requirements Summary

| Journey | 필요한 기능 |
|---------|-------------|
| **민지 (헤비 유저)** | AI 운세 조회 UI, 일/주/월/연간 탭, 빠른 응답 |
| **수진 (신규 유저)** | 회원가입 플로우, 사주 정보 입력, AI 운세 접근성 |
| **김선생 (상담사)** | (MVP) 현재는 별도 기능 없음, Phase 2에서 사전 분석 |
| **DongDong (관리자)** | AI 운세 통계, API 모니터링, 프롬프트 관리 |

---

## Innovation & Novel Patterns

### Detected Innovation Areas

1. **AI-Powered Fortune Analysis**
   - OpenAI API를 활용한 사주/운세 분석
   - 기존 정적 콘텐츠 기반 서비스와 차별화
   - 개인화된 AI 운세 제공

2. **Market Timing Innovation**
   - AI 사주 서비스 시장에서 명확한 리더 부재
   - First mover advantage 확보 기회
   - 트렌드(AI 시대)와 도메인(사주)의 결합

3. **Hybrid Service Model**
   - Phase 1: AI 운세 (MVP)
   - Phase 2: AI + 상담사 협업
   - Phase 3: 상담사 데이터 → AI 상담 (진화)

### Validation Approach

| 검증 항목 | 방법 |
|-----------|------|
| AI 응답 품질 | 사용자 피드백 수집, 정성적 평가 |
| 시장 반응 | AI 운세 이용률 30%+ 목표 |
| 기술 안정성 | API 응답시간 < 3초, 가용성 99%+ |

### Risk Mitigation

| 리스크 | 완화 전략 |
|--------|-----------|
| AI 응답 품질 불만족 | 프롬프트 템플릿 지속 개선, 사용자 피드백 반영 |
| OpenAI API 의존성 | 캐싱 전략, 대체 모델 고려 (장기) |
| 경쟁사 진입 | 빠른 이터레이션, 1인 개발자 민첩성 활용 |

---

## Web Application Specific Requirements

### Project-Type Overview

new-sajuline은 AI 기반 사주 상담 플랫폼으로, Nuxt 4 기반 하이브리드 렌더링(SSR/CSR)을 활용한 현대적인 웹 애플리케이션입니다. 모바일 퍼스트 접근법으로 30~40대 여성 헤비 유저를 주 타겟으로 하며, 실시간 채팅 상담과 AI 운세 서비스를 제공합니다.

### Technical Architecture Considerations

**Rendering Strategy:**
- **Hybrid SSR/CSR**: Nuxt 4의 하이브리드 렌더링 활용
  - SSR: 메인 페이지, 상담사 목록 (SEO 중요)
  - CSR: 마이페이지, 채팅, 결제 (동적 인터랙션)
- **ISR (Incremental Static Regeneration)**: 공지사항, 상담사 프로필

**Browser Support Matrix:**

| Browser | Minimum Version | Priority |
|---------|-----------------|----------|
| Chrome | 90+ | Primary |
| Safari | 14+ | Primary (iOS 대응) |
| Samsung Internet | 15+ | Primary (국내 모바일) |
| Firefox | 88+ | Secondary |
| Edge | 90+ | Secondary |
| IE | 미지원 | - |

### Responsive Design Requirements

**Mobile-First Breakpoints:**
- **Mobile**: 320px - 767px (Primary)
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

**Critical Mobile UX:**
- Touch target minimum: 44px × 44px
- Bottom navigation for primary actions
- Swipe gestures for 일/주/월/연간 운세 탭 전환
- 채팅 인터페이스 모바일 최적화

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP (Largest Contentful Paint) | < 2.5s | Core Web Vitals |
| FID (First Input Delay) | < 100ms | Core Web Vitals |
| CLS (Cumulative Layout Shift) | < 0.1 | Core Web Vitals |
| API Response (p95) | < 300ms | 서버 모니터링 |
| AI 운세 응답 | < 3s | OpenAI API 추적 |
| 채팅 RTT | < 200ms | WebSocket 모니터링 |
| Time to Interactive | < 3.5s | Lighthouse |

**Performance Budget:**
- Initial JS bundle: < 200KB (gzipped)
- Total page weight: < 1MB
- Image optimization: WebP with fallback

### SEO Strategy

**SSR for SEO-Critical Pages:**
- 메인 페이지 (/)
- 상담사 목록 (/counselors)
- 상담사 프로필 (/counselors/:id)
- 공지사항 (/notices)
- 서비스 소개 (/about)

**Technical SEO:**
- Semantic HTML5 markup
- Structured data (JSON-LD): Organization, Service, Person (상담사)
- Dynamic sitemap generation
- Meta tags: Open Graph, Twitter Cards
- Canonical URLs

**SEO 제외 영역:**
- 인증 필요 페이지 (마이페이지, 채팅, 결제)
- robots.txt로 크롤링 제외

### Accessibility Requirements

**WCAG 2.1 AA 준수 목표:**

| Category | Requirement |
|----------|-------------|
| Perceivable | 색상 대비 4.5:1 이상, 이미지 alt 텍스트 |
| Operable | 키보드 네비게이션, Focus indicators |
| Understandable | 일관된 네비게이션, 에러 메시지 명확화 |
| Robust | 시맨틱 HTML, ARIA labels |

**우선 접근성 항목:**
- 폼 요소 레이블 연결
- 버튼/링크 명확한 텍스트
- 모달 포커스 트랩
- 스크린 리더 호환성
- 확대 200%까지 레이아웃 유지

### Real-Time Features

**Socket.IO 기반 실시간 기능:**
- 채팅 메시지 송수신
- 상담사 온라인 상태 표시
- 타이핑 인디케이터
- 읽음 확인

**연결 관리:**
- 자동 재연결 (exponential backoff)
- 연결 상태 UI 표시
- 오프라인 큐잉 (재연결 시 전송)

### Implementation Considerations

**Security:**
- HTTPS 전용 (HSTS)
- CSP (Content Security Policy) 설정
- XSS/CSRF 방어

**Caching Strategy:**
- Service Worker: 정적 자산 캐싱
- CDN: CloudFront 활용
- API 캐싱: Redis (운세 결과 24시간)

**Error Handling:**
- Sentry 통합 (프론트엔드 에러 추적)
- Graceful degradation for AI 서비스
- 사용자 친화적 에러 메시지 (한국어)

---

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP

사용자의 "오늘의 운세를 빠르고 현대적으로 확인하고 싶다"는 핵심 문제를 해결하는 최소 기능 제품입니다. 기존 서비스의 올드한 UI와 느린 속도 문제를 해결하면서, AI 운세라는 차별화된 가치를 제공합니다.

**MVP Philosophy:**
- 기존 완료된 기능 활용 (상담, 회원, 결제)
- 신규 개발은 AI 운세에만 집중
- 빠른 출시 후 사용자 피드백 기반 개선

**Resource Requirements:**
- 1인 개발자 (풀스택)
- 운영 관리자 2명 (기존)
- 외부 의존성: OpenAI API

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

| Journey | MVP 지원 여부 |
|---------|---------------|
| 민지 (헤비 유저) | ✅ 완전 지원 |
| 수진 (신규 유저) | ✅ 완전 지원 |
| 김선생 (상담사) | ⚠️ 간접 지원 (전용 기능 없음) |
| DongDong (관리자) | ✅ 기본 지원 |

**Must-Have Capabilities:**

| 기능 | 우선순위 | 상태 |
|------|----------|------|
| AI 일일 운세 | P0 | 🆕 신규 개발 |
| AI 주간 운세 | P0 | 🆕 신규 개발 |
| AI 월간 운세 | P0 | 🆕 신규 개발 |
| AI 연간 운세 | P0 | 🆕 신규 개발 |
| 운세 결과 UI | P0 | 🆕 신규 개발 |
| 회원 시스템 | P0 | ✅ 완료 |
| 상담 시스템 | P0 | ✅ 완료 |
| 결제 시스템 | P0 | ✅ 완료 |

**MVP Exclusions:**
- ❌ 상담사 전용 AI 어시스턴트
- ❌ AI 채팅 상담
- ❌ 궁합 분석
- ❌ 타로/꿈해몽

### Post-MVP Features

**Phase 2: Growth (하이브리드 상담)**

| 기능 | 설명 | 의존성 |
|------|------|--------|
| 상담사 AI 어시스턴트 | 상담 전 AI 사전 분석 제공 | MVP 안정화 |
| 상담 요약 AI | 상담 내용 자동 요약 | Phase 1 데이터 |
| 개인화 추천 | AI 기반 상담사 추천 | 사용자 데이터 |

**Phase 3: Expansion (AI 중심 상담)**

| 기능 | 설명 | 의존성 |
|------|------|--------|
| AI 자동 상담 | 상담사 데이터 기반 AI 상담 | Phase 2 |
| 상담사 데이터 수집 | 해석 패턴 데이터화 | 상담사 협조 |
| 운세 알림 서비스 | 개인화 푸시 알림 | 사용자 기반 |
| 라이프스타일 추천 | 사주 기반 일상 추천 | AI 고도화 |

### Risk Mitigation Strategy

**Technical Risks:**

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| OpenAI API 장애 | High | 캐싱 전략 (24시간), 에러 핸들링 UI |
| API 응답 지연 | Medium | 타임아웃 설정, 로딩 UX 최적화 |
| 프롬프트 품질 | Medium | 템플릿 A/B 테스트, 피드백 수집 |

**Market Risks:**

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| AI 운세 불신 | Medium | 사주 전문 용어 활용, 신뢰도 강조 |
| 경쟁사 진입 | Low | 빠른 이터레이션, 선점 효과 |
| 사용자 이탈 | Medium | 무료 AI 운세로 진입장벽 낮춤 |

**Resource Risks:**

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| 1인 개발 병목 | High | MVP 범위 최소화, 기존 기능 활용 |
| API 비용 증가 | Medium | 캐싱 적극 활용, 사용량 모니터링 |
| 기술 부채 | Low | 클린 아키텍처 유지 (리뉴얼 완료) |

### MVP Success Criteria

**출시 조건:**
- [ ] AI 운세 4종 (일/주/월/연) 동작
- [ ] 응답 시간 3초 이내
- [ ] 에러율 1% 미만
- [ ] 모바일 UX 검증 완료

**성공 판단 (출시 후 2주):**
- [ ] 가입자 30%+ AI 운세 이용
- [ ] 서비스 가용성 99%+
- [ ] 부정적 피드백 10% 미만

---

## Functional Requirements

> **Capability Contract**: 이 목록에 없는 기능은 최종 제품에 존재하지 않습니다. 모든 UX 디자인, 아키텍처, Epic 분해는 이 FR 목록을 기반으로 합니다.

### 사용자 계정 관리 (User Account)

- FR1: 사용자는 이메일과 비밀번호로 회원가입할 수 있다
- FR2: 사용자는 카카오 계정으로 소셜 로그인할 수 있다
- FR3: 사용자는 네이버 계정으로 소셜 로그인할 수 있다
- FR4: 사용자는 휴대폰 번호로 본인인증을 완료할 수 있다
- FR5: 사용자는 사주 정보(생년월일, 태어난 시간, 성별, 음력 여부)를 입력할 수 있다
- FR6: 사용자는 프로필 정보를 조회하고 수정할 수 있다
- FR7: 사용자는 비밀번호를 변경할 수 있다
- FR8: 사용자는 회원 탈퇴를 요청할 수 있다
- FR9: 신규 가입 사용자는 가입 완료 시 웰컴 포인트를 자동 지급받는다

### AI 운세 서비스 (AI Fortune)

- FR10: 로그인한 사용자는 일일 운세를 AI 분석으로 조회할 수 있다
- FR11: 로그인한 사용자는 주간 운세를 AI 분석으로 조회할 수 있다
- FR12: 로그인한 사용자는 월간 운세를 AI 분석으로 조회할 수 있다
- FR13: 로그인한 사용자는 연간 운세를 AI 분석으로 조회할 수 있다
- FR14: 사용자는 운세 기간 유형(일/주/월/연)을 탭으로 전환할 수 있다
- FR15: 시스템은 사용자의 기존 사주 정보를 기반으로 AI 운세를 생성한다
- FR16: 시스템은 동일 사용자의 동일 기간 운세 요청 시 캐시된 결과를 제공한다

### 상담 서비스 (Consultation)

- FR17: 사용자는 온라인 상태인 상담사 목록을 조회할 수 있다
- FR18: 사용자는 상담사 프로필(소개, 전문분야, 평점, 가격)을 확인할 수 있다
- FR19: 사용자는 특정 상담사와 채팅 상담을 시작할 수 있다
- FR20: 사용자는 상담사에게 텍스트 메시지를 전송할 수 있다
- FR21: 사용자는 상담사로부터 실시간으로 메시지를 수신할 수 있다
- FR22: 사용자는 진행 중인 채팅에서 상담사의 타이핑 상태를 확인할 수 있다
- FR23: 사용자는 상담 완료 후 상담사에게 별점 리뷰를 작성할 수 있다
- FR24: 상담사는 고객의 채팅 요청을 수락하거나 거절할 수 있다
- FR25: 상담사는 자신의 온라인/오프라인 상태를 변경할 수 있다

### 결제 및 포인트 (Payment & Points)

- FR26: 사용자는 현재 보유 포인트 잔액을 조회할 수 있다
- FR27: 사용자는 포인트 충전 상품 목록을 조회할 수 있다
- FR28: 사용자는 신용카드로 포인트를 충전할 수 있다
- FR29: 사용자는 가상계좌로 포인트를 충전할 수 있다
- FR30: 사용자는 카카오페이/네이버페이로 포인트를 충전할 수 있다
- FR31: 시스템은 상담 진행 시 분당 요금으로 포인트를 자동 차감한다
- FR32: 사용자는 포인트 사용/충전 내역을 조회할 수 있다
- FR33: 시스템은 포인트 잔액 부족 시 상담을 자동 종료한다

### 콘텐츠 및 공지 (Content & Notices)

- FR34: 사용자는 공지사항 목록을 조회할 수 있다
- FR35: 사용자는 공지사항 상세 내용을 확인할 수 있다
- FR36: 사용자는 배너를 통해 이벤트/프로모션 정보를 확인할 수 있다
- FR37: 사용자는 1:1 문의를 작성할 수 있다
- FR38: 사용자는 자신의 문의 내역과 답변을 조회할 수 있다

### 알림 (Notifications)

- FR39: 사용자는 상담 관련 알림을 수신할 수 있다
- FR40: 사용자는 결제/포인트 관련 알림을 수신할 수 있다
- FR41: 사용자는 시스템 공지 알림을 수신할 수 있다
- FR42: 사용자는 알림 목록을 조회하고 읽음 처리할 수 있다

### 관리자 기능 (Admin)

- FR43: 관리자는 전체 회원 목록을 조회하고 검색할 수 있다
- FR44: 관리자는 회원 상세 정보와 활동 내역을 확인할 수 있다
- FR45: 관리자는 상담사 목록을 관리(승인/정지/삭제)할 수 있다
- FR46: 관리자는 상담사 신청서를 검토하고 승인/반려할 수 있다
- FR47: 관리자는 공지사항을 등록/수정/삭제할 수 있다
- FR48: 관리자는 배너를 등록/수정/삭제할 수 있다
- FR49: 관리자는 결제 내역을 조회할 수 있다
- FR50: 관리자는 1:1 문의에 답변을 작성할 수 있다
- FR51: 관리자는 AI 운세 이용 통계를 확인할 수 있다
- FR52: 관리자는 대시보드에서 핵심 지표를 확인할 수 있다

---

## Non-Functional Requirements

### Performance

**응답 시간 요구사항:**

| 구분 | 목표 | 측정 방법 |
|------|------|-----------|
| NFR-P1: API 응답시간 | p95 < 300ms | 서버 모니터링 |
| NFR-P2: AI 운세 응답 | < 3초 | OpenAI API 응답 추적 |
| NFR-P3: 채팅 메시지 RTT | < 200ms | WebSocket 모니터링 |
| NFR-P4: 페이지 초기 로드 | LCP < 2.5초 | Core Web Vitals |
| NFR-P5: 인터랙티브 시간 | TTI < 3.5초 | Lighthouse |

**리소스 요구사항:**
- NFR-P6: 초기 JS 번들 < 200KB (gzipped)
- NFR-P7: 전체 페이지 < 1MB
- NFR-P8: CLS (Cumulative Layout Shift) < 0.1

### Security

**데이터 보호:**
- NFR-S1: 모든 통신은 HTTPS(TLS 1.2+)로 암호화되어야 한다
- NFR-S2: 비밀번호는 Argon2id 알고리즘으로 해싱되어야 한다
- NFR-S3: 채팅 메시지는 AES-256-GCM으로 암호화 저장되어야 한다
- NFR-S4: 개인정보(사주 정보)는 암호화되어 저장되어야 한다

**인증 및 권한:**
- NFR-S5: JWT 토큰 만료 시간은 Access 15분, Refresh 7일이어야 한다
- NFR-S6: 인증 토큰은 HttpOnly 쿠키로 저장되어야 한다
- NFR-S7: CSRF 토큰으로 상태 변경 요청을 보호해야 한다

**API 보안:**
- NFR-S8: Rate Limiting이 적용되어야 한다 (100 req/min per IP)
- NFR-S9: CORS 정책이 허용된 도메인만 접근 가능해야 한다
- NFR-S10: SQL Injection, XSS 공격에 대한 방어가 적용되어야 한다

**결제 보안:**
- NFR-S11: 결제 정보는 PG사를 통해 처리되며 서버에 저장하지 않는다
- NFR-S12: 결제 웹훅은 서명 검증을 통해 인증되어야 한다

### Scalability

**용량 요구사항:**
- NFR-SC1: 동시 접속 사용자 500명을 지원해야 한다 (MVP 기준)
- NFR-SC2: 일일 AI 운세 요청 10,000건을 처리할 수 있어야 한다
- NFR-SC3: 동시 채팅 세션 100개를 지원해야 한다

**확장성 설계:**
- NFR-SC4: 수평 확장이 가능한 Stateless 아키텍처를 유지해야 한다
- NFR-SC5: 세션 데이터는 Redis에 저장하여 서버 간 공유되어야 한다
- NFR-SC6: 데이터베이스 연결 풀링을 사용해야 한다

### Reliability

**가용성:**
- NFR-R1: 서비스 가용성 99% 이상을 유지해야 한다
- NFR-R2: 계획된 유지보수는 사전 공지 후 진행해야 한다

**장애 복구:**
- NFR-R3: AI API 장애 시 캐시된 결과 또는 에러 메시지를 표시해야 한다
- NFR-R4: WebSocket 연결 끊김 시 자동 재연결되어야 한다 (exponential backoff)
- NFR-R5: 결제 실패 시 포인트 이중 차감이 발생하지 않아야 한다

**데이터 무결성:**
- NFR-R6: 포인트 거래는 트랜잭션으로 원자성을 보장해야 한다
- NFR-R7: 데이터베이스 백업을 일 1회 이상 수행해야 한다

### Accessibility

**WCAG 2.1 AA 준수:**
- NFR-A1: 텍스트와 배경의 명암비는 4.5:1 이상이어야 한다
- NFR-A2: 모든 인터랙티브 요소는 키보드로 접근 가능해야 한다
- NFR-A3: 포커스 표시자가 명확하게 보여야 한다
- NFR-A4: 폼 요소는 연결된 레이블이 있어야 한다
- NFR-A5: 이미지는 대체 텍스트를 제공해야 한다

**모바일 접근성:**
- NFR-A6: 터치 타겟 크기는 최소 44px × 44px이어야 한다
- NFR-A7: 200% 확대 시에도 레이아웃이 유지되어야 한다

### Integration

**외부 시스템 연동:**

| 연동 대상 | 요구사항 |
|-----------|----------|
| NFR-I1: OpenAI API | 타임아웃 10초, 실패 시 재시도 1회 |
| NFR-I2: Payletter (PG) | 웹훅 수신 후 5초 이내 응답 |
| NFR-I3: KCP (본인인증) | 인증 완료 결과 실시간 처리 |
| NFR-I4: Kakao/Naver OAuth | 토큰 만료 시 자동 갱신 |
| NFR-I5: MSSQL (ARS) | 읽기 전용 연결, 타임아웃 5초 |

**API 호환성:**
- NFR-I6: REST API는 JSON 형식을 사용해야 한다
- NFR-I7: API 버저닝(/api/v1/)을 지원해야 한다
- NFR-I8: 에러 응답은 일관된 형식을 따라야 한다

### Monitoring & Observability

**로깅:**
- NFR-M1: 모든 API 요청/응답은 구조화된 JSON 로그로 기록되어야 한다
- NFR-M2: 로그에는 요청 ID가 포함되어 추적 가능해야 한다
- NFR-M3: 민감 정보(비밀번호, 토큰)는 로그에 기록하지 않아야 한다

**모니터링:**
- NFR-M4: Sentry를 통해 에러가 실시간으로 수집되어야 한다
- NFR-M5: 핵심 지표(응답시간, 에러율)는 대시보드에서 확인 가능해야 한다

---

## Document Status

### Completion Summary
| 단계 | 상태 | 내용 |
|------|------|------|
| 1. Init | ✅ | 워크플로우 초기화 |
| 2. Discovery | ✅ | Product Brief 분석 완료 |
| 3. Success | ✅ | 성공 지표 정의 |
| 4. Journeys | ✅ | 4개 사용자 여정 문서화 |
| 5. Domain | ✅ | 도메인 분석 완료 |
| 6. Innovation | ✅ | 혁신 패턴 식별 |
| 7. Project Type | ✅ | Web Application 분류 |
| 8. Scoping | ✅ | MVP 범위 정의 |
| 9. Functional | ✅ | 52개 FR 정의 |
| 10. Non-Functional | ✅ | 35+ NFR 정의 |
| 11. Polish | ✅ | 문서 최적화 완료 |

### Requirements Summary
| 카테고리 | 수량 |
|----------|------|
| Functional Requirements (FR) | 52 |
| Non-Functional Requirements (NFR) | 35+ |
| User Journeys | 4 |

### Next Steps
1. **Architecture Workflow** - 기술 아키텍처 설계
2. **UX Design** - UI/UX 상세 설계 (선택)
3. **Epic & Story Creation** - 개발 스토리 생성

### Document Info
- **Generated**: 2026-01-15
- **Workflow**: BMAD PRD Workflow v1.0
- **Input Documents**: Product Brief, 6 Project Docs
- **Project Type**: Brownfield Web Application

