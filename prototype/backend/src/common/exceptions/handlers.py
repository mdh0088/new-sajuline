"""
전역 예외 처리 핸들러

모든 예외를 일관된 형태로 처리하고 응답
보안상 중요한 정보 노출 방지
"""

import logging
from typing import Any, Dict, Optional
from enum import Enum as PyEnum

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse

from src.common.exceptions.custom import (
    BusinessException,
    AuthenticationException,
    AuthorizationException,
    AccountLockedException,
    AccountInactiveException,
    ValidationException,
    NotFoundException,
    ConflictException,
    ExternalServiceException
)

from src.common.response.wrapper import APIResponse, ErrorBody, ResponseMeta
from src.common.exceptions.error_codes import STATUS_TO_ERROR_CODE, ErrorCode

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    error_code: Optional[str],
    message: str,
    details: Any = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    표준화된 에러 응답 객체를 생성하여 반환합니다.
    """
    # 상태코드 기준 표준 에러코드 매핑 (명시된 error_code가 없으면 매핑 사용)
    mapped = STATUS_TO_ERROR_CODE.get(status_code, ErrorCode.INTERNAL_ERROR)
    code = error_code or mapped
    code_str = code.value if isinstance(code, PyEnum) else str(code)

    body = APIResponse[None](
        success=False,
        message=message,
        data=None,
        error=ErrorBody(
            code=code_str,
            message=message,
            # details는 Any 허용, list가 들어오면 그대로 전달
            details=details if details is not None else None
        ),
        meta=ResponseMeta(request_id=request_id) if request_id else ResponseMeta(),
    )
    # JSON 직렬화 안전 형태로 덤프
    return body.model_dump(mode="json")


async def business_exception_handler(
    request: Request, 
    exc: BusinessException
) -> JSONResponse:
    """
    비즈니스 로직 처리 중 발생한 예외를 표준화된 JSON 에러 응답으로 반환합니다.
    
    비즈니스 예외 발생 시 경고 로그를 남기고, 예외에 포함된 상태 코드와 상세 정보를 포함한 일관된 에러 응답을 제공합니다.
    
    Returns:
        JSONResponse: 비즈니스 예외 정보를 담은 JSON 에러 응답
    """
    logger.warning(
        "business_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "error.code": exc.error_code,
            "error.message": exc.message,
            "status_code": exc.status_code,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def authentication_exception_handler(
    request: Request, 
    exc: AuthenticationException
) -> JSONResponse:
    """
    인증 실패 시 401 Unauthorized 응답을 반환하는 FastAPI 예외 처리기입니다.
    
    클라이언트 인증에 실패한 경우 표준화된 에러 응답과 함께 'WWW-Authenticate: Bearer' 헤더를 포함하여 반환합니다.
    """
    logger.warning(
        "authentication_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "client.ip": request.client.host if request.client else None,
            "error.code": exc.error_code,
            "error.message": exc.message,
            "status_code": status.HTTP_401_UNAUTHORIZED,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=exc.error_code,
            message=exc.message,
            request_id=getattr(request.state, "request_id", None)
        ),
        headers={"WWW-Authenticate": "Bearer"}
    )


async def authorization_exception_handler(
    request: Request, 
    exc: AuthorizationException
) -> JSONResponse:
    """
    권한이 없는 요청에 대해 403 Forbidden 에러 응답을 반환합니다.
    
    Parameters:
        request (Request): 현재 요청 객체
        exc (AuthorizationException): 권한 예외 인스턴스
    
    Returns:
        JSONResponse: 표준화된 에러 정보를 담은 403 Forbidden 응답
    """
    logger.warning(
        "authorization_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "error.code": exc.error_code,
            "error.message": exc.message,
            "status_code": status.HTTP_403_FORBIDDEN,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=create_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=exc.error_code,
            message=exc.message,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    FastAPI 요청 데이터의 유효성 검사 실패 시 표준화된 에러 응답을 반환합니다.
    
    입력값이 올바르지 않은 경우 422 상태 코드와 함께 에러 코드, 메시지, 상세 검증 오류 정보를 포함한 JSON 응답을 반환합니다.
    """
    logger.warning(
        "validation_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "errors.count": len(exc.errors()),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="입력값이 올바르지 않습니다.",
            details=exc.errors(),
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """
    FastAPI의 HTTPException을 처리하여 표준화된 JSON 에러 응답을 반환합니다.
    
    HTTP 예외 발생 시 경고 로그를 남기고, 에러 코드 "HTTP_ERROR"와 함께 일관된 에러 응답을 생성합니다.
    
    Returns:
        JSONResponse: HTTP 상태 코드와 표준 에러 형식의 JSON 응답
    """
    logger.warning(
        "http_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "status_code": exc.status_code,
            "error.message": str(exc.detail),
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            error_code=None,  # 상태코드→에러코드 표준 매핑 사용
            message=str(exc.detail),
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    예상치 못한 모든 예외를 처리하여 표준화된 500 내부 서버 오류 응답을 반환합니다.
    
    FastAPI 요청 처리 중 발생하는 예기치 않은 예외를 포착하여, 민감한 정보 노출 없이 일관된 에러 응답을 제공합니다.
    
    Returns:
        JSONResponse: 500 내부 서버 오류와 표준 에러 응답 본문을 포함한 JSON 응답
    """
    logger.error(
        "unhandled_exception",
        extra={
            "http.method": request.method,
            "http.path": request.url.path,
            "exception.type": type(exc).__name__,
            "exception.message": str(exc),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message="내부 서버 오류가 발생했습니다.",
            request_id=getattr(request.state, "request_id", None)
        )
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 앱에 예외 핸들러 등록
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # 커스텀 비즈니스 예외
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(AuthorizationException, authorization_exception_handler)
    app.add_exception_handler(AccountLockedException, authorization_exception_handler)
    app.add_exception_handler(AccountInactiveException, authorization_exception_handler)
    app.add_exception_handler(ValidationException, business_exception_handler)
    app.add_exception_handler(NotFoundException, business_exception_handler)
    app.add_exception_handler(ConflictException, business_exception_handler)
    app.add_exception_handler(ExternalServiceException, business_exception_handler)
    
    # FastAPI 기본 예외
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 모든 예외 (최후의 방어선)
    app.add_exception_handler(Exception, generic_exception_handler) 