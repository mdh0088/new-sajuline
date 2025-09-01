# 사주라인 API 아키텍처 가이드

## 개요
사주라인 프로젝트의 FastAPI 기반 백엔드 API 개발 시 준수해야 할 아키텍처 패턴과 코드 규격을 정의합니다.

## 디렉터리 구조 및 역할

```
backend/src/
├── api/v1/          # API 엔드포인트 (컨트롤러)
├── schemas/         # Pydantic 스키마 (Request/Response)
├── models/          # SQLAlchemy 모델 (DB 테이블)
├── services/        # 비즈니스 로직 (서비스 계층)
├── repositories/    # 데이터 액세스 (리포지토리 패턴)
├── common/          # 공통 유틸리티 (응답, 로깅, 미들웨어)
├── exceptions/      # 커스텀 예외 클래스
├── config/          # 설정 파일
└── core/           # 데이터베이스 연결 등 핵심 설정
```

## 스키마 (Pydantic) 작성 규칙

### 1. 네이밍 컨벤션
- **Base**: `UserBase` - 공통 필드를 담는 기본 스키마
- **Create**: `UserCreate`, `UserSignup` - 생성/등록 요청 스키마  
- **Update**: `UserUpdate` - 수정 요청 스키마
- **Response**: `UserResponse` - 응답 스키마
- **Request**: `LoginRequest` - 특별한 액션 요청 스키마

### 2. 필드 정의 패턴
```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class UserBase(BaseModel):
    """공통 필드를 담는 기본 스키마"""
    email: EmailStr = Field(..., description="이메일")
    nickname: str = Field(..., min_length=2, max_length=50, description="닉네임")
    phone: str = Field(..., min_length=1, max_length=15, description="전화번호")
    # Enum 사용 권장
    gender: Optional[Gender] = Field(None, description="성별")
    join_type: JoinType = Field(default=JoinType.COMMON, description="가입 유형")

class UserResponse(UserBase):
    """응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    created_at: datetime = Field(..., description="생성일시")
    
    # SQLAlchemy 모델과 연동
    model_config = ConfigDict(from_attributes=True)
```

### 3. Enum 활용
```python
from enum import Enum

class JoinType(str, Enum):
    COMMON = "COMMON"
    KAKAO = "KAKAO" 
    NAVER = "NAVER"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
```

### 4. Validation 패턴
- **이메일**: `EmailStr` 사용
- **전화번호**: `min_length=1, max_length=15` (유연한 형식)
- **패스워드**: `min_length=8, max_length=128`
- **ID**: `min_length=4, max_length=20`
- **닉네임**: `min_length=2, max_length=50`

## 모델 (SQLAlchemy) 작성 규칙

### 1. 기본 구조
```python
from sqlalchemy import String, DateTime, Boolean, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """사용자 정보 테이블"""
    
    __tablename__ = "t_user"
    
    # 기본키
    user_id: Mapped[str] = mapped_column(
        String(100), 
        primary_key=True, 
        comment="사용자 ID"
    )
    
    # 필수 필드
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="이메일"
    )
    
    # 선택 필드
    phone: Mapped[Optional[str]] = mapped_column(
        String(15), 
        nullable=True,
        comment="전화번호"
    )
    
    # 타임스탬프 (표준)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        default=datetime.utcnow,
        comment="생성일시"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        onupdate=datetime.utcnow,
        comment="수정일시"
    )
    
    # 인덱스 및 제약조건
    __table_args__ = (
        Index('idx_user_status', 'user_status'),
        CheckConstraint(
            "user_status IN ('ACTIVE','DORMANT','WITHDRAWN')",
            name='chk_user_status'
        ),
        {'comment': '사용자 정보'}
    )
```

## 서비스 (Business Logic) 작성 규칙

### 1. 클래스 구조
```python
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import NotFoundError, DuplicateError

class UserService:
    """사용자 비즈니스 로직 서비스"""
    
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """사용자 생성 비즈니스 로직"""
        log = get_logger_with_request_id()
        log.info("Creating new user", user_id=user_data.user_id)
        
        # 1. 유효성 검사
        await self._validate_user_creation(user_data)
        
        # 2. 비즈니스 로직 수행
        user = await self.user_repo.create(user_data)
        
        # 3. 응답 생성
        log.info("User created successfully", user_id=user.user_id)
        return UserResponse.model_validate(user)
```

### 2. 로깅 패턴
```python
log = get_logger_with_request_id()
log.info("Operation started", key_field=value)
log.warning("Warning occurred", details=details)
log.error("Error occurred", error=str(e))
```

### 3. 예외 처리
```python
# 표준 예외 사용
raise NotFoundError("사용자를 찾을 수 없습니다.")
raise DuplicateError("이미 존재하는 사용자 ID입니다.")
raise ValidationError("유효하지 않은 입력입니다.")
raise AuthenticationError("인증에 실패했습니다.")
```

## API 엔드포인트 작성 규칙

### 1. 라우터 구조
```python
from fastapi import APIRouter, Depends, Request, Response, status
from src.common.response import APIResponse, ok, fail
from src.common.middleware.rate_limit import limiter

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/signup", 
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="사용자 회원가입",
    description="이메일과 비밀번호로 새 계정을 생성합니다.",
    responses={
        201: {"description": "회원가입 성공"},
        400: {"description": "중복된 사용자 정보"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("3/hour")  # Rate Limiting
async def signup(
    request: Request,  # Rate Limiting 필수
    signup_data: UserSignup,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """사용자 회원가입"""
    result = await user_service.signup(signup_data)
    return ok(data=result, message="회원가입이 완료되었습니다.")
```

### 2. Dependency Injection 패턴
```python
def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    return UserRepository(db)

def get_auth_service() -> AuthService:
    return AuthService()

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserService:
    return UserService(user_repo, auth_service)
```

### 3. 응답 래핑 패턴
```python
from src.common.response import APIResponse, ok, fail

# 성공 응답
return ok(data=result, message="작업이 완료되었습니다.")

# 실패 응답 (일반적으로 예외 핸들러에서 처리)
return fail(message="오류가 발생했습니다.", status_code=400)
```

### 4. Rate Limiting 적용
```python
# 회원가입: 시간당 3회
@limiter.limit("3/hour")

# 로그인: 분당 15회  
@limiter.limit("15/minute")

# 인증: 분당 10회
@limiter.limit("10/minute")

# 일반 조회: 분당 60회
@limiter.limit("60/minute")
```

## 데이터베이스 연동 규칙

### 1. 세션 관리
```python
from src.core.database import get_db_maria

# API에서 세션 주입
@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db_maria)):
    pass

# Repository에서 세션 사용
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
```

### 2. 트랜잭션 처리
```python
# 자동 커밋 (기본)
user = await self.user_repo.create(user_data)

# 수동 트랜잭션 (복잡한 로직)
async with self.db.begin():
    user = await self.user_repo.create(user_data)
    await self.other_repo.create_related(user.user_id)
```

## 보안 및 성능 가이드

### 1. 입력 검증
- Pydantic 스키마로 1차 검증
- 서비스 계층에서 비즈니스 로직 검증
- SQL Injection 방지 (SQLAlchemy ORM 사용)

### 2. 인증/인가
```python
# JWT 토큰 생성
access_token = self.auth_service.create_access_token(
    user_id=user.user_id,
    email=user.email,
    role="user"
)

# HttpOnly 쿠키 설정
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,
    samesite="lax",
    max_age=30 * 60
)
```

### 3. 민감 데이터 처리
- 비밀번호: bcrypt 해싱
- PII 데이터: 로깅 시 마스킹
- API 키: 환경변수로 관리

## 테스트 및 문서화

### 1. API 문서화
- FastAPI 자동 문서화 활용
- 각 엔드포인트에 `summary`, `description` 필수
- `responses`로 에러 케이스 명시

### 2. 에러 응답 표준화
```python
{
    "success": false,
    "message": "오류 메시지",
    "error_code": "USER_NOT_FOUND",
    "details": {...}
}
```

## 코드 품질 도구

### 1. 필수 검사 (코드 작성 후)
```bash
# 포매팅
black src/ && isort src/

# 린팅 + 타입 체크  
flake8 src/ && mypy src/

# 테스트 + 커버리지
pytest --cov=src tests/
```

### 2. Git 커밋 전 체크리스트
- [ ] 위 품질 검사 모두 통과
- [ ] API 문서 업데이트 확인
- [ ] 로깅 적절히 추가
- [ ] Rate Limiting 적용
- [ ] 예외 처리 완료

---

**이 가이드를 따라 일관된 API를 개발하여 코드 품질과 유지보수성을 확보합니다.**