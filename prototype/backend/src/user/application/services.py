"""
User 애플리케이션 서비스
사용자 프로필, 설정, 포인트 관리 유즈케이스
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from ...common.exceptions.custom import (
    UserNotFoundException,
    DuplicateNicknameException,
    DuplicatePhoneException,
    PointsInsufficientException,
)

from ..domain.entities import (
    UserProfile, UpdateProfileRequest, UpdateProfileResponse,
    PointTransaction, AddPointsRequest, UsePointsRequest, PointTransactionResponse,
    UserSettings, UserSettingsRequest, UserStatsResponse,
    DeleteAccountRequest, DeleteAccountResponse, SubscriptionType
)
from ..domain.ports import UserRepositoryPort
from ...common.utils.sanitizer import Sanitizer
from ...common.logging.events import log_event


class UserApplicationService:
    """사용자 애플리케이션 서비스"""
    
    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self.user_repository: UserRepositoryPort = user_repository

    async def get_user_profile(self, user_id: str) -> UserProfile:
        """사용자 프로필 조회"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        return UserProfile(
            id=user.user_id,
            email=user.email,
            name=user.nickname,  # DB의 nickname을 name으로 매핑
            nickname=user.nickname,
            status=user.user_status.lower(),
            subscription_type=SubscriptionType.PREMIUM if user.is_premium else SubscriptionType.FREE,
            phone_number=user.phone if user.phone else None,
            profile_image_url=user.profile_image_url,
            birth_date=user.birth_date,
            gender=user.gender,
            point_balance=user.point_balance,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def update_profile(self, user_id: str, update_request: UpdateProfileRequest) -> UpdateProfileResponse:
        """사용자 프로필 업데이트"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        # 업데이트할 데이터 준비
        update_data = {}
        if update_request.nickname is not None:
            # 닉네임 XSS 방어를 위한 sanitization
            sanitized_nickname = Sanitizer.sanitize_html(update_request.nickname)
            
            # 닉네임 중복 확인
            existing_user = await self.user_repository.get_user_by_nickname(sanitized_nickname)
            if existing_user and existing_user.user_id != user_id:
                raise DuplicateNicknameException()
            update_data["nickname"] = sanitized_nickname
        
        if update_request.phone_number is not None:
            # 전화번호 중복 확인
            existing_user = await self.user_repository.get_user_by_phone(update_request.phone_number)
            if existing_user and existing_user.user_id != user_id:
                raise DuplicatePhoneException()
            update_data["phone"] = update_request.phone_number
        
        if update_request.birth_date is not None:
            update_data["birth_date"] = update_request.birth_date
        
        if update_request.gender is not None:
            update_data["gender"] = update_request.gender
        
        # 업데이트 실행
        updated_user = await self.user_repository.update_user(user_id, update_data)
        
        # 응답 생성
        profile = UserProfile(
            id=updated_user.user_id,
            email=updated_user.email,
            name=updated_user.nickname,
            nickname=updated_user.nickname,
            status=updated_user.user_status.lower(),
            subscription_type=SubscriptionType.PREMIUM if updated_user.is_premium else SubscriptionType.FREE,
            phone_number=updated_user.phone if updated_user.phone else None,
            profile_image_url=updated_user.profile_image_url,
            birth_date=updated_user.birth_date,
            gender=updated_user.gender,
            point_balance=updated_user.point_balance,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
        return UpdateProfileResponse(profile=profile)

    async def add_points(self, user_id: str, add_request: AddPointsRequest) -> PointTransactionResponse:
        """포인트 추가 (충전)"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        # 포인트 거래 생성
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        new_balance = user.point_balance + add_request.amount
        
        transaction_data = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": add_request.amount,
            "transaction_type": "charge",
            "description": add_request.description,
            "balance_before": user.point_balance,
            "balance_after": new_balance
        }
        
        # 트랜잭션으로 포인트 업데이트 및 거래 기록 생성
        transaction, updated_user = await self.user_repository.create_point_transaction(
            user_id, new_balance, transaction_data
        )
        
        # 충전 성공 이벤트
        log_event(
            "payment.charge.success",
            domain="app.payment",
            level="INFO",
            user_id=user_id,
            order_id=transaction_id,
            amount=add_request.amount,
            currency="P",
            balance_after=updated_user.point_balance,
        )

        # 응답 생성
        point_transaction = PointTransaction(
            id=transaction.transaction_id,
            user_id=transaction.user_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            description=transaction.description,
            balance_after=transaction.balance_after,
            created_at=transaction.created_at
        )
        
        return PointTransactionResponse(
            message=f"{add_request.amount}P가 추가되었습니다.",
            transaction=point_transaction,
            current_balance=updated_user.point_balance
        )

    async def use_points(self, user_id: str, use_request: UsePointsRequest) -> PointTransactionResponse:
        """포인트 사용"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            # 실패 이벤트
            log_event(
                "payment.charge.fail",
                domain="app.payment",
                level="ERROR",
                user_id=user_id,
                error_code="USER_NOT_FOUND",
                reason="user_not_found",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 포인트 잔액 확인
        if user.point_balance < use_request.amount:
            log_event(
                "payment.charge.fail",
                domain="app.payment",
                level="ERROR",
                user_id=user_id,
                error_code="POINTS_INSUFFICIENT",
                reason="insufficient_balance",
                balance=user.point_balance,
                amount=use_request.amount,
            )
            raise PointsInsufficientException()
        
        # 포인트 거래 생성
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        new_balance = user.point_balance - use_request.amount
        
        transaction_data = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": -use_request.amount,  # 음수로 저장
            "transaction_type": "use",
            "description": use_request.description,
            "balance_before": user.point_balance,
            "balance_after": new_balance
        }
        
        # 트랜잭션으로 포인트 업데이트 및 거래 기록 생성
        transaction, updated_user = await self.user_repository.create_point_transaction(
            user_id, new_balance, transaction_data
        )
        
        # 사용 성공 이벤트 (차감)
        log_event(
            "payment.charge.success",
            domain="app.payment",
            level="INFO",
            user_id=user_id,
            order_id=transaction_id,
            amount=-use_request.amount,
            currency="P",
            balance_after=updated_user.point_balance,
        )

        # 응답 생성
        point_transaction = PointTransaction(
            id=transaction.transaction_id,
            user_id=transaction.user_id,
            amount=abs(transaction.amount),  # 응답에서는 양수로 표시
            transaction_type=transaction.transaction_type,
            description=transaction.description,
            balance_after=transaction.balance_after,
            created_at=transaction.created_at
        )
        
        return PointTransactionResponse(
            message=f"{use_request.amount}P가 사용되었습니다.",
            transaction=point_transaction,
            current_balance=updated_user.point_balance
        )

    async def get_point_transactions(self, user_id: str, limit: int = 20, offset: int = 0) -> List[PointTransaction]:
        """포인트 거래 내역 조회"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        transactions = await self.user_repository.get_point_transactions(user_id, limit, offset)
        
        return [
            PointTransaction(
                id=t.transaction_id,
                user_id=t.user_id,
                amount=abs(t.amount),  # 절댓값으로 표시
                transaction_type=t.transaction_type,
                description=t.description,
                balance_after=t.balance_after,
                created_at=t.created_at
            )
            for t in transactions
        ]

    async def get_user_settings(self, user_id: str) -> UserSettings:
        """사용자 설정 조회"""
        settings = await self.user_repository.get_user_settings(user_id)
        if not settings:
            # 기본 설정 생성
            settings = await self.user_repository.create_user_settings(user_id)
        
        return UserSettings(
            user_id=settings.user_id,
            notification_email=settings.notification_email,
            notification_sms=settings.notification_sms,
            notification_push=settings.notification_push,
            marketing_consent=settings.marketing_consent,
            updated_at=settings.updated_at
        )

    async def update_user_settings(self, user_id: str, settings_request: UserSettingsRequest) -> UserSettings:
        """사용자 설정 업데이트"""
        # 업데이트할 데이터 준비
        update_data = {}
        if settings_request.notification_email is not None:
            update_data["notification_email"] = settings_request.notification_email
        if settings_request.notification_sms is not None:
            update_data["notification_sms"] = settings_request.notification_sms
        if settings_request.notification_push is not None:
            update_data["notification_push"] = settings_request.notification_push
        if settings_request.marketing_consent is not None:
            update_data["marketing_consent"] = settings_request.marketing_consent
        
        # 설정 업데이트
        updated_settings = await self.user_repository.update_user_settings(user_id, update_data)
        
        return UserSettings(
            user_id=updated_settings.user_id,
            notification_email=updated_settings.notification_email,
            notification_sms=updated_settings.notification_sms,
            notification_push=updated_settings.notification_push,
            marketing_consent=updated_settings.marketing_consent,
            updated_at=updated_settings.updated_at
        )

    async def get_user_stats(self, user_id: str) -> UserStatsResponse:
        """사용자 통계 조회"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        stats = await self.user_repository.get_user_stats(user_id)
        
        return UserStatsResponse(
            total_consultations=stats.get("total_consultations", 0),
            total_points_used=stats.get("total_points_used", 0),
            total_points_earned=stats.get("total_points_earned", 0),
            favorite_consultants=stats.get("favorite_consultants", []),
            member_since=user.created_at,
            last_activity=user.last_login_at
        )

    async def delete_account(self, user_id: str, delete_request: DeleteAccountRequest) -> DeleteAccountResponse:
        """계정 삭제"""
        # TODO: 비밀번호 확인은 Auth 도메인에서 처리하도록 분리 필요
        # 현재는 단순히 계정 비활성화만 처리
        
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 계정 비활성화 (실제 삭제가 아닌 상태 변경)
        deleted_at = datetime.utcnow()
        await self.user_repository.deactivate_user(user_id, delete_request.reason, deleted_at)
        
        return DeleteAccountResponse(deleted_at=deleted_at) 