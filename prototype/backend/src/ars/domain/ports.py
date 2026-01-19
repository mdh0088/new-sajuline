"""
ARS 도메인 포트 정의 (ABC)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import ARSUser


class ARSUserRepositoryPort(ABC):
    @abstractmethod
    async def create_tm60_user(
        self,
        u_id: str,
        u_tel: str,
        u_kname: str,
        u_passwd: str = "",
    ) -> ARSUser:
        ...


