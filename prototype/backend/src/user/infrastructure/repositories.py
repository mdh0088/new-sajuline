"""
User 인프라스트럭처 - 리포지토리 구현
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..domain.models import User
from ..domain.entities import UserEntity
from ..domain.ports import UserRepositoryPort as IUserRepositoryPort
from ...common.exceptions.custom import DatabaseError, ConflictException




class MariaDBUserRepository(IUserRepositoryPort):
    """MariaDB User 리포지토리 구현

    도메인 포트(Protocol)를 구조적으로 충족합니다.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserEntity]:
        """ID로 사용자 조회"""
        try:
            query = select(User).where(User.user_id == user_id)
            result = await self.session.execute(query)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 ID 조회 실패: {str(e)}")
    
    async def get_user_by_nickname(self, nickname: str) -> Optional[UserEntity]:
        """닉네임으로 사용자 조회"""
        try:
            query = select(User).where(User.nickname == nickname)
            result = await self.session.execute(query)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 닉네임 조회 실패: {str(e)}")
    
    async def get_user_by_phone(self, phone: str) -> Optional[UserEntity]:
        """전화번호로 사용자 조회"""
        try:
            query = select(User).where(User.phone == phone)
            result = await self.session.execute(query)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 전화번호 조회 실패: {str(e)}")
    
    async def get_user_by_user_id(self, user_id: str) -> Optional[UserEntity]:
        """user_id로 사용자 조회 (get_user_by_id와 동일)"""
        return await self.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        """이메일로 사용자 조회"""
        try:
            query = select(User).where(User.email == email)
            result = await self.session.execute(query)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 이메일 조회 실패: {str(e)}")
    
    async def update_user(self, user: UserEntity) -> None:
        """사용자 엔티티 업데이트"""
        try:
            update_fields = {
                "email": user.email,
                "password_hash": user.password_hash,
                "nickname": user.nickname,
                "phone": user.phone,
                "join_type": user.join_type,
                "social_provider": user.social_provider,
                "social_id": user.social_id,
                "user_status": user.user_status,
                "grade_code": user.grade_code,
                "profile_image_url": user.profile_image_url,
                "birth_date": user.birth_date,
                "gender": user.gender,
                "is_marketing_agreed": user.is_marketing_agreed,
                "failed_login_count": user.failed_login_count,
                "locked_until": user.locked_until,
                "last_login_at": user.last_login_at,
                "withdrawn_at": user.withdrawn_at,
                "updated_at": datetime.utcnow(),
            }
            # None 값도 업데이트할 수 있도록 그대로 전달
            await self.session.execute(
                update(User)
                .where(User.user_id == user.user_id)
                .values(**update_fields)
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 업데이트 실패: {str(e)}")
    
    async def create_user(self, user_id: str, email: str, password_hash: Optional[str], 
                         phone: Optional[str], nickname: Optional[str], join_type: str, 
                         gender: Optional[str] = None, agree_marketing: bool = False) -> UserEntity:
        """사용자 생성"""
        try:
            user = User(
                user_id=user_id,
                email=email,
                password_hash=password_hash or "",
                phone=phone or "",
                nickname=nickname or user_id,
                join_type=join_type,
                gender=gender,
                is_marketing_agreed=agree_marketing,
                user_status="ACTIVE",
                grade_code="WHITE",
                created_at=datetime.utcnow()
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return self._to_entity(user)
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(f"사용자 생성 실패 - 중복된 데이터: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 생성 실패: {str(e)}")

    async def create_user_deferred_commit(self, user_id: str, email: str, password_hash: Optional[str], 
                         phone: Optional[str], nickname: Optional[str], join_type: str, 
                         gender: Optional[str] = None, agree_marketing: bool = False) -> UserEntity:
        """flush까지 수행하고 commit은 호출자가 제어"""
        try:
            user = User(
                user_id=user_id,
                email=email,
                password_hash=password_hash or "",
                phone=phone or "",
                nickname=nickname or user_id,
                join_type=join_type,
                gender=gender,
                is_marketing_agreed=agree_marketing,
                user_status="ACTIVE",
                grade_code="WHITE",
                created_at=datetime.utcnow()
            )
            self.session.add(user)
            await self.session.flush()
            return self._to_entity(user)
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(f"사용자 생성 실패 - 중복된 데이터: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 생성 실패: {str(e)}")
    
    async def update_user_by_id(self, user_id: str, update_data: Dict[str, Any]) -> UserEntity:
        """사용자 정보 업데이트"""
        try:
            # 업데이트할 데이터에 수정 시간 추가
            update_data["updated_at"] = datetime.utcnow()
            
            query = (
                update(User)
                .where(User.user_id == user_id)
                .values(**update_data)
            )
            await self.session.execute(query)
            await self.session.commit()
            
            # 업데이트된 사용자 조회
            updated_user = await self.get_user_by_id(user_id)
            if not updated_user:
                raise DatabaseError("업데이트된 사용자를 찾을 수 없습니다.")
            
            return updated_user
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 정보 업데이트 실패: {str(e)}")
    
    async def create_point_transaction(self, user_id: str, new_balance: int, 
                                     transaction_data: Dict[str, Any]) -> Tuple[Any, UserEntity]:
        """포인트 거래 생성 및 잔액 업데이트"""
        try:
            # TODO: PointTransaction 모델 생성 후 구현
            # 현재는 사용자 포인트 잔액만 업데이트
            
            # 사용자 포인트 업데이트
            await self.session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(point_balance=new_balance, updated_at=datetime.utcnow())
            )
            
            # TODO: 포인트 거래 테이블에 기록 추가
            # transaction = PointTransaction(**transaction_data)
            # self.session.add(transaction)
            
            await self.session.commit()
            
            # 업데이트된 사용자 조회
            updated_user = await self.get_user_by_id(user_id)
            
            # 임시 거래 객체 생성 (실제 모델 구현 전까지)
            from types import SimpleNamespace
            transaction = SimpleNamespace(**transaction_data, created_at=datetime.utcnow())
            
            return transaction, updated_user
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"포인트 거래 생성 실패: {str(e)}")
    
    async def get_point_transactions(self, user_id: str, limit: int, offset: int) -> List[Any]:
        """포인트 거래 내역 조회"""
        try:
            # TODO: PointTransaction 모델 생성 후 구현
            # 현재는 빈 리스트 반환
            return []
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"포인트 거래 내역 조회 실패: {str(e)}")
    
    async def get_user_settings(self, user_id: str) -> Optional[Any]:
        """사용자 설정 조회"""
        try:
            # TODO: UserSettings 모델 생성 후 구현
            # 현재는 None 반환
            return None
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 설정 조회 실패: {str(e)}")
    
    async def create_user_settings(self, user_id: str) -> Any:
        """사용자 설정 생성"""
        try:
            # TODO: UserSettings 모델 생성 후 구현
            # 현재는 임시 객체 반환
            from types import SimpleNamespace
            settings = SimpleNamespace(
                user_id=user_id,
                notification_email=True,
                notification_sms=False,
                notification_push=True,
                marketing_consent=False,
                updated_at=datetime.utcnow()
            )
            return settings
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 설정 생성 실패: {str(e)}")
    
    async def update_user_settings(self, user_id: str, update_data: Dict[str, Any]) -> Any:
        """사용자 설정 업데이트"""
        try:
            # TODO: UserSettings 모델 생성 후 구현
            # 현재는 임시 객체 반환
            from types import SimpleNamespace
            settings = SimpleNamespace(
                user_id=user_id,
                notification_email=update_data.get("notification_email", True),
                notification_sms=update_data.get("notification_sms", False),
                notification_push=update_data.get("notification_push", True),
                marketing_consent=update_data.get("marketing_consent", False),
                updated_at=datetime.utcnow()
            )
            return settings
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 설정 업데이트 실패: {str(e)}")
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """사용자 통계 조회"""
        try:
            # TODO: 실제 통계 쿼리 구현
            # 현재는 기본값 반환
            stats = {
                "total_consultations": 0,
                "total_points_used": 0,
                "total_points_earned": 0,
                "favorite_consultants": []
            }
            return stats
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"사용자 통계 조회 실패: {str(e)}")
    
    async def deactivate_user(self, user_id: str, reason: Optional[str], deleted_at: datetime) -> None:
        """사용자 계정 비활성화"""
        try:
            # 사용자 상태를 DELETED로 변경
            query = (
                update(User)
                .where(User.user_id == user_id)
                .values(
                    user_status="DELETED",
                    updated_at=deleted_at
                )
            )
            await self.session.execute(query)
            
            # TODO: 탈퇴 사유 및 탈퇴 시간 기록을 위한 별도 테이블 추가 고려
            
            await self.session.commit()
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 계정 비활성화 실패: {str(e)}") 

    async def delete_user_by_id(self, user_id: str) -> None:
        """사용자 삭제 (보상 트랜잭션용)"""
        try:
            result = await self.session.execute(select(User).where(User.user_id == user_id))
            orm = result.scalar_one_or_none()
            if orm is None:
                return
            await self.session.delete(orm)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 삭제 실패: {str(e)}")

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"커밋 실패: {str(e)}")

    async def rollback(self) -> None:
        try:
            await self.session.rollback()
        except SQLAlchemyError as e:
            raise DatabaseError(f"롤백 실패: {str(e)}")
    def _to_entity(self, orm: User) -> UserEntity:
        return UserEntity(
            user_id=orm.user_id,
            email=orm.email,
            password_hash=orm.password_hash,
            nickname=orm.nickname,
            phone=orm.phone,
            join_type=orm.join_type,
            social_provider=orm.social_provider,
            social_id=orm.social_id,
            user_status=orm.user_status,
            grade_code=orm.grade_code,
            profile_image_url=orm.profile_image_url,
            birth_date=orm.birth_date,
            gender=orm.gender,
            is_marketing_agreed=bool(orm.is_marketing_agreed),
            failed_login_count=orm.failed_login_count,
            locked_until=orm.locked_until,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            last_login_at=orm.last_login_at,
            withdrawn_at=orm.withdrawn_at,
        )
        