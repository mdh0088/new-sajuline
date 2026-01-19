"""
통합 API 성공 응답 래핑 데코레이터

역할 분리 원칙에 따라 성공 결과만 표준 Wrapper로 감싸고,
예외 처리는 전역 예외 핸들러(handlers.py)에 위임합니다.
"""

import functools
import logging
from typing import Any, Callable
from fastapi import Request

from ..response.wrapper import APIResponse, APIResponseBuilder
from ..exceptions.custom import (
    ValidationException,
    BusinessException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    ExternalServiceException
)

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """
    FastAPI 엔드포인트 함수에 적용하여 성공 결과만 표준 Wrapper로 래핑합니다.
    예외는 가로채지 않고 재발생시켜 전역 예외 핸들러가 처리하도록 위임합니다.
    요청 객체가 전달된 경우 request_id를 추출하여 성공 응답 meta에 반영합니다.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        """성공 시 결과 래핑, 실패 시 전역 핸들러 위임."""
        request_id = None
        
        # Request 객체에서 request_id 추출 시도
        try:
            for arg in args:
                if isinstance(arg, Request):
                    request_id = getattr(arg.state, 'request_id', None)
                    break
        except Exception:
            pass
        
        try:
            result = await func(*args, **kwargs)
            # 이미 APIResponse 형태면 그대로 반환
            if isinstance(result, APIResponse):
                return result
            # 일반 데이터는 성공 응답으로 래핑
            return APIResponseBuilder.success(
                data=result,
                request_id=request_id
            )
        except Exception as e:
            # 로깅만 수행하고 전역 예외 핸들러에 위임
            logger.exception(
                f"API error bubbled to global handlers: {str(e)} (type: {type(e).__name__}, request_id: {request_id})"
            )
            raise
    
    return wrapper


def handle_business_logic(func: Callable) -> Callable:
    """
    비즈니스 로직 함수에서 발생하는 예외를 표준화하여 처리하는 비동기 데코레이터입니다.
    
    ValidationException과 BusinessException이 발생하면 경고 로그를 남기고 예외를 재발생시킵니다. 그 외의 예외는 BusinessException으로 변환하여 상위로 전달합니다.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        """
        비즈니스 로직 함수에서 발생하는 예외를 표준화하여 처리하는 비동기 래퍼 함수입니다.
        
        ValidationException 또는 BusinessException이 발생하면 경고 로그를 남기고 예외를 재발생시킵니다. 그 외의 예기치 않은 예외가 발생하면 에러 로그를 남기고, 일반적인 비즈니스 로직 오류로 변환하여 BusinessException을 발생시킵니다.
        """
        try:
            return await func(*args, **kwargs)
            
        except (ValidationException, BusinessException) as e:
            logger.warning(f"Business logic validation failed: {e.message} (code: {e.error_code})")
            raise  # 상위 데코레이터에서 처리하도록 재발생
            
        except Exception as e:
            logger.error(f"Unexpected error in business logic: {str(e)} (type: {type(e).__name__})")
            raise BusinessException(
                message="비즈니스 로직 처리 중 오류가 발생했습니다.",
                error_code="BUSINESS_LOGIC_ERROR"
            ) from e
    
    return wrapper


# 하위 호환성을 위한 별칭
handle_errors = handle_api_errors 