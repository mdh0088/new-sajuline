"""
포인트 거래 내역 관련 데이터 액세스 클래스
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import logger, get_logger_with_request_id
from src.models.point_transaction_model import PointTransaction, TransactionType, CurrencyType, ReferenceType


class PointTransactionRepository:
    """포인트 거래 내역 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
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
        포인트 거래 내역 생성
        - 모든 포인트 거래에 대한 로그를 기록
        - 이벤트 포인트 지급시: transaction_type=EARN, reference_type=EVENT
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
        
        transaction = PointTransaction(
            user_id=user_id,
            transaction_type=transaction_type.value,
            currency_type=currency_type.value,
            amount=amount,
            balance_after=balance_after,
            reference_type=reference_type.value if reference_type else None,
            reference_id=reference_id,
            description=description,
            earn_rate=earn_rate,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        
        log.info("Point transaction created successfully", 
                transaction_id=transaction.transaction_id,
                user_id=user_id,
                amount=amount,
                balance_after=balance_after)
        return transaction