"""
Counselor 도메인 포트 정의 (ABC)
"""

from __future__ import annotations

from typing import List, Optional
from abc import ABC, abstractmethod

from .entities import CounselorEntity


class CounselorRepositoryPort(ABC):
    @abstractmethod
    async def get_counselor_by_email(self, email: str) -> Optional[CounselorEntity]: ...

    @abstractmethod
    async def get_counselor_by_id(self, counselor_id: str) -> Optional[CounselorEntity]: ...

    @abstractmethod
    async def get_counselor_by_code(self, counselor_code: str) -> Optional[CounselorEntity]: ...

    @abstractmethod
    async def get_counselor_by_nickname(self, nickname: str) -> Optional[CounselorEntity]: ...

    @abstractmethod
    async def get_active_specialties(self) -> List[dict]: ...

    @abstractmethod
    async def update_counselor_status(self, counselor_id: str, status: str) -> None: ...

    @abstractmethod
    async def update_online_status(self, counselor_id: str, is_online: bool) -> None: ...


