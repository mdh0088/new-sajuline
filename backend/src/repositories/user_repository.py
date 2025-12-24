"""
사용자 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

KST = ZoneInfo("Asia/Seoul")
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.engine import Result

from src.models.user_model import User, UserOut, JoinType, UserStatus
from src.schemas.user_schema import UserSignup
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class UserRepository:
    """사용자 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create_from_signup(self, signup_data: UserSignup, password_hash: Optional[str] = None, join_type: JoinType = JoinType.COMMON) -> User:
        """회원가입용 사용자 생성"""
        user = User(
            user_id=signup_data.user_id,
            email=signup_data.email,
            password_hash=password_hash,
            nickname=signup_data.nickname,
            phone=signup_data.phone,
            join_type=join_type,
            social_provider=signup_data.social_provider,
            social_id=signup_data.social_id,
            profile_image_url=signup_data.profile_image_url,
            birth_date=signup_data.birth_date,
            gender=signup_data.gender,
            is_marketing_agreed=signup_data.is_marketing_agreed,
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
        """전화번호로 사용자 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up user by phone", phone=phone)

        stmt = select(User).where(User.phone == phone)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        log.info("User lookup by phone completed", phone=phone, found=user is not None)
        return user

    @logger.catch(reraise=True)
    async def get_by_user_id_and_phone_for_password_reset(self, user_id: str, phone: str) -> Optional[User]:
        """
        비밀번호 찾기용 사용자 조회
        user_id, phone이 일치하고 join_type이 'COMMON'인 사용자만 조회
        """
        log = get_logger_with_request_id()
        log.info("Looking up COMMON user for password reset", user_id=user_id, phone=phone)

        stmt = select(User).where(
            and_(
                User.user_id == user_id,
                User.phone == phone,
                User.join_type == JoinType.COMMON
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        log.info("Password reset user lookup completed", user_id=user_id, found=user is not None)
        return user

    @logger.catch(reraise=True)
    async def get_by_user_id_and_phone(self, user_id: str, phone: str) -> Optional[User]:
        """
        user_id, phone으로 사용자 조회 (join_type 무관)
        """
        log = get_logger_with_request_id()
        log.info("Looking up user by user_id and phone", user_id=user_id, phone=phone)

        stmt = select(User).where(
            and_(
                User.user_id == user_id,
                User.phone == phone
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        log.info("User lookup completed", user_id=user_id, found=user is not None)
        return user

# TODO: 사용자 목록 조회 - 추후 참고용
    # @logger.catch(reraise=True)
    # async def get_list(
    #     self, 
    #     skip: int = 0, 
    #     limit: int = 100,
    #     user_status: Optional[str] = None
    # ) -> List[User]:
    #     """사용자 목록 조회"""
    #     stmt = select(User)
    #     
    #     if user_status:
    #         stmt = stmt.where(User.user_status == user_status)
    #     
    #     stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())
    #     
    #     result = await self.db.execute(stmt)
    #     return list(result.scalars().all())
    # 
    # @logger.catch(reraise=True)
    # async def get_count(self, user_status: Optional[str] = None) -> int:
    #     """사용자 총 개수"""
    #     stmt = select(User.user_id)
    #     
    #     if user_status:
    #         stmt = stmt.where(User.user_status == user_status)
    #     
    #     result = await self.db.execute(stmt)
    #     return len(list(result.scalars().all()))
    
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
    async def exists_by_nickname(self, nickname: str) -> bool:
        """닉네임 존재 여부 확인"""
        stmt = select(User.user_id).where(User.nickname == nickname)
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
                updated_at=datetime.now(KST)
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
                updated_at=datetime.now(KST)
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
                last_login_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    @logger.catch(reraise=True)
    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """비밀번호 업데이트 (비밀번호 찾기/변경)"""
        log = get_logger_with_request_id()
        log.info("Updating user password", user_id=user_id)

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                password_hash=password_hash,
                password_changed_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)

        log.info("User password updated", user_id=user_id, success=result.rowcount > 0)
        return result.rowcount > 0
    
    @logger.catch(reraise=True)
    async def delete_by_user_id(self, user_id: str) -> bool:
        """사용자 완전 삭제 (회원가입 실패시 보상 트랜잭션용)"""
        stmt = delete(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    @logger.catch(reraise=True)
    async def update_mileage_point(self, user_id: str, new_mileage_point: int) -> bool:
        """사용자 마일리지 포인트 업데이트"""
        log = get_logger_with_request_id()
        log.info("Updating user mileage point", user_id=user_id, new_mileage_point=new_mileage_point)

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                mileage_point=new_mileage_point,
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        updated = result.rowcount > 0

        log.info("User mileage point update completed", user_id=user_id, updated=updated)
        return updated

    @logger.catch(reraise=True)
    async def get_withdrawal_count(self) -> int:
        """
        현재 탈퇴 회원 수 조회 (withdrawal_id 생성용)

        Returns:
            int: 현재 탈퇴 회원 수
        """
        log = get_logger_with_request_id()
        log.info("Getting withdrawal count for new withdrawal_id")

        stmt = select(func.count()).select_from(UserOut)
        result = await self.db.execute(stmt)
        count = result.scalar() or 0

        log.info("Current withdrawal count", count=count)
        return count

    @logger.catch(reraise=True)
    async def create_user_out(
        self,
        user_id: str,
        withdrawal_id: str,
        nickname: str,
        phone: str,
        email: str,
        reason: Optional[str] = None
    ) -> UserOut:
        """
        회원 탈퇴 정보 기록

        Args:
            user_id: 탈퇴한 사용자 원본 ID
            withdrawal_id: 탈퇴 ID (withdrawal_0, withdrawal_1, ...)
            nickname: 탈퇴한 사용자 닉네임
            phone: 탈퇴한 사용자 전화번호
            email: 탈퇴한 사용자 이메일
            reason: 탈퇴 사유 (선택)
        """
        log = get_logger_with_request_id()
        log.info("Creating user out record", user_id=user_id, withdrawal_id=withdrawal_id)

        user_out = UserOut(
            user_id=user_id,
            withdrawal_id=withdrawal_id,
            nickname=nickname,
            phone=phone,
            email=email,
            reason=reason
        )

        self.db.add(user_out)
        await self.db.flush()
        await self.db.refresh(user_out)

        log.info("User out record created",
                user_id=user_id,
                withdrawal_id=withdrawal_id,
                out_idx=user_out.out_idx)
        return user_out

    @logger.catch(reraise=True)
    async def update_user_for_withdrawal(
        self,
        user_id: str,
        withdrawal_id: str
    ) -> bool:
        """
        탈퇴 처리 시 사용자 정보 업데이트
        - user_id를 withdrawal_id로 변경
        - email, nickname, phone을 NULL로 변경
        - 상태를 WITHDRAWN으로 변경

        Args:
            user_id: 원본 사용자 ID
            withdrawal_id: 새로운 탈퇴 ID (withdrawal_0, withdrawal_1, ...)

        Returns:
            bool: 업데이트 성공 여부
        """
        log = get_logger_with_request_id()
        log.info("Updating user for withdrawal",
                user_id=user_id,
                withdrawal_id=withdrawal_id)

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                user_id=withdrawal_id,
                email=None,
                nickname=None,
                phone=None,
                user_status=UserStatus.WITHDRAWN,
                withdrawn_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        updated = result.rowcount > 0

        log.info("User updated for withdrawal",
                user_id=user_id,
                withdrawal_id=withdrawal_id,
                updated=updated)
        return updated

    @logger.catch(reraise=True)
    async def update_user_status_to_withdrawn(self, user_id: str) -> bool:
        """사용자 상태를 WITHDRAWN으로 변경"""
        log = get_logger_with_request_id()
        log.info("Updating user status to WITHDRAWN", user_id=user_id)

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                user_status=UserStatus.WITHDRAWN,
                withdrawn_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            )
            .execution_options(synchronize_session="evaluate")
        )
        result = await self.db.execute(stmt)
        updated = result.rowcount > 0

        log.info("User status updated to WITHDRAWN", user_id=user_id, updated=updated)
        return updated

    @logger.catch(reraise=True)
    async def get_recent_withdrawal_by_phone(
        self,
        phone: str,
        months: int = 2
    ) -> Optional[Tuple[UserOut, int]]:
        """
        전화번호로 최근 탈퇴 이력 조회 (재가입 제한 검사용)

        Args:
            phone: 검사할 전화번호
            months: 제한 기간 (기본 2개월)

        Returns:
            Tuple[UserOut, int] | None: (탈퇴 정보, 남은 일수) 또는 None (제한 없음)
        """
        log = get_logger_with_request_id()
        log.info("Checking recent withdrawal by phone", phone=phone, months=months)

        # 제한 기간 계산 (현재 시점 기준 N개월 전)
        cutoff_date = datetime.now(KST) - timedelta(days=months * 30)

        # 해당 전화번호로 제한 기간 내 탈퇴 이력 조회 (가장 최근 탈퇴)
        stmt = (
            select(UserOut)
            .where(
                and_(
                    UserOut.phone == phone,
                    UserOut.created_at >= cutoff_date
                )
            )
            .order_by(UserOut.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        user_out = result.scalar_one_or_none()

        if user_out:
            # 재가입 가능 일자 계산
            rejoin_available_date = user_out.created_at + timedelta(days=months * 30)
            # timezone-aware로 변환하여 비교
            if rejoin_available_date.tzinfo is None:
                rejoin_available_date = rejoin_available_date.replace(tzinfo=KST)
            remaining_days = (rejoin_available_date - datetime.now(KST)).days
            remaining_days = max(0, remaining_days)  # 음수 방지

            log.info("Recent withdrawal found",
                    phone=phone,
                    withdrawal_date=user_out.created_at,
                    remaining_days=remaining_days)
            return user_out, remaining_days

        log.info("No recent withdrawal found", phone=phone)
        return None

    @logger.catch(reraise=True)
    async def delete_user_out_by_phone(self, phone: str) -> int:
        """
        전화번호로 t_user_out 레코드 삭제 (재가입 성공 시 정리용)

        Args:
            phone: 삭제할 전화번호

        Returns:
            int: 삭제된 레코드 수
        """
        log = get_logger_with_request_id()
        log.info("Deleting user out records by phone", phone=phone)

        stmt = delete(UserOut).where(UserOut.phone == phone)
        result = await self.db.execute(stmt)
        deleted_count = result.rowcount

        log.info("User out records deleted", phone=phone, deleted_count=deleted_count)
        return deleted_count

