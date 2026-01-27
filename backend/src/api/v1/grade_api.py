"""
멤버십 등급(Grade) 공개 API 엔드포인트
게스트 접근 허용: 권한 체크 불필요
"""
from fastapi import APIRouter

from src.core.dependencies import GradeServiceDep
from src.schemas.grade_schema import GradeResponse
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id


router = APIRouter(prefix="/grades", tags=["grades"])


@router.get("/public", response_model=APIResponse[list[GradeResponse]], summary="멤버십 등급 목록(공개)")
async def list_public_grades(
    grade_service: GradeServiceDep
) -> APIResponse[list[GradeResponse]]:
    """
    공개 멤버십 등급 목록 조회
    - 권한 체크 없음(게스트 가능)
    - is_active=True만 노출
    - grade_level ASC 정렬
    """
    log = get_logger_with_request_id()
    log.info("API: list public grades")
    items = await grade_service.list_public_grades()
    return ok(data=items, message="등급 목록 조회 성공")


