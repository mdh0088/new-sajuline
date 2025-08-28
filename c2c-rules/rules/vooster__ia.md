# 사주라인 리뉴얼 MVP Information Architecture (IA)

## 1. Site Map (사이트맵)
- 홈 / 랜딩 (비로그인 가능)
  - AI 운세 프리뷰(소프트 게이트)
  - 핵심 베네핏(검증/요금/후기) 섹션
  - 추천 상담사/이벤트/공지
- AI 운세
  - 오늘의 운세 /ai/today (로그인 필요, 프리뷰는 비로그인 요약)
  - 상세 리포트 /ai/report (로그인 필요)
  - 운세 히스토리 /ai/history (로그인 필요)
- 탐색 /explore (상담사 리스트)
  - 필터/정렬(전문분야, 스타일, 가격, 응답속도, 세션시간)
  - 저장된 필터셋
- 상담사
  - 상담사 프로필 /consultants/:slug
    - 예약 /consultants/:slug/book (로그인 필요)
- 예약/결제
  - 예약 생성 /bookings/new?consultant=:id (로그인 필요)
  - 예약 상세 /bookings/:id (로그인 필요)
  - 포인트 충전 /points/checkout (로그인 필요)
  - 포인트 내역 /points/history (로그인 필요)
  - 멤버십(향후) /membership (로그인 권장)
- 상담(실시간 채팅)
  - 상담실 /chat/sessions/:id (로그인 필요)
  - 상담 요약 리포트 /chat/sessions/:id/summary (로그인 필요)
- 커뮤니티
  - 후기 /community/reviews
  - Q&A /community/qna
  - 상담사 랭킹 /community/rankings
  - 이벤트 /community/events
- 내 정보 / 계정
  - 대시보드 /account (로그인 필요)
  - 프로필 /account/profile
  - 선호도 /account/preferences
  - 즐겨찾기 /account/favorites
  - 상담/결제 히스토리 /account/history
  - 알림 설정 /account/notifications
  - 설정(보안/연결계정) /account/settings
- 고객지원
  - FAQ /support/faq
  - 챗봇 /support/chatbot
  - 1:1 문의 /support/contact
  - 공지사항 /support/notices
  - 신고 /support/report
- 인증
  - 로그인 /auth/login
  - 회원가입 /auth/signup
  - SMS 인증 /auth/verify-sms
  - 비밀번호 재설정 /auth/reset-password
- 정보/정책
  - 요금제 /pricing
  - 소개 /about
  - 이용약관 /legal/terms
  - 개인정보처리방침 /legal/privacy

반응형 고려
- 모바일: 하단 탭(홈·탐색·상담·내 정보) 중심, 주요 리스트는 1~2열 카드
- 태블릿: 2~3열 카드, 상단 앱바 + 보조 탭
- 데스크톱: 12컬럼 그리드, Topbar + LNB(서브탭) 병행

## 2. User Flow (사용자 흐름)
핵심 경험 3가지를 기준으로 대표 여정을 구체화합니다.

- 키 태스크 A: 랜딩 → AI 프리뷰 → 소프트 게이트 → 간편 가입 → 첫 액션
  1) 사용자가 랜딩에서 “AI 미리보기” 클릭
  2) 생년월일시 입력 → 3초 스켈레톤 → 요약/모자이크 결과 노출
  3) “전체 결과 보기” 클릭 시 소프트 게이트(소셜/이메일+SMS)
  4) 가입 완료 → 웰컴 포인트 노출 + 3단계 가이드(홈→예약→결제)
  5) CTA: “추천 상담사 보기” 또는 “상세 리포트 열람”로 분기

- 키 태스크 B: 상담사 매칭/예약 → 포인트 충전 → 예약 확정
  1) 탐색 /explore 진입 → 고급 필터/정렬 적용 → 후보 리스트
  2) 상담사 프로필에서 평점, 분당가, 응답속도, 가용 슬롯 확인
  3) “바로 예약” 클릭 → 바텀시트에 분당가/예상 총액/잔여 포인트/환불 규정 표시
  4) 포인트 부족 시 /points/checkout로 1탭 충전(최근 결제수단)
  5) 결제 성공 → 예약 확정 화면 및 알림 구독 유도

- 키 태스크 C: 실시간 채팅 상담 → 종료/평가 → 재방문 유도
  1) 예약 시간에 /chat/sessions/:id 진입 → 자동 연결 + 품질 인디케이터
  2) 파일 공유, /summary, /bookmark 스니펫 사용, 잔여 포인트 안내
  3) 종료 시 자동 요약 리포트 → 1문장 후기 입력(보상 포인트)
  4) 원클릭 재예약/즐겨찾기 알림 설정 → 개인화 추천 노출

예외/오류 처리
- 연결 끊김: 자동 재연결 + 상태 토스트 + 재시도 버튼
- 결제 실패: 원인별 가이드(카드/한도/네트워크) + 대체 결제수단 제안
- 인기 상담사 예약 불가: 대기알림 설정 + 유사 프로필 추천

## 3. Navigation Structure (네비게이션 구조)
전략: Topbar 중심(데스크톱/태블릿) + 모바일 하단 탭 병행, 플로팅 CTA 보조

- 글로벌 네비게이션(GNB: Topbar)
  - 좌측: 로고, 홈, AI 운세, 탐색, 커뮤니티, 고객지원, 가격
  - 우측 유틸: 검색, 알림, 포인트(잔액/충전), 프로필(로그인/아바타 드롭다운)
  - 상태: 스크롤 시 콤팩트, 포커스 링/키보드 탐색 지원

- 로컬 네비게이션(LNB: 서브탭/브레드크럼)
  - AI 운세: 오늘 · 리포트 · 히스토리 탭
  - 상담사 상세: 소개 · 후기 · 예약 탭
  - 계정: 프로필 · 선호도 · 즐겨찾기 · 히스토리 · 알림 · 설정 탭

- 모바일 하단 탭
  - 홈 · 탐색 · 상담 · 내 정보 (아이콘+라벨, 44px+ 터치 타깃)
  - 상단 앱바에 보조 액션(검색/알림/포인트)

- 플로팅 CTA
  - “상담 시작/바로 예약” 고정(스크롤 업 시 표시), 접근성 고려 ARIA 라벨 제공

- 접근성/반응형
  - 대비 4.5:1, 키보드 포커스 링, 스크린리더 레이블
  - 브레이크포인트별 메뉴 축약: 데스크톱 텍스트+아이콘, 모바일 아이콘 우선

## 4. Page Hierarchy (페이지 계층 구조)
- / (Depth 1)
  - /pricing (1)
  - /about (1)
- /ai (1)
  - /ai/today (2) [Auth]
  - /ai/report (2) [Auth]
  - /ai/history (2) [Auth]
- /explore (1)
- /consultants (1)
  - /consultants/:slug (2)
    - /consultants/:slug/book (3) [Auth]
- /bookings (1) [Auth]
  - /bookings/new (2) [Auth]
  - /bookings/:id (2) [Auth]
- /chat (1) [Auth]
  - /chat/sessions/:id (2) [Auth]
  - /chat/sessions/:id/summary (3) [Auth]
- /points (1) [Auth]
  - /points/checkout (2) [Auth]
  - /points/history (2) [Auth]
- /membership (1) (향후)
- /community (1)
  - /community/reviews (2)
  - /community/qna (2)
  - /community/rankings (2)
  - /community/events (2)
- /account (1) [Auth]
  - /account/profile (2) [Auth]
  - /account/preferences (2) [Auth]
  - /account/favorites (2) [Auth]
  - /account/history (2) [Auth]
  - /account/notifications (2) [Auth]
  - /account/settings (2) [Auth]
- /support (1)
  - /support/faq (2)
  - /support/chatbot (2)
  - /support/contact (2)
  - /support/notices (2)
  - /support/report (2)
- /auth (1)
  - /auth/login (2)
  - /auth/signup (2)
  - /auth/verify-sms (2)
  - /auth/reset-password (2)
- /legal (1)
  - /legal/terms (2)
  - /legal/privacy (2)

## 5. Content Organization (콘텐츠 구성)
| 페이지 | 핵심 콘텐츠 요소 |
|---|---|
| 홈/랜딩 | 히어로(가치제안/H1), AI 미리보기 폼, 신뢰 신호(검증배지/평점/후기 수), 추천 상담사 카드, 요금 스냅샷, 공지/이벤트, FAQ 프리뷰, CTA(상담 시작) |
| AI 오늘/리포트 | 상단 요약(고정), 섹션별 카드(연애/직장/재무), 추천 행동, 근거/참고, 공유/저장, 프리뷰 게이트(비로그인) |
| AI 히스토리 | 기간 필터, 카드형 리포트 리스트, 검색, 상세 보기 |
| 탐색(리스트) | 필터 바(전문분야/스타일/응답속도/가격/세션시간), 정렬, 저장된 필터칩, 카드 리스트(아바타, 배지, 평점, 분당가, 응답속도, 바로예약) |
| 상담사 프로필 | 헤더(이름/배지/평점/분당가), 소개/전문분야, 후기 요약/상세, 실시간 가용 슬롯, 유사 상담사 추천, 예약 버튼 |
| 예약/요약 바텀시트 | 상담사 정보, 분당가, 예상 시간 선택, 예상 총액, 잔여 포인트, 환불 규정, 결제/충전 CTA |
| 포인트 충전 | 충전 패키지, 결제수단(기억/추가), 프로모션 코드, 영수증/세금계산서(옵션), 보안 배지 |
| 상담실(채팅) | 메시지 영역 최대화, 입력창(스니펫/이모지/파일첨부), 네트워크/잔여 포인트 인디케이터, 자동 요약 패널, 북마크/핀 메모 |
| 커뮤니티(후기/Q&A/랭킹) | 탭, 리스트(무한스크롤/페이지네이션), 작성 폼(로그인 필요), 정렬/필터, 모더레이션 신고 |
| 계정 대시보드 | 오늘의 요약, 최근 상담/예약, 포인트/멤버십 상태, 퀵 액션(재예약/충전), 알림 |
| 고객지원 | FAQ(검색/카테고리, 스키마 적용), 챗봇 진입, 1:1 문의 폼, 공지사항 리스트/상세, 신고 폼 |
| 인증 | 로그인(소셜/이메일), 회원가입(단계 표시, 최소 필수: 이메일/휴대폰/생년월일시), SMS 인증, 비밀번호 재설정 |

SEO 콘텐츠 전략
- 메타 타이틀/H1: 핵심 키워드 포함(예: “AI 사주 운세, 검증 상담사 매칭 | 사주라인”)
- 스키마: BreadcrumbList, Article(리포트), FAQPage, Product(상담/패키지), LocalBusiness(상담사), Review
- 내부링크: 홈 → 탐색/AI/가격, 상담사 프로필 → 유사 상담사/후기
- 롱폼 콘텐츠: “사주 보는 법”, “상담사 선택 가이드” 블로그(향후 /learn)
- 성과요약/후기: 신뢰 신호를 상단 가시영역에 노출

## 6. Interaction Patterns (인터랙션 패턴)
- 로딩/피드백
  - 3초 내 스켈레톤, 점진적 공개, 주요 CTA 로딩 상태 명확화
- 게이트/인증
  - 소프트 게이트: 전체 결과/저장 직전 로그인 유도(모달/바텀시트)
  - 위험 액션: 2차 확인(모달) 및 OTP/SMS(환불/삭제)
- 필터/검색
  - 상단 고정 필터바, 필터칩, 저장 가능한 필터셋, 즉시 적용
  - 검색 제안(상담사 이름/전문분야), 최근 검색
- 리스트
  - 무한스크롤(모바일)/페이지네이션(데스크톱), 빈 상태 친절 카피+CTA
- 결제
  - 바텀시트 요약(모바일), 사이드 패널(데스크톱), 실패 사유 안내+재시도
- 채팅
  - 자동 재연결, 입력중 표시, 파일 퀵뷰, 잔여 포인트 경고/자동충전 토글
- 알림/토스트
  - 성공/오류/경고 3~5초, 접근성 ARIA-live 적용
- 접근성
  - 포커스 트랩(모달), 키보드 내비, 라벨/도움말 텍스트, 터치 타깃 44px+

## 7. URL Structure (URL 구조)
원칙
- SEO 친화: 소문자-kebab-case, 의미 있는 리소스명, 짧고 일관성
- 국제문자 미사용(상담사 슬러그는 영문 전사 + 아이디), HTTPS 강제, 트레일링 슬래시 미사용
- 정규화: canonical 태그, www 비사용 일원화(301)
- 파라미터: 필터/정렬은 쿼리스트링 사용, 상태 공유 가능

패턴
- 일반 목록: https://sajuline.com/explore?topic=career&style=warm&price_max=300
- 상세: https://sajuline.com/consultants/jiyun-kim-287
- AI 리포트: https://sajuline.com/ai/report?date=1993-05-21T09:30
- 예약: https://sajuline.com/bookings/new?consultant=287
- 채팅: https://sajuline.com/chat/sessions/9f3a2
- 커뮤니티: https://sajuline.com/community/reviews?sort=recent
- 계정: https://sajuline.com/account/history
- 정책: https://sajuline.com/legal/privacy

기술/SEO 고려
- Nuxt SSR + 동적 라우트 prefetch, sitemap.xml/robots.txt 구성
- Open Graph/Twitter Card: 프로필/리포트/후기 썸네일
- UTM 파라미터 유지, internal ref 파라미터는 canonical로 제거
- 404/410 처리, 오류 페이지에 검색/탐색 링크 제공

## 8. Component Hierarchy (컴포넌트 계층 구조)
글로벌 컴포넌트
- AppShell
  - Header/Topbar(GNB): 로고, GNB 메뉴, 검색, 알림, 포인트, 프로필
  - BottomTab(모바일): 홈·탐색·상담·내 정보
  - Toast/Snackbar, Modal/BottomSheet, Tooltip
  - Footer: 퀵링크(가격/지원/정책), 저작권, SNS
- Layout
  - Container(1200px), Grid(12컬럼), Section, CardGrid

데이터/표시 컴포넌트
- Card
  - ConsultantCard(아바타, 검증 배지, 평점, 분당가, 응답속도, 바로예약)
  - AICard(요약/섹션/추천행동, 그라데이션 라인/글로우)
  - ReviewCard, QnaCard, EventCard
- List/Table
  - PaginatedList, InfiniteList, StickyHeaderTable(데스크톱)
- Media
  - Avatar, Badge(Verified/Premium/New), RatingStars, Tag/Chip
- Status
  - Skeleton, EmptyState, ErrorState, LoadingSpinner

입력/폼 컴포넌트
- Input(Text/Number/DateTime), Select, Radio/Checkbox, Slider(가격 범위)
- SearchBar(자동완성), FilterBar(필터칩/저장)
- Uploader(파일/이미지), RichText(커뮤니티)
- AuthForm(로그인/가입/SMS), OTPInput

네비/피드백 컴포넌트
- Breadcrumbs, Tabs(LNB), Pagination, Stepper(가입/결제 단계)
- Toast, InlineAlert(Success/Warning/Error/Info)

페이지 전용 컴포넌트
- Hero(랜딩), TrustSignals(후기/배지/보증), PricingTable
- ProfileHeader(상담사), AvailabilityCalendar, BookingSummarySheet
- ChatRoom(MessageList, Composer, StatusBar, SummaryPanel, Memo/BookmarkPanel)
- PointsWallet(Balance, Packages, PaymentMethods), Receipt

디자인 토큰/스타일(Design Guide 준수)
- Colors: Deep Navy/Slate Gray, Accent Teal, Indigo→Teal 글로우, Semantic
- Typography: Pretendard/Inter, H1~Caption 스케일, Inter Tabular 숫자
- Spacing: 4px 베이스, Radius(버튼 12, 입력 10, 카드 12, 모달 16), Elevation 규칙

반응형 가이드
- 모바일: 카드 1~2열, 필터는 바텀시트, 예약/결제 요약 바텀시트
- 태블릿: 2~3열, 좌우 패널 레이아웃 가능
- 데스크톱: 리스트+디테일 2패널, 테이블 보기, 사이드 요약 패널

인증/접근 제어(Required + 소프트 게이트)
- 비로그인: 랜딩, AI 프리뷰(요약/모자이크), 커뮤니티 열람, 지원/정책
- 로그인 필요: AI 전체 결과/저장, 즐겨찾기, 예약/결제, 채팅, 히스토리, 계정
- 추가 인증: 결제/환불/민감 변경(SMS/OTP), 계정 삭제 시 재인증

끝.