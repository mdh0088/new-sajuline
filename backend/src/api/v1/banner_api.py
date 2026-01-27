"""
배너 API 엔드포인트
 - 메인 배너 목록 (게스트)
 - 배너 클릭 카운트 증가
"""
from fastapi import APIRouter, HTTPException

from src.core.dependencies import BannerServiceDep
from src.common.response import ok, APIResponse
from src.common.logging import get_logger_with_request_id
from src.schemas.banner_schema import BannerResponse


router = APIRouter(prefix="/banners", tags=["banners"])


@router.get(
    "/public/main",
    response_model=APIResponse[list[BannerResponse]],
    summary="메인 배너 목록(공개)",
    description="banner_type=MAIN, is_active=True, 현재 유효기간 내 배너를 display_order ASC로 반환"
)
async def list_public_main_banners(service: BannerServiceDep) -> APIResponse[list[BannerResponse]]:
    log = get_logger_with_request_id()
    log.info("API: list public main banners")
    items = await service.list_public_main()
    return ok(data=items, message="배너 목록 조회 성공")


@router.post(
    "/{banner_id}/click",
    response_model=APIResponse[dict],
    summary="배너 클릭 카운트 증가",
)
async def increase_click(banner_id: int, service: BannerServiceDep) -> APIResponse[dict]:
    log = get_logger_with_request_id()
    log.info("API: increase banner click", banner_id=banner_id)
    success = await service.increase_click(banner_id)
    if not success:
        raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")
    return ok(data={"banner_id": banner_id, "clicked": True}, message="클릭 카운트 증가")


