"""
공통 Repository Base 클래스

모든 Repository가 상속받는 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime


T = TypeVar('T')  # 엔티티 타입을 위한 제네릭 타입


class RepositoryPort(ABC, Generic[T]):
    """기본 Repository 포트 (인터페이스)"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """ID로 엔티티 조회"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """모든 엔티티 조회 (페이지네이션)"""
        pass
    
    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> T:
        """엔티티 생성"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> T:
        """엔티티 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """엔티티 삭제"""
        pass


class CacheableRepositoryPort(RepositoryPort[T]):
    """캐시 가능한 Repository 포트"""
    
    @abstractmethod
    async def get_from_cache(self, cache_key: str) -> Optional[T]:
        """캐시에서 조회"""
        pass
    
    @abstractmethod
    async def set_to_cache(self, cache_key: str, entity: T, ttl: int = 3600) -> None:
        """캐시에 저장"""
        pass
    
    @abstractmethod
    async def delete_from_cache(self, cache_key: str) -> None:
        """캐시에서 삭제"""
        pass


class AuditableRepositoryPort(RepositoryPort[T]):
    """감사 가능한 Repository 포트 (생성/수정 추적)"""
    
    @abstractmethod
    async def get_by_created_at(self, start_date: datetime, end_date: datetime) -> List[T]:
        """생성일로 조회"""
        pass
    
    @abstractmethod
    async def get_by_updated_at(self, start_date: datetime, end_date: datetime) -> List[T]:
        """수정일로 조회"""
        pass
    
    @abstractmethod
    async def get_audit_log(self, entity_id: str) -> List[Dict[str, Any]]:
        """엔티티 변경 이력 조회"""
        pass