# 로깅 패턴 가이드라인 (Logging Guidelines)

## 기본 원칙

- **Loguru 기반**: `@logger.catch` 데코레이터로 자동 예외 처리
- **Request ID 추적**: 모든 요청에 대한 상관관계 추적 유지
- **레이어별 차별화**: 메서드 중요도에 따른 로깅 레벨 구분
- **단순성 우선**: 복잡한 로깅 로직 지양, 비즈니스 로직에 집중

## 로깅 패턴 규칙

### 1. 단순 패턴 (@logger.catch만)

**적용 대상**:
- Repository 레이어의 단순 CRUD 메서드 (get_by_id, exists_by_email 등)
- Service 레이어의 단순 조회/검증 메서드
- 별도의 비즈니스 로깅이 불필요한 작업
- 내부적으로만 사용되는 헬퍼 메서드

```python
@logger.catch
async def get_by_id(self, user_id: str) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()

@logger.catch
async def exists_by_email(self, email: str) -> bool:
    stmt = select(User.user_id).where(User.email == email)
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none() is not None
```

### 2. 상세 패턴 (@logger.catch + get_logger_with_request_id)

**적용 대상**:
- **API 엔드포인트**: 사용자 대면 기능 (로그인, 회원가입 등)
- **중요한 비즈니스 프로세스**: 사용자 생성, 인증, 결제 등
- **외부 시스템 연동**: AI API, 소셜 로그인, 결제 서비스 등
- **데이터 변경 작업**: CREATE, UPDATE, DELETE 등 중요한 상태 변경
- **감사/추적 필요**: 보안, 컴플라이언스 관련 작업

```python
@logger.catch
async def create_user(self, user_data: UserCreate) -> UserResponse:
    log = get_logger_with_request_id()
    log.info("Creating new user", user_id=user_data.user_id, email=user_data.email)
    
    # 중복 검증
    if await self.user_repo.exists_by_user_id(user_data.user_id):
        log.warning("User ID already exists", user_id=user_data.user_id)
        raise DuplicateError("이미 존재하는 사용자 ID입니다.")
    
    # 사용자 생성 로직
    user = await self.user_repo.create(user_data, password_hash)
    
    log.info("User created successfully", user_id=user.user_id, email=user.email)
    return UserResponse.model_validate(user)

@router.post("/login")
@logger.catch
async def login(request: LoginRequest, user_service: UserService = Depends(get_user_service)):
    log = get_logger_with_request_id()
    log.info("Login attempt", user_id=request.user_id)
    
    # 로그인 로직
    access_token, user_response = await user_service.login(request.user_id, request.password)
    
    log.info("Authentication successful", user_id=user_response.user_id)
    return ok(data=login_data, message="로그인 성공")
```

## Import 패턴

```python
# 모든 로깅 관련 import는 통일
from src.common.logging import logger, get_logger_with_request_id
```

## 로깅 메시지 규칙

### 성공 로그
```python
log.info("User created successfully", user_id=user.user_id, email=user.email)
log.info("Login successful", user_id=user_response.user_id)
log.info("Payment processed", order_id=order.id, amount=payment.amount)
```

### 경고 로그 (비즈니스 룰 위반)
```python
log.warning("User ID already exists", user_id=user_data.user_id)
log.warning("Authentication failed", identifier=user_id_or_email, reason="invalid_password")
log.warning("Account locked", user_id=user.user_id, locked_until=user.locked_until)
```

### 에러 로그 (자동 처리)
- `@logger.catch`가 모든 예외를 자동으로 ERROR 레벨로 로깅
- 수동으로 error 로그를 작성하지 않음

## 금지 사항

### ❌ 사용 금지
```python
# 수동 try-catch (이미 @logger.catch가 처리)
try:
    result = await some_method()
except Exception as e:
    logger.error(f"Failed: {e}")
    raise

# 시간 측정 (불필요한 복잡성)
start_time = time.time()
# ... logic
duration_ms = (time.time() - start_time) * 1000

# 복잡한 이벤트 클래스
ServiceEvents.business_operation_started("create_user", ...)
```

### ❌ 민감 정보 로깅 금지
```python
# 절대 로깅하면 안 되는 정보
log.info("User login", password=password)  # ❌
log.info("API call", token=access_token)   # ❌
log.info("Payment", card_number=card_num)  # ❌
```

### ✅ 올바른 민감 정보 처리
```python
log.info("User login", user_id=user_id)  # ✅ 
log.info("API call authenticated", user_id=user_id)  # ✅
log.info("Payment processed", amount=amount, currency="KRW")  # ✅
```

## 레이어별 적용 예시

### Repository Layer (주로 단순 패턴)
```python
class UserRepository:
    @logger.catch  # 단순 조회
    async def get_by_id(self, user_id: str) -> Optional[User]:
        # ...

    @logger.catch  # 상세 패턴: 중요한 데이터 생성
    async def create(self, user_data: UserCreate, password_hash: str) -> User:
        log = get_logger_with_request_id()
        log.info("Creating user record", user_id=user_data.user_id)
        # ...
        log.info("User record created", user_id=user.user_id)
```

### Service Layer (주로 상세 패턴)
```python
class UserService:
    @logger.catch  # 상세 패턴: 중요한 비즈니스 로직
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        log = get_logger_with_request_id()
        # ...

    @logger.catch  # 단순 패턴: 단순 조회
    async def get_user(self, user_id: str) -> UserResponse:
        # ...
```

### API Layer (모두 상세 패턴)
```python
@router.post("/users")
@logger.catch  # 항상 상세 패턴
async def create_user(request: UserCreate):
    log = get_logger_with_request_id()
    # ...
```

## 로그 분석 및 모니터링

### Request ID를 통한 추적
```bash
# 특정 요청의 전체 흐름 추적
grep "abc-123-def" logs/app.log

# 로그인 실패 패턴 분석  
grep "Authentication failed" logs/app.log | grep $(date +%Y-%m-%d)
```

### 구조화된 로그 활용
- Request ID 기반 상관관계 분석
- 에러 패턴 자동 감지
- 성능 지표 추출
- 사용자 행동 분석

이 가이드라인을 통해 일관성 있고 효율적인 로깅 시스템을 구축하여 디버깅, 모니터링, 분석을 용이하게 합니다.