"""
포인트 거래 관련 비즈니스 로직 서비스
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal

from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.grade_repository import GradeRepository
from src.models.point_transaction_model import PointTransaction, TransactionType, CurrencyType, ReferenceType
from src.common.logging import logger, get_logger_with_request_id


class PointTransactionService:
    """포인트 거래 비즈니스 로직 서비스"""

    def __init__(
        self,
        point_transaction_repo: PointTransactionRepository,
        user_repo: Optional[UserRepository] = None,
        grade_repo: Optional[GradeRepository] = None
    ):
        self.point_transaction_repo = point_transaction_repo
        self.user_repo = user_repo
        self.grade_repo = grade_repo
    
    async def create_transaction(
        self,
        user_id: str,
        transaction_type: TransactionType,
        currency_type: CurrencyType,
        amount: int,
        balance_after: int,
        reference_type: Optional[ReferenceType] = None,
        reference_id: Optional[str] = None,
        description: Optional[str] = None,
        earn_rate: Optional[float] = None,
        expires_at: Optional[datetime] = None
    ) -> PointTransaction:
        """
        포인트 거래 내역 생성 (범용)
        - 이벤트, 결제, 상담 등 모든 포인트 거래에 사용 가능
        """
        log = get_logger_with_request_id()
        log.info("Creating point transaction", 
                user_id=user_id,
                transaction_type=transaction_type.value,
                currency_type=currency_type.value,
                amount=amount,
                balance_after=balance_after,
                reference_type=reference_type.value if reference_type else None,
                reference_id=reference_id)
        
        transaction = await self.point_transaction_repo.create_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            earn_rate=earn_rate,
            expires_at=expires_at
        )
        
        log.info("Point transaction created successfully",
                transaction_id=transaction.transaction_id,
                user_id=user_id,
                transaction_type=transaction_type.value,
                amount=amount)

        return transaction

    async def earn_mileage_from_payment(
        self,
        user_id: str,
        point_amount: int,
        order_no: str
    ) -> Optional[dict]:
        """
        포인트 충전 시 마일리지 적립

        Args:
            user_id: 사용자 ID
            point_amount: 충전된 포인트
            order_no: 결제 주문번호 (reference_id)

        Returns:
            적립 결과 딕셔너리 또는 None
            {
                "earned_mileage": int,
                "balance_after": int,
                "earn_rate": float
            }

        Raises:
            ValueError: 필수 Repository가 주입되지 않았을 때
        """
        log = get_logger_with_request_id()
        log.info("Starting mileage earning process",
                user_id=user_id,
                point_amount=point_amount,
                order_no=order_no)

        # Repository 의존성 검증
        if not self.user_repo:
            log.error("UserRepository not injected")
            raise ValueError("UserRepository가 주입되지 않았습니다")

        if not self.grade_repo:
            log.error("GradeRepository not injected")
            raise ValueError("GradeRepository가 주입되지 않았습니다")

        try:
            # 1. 사용자 정보 조회 (grade_code 필요)
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                log.warning("User not found for mileage earning", user_id=user_id)
                return None

            # 2. 사용자 등급의 point_earn_rate 조회
            grade = await self.grade_repo.get_by_code(user.grade_code)
            if not grade:
                log.warning("Grade not found for mileage earning",
                           user_id=user_id,
                           grade_code=user.grade_code)
                return None

            # 3. point_earn_rate가 0이면 적립하지 않음
            if grade.point_earn_rate <= 0:
                log.info("Point earn rate is 0, skipping mileage earning",
                        user_id=user_id,
                        grade_code=user.grade_code,
                        earn_rate=float(grade.point_earn_rate))
                return None

            # 4. 마일리지 계산 (point_earn_rate는 백분율)
            # 예: point_earn_rate=1, point_amount=30000 -> 300 마일리지
            mileage_to_earn = int(point_amount * float(grade.point_earn_rate) / 100)

            if mileage_to_earn <= 0:
                log.info("Calculated mileage is 0, skipping",
                        user_id=user_id,
                        point_amount=point_amount,
                        earn_rate=float(grade.point_earn_rate))
                return None

            # 5. 현재 마일리지에 추가
            new_mileage = user.mileage_point + mileage_to_earn

            # 6. t_user 테이블의 mileage_point 업데이트
            mileage_updated = await self.user_repo.update_mileage_point(user_id, new_mileage)

            if not mileage_updated:
                log.error("Failed to update user mileage",
                         user_id=user_id,
                         mileage_to_earn=mileage_to_earn)
                return None

            log.info("Mileage earned successfully",
                    user_id=user_id,
                    earned_mileage=mileage_to_earn,
                    previous_mileage=user.mileage_point,
                    new_mileage=new_mileage,
                    earn_rate=float(grade.point_earn_rate))

            # 7. t_point_transaction에 거래 내역 기록
            try:
                await self.point_transaction_repo.create_transaction(
                    user_id=user_id,
                    transaction_type=TransactionType.EARN,
                    currency_type=CurrencyType.MILEAGE,
                    amount=mileage_to_earn,
                    balance_after=new_mileage,
                    reference_type=ReferenceType.TRADE,
                    reference_id=order_no,
                    description="상품 구매 적립",
                    earn_rate=float(grade.point_earn_rate)
                )

                # 커밋은 호출자(API)에서 처리하거나 여기서 처리
                await self.point_transaction_repo.db.commit()

                log.info("Mileage transaction recorded successfully",
                        user_id=user_id,
                        transaction_type="EARN",
                        amount=mileage_to_earn,
                        order_no=order_no)

            except Exception as tx_error:
                log.error("Failed to record mileage transaction",
                         user_id=user_id,
                         error=str(tx_error))
                # 트랜잭션 기록 실패해도 마일리지는 이미 적립됨
                # 롤백하지 않고 결과 반환

            # 8. 적립 결과 반환
            return {
                "earned_mileage": mileage_to_earn,
                "balance_after": new_mileage,
                "earn_rate": float(grade.point_earn_rate)
            }

        except Exception as e:
            log.error("Mileage earning failed",
                     user_id=user_id,
                     point_amount=point_amount,
                     error=str(e))
            return None