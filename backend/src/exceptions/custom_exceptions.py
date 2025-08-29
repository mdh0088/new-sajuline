"""
사주라인 커스텀 예외 클래스들
일관된 에러 처리를 위한 공통 예외 정의
"""


class BaseAppException(Exception):
    """애플리케이션 기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """리소스를 찾을 수 없을 때 사용"""
    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다"):
        super().__init__(message, status_code=404)


class DuplicateError(BaseAppException):
    """중복 데이터가 있을 때 사용"""
    def __init__(self, message: str = "이미 존재하는 데이터입니다"):
        super().__init__(message, status_code=409)


class AuthenticationError(BaseAppException):
    """인증 실패할 때 사용"""
    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(message, status_code=401)


class ValidationError(BaseAppException):
    """데이터 검증 실패할 때 사용"""
    def __init__(self, message: str = "입력 데이터가 올바르지 않습니다"):
        super().__init__(message, status_code=400)