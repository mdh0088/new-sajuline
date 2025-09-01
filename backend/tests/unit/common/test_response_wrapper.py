"""
Response Wrapper 단위 테스트

API 응답 래퍼의 성공/실패/페이지네이션 응답 생성 기능을 테스트합니다.
"""
import pytest
from datetime import datetime
from src.common.response.wrapper import (
    APIResponse, APIResponseBuilder, PaginationMeta, ResponseMeta, ErrorBody,
    ok, fail
)


@pytest.mark.unit
class TestAPIResponseBuilder:
    """APIResponseBuilder 단위 테스트 클래스"""

    def test_success_response_basic(self):
        """기본 성공 응답 생성 테스트"""
        # Given
        test_data = {"message": "테스트 데이터"}
        test_message = "성공했습니다"
        
        # When
        response = APIResponseBuilder.success(data=test_data, message=test_message)
        
        # Then
        assert response.success is True
        assert response.message == test_message
        assert response.data == test_data
        assert response.error is None
        assert response.meta is not None
        assert response.meta.timestamp is not None

    def test_success_response_with_request_id(self):
        """요청 ID가 포함된 성공 응답 테스트"""
        # Given
        test_data = {"key": "value"}
        request_id = "test-request-123"
        
        # When
        response = APIResponseBuilder.success(data=test_data, request_id=request_id)
        
        # Then
        assert response.success is True
        assert response.meta.request_id == request_id

    def test_success_response_default_message(self):
        """기본 메시지가 적용되는 성공 응답 테스트"""
        # Given
        test_data = {"test": True}
        
        # When
        response = APIResponseBuilder.success(data=test_data)
        
        # Then
        assert response.message == "성공"

    def test_error_response_basic(self):
        """기본 에러 응답 생성 테스트"""
        # Given
        error_message = "에러가 발생했습니다"
        
        # When
        response = APIResponseBuilder.error(message=error_message)
        
        # Then
        assert response.success is False
        assert response.message == error_message
        assert response.data is None
        assert response.error is not None
        assert response.error.code == "ERROR"
        assert response.error.message == error_message
        assert response.error.details is None

    def test_error_response_with_details(self):
        """상세 정보가 포함된 에러 응답 테스트"""
        # Given
        error_message = "유효성 검사 실패"
        error_details = {
            "code": "VALIDATION_ERROR",
            "field": "email",
            "reason": "잘못된 이메일 형식"
        }
        
        # When
        response = APIResponseBuilder.error(message=error_message, errors=error_details)
        
        # Then
        assert response.success is False
        assert response.error.code == "VALIDATION_ERROR"
        assert response.error.details["field"] == "email"
        assert response.error.details["reason"] == "잘못된 이메일 형식"

    def test_error_response_with_request_id(self):
        """요청 ID가 포함된 에러 응답 테스트"""
        # Given
        error_message = "서버 에러"
        request_id = "error-request-456"
        
        # When
        response = APIResponseBuilder.error(message=error_message, request_id=request_id)
        
        # Then
        assert response.meta.request_id == request_id

    def test_paginated_response_basic(self):
        """기본 페이지네이션 응답 테스트"""
        # Given
        test_data = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]
        page = 1
        limit = 10
        total = 25
        
        # When
        response = APIResponseBuilder.paginated(
            data=test_data, page=page, limit=limit, total=total
        )
        
        # Then
        assert response.success is True
        assert response.data == test_data
        assert response.message == "조회 성공"
        assert response.meta.pagination is not None
        assert response.meta.pagination.page == page
        assert response.meta.pagination.limit == limit
        assert response.meta.pagination.total == total
        assert response.meta.pagination.total_pages == 3  # ceil(25/10)

    def test_paginated_response_edge_cases(self):
        """페이지네이션 가장자리 케이스 테스트"""
        # Given - 정확히 나누어 떨어지는 경우
        test_data = []
        page = 5
        limit = 5
        total = 25
        
        # When
        response = APIResponseBuilder.paginated(
            data=test_data, page=page, limit=limit, total=total
        )
        
        # Then
        assert response.meta.pagination.total_pages == 5  # 정확히 나누어 떨어짐

    def test_paginated_response_zero_total(self):
        """총 개수가 0인 경우 페이지네이션 테스트"""
        # Given
        test_data = []
        page = 1
        limit = 10
        total = 0
        
        # When
        response = APIResponseBuilder.paginated(
            data=test_data, page=page, limit=limit, total=total
        )
        
        # Then
        assert response.meta.pagination.total_pages == 0

    def test_paginated_response_with_custom_message(self):
        """커스텀 메시지가 포함된 페이지네이션 응답 테스트"""
        # Given
        test_data = [{"id": 1}]
        custom_message = "사용자 목록 조회 완료"
        
        # When
        response = APIResponseBuilder.paginated(
            data=test_data, page=1, limit=10, total=1, message=custom_message
        )
        
        # Then
        assert response.message == custom_message


@pytest.mark.unit
class TestConvenienceFunctions:
    """편의 함수 테스트 클래스"""

    def test_ok_function_basic(self):
        """ok() 편의 함수 기본 테스트"""
        # Given
        test_data = {"result": "success"}
        
        # When
        response = ok(test_data)
        
        # Then
        assert response.success is True
        assert response.data == test_data

    def test_ok_function_with_message(self):
        """메시지가 포함된 ok() 함수 테스트"""
        # Given
        test_data = {"user_id": "12345"}
        custom_message = "사용자 생성 완료"
        
        # When
        response = ok(test_data, message=custom_message)
        
        # Then
        assert response.message == custom_message

    def test_fail_function_basic(self):
        """fail() 편의 함수 기본 테스트"""
        # Given
        error_message = "처리 실패"
        
        # When
        response = fail(error_message)
        
        # Then
        assert response.success is False
        assert response.message == error_message
        assert response.error.code == "ERROR"

    def test_fail_function_with_code(self):
        """에러 코드가 포함된 fail() 함수 테스트"""
        # Given
        error_message = "유효하지 않은 요청"
        error_code = "INVALID_REQUEST"
        
        # When
        response = fail(error_message, code=error_code)
        
        # Then
        assert response.error.code == error_code

    def test_fail_function_with_details(self):
        """상세 정보가 포함된 fail() 함수 테스트"""
        # Given
        error_message = "필드 검증 실패"
        error_code = "VALIDATION_FAILED"
        details = {"field": "password", "min_length": 8}
        
        # When
        response = fail(error_message, code=error_code, details=details)
        
        # Then
        assert response.error.code == error_code
        assert response.error.details["field"] == "password"
        assert response.error.details["min_length"] == 8


@pytest.mark.unit
class TestResponseMetaAndPagination:
    """응답 메타데이터와 페이지네이션 모델 테스트"""

    def test_response_meta_creation(self):
        """ResponseMeta 생성 테스트"""
        # When
        meta = ResponseMeta()
        
        # Then
        assert meta.timestamp is not None
        assert isinstance(meta.timestamp, datetime)
        assert meta.request_id is None
        assert meta.pagination is None

    def test_response_meta_with_request_id(self):
        """요청 ID가 포함된 ResponseMeta 테스트"""
        # Given
        request_id = "test-123"
        
        # When
        meta = ResponseMeta(request_id=request_id)
        
        # Then
        assert meta.request_id == request_id

    def test_pagination_meta_creation(self):
        """PaginationMeta 생성 테스트"""
        # Given
        page = 2
        limit = 15
        total = 100
        
        # When
        pagination = PaginationMeta(
            page=page, limit=limit, total=total, 
            total_pages=(total + limit - 1) // limit
        )
        
        # Then
        assert pagination.page == page
        assert pagination.limit == limit
        assert pagination.total == total
        assert pagination.total_pages == 7  # ceil(100/15)

    def test_error_body_creation(self):
        """ErrorBody 생성 테스트"""
        # Given
        code = "AUTH_FAILED"
        message = "인증에 실패했습니다"
        details = {"reason": "invalid_token"}
        
        # When
        error = ErrorBody(code=code, message=message, details=details)
        
        # Then
        assert error.code == code
        assert error.message == message
        assert error.details == details