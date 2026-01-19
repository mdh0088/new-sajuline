"""
공통 데코레이터 모듈

API 에러 처리, 컨텍스트 주입 등의 데코레이터 제공
코드 중복 제거 및 일관된 처리 패턴 적용
"""

from .error_handler import handle_api_errors

__all__ = ["handle_api_errors"]