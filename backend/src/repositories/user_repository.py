"""
사용자 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.engine import Result

from src.models.user_model import User
from src.schemas.user_schema import UserCreate, UserUpdate
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class UserRepository:
    """사용자 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create(self, user_data: UserCreate, password_hash: Optional[str] = None) -> User:
        """사용자 생성"""
        user = User(
            user_id=user_data.user_id,
            email=user_data.email,
            password_hash=password_hash,
            nickname=user_data.nickname,
            phone=user_data.phone,
            join_type=user_data.join_type,
            social_provider=user_data.social_provider,
            social_id=user_data.social_id,
            profile_image_url=user_data.profile_image_url,
            birth_date=user_data.birth_date,
            gender=user_data.gender,
            is_marketing_agreed=user_data.is_marketing_agreed,
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    @logger.catch(reraise=True)
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up user by ID", user_id=user_id)
        
        # 테스트용 강제 오류 발생
        if user_id == "repo_error_test":
            raise BaseAppException("Repository layer: 강제 DB 연결 오류 테스트", status_code=500)
        
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        log.info("User lookup completed", user_id=user_id, found=user is not None)
        return user
    
    @logger.catch(reraise=True)
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up user by email", email=email)
        
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        log.info("User lookup by email completed", email=email, found=user is not None)
        return user
    
    @logger.catch(reraise=True)
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """전화번호로 조회"""
        stmt = select(User).where(User.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    @logger.catch(reraise=True)
    async def get_by_social_id(self, social_provider: str, social_id: str) -> Optional[User]:
        """소셜 로그인 정보로 조회"""
        stmt = select(User).where(
            and_(
                User.social_provider == social_provider,
                User.social_id == social_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    @logger.catch(reraise=True)
    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 수정"""
        update_data = {
            key: value for key, value in user_data.model_dump(exclude_unset=True).items()
            if value is not None
        }
        
        if not update_data:
            return await self.get_by_id(user_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(**update_data)
            .execution_options(synchronize_session="evaluate")
        )
        
        await self.db.execute(stmt)
        return await self.get_by_id(user_id)
    
    @logger.catch(reraise=True)
    async def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        stmt = delete(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_status: Optional[str] = None
    ) -> List[User]:
        """사용자 목록 조회"""
        stmt = select(User)
        
        if user_status:
            stmt = stmt.where(User.user_status == user_status)
        
        stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @logger.catch(reraise=True)
    async def get_count(self, user_status: Optional[str] = None) -> int:
        """사용자 총 개수"""
        stmt = select(User.user_id)
        
        if user_status:
            stmt = stmt.where(User.user_status == user_status)
        
        result = await self.db.execute(stmt)
        return len(list(result.scalars().all()))
    
    @logger.catch(reraise=True)
    async def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        stmt = select(User.user_id).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def exists_by_user_id(self, user_id: str) -> bool:
        """사용자 ID 존재 여부 확인"""
        stmt = select(User.user_id).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def exists_by_phone(self, phone: str) -> bool:
        """전화번호 존재 여부 확인"""
        stmt = select(User.user_id).where(User.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    @logger.catch(reraise=True)
    async def increment_failed_login(self, user_id: str) -> bool:
        """로그인 실패 횟수 증가"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                failed_login_count=User.failed_login_count + 1,
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def reset_failed_login(self, user_id: str) -> bool:
        """로그인 실패 횟수 초기화"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                failed_login_count=0,
                locked_until=None,
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def update_last_login(self, user_id: str) -> bool:
        """마지막 로그인 시간 업데이트"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                last_login_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0