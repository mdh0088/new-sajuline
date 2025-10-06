# Admin Front - 사주라인 관리자 프론트엔드

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [디렉토리 구조](#디렉토리-구조)
3. [기술 스택](#기술-스택)
4. [API 호출 흐름 분석](#api-호출-흐름-분석)
5. [HTTP 인터셉터 구조](#http-인터셉터-구조)
6. [TableOptions & SearchOptions 사용법](#tableoptions--searchoptions-사용법)
7. [공통 컴포넌트 활용](#공통-컴포넌트-활용)
8. [개발 가이드](#개발-가이드)

---

## 프로젝트 개요

**사주라인 관리자 시스템 프론트엔드**
- **프레임워크**: Vue 3.5 + Vite 5.2 + TypeScript 5.5
- **UI 라이브러리**: Element Plus 2.7 + Bootstrap 5.3
- **상태 관리**: Pinia 2.1 (Persisted State 지원)
- **빌드 도구**: Vite (개발 서버 + 프로덕션 빌드)

---

## 디렉토리 구조

```
admin-front/
├── src/
│   ├── api/                    # API 호출 레이어
│   │   ├── _config/           # HTTP 설정 및 유틸
│   │   │   ├── http.ts        # Axios 인스턴스 및 인터셉터
│   │   │   ├── http_json.ts   # JSON 전용 HTTP 클라이언트
│   │   │   └── promiseAction.ts # Promise 처리 유틸
│   │   ├── banner/            # 배너 API
│   │   ├── common/            # 공통 API
│   │   ├── counselor/         # 상담사 API
│   │   ├── customer-support/  # 고객지원 API
│   │   ├── exhibition/        # 기획전 API
│   │   ├── grade/             # 등급 API
│   │   ├── kakaoAlarm/        # 카카오 알림 API
│   │   ├── manager/           # 관리자 API
│   │   ├── mileage/           # 마일리지 API
│   │   ├── popup/             # 팝업 API
│   │   ├── product/           # 상품 API
│   │   ├── review/            # 후기 API
│   │   └── user/              # 회원 API
│   │
│   ├── assets/                # 정적 리소스
│   ├── commonUtils/           # 공통 유틸리티
│   ├── models/               # 데이터 모델 클래스
│   ├── router/               # Vue Router 설정
│   ├── store/                # Pinia 스토어
│   ├── types/                # TypeScript 타입 정의
│   ├── views/                # Vue 컴포넌트
│   │   ├── common/          # 공통 컴포넌트
│   │   │   ├── list/       # 테이블 리스트
│   │   │   ├── pagination/ # 페이지네이션
│   │   │   ├── search/     # 검색 컴포넌트
│   │   │   └── switch/     # 스위치 컴포넌트
│   │   ├── modules/         # 레이아웃 모듈
│   │   └── pages/           # 페이지 컴포넌트
│   │
│   ├── App.vue              # 루트 컴포넌트
│   └── main.ts             # 앱 진입점
│
├── .env.dev                # 개발 환경 변수
├── .env.prod               # 프로덕션 환경 변수
├── package.json            # 의존성 및 스크립트
└── vite.config.ts          # Vite 설정
```

---

## 기술 스택

### Core
- **Vue 3.5.22**: Composition API + `<script setup>` 패턴
- **TypeScript 5.5.4**: 강타입 언어 지원
- **Vite 5.2.10**: 빠른 개발 서버 및 번들러

### UI Framework
- **Element Plus 2.7.8**: 메인 UI 컴포넌트 라이브러리
- **Bootstrap 5.3.2**: 레이아웃 및 그리드 시스템

### State & Router
- **Pinia 2.1.7**: Vue 3 공식 상태 관리
- **Vue Router 4.1.6**: SPA 라우팅

### HTTP & Utils
- **Axios 1.6.5**: HTTP 클라이언트
- **SweetAlert2 11.6.13**: 모달 및 알림

---

## API 호출 흐름 분석

### 전체 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        사용자 인터랙션                            │
│                    (버튼 클릭, 검색, 페이지 변경 등)                │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      1. Vue 페이지 컴포넌트                        │
│                   (예: BannerPage.vue)                           │
│                                                                   │
│  - searchOptions, tableOptions 상태 관리                         │
│  - 사용자 이벤트 핸들러 (doSearch, createBanner 등)               │
│  - 공통 컴포넌트 사용 (CommonSearch, CommonList)                  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. 비즈니스 로직 레이어                         │
│                   (예: bannerPage.ts)                            │
│                                                                   │
│  - 페이지별 비즈니스 로직 구현                                     │
│  - promiseAction.promiseSettled() 사용                           │
│  - API 호출 및 응답 처리                                          │
│  - 상태 업데이트 (tableOptions, 알림 등)                          │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       3. API 호출 레이어                          │
│                   (예: bannerApi.ts)                             │
│                                                                   │
│  - 엔드포인트 URL 정의                                            │
│  - HTTP 메서드 래핑 (GET, POST, PATCH, DELETE)                   │
│  - FormData 처리 (파일 업로드)                                    │
│  - http 인스턴스 사용                                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. HTTP 인터셉터 레이어                         │
│                   (http.ts - Axios Instance)                     │
│                                                                   │
│  [Request Interceptor]                                           │
│  - JWT 토큰 자동 주입 (Authorization 헤더)                        │
│  - managerId 자동 추가                                            │
│  - FormData 변환 처리                                             │
│  - 캐시 방지 헤더 설정                                            │
│                                                                   │
│  [Response Interceptor]                                          │
│  - 응답 데이터 처리                                               │
│  - 에러 핸들링                                                    │
│  - 토큰 갱신 처리                                                 │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      5. Backend API Server                       │
│                    (admin-backend FastAPI)                       │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       6. 응답 처리 및 UI 업데이트                  │
│                                                                   │
│  - promiseAction에서 성공/실패 처리                               │
│  - tableOptions.items 업데이트 (목록 갱신)                        │
│  - SweetAlert2 알림 표시                                          │
│  - 페이지 리로드 또는 Drawer 닫기                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 상세 흐름 설명

#### 1️⃣ Vue 페이지 컴포넌트 (BannerPage.vue)

```typescript
// BannerPage.vue
const tableOptions = ref<TableOptions<BannerInfo>>(
  new TableOptionsClass({headers: bannerHeader})
)
const searchOptions = ref(new SearchOptionsClassList(bannerSearchOptions))

const doSearch = async (sort:string='asc', sortKey:string='') => {
  const queryParams:BannerRequest = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    type: searchOptions.value.getOptionByKey('type').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage ?? 10,
    sort: targetSort.value,
    sortKey: targetSortKey.value
  };

  await getBannerList(queryParams, tableOptions)
}
```

#### 2️⃣ 비즈니스 로직 레이어 (bannerPage.ts)

```typescript
import * as promiseAction from '@/api/_config/promiseAction';
import * as bannerApi from '@/api/banner/bannerApi';

export const getBannerList = async (queryParams, tableOptions) => {
  let requests = [];
  tableOptions.value.isLoading = true;
  requests.push(bannerApi.getBannerList(queryParams));

  const result = await promiseAction.promiseSettled(requests);
  result.forEach(data => {
    const { success, value } = data;
    if (success) {
      tableOptions.value.items = value.items;
      tableOptions.value.totalCnt = value.total_count;
      tableOptions.value.isLoading = false;
    }
  });
}
```

#### 3️⃣ API 호출 레이어 (bannerApi.ts)

```typescript
import http from '@/api/_config/http';

const proxyURL = '/api/banner';

export async function getBannerList(data) {
  return http.post(`${proxyURL}/banners`, data);
}

export async function createBanner(data, formData) {
  return http.post(`${proxyURL}/create-banner`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: { 'dataType': 'formData' },
    env: { FormData: formData }
  });
}
```

---

## HTTP 인터셉터 구조

**파일 위치**: `src/api/_config/http.ts`

### 기본 설정

```typescript
const instance = axios.create({});
instance.defaults.timeout = 120000; // 2분
instance.defaults.headers.post['Content-Type'] = 'application/json';
instance.defaults.headers.get['Cache-Control'] = 'no-cache';
```

### Request Interceptor (요청 인터셉터)

#### 1. JWT 토큰 자동 주입

```typescript
const excludedUrls = ['/api/log-in']; // 토큰 검증 제외 URL

instance.interceptors.request.use(async function (config) {
  if (!excludedUrls.includes(config.url)) {
    const userToken = sessionStorage.getItem('userToken');
    
    if (userToken) {
      config.headers.Authorization = `Bearer ${userToken}`;
    } else {
      await jwtTokenIvaild(); // 세션 만료 → 로그인 페이지
    }
  }
  return config;
});
```

#### 2. managerId 자동 추가

```typescript
const userInfo = JSON.parse(sessionStorage.getItem('userInfo'))?.value;
const getUserInfo = JSON.parse(crypto.decrypteTarget(userInfo.data));
const managerId = getUserInfo.managerId;

if (config.data && userToken) {
  config.data.managerId = managerId;
  config.data = JSON.stringify(config.data);
}
```

#### 3. FormData 처리 (파일 업로드)

```typescript
if (config.params?.dataType === 'formData') {
  let formData = config.env.FormData;
  formData.append("json_data", JSON.stringify(config.data));
  config.data = formData;
}
```

### 토큰 만료 처리

```typescript
const jwtTokenIvaild = async () => {
  const msg = '세션이 만료되었습니다. 계속하려면 다시 로그인 하세요.';
  await swal.swalConfirmWithNoCancel(msg, 'error');
  
  sessionStorage.removeItem('userToken');
  sessionStorage.removeItem('userInfo');
  location.href = '/login';
};
```

---

## TableOptions & SearchOptions 사용법

### ⚠️ 필수 조건

#### 1. 상수 선언 (Constants 파일)

**파일 위치**: `src/views/pages/{domain}/{domain}Constants.ts`

**중요**: tableOption과 searchOption 상수는 **검색 API와 목록 조회 API의 request payload와 response 데이터 구조에 정확히 맞춰** 선언해야 합니다.

**예시**: `src/views/pages/banner/bannerConstants.ts`
- `bannerHeader`: API response의 데이터 필드와 매칭
- `bannerSearchOptions`: API request의 검색 파라미터와 매칭

#### 2. 클래스 인스턴스 생성 (Vue 컴포넌트)

**필수 import**:
```typescript
import {bannerHeader, bannerSearchOptions} from "@/views/pages/banner/bannerContants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
```

**필수 선언 양식**:
```typescript
// TableOptions: 제네릭 타입 + TableOptionsClass 사용
const tableOptions = ref<TableOptions<BannerInfo>>(
  new TableOptionsClass({headers: bannerHeader})
)

// SearchOptions: SearchOptionsClassList 사용
const searchOptions = ref(new SearchOptionsClassList(bannerSearchOptions))
```

**주의사항**:
- `TableOptions<T>`: 제네릭 타입으로 데이터 모델 지정 (예: `BannerInfo`)
- `new TableOptionsClass()`: models/common.ts의 클래스 사용 필수
- `new SearchOptionsClassList()`: 배열 데이터를 자동으로 클래스 인스턴스로 변환

---

### 타입 정의 (src/types/common.ts)

```typescript
export interface Tableheader {
  value: string;           // 데이터 키 (API response 필드명과 일치)
  label: string;           // 컬럼명
  isShow: boolean;         // 표시 여부
  type: "key" | "text" | "number" | "date" | "custom";
  width?: string;
  isSortable: boolean;
  options: any;
}

export interface SearchOptions {
  key: string;             // 검색 파라미터 키 (API request와 일치)
  value: any;
  label: string;
  type: "string" | "select" | "date";
  width?: string | number;
  options: any;
}
```

### 상수 정의 (bannerContants.ts)

```typescript
export const bannerHeader: Array<Tableheader> = [
  {
    value: 'banner_idx',
    label: '인덱스',
    isShow: false,
    type: "key",
    isSortable: false
  },
  {
    value: 'showYn',
    label: '노출여부',
    isShow: true,
    type: "custom",
    isSortable: false
  }
];

export const bannerSearchOptions: Array<SearchOptions> = [
  {
    key: 'searchName',
    value: '',
    label: '키워드',
    type: 'string',
    options: {}
  },
  {
    key: 'dateValue',
    value: [],
    label: '검색기간',
    type: 'date',
    options: {
      isRange: true,
      dateType: 'date',
      format: 'yyyy-MM-dd'
    }
  }
];
```

### Vue 컴포넌트에서 사용

**전체 예시**: `src/views/pages/banner/BannerPage.vue`

```vue
<template>
  <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  <CommonList v-model:tableOptions="tableOptions" :doSearch="doSearch">
    <template v-slot:customSlot-showYn="{ data }">
      <CustomSwitch v-model:switchValue="data.showYn" />
    </template>
  </CommonList>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
// ✅ 필수 1: Constants import
import {bannerHeader, bannerSearchOptions} from "@/views/pages/banner/bannerContants"
// ✅ 필수 2: 모델 클래스 import
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"

// ✅ 필수 3: 클래스 인스턴스 생성 (정확한 양식)
const tableOptions = ref<TableOptions<BannerInfo>>(
  new TableOptionsClass({headers: bannerHeader})
)
const searchOptions = ref(new SearchOptionsClassList(bannerSearchOptions))

// doSearch 함수에서 searchOptions 값 추출
const doSearch = async () => {
  const queryParams = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    type: searchOptions.value.getOptionByKey('type').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage ?? 10
  };

  // API 호출...
}

onMounted(() => {
  doSearch();
});
</script>
```

**핵심 포인트**:
1. **Constants import**: 페이지별 상수 파일에서 header와 searchOptions 가져오기
2. **모델 클래스 import**: `TableOptionsClass`, `SearchOptionsClassList` 필수
3. **제네릭 타입**: `TableOptions<T>`에 데이터 모델 타입 지정
4. **getOptionByKey()**: searchOptions에서 값 추출 시 사용

---

## 공통 컴포넌트 활용

### 1. CommonSearch.vue - 검색 영역

```vue
<CommonSearch
  v-model:searchOptions="searchOptions"
  :doSearch="doSearch"
/>
```

### 2. CommonList.vue - 테이블 리스트

```vue
<CommonList
  v-model:tableOptions="tableOptions"
  :doSearch="doSearch"
>
  <template v-slot:customSlot-{컬럼명}="{ data }">
    <!-- 커스텀 렌더링 -->
  </template>
</CommonList>
```

### 3. CustomSwitch.vue - 토글 스위치

```vue
<CustomSwitch
  v-model:switchValue="data.showYn"
  :rowValue="data"
  :switchEvent="updateHandler"
/>
```

---

## 개발 가이드

### 개발 환경 설정

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build:prod
```

### 새 페이지 추가 가이드

#### 1. Constants 파일 생성
**파일**: `src/views/pages/{domain}/{domain}Constants.ts`

**⚠️ 중요**: API의 request/response 구조와 정확히 매칭되어야 합니다.

```typescript
// API Response 데이터 구조에 맞춰 헤더 정의
export const exampleHeader: Array<Tableheader> = [
  {
    value: 'id',              // ← API response 필드명과 일치
    label: 'ID',
    isShow: true,
    type: "key",
    isSortable: false
  },
  {
    value: 'name',            // ← API response 필드명과 일치
    label: '이름',
    isShow: true,
    type: "text",
    isSortable: true
  }
];

// API Request 파라미터 구조에 맞춰 검색 옵션 정의
export const exampleSearchOptions: Array<SearchOptions> = [
  {
    key: 'searchName',        // ← API request 파라미터명과 일치
    value: '',
    label: '키워드',
    type: 'string',
    options: {}
  },
  {
    key: 'status',            // ← API request 파라미터명과 일치
    value: 'all',
    label: '상태',
    type: 'select',
    options: {
      items: [
        { value: 'all', label: '전체' },
        { value: 'active', label: '활성' }
      ]
    }
  }
];
```

#### 2. 비즈니스 로직 파일 생성
**파일**: `src/views/pages/{domain}/{domain}Page.ts`

```typescript
import * as promiseAction from '@/api/_config/promiseAction';
import * as exampleApi from '@/api/{domain}/{domain}Api';

export const getExampleList = async (queryParams, tableOptions) => {
  let requests = [];
  tableOptions.value.isLoading = true;
  requests.push(exampleApi.getExampleList(queryParams));

  const result = await promiseAction.promiseSettled(requests);
  result.forEach(data => {
    const { success, value } = data;
    if (success) {
      tableOptions.value.items = value.items;
      tableOptions.value.totalCnt = value.total_count;
      tableOptions.value.isLoading = false;
    }
  });
}
```

#### 3. API 파일 생성
**파일**: `src/api/{domain}/{domain}Api.ts`

```typescript
import http from '@/api/_config/http';

const proxyURL = '/api/{domain}';

export async function getExampleList(data) {
  return http.post(`${proxyURL}/list`, data);
}
```

#### 4. Vue 컴포넌트 생성
**파일**: `src/views/pages/{domain}/{Domain}Page.vue`

```vue
<template>
  <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  <CommonList v-model:tableOptions="tableOptions" :doSearch="doSearch"/>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
// ✅ 필수 import
import {exampleHeader, exampleSearchOptions} from "./{domain}Constants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"

// ✅ 필수 클래스 인스턴스 생성
const tableOptions = ref<TableOptions<ExampleInfo>>(
  new TableOptionsClass({headers: exampleHeader})
)
const searchOptions = ref(new SearchOptionsClassList(exampleSearchOptions))

const doSearch = async () => {
  const queryParams = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    status: searchOptions.value.getOptionByKey('status').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage ?? 10
  };
  await getExampleList(queryParams, tableOptions)
}

onMounted(() => doSearch());
</script>
```

#### 5. 라우터 등록
**파일**: `src/router/index.ts`

```typescript
{
  path: '{domain}/{path}',
  name: '{메뉴명}',
  component: () => import("@/views/pages/{domain}/{Domain}Page.vue"),
  meta: { title: '{페이지 제목}' }
}
```

### 핵심 패턴

1. **상수 정의** → Constants.ts
2. **인스턴스 생성** → Vue 컴포넌트
3. **공통 컴포넌트 바인딩** → CommonSearch, CommonList
4. **API 호출** → promiseAction.promiseSettled()
5. **상태 업데이트** → tableOptions, searchOptions

---

## 참고 자료

- [Vue 3 공식 문서](https://vuejs.org/)
- [Element Plus 공식 문서](https://element-plus.org/)
- [Pinia 공식 문서](https://pinia.vuejs.org/)

---

Copyright © 2025 Sajuline. All rights reserved.
