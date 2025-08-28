"""
User 도메인 포트 정의 (ABC)

애플리케이션 서비스는 이 포트에만 의존합니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


from .entities import UserEntity


class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_user_by_user_id(self, user_id: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_user_by_nickname(self, nickname: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_user_by_phone(self, phone: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def update_user(self, user: UserEntity) -> None: ...

    @abstractmethod
    async def update_user_by_id(self, user_id: str, update_data: Dict[str, Any]) -> UserEntity: ...

    @abstractmethod
    async def create_user(
        self,
        user_id: str,
        email: str,
        password_hash: Optional[str],
        phone: Optional[str],
        nickname: Optional[str],
        join_type: str,
        gender: Optional[str] = None,
        agree_marketing: bool = False,
    ) -> UserEntity: ...

    @abstractmethod
    async def create_user_deferred_commit(
        self,
        user_id: str,
        email: str,
        password_hash: Optional[str],
        phone: Optional[str],
        nickname: Optional[str],
        join_type: str,
        gender: Optional[str] = None,
        agree_marketing: bool = False,
    ) -> UserEntity: ...

    @abstractmethod
    async def create_point_transaction(
        self, user_id: str, new_balance: int, transaction_data: Dict[str, Any]
    ) -> Tuple[Any, UserEntity]: ...

    @abstractmethod
    async def get_point_transactions(self, user_id: str, limit: int, offset: int) -> List[Any]: ...

    @abstractmethod
    async def get_user_settings(self, user_id: str) -> Optional[Any]: ...

    @abstractmethod
    async def create_user_settings(self, user_id: str) -> Any: ...

    @abstractmethod
    async def update_user_settings(self, user_id: str, update_data: Dict[str, Any]) -> Any: ...

    @abstractmethod
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]: ...

    @abstractmethod
    async def deactivate_user(self, user_id: str, reason: Optional[str], deleted_at: datetime) -> None: ...

    @abstractmethod
    async def delete_user_by_id(self, user_id: str) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


