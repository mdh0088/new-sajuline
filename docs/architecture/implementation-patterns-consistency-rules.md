# Implementation Patterns & Consistency Rules

### Naming Patterns

**Database Naming (MariaDB):**
| 항목 | 규칙 | 예시 |
|------|------|------|
| 테이블 | snake_case, 복수형 | `users`, `fortune_histories` |
| 컬럼 | snake_case | `user_id`, `created_at` |
| FK | `{table}_id` | `user_id`, `counselor_id` |
| Index | `idx_{table}_{column}` | `idx_users_email` |
| Enum | PascalCase | `FortuneType`, `PaymentStatus` |

**API Naming (REST):**
| 항목 | 규칙 | 예시 |
|------|------|------|
| 엔드포인트 | 복수형, kebab-case | `/api/v1/fortunes`, `/api/v1/chat-rooms` |
| Path 파라미터 | `{param}` | `/users/{user_id}` |
| Query 파라미터 | snake_case | `?page_size=10&sort_by=created_at` |
| Request Body | snake_case | `{ "birth_date": "1990-01-01" }` |

**Code Naming:**
| 영역 | Python (Backend) | TypeScript (Frontend) |
|------|------------------|----------------------|
| 함수 | snake_case | camelCase |
| 클래스 | PascalCase | PascalCase |
| 변수 | snake_case | camelCase |
| 상수 | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE |
| 파일 | snake_case.py | PascalCase.vue, camelCase.ts |

### Structure Patterns

**Backend (FastAPI):**
```
backend/src/
├── api/v1/              # API 라우터 (엔드포인트별)
│   └── {domain}_api.py  # fortune_api.py
├── services/            # 비즈니스 로직
│   └── {domain}_service.py
├── repositories/        # 데이터 접근
│   └── {domain}_repository.py
├── models/              # SQLAlchemy 모델
│   └── {domain}_model.py
├── schemas/             # Pydantic 스키마
│   └── {domain}_schema.py
└── common/              # 공용 유틸리티
    ├── middleware/
    └── utils/
```

**Frontend (Nuxt 4):**
```
frontend/
├── pages/               # 라우트 페이지
│   └── {feature}/
│       ├── index.vue
│       └── [id].vue
├── app/
│   ├── components/      # 공용 컴포넌트
│   │   └── {Feature}/
│   │       └── {Feature}Card.vue
│   └── composables/     # Vue 컴포저블
│       └── use{Feature}.ts
├── stores/              # Pinia 스토어
│   └── {feature}.ts
└── types/               # TypeScript 타입
    └── {feature}.d.ts
```

### Format Patterns

**API Response Format:**
```json
// 성공 응답
{
  "success": true,
  "data": { ... },
  "message": "운세를 성공적으로 조회했습니다"
}

// 에러 응답
{
  "success": false,
  "error": {
    "code": "FORTUNE_NOT_FOUND",
    "message": "오늘의 운세를 찾을 수 없습니다",
    "details": null
  }
}

// 페이지네이션 응답
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 100,
    "total_pages": 5
  }
}
```

**날짜/시간 형식:**
| 용도 | 형식 | 예시 |
|------|------|------|
| API 전송 | ISO 8601 | `"2026-01-15T14:30:00Z"` |
| DB 저장 | DATETIME | `2026-01-15 14:30:00` |
| UI 표시 | 한국어 형식 | `2026년 1월 15일 (수)` |
| 운세 날짜 | YYYY-MM-DD | `"2026-01-15"` |

### Communication Patterns

**Event Naming (Socket.IO):**
```
// 클라이언트 → 서버
chat:join, chat:leave, chat:message, chat:typing

// 서버 → 클라이언트
chat:joined, chat:message_received, chat:typing_indicator
```

**State Management (Pinia):**
```typescript
// 스토어 이름: use{Feature}Store
export const useFortuneStore = defineStore('fortune', () => {
  // State: camelCase
  const dailyFortune = ref<Fortune | null>(null)
  const isLoading = ref(false)

  // Actions: 동사로 시작
  async function fetchDailyFortune() { ... }
  function clearFortune() { ... }

  return { dailyFortune, isLoading, fetchDailyFortune, clearFortune }
})
```

### Process Patterns

**에러 핸들링:**
```python
# Backend: 커스텀 예외 사용
class FortuneNotFoundError(BaseException):
    code = "FORTUNE_NOT_FOUND"
    message = "운세를 찾을 수 없습니다"

# 서비스에서 예외 발생
raise FortuneNotFoundError()

# API에서 글로벌 핸들러로 처리
@app.exception_handler(BaseException)
async def handle_app_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {...}}
    )
```

**로딩 상태:**
```typescript
// Frontend: TanStack Query 패턴
const { data, isLoading, isError, error } = useQuery({
  queryKey: ['fortune', 'daily'],
  queryFn: () => api.getFortune('daily'),
  staleTime: 1000 * 60 * 60 * 24, // 24시간
})
```

### Enforcement Guidelines

**AI Agent 필수 준수 사항:**
1. 모든 새 파일은 기존 디렉토리 구조를 따른다
2. API 응답은 반드시 표준 형식을 사용한다
3. 데이터베이스 컬럼은 snake_case로 명명한다
4. 프론트엔드 컴포넌트는 PascalCase 파일명을 사용한다
5. 에러는 커스텀 예외 클래스로 처리한다
6. 날짜는 ISO 8601 형식으로 API에 전송한다

**패턴 검증:**
- ESLint/Prettier: 코드 스타일 자동 검증
- mypy: Python 타입 검증
- API 테스트: 응답 형식 검증
- PR 리뷰: 구조 패턴 검증

---
