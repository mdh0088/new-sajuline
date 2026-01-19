"""
Auth 도메인 포트 정의 (ABC)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from ..domain.entities import SocialUserInfo


class AuthRepositoryPort(ABC):
    @abstractmethod
    async def create_session(self, session_data: Dict[str, Any]) -> None: ...

    @abstractmethod
    async def deactivate_user_sessions(self, user_id: str) -> None: ...

    @abstractmethod
    async def blacklist_token(self, token: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def is_token_blacklisted(self, token: str) -> bool: ...

    @abstractmethod
    async def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def update_user_social_info(
        self,
        user_id: str,
        social_provider: str,
        social_id: str,
        profile_image_url: Optional[str],
    ) -> None: ...

    @abstractmethod
    async def get_kakao_user_info(self, code: str) -> SocialUserInfo: ...

    @abstractmethod
    async def get_naver_user_info(self, code: str) -> SocialUserInfo: ...


