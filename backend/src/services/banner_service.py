"""
배너 비즈니스 로직 서비스
"""
from typing import List

from src.repositories.banner_repository import BannerRepository
from src.schemas.banner_schema import BannerResponse
from src.common.logging import get_logger_with_request_id


class BannerService:
    """배너 비즈니스 로직"""

    def __init__(self, repo: BannerRepository):
        self.repo = repo

    async def list_public_main(self) -> List[BannerResponse]:
        """메인 배너 공개 목록 반환"""
        log = get_logger_with_request_id()
        log.info("Service: list_public_main banners")
        items = await self.repo.list_public_main_banners()
        return [BannerResponse.model_validate(x) for x in items]

    async def increase_click(self, banner_id: int) -> bool:
        """클릭수 증가"""
        log = get_logger_with_request_id()
        log.info("Service: increase banner click", banner_id=banner_id)
        return await self.repo.increment_click_count(banner_id)


