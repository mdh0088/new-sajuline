"""
사용자 정의 예외 클래스

비즈니스 로직에서 발생하는 다양한 예외 상황을 명확하게 분류
일관된 에러 처리를 위한 기반 클래스 제공
"""

from typing import Any, Dict, Optional
from fastapi import status


class BaseCustomException(Exception):
    """
    커스텀 예외의 기본 클래스
    
    모든 사용자 정의 예외는 이 클래스를 상속
    일관된 에러 구조와 로깅을 위한 기반 제공
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """예외 정보를 딕셔너리로 변환"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class BusinessException(BaseCustomException):
    """
    일반적인 비즈니스 로직 예외
    
    비즈니스 규칙 위반이나 유효하지 않은 상태에서 발생
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "BUSINESS_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, details)


class ValidationException(BaseCustomException):
    """
    입력값 검증 예외
    
    요청 데이터가 비즈니스 규칙에 맞지 않을 때 발생
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if field:
            if not details:
                details = {}
            details["field"] = field
            
        super().__init__(
            message,
            error_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details
        )


class AuthenticationException(BaseCustomException):
    """
    인증 실패 예외
    
    로그인 실패, 토큰 무효 등 인증 관련 오류
    """
    
    def __init__(
        self,
        message: str = "인증에 실패했습니다.",
        error_code: str = "AUTHENTICATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            error_code,
            status.HTTP_401_UNAUTHORIZED,
            details
        )


class AuthorizationException(BaseCustomException):
    """
    권한 부족 예외
    
    인증된 사용자이지만 특정 리소스 접근 권한이 없을 때 발생
    """
    
    def __init__(
        self,
        message: str = "해당 리소스에 접근할 권한이 없습니다.",
        error_code: str = "AUTHORIZATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            error_code,
            status.HTTP_403_FORBIDDEN,
            details
        )


class AccountLockedException(BaseCustomException):
    """
    계정 잠금 예외
    
    로그인 시도 횟수 초과 등으로 계정이 잠겼을 때 발생
    """
    
    def __init__(
        self,
        message: str = "계정이 잠겼습니다.",
        locked_until: Optional[str] = None,
        error_code: str = "ACCOUNT_LOCKED",
        details: Optional[Dict[str, Any]] = None
    ):
        if locked_until:
            if not details:
                details = {}
            details["locked_until"] = locked_until
            
        super().__init__(
            message,
            error_code,
            status.HTTP_403_FORBIDDEN,
            details
        )


class AccountInactiveException(BaseCustomException):
    """
    비활성 계정 예외
    
    계정이 비활성화되었을 때 발생
    """
    
    def __init__(
        self,
        message: str = "비활성화된 계정입니다.",
        error_code: str = "ACCOUNT_INACTIVE",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            error_code,
            status.HTTP_403_FORBIDDEN,
            details
        )


class NotFoundException(BaseCustomException):
    """
    리소스 미발견 예외
    
    요청된 리소스를 찾을 수 없을 때 발생
    """
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        error_code: str = "RESOURCE_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        if resource:
            if not details:
                details = {}
            details["resource"] = resource
            
        super().__init__(
            message,
            error_code,
            status.HTTP_404_NOT_FOUND,
            details
        )


class ConflictException(BaseCustomException):
    """
    리소스 충돌 예외
    
    중복된 데이터 생성 시도 등 충돌 상황에서 발생
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "RESOURCE_CONFLICT",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            error_code,
            status.HTTP_409_CONFLICT,
            details
        )


class ExternalServiceException(BaseCustomException):
    """
    외부 서비스 연동 예외
    
    외부 API 호출 실패, 타임아웃 등 외부 의존성 문제
    """
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if service:
            if not details:
                details = {}
            details["service"] = service
            
        super().__init__(
            message,
            error_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details
        )


class RateLimitException(BaseCustomException):
    """
    요청 빈도 제한 예외
    
    API 호출 빈도가 제한을 초과했을 때 발생
    """
    
    def __init__(
        self,
        message: str = "요청 빈도가 제한을 초과했습니다.",
        retry_after: Optional[int] = None,
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None
    ):
        if retry_after:
            if not details:
                details = {}
            details["retry_after"] = retry_after
            
        super().__init__(
            message,
            error_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
            details
        )


class PaymentException(BaseCustomException):
    """
    결제 관련 예외
    
    결제 실패, 포인트 부족 등 결제 관련 오류
    """
    
    def __init__(
        self,
        message: str,
        payment_method: Optional[str] = None,
        error_code: str = "PAYMENT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if payment_method:
            if not details:
                details = {}
            details["payment_method"] = payment_method
            
        super().__init__(
            message,
            error_code,
            status.HTTP_402_PAYMENT_REQUIRED,
            details
        )


class AIServiceException(BaseCustomException):
    """
    AI 서비스 관련 예외
    
    AI 모델 호출 실패, 응답 파싱 오류 등
    """
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        error_code: str = "AI_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if model:
            if not details:
                details = {}
            details["model"] = model
            
        super().__init__(
            message,
            error_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details
        )


class DatabaseException(BaseCustomException):
    """
    데이터베이스 관련 예외
    
    DB 연결 실패, 트랜잭션 오류 등
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if operation:
            if not details:
                details = {}
            details["operation"] = operation
            
        super().__init__(
            message,
            error_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details
        )


class CacheException(BaseCustomException):
    """
    캐시 관련 예외
    
    Redis 연결 실패, 캐시 작업 오류 등
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        error_code: str = "CACHE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        if operation:
            if not details:
                details = {}
            details["operation"] = operation
            
        super().__init__(
            message,
            error_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details
        )


# 편의를 위한 별칭들
ValidationError = ValidationException
BusinessLogicError = BusinessException
ExternalServiceError = ExternalServiceException
DatabaseError = DatabaseException
CacheError = CacheException 

# =====================
# Domain-specific exceptions (specialized codes)
# =====================

class UserNotFoundException(NotFoundException):
    def __init__(self, message: str = "사용자를 찾을 수 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, resource="user", error_code="USER_NOT_FOUND", details=details)


class AuthUnauthorizedException(AuthenticationException):
    def __init__(self, message: str = "인증이 필요합니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="AUTH_UNAUTHORIZED", details=details)


class ForbiddenException(AuthorizationException):
    def __init__(self, message: str = "접근 권한이 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="AUTH_FORBIDDEN", details=details)


class DuplicateUserIdException(ConflictException):
    def __init__(self, message: str = "이미 사용 중인 사용자 ID입니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="USER_ID_CONFLICT", details=details)


class DuplicateEmailException(ConflictException):
    def __init__(self, message: str = "이미 사용 중인 이메일입니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="EMAIL_CONFLICT", details=details)


class DuplicatePhoneException(ConflictException):
    def __init__(self, message: str = "이미 사용 중인 전화번호입니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="PHONE_CONFLICT", details=details)


class DuplicateNicknameException(ConflictException):
    def __init__(self, message: str = "이미 사용 중인 닉네임입니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="NICKNAME_CONFLICT", details=details)


class PointsInsufficientException(PaymentException):
    def __init__(self, message: str = "포인트가 부족합니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, payment_method="points", error_code="POINTS_INSUFFICIENT", details=details)


class ExternalMSSQLException(ExternalServiceException):
    def __init__(self, message: str = "MSSQL 연동 중 오류가 발생했습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, service="MSSQL", error_code="EXTERNAL_MSSQL_ERROR", details=details)


class ChatRoomNotFoundException(NotFoundException):
    def __init__(self, message: str = "채팅방을 찾을 수 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, resource="chat_room", error_code="CHAT_ROOM_NOT_FOUND", details=details)


class CounselorNotFoundException(NotFoundException):
    def __init__(self, message: str = "상담사를 찾을 수 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, resource="counselor", error_code="COUNSELOR_NOT_FOUND", details=details)