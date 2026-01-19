"""
API Response 래퍼 및 빌더 패턴

모든 API 응답을 표준화된 형식으로 통일
프론트엔드에서 예측 가능한 응답 구조 제공
"""

from typing import Any, Optional, Dict, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo

T = TypeVar('T')
KST = ZoneInfo("Asia/Seoul")  # 이름 포함, DST 자동 처리

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
        """
        일반적인 성공 API 응답을 생성하여 반환합니다.
        
        Parameters:
            data: 응답에 포함할 데이터 객체 (선택 사항)
            message: 성공 메시지 (기본값: "성공")
            request_id: 요청 식별자 (선택 사항)
        
        Returns:
            APIResponse: 성공 상태, 메시지, 데이터, 메타 정보를 포함한 표준화된 API 응답 객체
        """
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
        """
        에러 메시지와 선택적 오류 세부 정보를 포함하는 표준화된 API 에러 응답을 생성합니다.
        
        Parameters:
            message (str): 클라이언트에 전달할 에러 메시지.
            errors (dict, optional): 추가적인 오류 세부 정보가 담긴 딕셔너리.
            request_id (str, optional): 요청 식별자.
        
        Returns:
            APIResponse: 에러 상태와 메타데이터가 포함된 API 응답 객체.
        """
        meta = ResponseMeta(request_id=request_id) if request_id else ResponseMeta()

        # 하위 호환: 기존 dict(errors) 입력을 ErrorBody로 매핑
        error_body: ErrorBody
        if errors is None:
            error_body = ErrorBody(code="ERROR", message=message)
        else:
            code = str(errors.get("code", "ERROR"))
            # 남은 키들은 details로 모아 전달
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
        """
        지정된 데이터와 페이지네이션 정보를 포함하는 표준화된 API 페이지네이션 응답을 생성합니다.
        
        Parameters:
            data (list): 응답에 포함될 데이터 목록
            page (int): 현재 페이지 번호
            limit (int): 페이지당 항목 수
            total (int): 전체 항목 수
            message (str, optional): 응답 메시지 (기본값: "조회 성공")
            request_id (str, optional): 요청 식별자
        
        Returns:
            APIResponse: 페이지네이션 메타데이터와 함께 성공 상태의 API 응답 객체
        """
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
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "생성 완료",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """
        새로운 리소스가 성공적으로 생성되었음을 나타내는 표준 API 응답을 반환합니다.
        
        Parameters:
            data: 생성된 리소스에 대한 선택적 데이터입니다.
            message: 응답 메시지(기본값: "생성 완료").
            request_id: 요청 식별자(선택적).
        
        Returns:
            APIResponse: 생성 성공 상태와 함께 데이터 및 메타 정보를 포함한 응답 객체입니다.
        """
        return APIResponseBuilder.success(
            data=data,
            message=message,
            request_id=request_id
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "수정 완료", 
        request_id: Optional[str] = None
    ) -> APIResponse:
        """
        리소스의 수정이 성공했음을 나타내는 표준 API 응답을 반환합니다.
        
        Parameters:
            data: 응답에 포함할 선택적 데이터입니다.
            message: 응답 메시지(기본값: "수정 완료")입니다.
            request_id: 요청 식별자(선택 사항)입니다.
        
        Returns:
            APIResponse: 수정 성공 상태와 함께 데이터 및 메타 정보를 포함한 표준 API 응답 객체입니다.
        """
        return APIResponseBuilder.success(
            data=data,
            message=message,
            request_id=request_id
        )
    
    @staticmethod
    def deleted(
        message: str = "삭제 완료",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """
        리소스 삭제가 성공했음을 나타내는 표준 API 응답을 반환합니다.
        
        Parameters:
            message (str): 응답 메시지. 기본값은 "삭제 완료"입니다.
            request_id (Optional[str]): 요청 식별자. 지정하지 않으면 포함되지 않습니다.
        
        Returns:
            APIResponse: 삭제 성공 상태와 메시지를 포함한 표준화된 API 응답 객체
        """
        return APIResponseBuilder.success(
            message=message,
            request_id=request_id
        )


# 하위 호환성을 위한 별칭
ResponseWrapper = APIResponse 


# 공통 헬퍼
def ok(data: T, meta: Optional[ResponseMeta] = None, message: Optional[str] = None) -> APIResponse[T]:
    """성공 응답 헬퍼"""
    return APIResponse(
        success=True,
        message=message,
        data=data,
        error=None,
        meta=meta or ResponseMeta(),
    )


def fail(code: str, message: str, *, details: Optional[Dict[str, Any]] = None) -> APIResponse[None]:
    """실패 응답 헬퍼 (status 코드는 라우터에서 결정)"""
    return APIResponse(
        success=False,
        message=message,
        data=None,
        error=ErrorBody(code=code, message=message, details=details),
        meta=None,
    )