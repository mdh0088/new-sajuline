# Web Application Specific Requirements

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
