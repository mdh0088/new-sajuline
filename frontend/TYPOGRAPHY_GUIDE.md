# 사주라인 타이포그래피 가이드

## 폰트 크기 시스템

작은 화면(400px 이하)에서 일관된 사용자 경험을 위한 통일된 폰트 크기 시스템입니다.

---

## 📏 폰트 레벨 체계

### 타이틀 레벨

| 레벨 | 크기 | CSS 변수 | 사용 예시 | 클래스명 |
|------|------|----------|----------|----------|
| **Display** | 22px | `--font-size-display` | 메인 페이지 큰 타이틀 | `.page-title`, `.mileage-page-title` |
| **H1** | 20px | `--font-size-h1` | 페이지 타이틀 | `.auth-title`, `.content-title` |
| **H2** | 18px | `--font-size-h2` | 섹션 타이틀 | `.section-title`, `.header-title` |
| **H3** | 16px | `--font-size-h3` | 서브 타이틀 | `.sub-title`, `.category-title` |
| **H4** | 15px | `--font-size-h4` | 작은 타이틀 | `.item-title`, `.counselor-name-small` |
| **H5** | 14px | `--font-size-h5` | 미니 타이틀 | `.mini-title`, `.search-title` |

### 본문 레벨

| 레벨 | 크기 | CSS 변수 | 사용 예시 | 클래스명 |
|------|------|----------|----------|----------|
| **Body Large** | 14px | `--font-size-body-large` | 큰 본문, 버튼, 입력 필드 | `.input-field`, `.button-text` |
| **Body** | 13px | `--font-size-body` | 기본 본문 텍스트 | `.description-text`, `.content-body` |
| **Body Small** | 12px | `--font-size-body-small` | 작은 본문, 보조 정보 | `.helper-text`, `.notice-text` |
| **Caption** | 11px | `--font-size-caption` | 캡션, 뱃지 (최소 크기) | `.tag-small`, `.badge-text` |

---

## 🎯 사용 원칙

### 1. 최소 폰트 크기
- **11px**이 최소 크기입니다
- 캡션, 뱃지, 작은 라벨에만 사용
- 가독성이 중요한 경우 12px 이상 사용

### 2. 기본 본문 크기
- **12-13px**을 기본 본문으로 사용
- 13px: 주요 설명, 일반 텍스트
- 12px: 보조 정보, 작은 설명

### 3. 타이틀 크기
- **18-22px** 범위 사용
- 22px: 메인 페이지 큰 타이틀
- 20px: 일반 페이지 타이틀
- 18px: 섹션 타이틀 (레이아웃이 좁은 경우)

### 4. 반응형 조정
- 20px 이상 타이틀이 너무 커 보이면 18px로 조정
- 레이아웃과 컨텐츠 양을 고려하여 선택

---

## 💻 코드 사용법

### CSS 변수 사용

```css
/* 올바른 사용 */
.my-title {
    font-size: var(--font-size-h2);
}

.my-text {
    font-size: var(--font-size-body);
}

/* 지양: 하드코딩 */
.my-title {
    font-size: 18px; /* ❌ */
}
```

### 클래스 사용

```html
<!-- 타이틀 -->
<h1 class="page-title">사주라인</h1>
<h2 class="section-title">인기 상담사</h2>

<!-- 본문 -->
<p class="description-text">상담사 설명...</p>
<span class="helper-text">보조 정보</span>
<span class="badge-text">뱃지</span>

<!-- 버튼 -->
<button class="button-text">상담하기</button>
```

---

## 📱 컴포넌트별 적용

### 1. 헤더
```css
.header-title          /* 18px - 섹션 타이틀 */
.logo                  /* 20px - 로고 텍스트 */
.icon-btn              /* 18px - 아이콘 */
```

### 2. 카드 (상담사, 상품 등)
```css
.counselor-name-small  /* 15px - 이름 */
.counselor-code        /* 11px - 코드 */
.counselor-specialty   /* 13px - 전문 분야 */
.counselor-desc        /* 13px - 설명 */
.tag-small             /* 11px - 태그 */
.price-amount          /* 15px - 가격 */
.rating-score          /* 13px - 평점 */
```

### 3. 폼
```css
.input-field           /* 14px - 입력 필드 */
.input-label           /* 13px - 라벨 */
.button-text           /* 14px - 버튼 */
.helper-text           /* 12px - 도움말 */
.error-message         /* 12px - 에러 */
```

### 4. 리스트
```css
.list-item-title       /* 15px - 아이템 제목 */
.list-item-description /* 13px - 아이템 설명 */
.list-item-date        /* 12px - 날짜 */
```

### 5. 모달
```css
.modal-title           /* 18px - 모달 제목 */
.modal-subtitle        /* 13px - 모달 부제목 */
.modal-content-text    /* 13px - 모달 내용 */
.modal-button          /* 14px - 모달 버튼 */
```

---

## 🔍 특수 케이스

### 가격 표시
```css
.current-point .point-value    /* 30px - 현재 포인트 (강조) */
.profile-mileage-amount        /* 20px - 마일리지 */
.counselor-price-small         /* 15px - 상담 가격 */
.mileage-price-amount          /* 17px - 마일리지 가격 */
```

### 아이콘
```css
.icon-btn                      /* 18px - 일반 아이콘 */
.nav-icon                      /* 20px - 네비게이션 아이콘 */
.search-icon                   /* 18px - 검색 아이콘 */
```

---

## ✅ 체크리스트

새로운 컴포넌트를 만들 때:

- [ ] 타이틀은 18-22px 범위 사용
- [ ] 본문은 12-13px 사용
- [ ] 최소 크기는 11px 유지
- [ ] CSS 변수 사용 (`var(--font-size-*)`)
- [ ] 적절한 클래스명 사용
- [ ] 400px 이하 화면에서 테스트

---

## 🚫 피해야 할 것

❌ **하드코딩된 폰트 크기**
```css
/* 나쁜 예 */
.my-text {
    font-size: 14px;
}
```

❌ **11px 이하 크기**
```css
/* 나쁜 예 */
.tiny-text {
    font-size: 10px; /* 가독성 저하 */
}
```

❌ **불규칙한 크기**
```css
/* 나쁜 예 */
.weird-size {
    font-size: 13.5px; /* 시스템에 없는 크기 */
}
```

❌ **미디어 쿼리 누락**
```css
/* 나쁜 예 - 400px 이하에서만 적용되어야 함 */
.my-title {
    font-size: var(--font-size-h2);
}

/* 좋은 예 */
@media (max-width: 400px) {
    .my-title {
        font-size: var(--font-size-h2);
    }
}
```

---

## 📦 파일 구조

```
frontend/assets/css/
├── main.css          # 글로벌 CSS 변수 정의
├── typography.css    # 통일된 폰트 시스템 (자동 적용)
└── [page].css       # 페이지별 CSS (필요시 오버라이드)
```

---

## 🔄 업데이트 방법

### 전역 폰트 크기 변경
`main.css`에서 CSS 변수 수정:

```css
@media (max-width: 400px) {
    :root {
        --font-size-h2: 18px; /* 섹션 타이틀 크기 변경 */
    }
}
```

### 특정 컴포넌트만 변경
해당 컴포넌트 CSS 파일에서:

```css
@media (max-width: 400px) {
    .special-title {
        font-size: var(--font-size-h3) !important; /* H2 → H3로 변경 */
    }
}
```

---

## 💡 팁

1. **일관성 유지**: 같은 역할의 요소는 같은 폰트 크기 사용
2. **계층 구조**: 정보의 중요도에 따라 폰트 크기 차별화
3. **가독성 우선**: 작은 화면에서도 읽기 쉽게
4. **테스트 필수**: 실제 기기에서 확인
5. **CSS 변수 활용**: 유지보수 용이

---

## 📞 문의

타이포그래피 시스템 관련 문의사항은 프론트엔드 팀에 문의해 주세요.

**마지막 업데이트**: 2025-01-12
