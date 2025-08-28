# 코드 스타일 및 컨벤션

## 전반적인 원칙 (Clean Code Guidelines 기반)

### 핵심 원칙
- **DRY**: 중복 제거를 철저히 수행
- **KISS**: 작동하는 가장 간단한 해결책
- **YAGNI**: 현재 필요한 것만 구축
- **SOLID**: 5가지 원칙을 일관되게 적용
- **Boy Scout Rule**: 발견한 코드보다 깔끔하게 남기기

## Python (Backend) 스타일

### 포매팅 도구
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

### 네이밍 컨벤션
- **클래스**: PascalCase (예: `UserService`, `AuthRepository`)
- **함수/메서드**: snake_case (예: `get_user_by_id`, `validate_token`)
- **변수**: snake_case (예: `user_data`, `api_response`)
- **상수**: UPPER_SNAKE_CASE (예: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)
- **불린**: is_/has_/can_ 접두사 (예: `is_authenticated`, `has_permission`)

### 함수/메서드 규칙
- **단일 책임**: 하나의 변경 이유만 가짐
- **최대 길이**: 20줄 (10줄 이하 선호)
- **매개변수**: 최대 3개 (더 필요시 객체 사용)
- **순수 함수**: 부작용 없음
- **조기 반환**: 중첩 조건보다 우선

### 타입 힌팅 (MyPy 설정)
```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
disallow_incomplete_defs = true
strict_equality = true
```

## TypeScript/Vue (Frontend) 스타일

### 네이밍 컨벤션
- **컴포넌트**: PascalCase (예: `UserProfile.vue`, `ChatWidget.vue`)
- **함수**: camelCase (예: `getUserData`, `validateForm`)
- **변수**: camelCase (예: `userData`, `apiResponse`)
- **상수**: UPPER_SNAKE_CASE (예: `API_BASE_URL`, `MAX_FILE_SIZE`)
- **인터페이스**: I 접두사 (예: `IUser`, `IApiResponse`)

### Vue 컴포넌트 구조
```vue
<template>
  <!-- 템플릿 -->
</template>

<script setup lang="ts">
// Composition API 사용
// 1. imports
// 2. props/emits 정의
// 3. reactive data
// 4. computed
// 5. methods
// 6. lifecycle hooks
</script>

<style scoped>
/* Tailwind 우선, 필요시 추가 스타일 */
</style>
```

## 프로젝트 구조 컨벤션

### Backend 구조 (도메인 중심)
```
backend/
├── src/
│   ├── auth/           # 인증 도메인
│   ├── user/           # 사용자 도메인
│   ├── counselor/      # 상담사 도메인
│   ├── chat/           # 채팅 도메인
│   ├── payment/        # 결제 도메인
│   └── common/         # 공통 컴포넌트
│       ├── config/
│       ├── database/
│       ├── exceptions/
│       ├── middleware/
│       └── utils/
```

### 도메인별 계층화
```
domain/
├── api/            # 라우터 (프레젠테이션)
├── services/       # 도메인 로직
├── repositories/   # 데이터 액세스
├── models/         # ORM 모델
├── schemas/        # Pydantic DTO
└── __init__.py
```

### Frontend 구조 (기능 중심)
```
frontend/
├── components/     # 재사용 컴포넌트
├── pages/          # 페이지 컴포넌트
├── composables/    # 비즈니스 로직
├── stores/         # Pinia 스토어
├── types/          # TypeScript 타입
├── utils/          # 유틸리티 함수
└── assets/         # 정적 자산
```

## Git 커밋 컨벤션

### 커밋 메시지 형식
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 타입 (필수)
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포매팅
- `refactor`: 리팩터링
- `perf`: 성능 개선
- `test`: 테스트 관련
- `chore`: 기타 작업
- `ci`: CI/CD 관련
- `build`: 빌드 관련

### 예시
```
feat(auth): add OAuth2 Google login

fix: resolve memory leak in user session cleanup

docs(api): update authentication endpoints
```

## 코멘트 및 문서화

### 코멘트 원칙
- **코드는 자체 문서화**되어야 함
- **WHY를 설명**, WHAT은 설명하지 않음
- **공개 API는 철저히 문서화**
- **주석처리된 코드는 즉시 삭제**

### Python Docstring
```python
def get_user_by_id(user_id: int) -> Optional[User]:
    """사용자 ID로 사용자 정보를 조회합니다.
    
    Args:
        user_id: 조회할 사용자의 ID
        
    Returns:
        사용자 정보 또는 None (존재하지 않을 경우)
        
    Raises:
        DatabaseError: 데이터베이스 연결 실패 시
    """
```

## 에러 처리

### 원칙
- **빠른 실패**: 명확한 메시지와 함께
- **예외 사용**: 에러 코드보다 예외 선호
- **적절한 레벨**에서 에러 처리
- **일반적인 예외 금지**: 구체적인 예외만
- **컨텍스트와 함께** 로깅

### Python 예외 처리
```python
try:
    user = await user_service.get_by_id(user_id)
except UserNotFoundError as e:
    logger.error(f"User not found: {user_id}", extra={"user_id": user_id})
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
except DatabaseError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")
```

## 테스트 컨벤션

### 테스트 원칙
- **TDD** 가능한 경우 적용
- **행위 테스트**, 구현이 아닌 동작
- **하나의 검증**만 수행
- **설명적인 테스트명**: `should_X_when_Y`
- **AAA 패턴**: Arrange, Act, Assert

### 테스트 구조
```python
class TestUserService:
    async def test_should_return_user_when_valid_id_provided(self):
        # Arrange
        user_id = 1
        expected_user = User(id=1, email="test@example.com")
        
        # Act
        result = await user_service.get_by_id(user_id)
        
        # Assert
        assert result == expected_user
```

## 성능 및 최적화

### 원칙
- **측정 후 최적화**
- **알고리즘 우선** 최적화
- **비싼 연산 캐시**
- **적절한 지연 로딩**
- **조기 최적화 방지**

## 보안 가이드라인

### 핵심 원칙
- **사용자 입력 신뢰 금지**
- **모든 입력 검증**
- **파라미터화된 쿼리** 사용
- **최소 권한 원칙**
- **종속성 최신 유지**
- **코드에 비밀 정보 금지**