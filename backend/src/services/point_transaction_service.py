"""
포인트 거래 관련 비즈니스 로직 서비스
"""
from typing import Optional
from datetime import datetime

from src.repositories.point_transaction_repository import PointTransactionRepository
from src.models.point_transaction_model import PointTransaction, TransactionType, CurrencyType, ReferenceType
from src.common.logging import logger, get_logger_with_request_id


class PointTransactionService:
    """포인트 거래 비즈니스 로직 서비스"""
    
    def __init__(self, point_transaction_repo: PointTransactionRepository):
        self.point_transaction_repo = point_transaction_repo
    
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