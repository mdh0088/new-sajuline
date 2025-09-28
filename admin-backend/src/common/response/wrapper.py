"""
API Response 래퍼 및 빌더 패턴
"""
from typing import Any, Optional, Dict, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo

T = TypeVar('T')
KST = ZoneInfo("Asia/Seoul")


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    page: int = Field(description="현재 페이지")
    limit: int = Field(description="페이지당 항목 수")
    total: int = Field(description="전체 항목 수")
    total_pages: int = Field(description="전체 페이지 수")


class ResponseMeta(BaseModel):
    """응답 메타데이터"""
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=KST),
        description="응답 시간 (KST)"
    )
    request_id: Optional[str] = Field(None, description="요청 ID")
    pagination: Optional[PaginationMeta] = Field(None, description="페이지네이션 정보")


class ErrorBody(BaseModel):
    """표준 에러 본문"""
    code: str = Field(description="에러 코드")
    message: str = Field(description="에러 메시지")
    details: Optional[Any] = Field(None, description="추가 상세 정보")


class APIResponse(BaseModel, Generic[T]):
    """표준 API 응답 형식"""
    success: bool = Field(description="성공 여부")
    message: Optional[str] = Field(None, description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    error: Optional[ErrorBody] = Field(None, description="에러 정보")
    meta: Optional[ResponseMeta] = Field(None, description="메타데이터")


class APIResponseBuilder:
    """API Response 빌더 패턴"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "성공",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """성공 응답 생성"""
        meta = ResponseMeta(request_id=request_id) if request_id else ResponseMeta()

        return APIResponse(
            success=True,
            message=message,
            data=data,
            meta=meta
        )

    @staticmethod
    def error(
        message: str,
        errors: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> APIResponse:
        """에러 응답 생성"""
        meta = ResponseMeta(request_id=request_id) if request_id else ResponseMeta()

        # 에러 정보 매핑
        error_body: ErrorBody
        if errors is None:
            error_body = ErrorBody(code="ERROR", message=message)
        else:
            code = str(errors.get("code", "ERROR"))
            details: Dict[str, Any] = {}
            for k, v in errors.items():
                if k != "code":
                    details[k] = v
            error_body = ErrorBody(code=code, message=message, details=details or None)

        return APIResponse(
            success=False,
            message=message,
            data=None,
            error=error_body,
            meta=meta
        )

    @staticmethod
    def paginated(
        data: list,
        page: int,
        limit: int,
        total: int,
        message: str = "조회 성공",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """페이지네이션 응답 생성"""
        pagination = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=(total + limit - 1) // limit
        )

        meta = ResponseMeta(
            request_id=request_id,
            pagination=pagination
        )

        return APIResponse(
            success=True,
            message=message,
            data=data,
            meta=meta
        )


# 편의 함수
def ok(data: T, message: Optional[str] = None, request_id: Optional[str] = None) -> APIResponse[T]:
    """성공 응답 헬퍼"""
    return APIResponseBuilder.success(data=data, message=message, request_id=request_id)


def fail(message: str, code: str = "ERROR", details: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> APIResponse[None]:
    """실패 응답 헬퍼"""
    errors = {"code": code}
    if details:
        errors.update(details)
    return APIResponseBuilder.error(message=message, errors=errors, request_id=request_id)