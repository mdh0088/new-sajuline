"""
포인트 거래 내역 관련 데이터 액세스 클래스
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

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

    @logger.catch(reraise=True)
    async def get_mileage_history(
        self,
        user_id: str,
        transaction_type: TransactionType,
        start_dt: Optional[str] = None,
        end_dt: Optional[str] = None,
        order_type: str = "latest",
        page: int = 1,
        limit: int = 20
    ) -> tuple[list[PointTransaction], int]:
        """
        마일리지 내역 조회 (페이징, 날짜 필터, 정렬)
        - currency_type = POINT
        - reference_type: transaction_type에 따라 결정
          * USE: MILEAGE_PRODUCT (마일리지 상품 구매)
          * EARN: MILEAGE (마일리지 적립)
        - transaction_type = EARN or USE (파라미터로 받음)
        - 날짜 범위 필터링 (start_dt ~ end_dt)
        - 정렬: latest(최신순), highest(높은순), lowest(낮은순)

        Args:
            user_id: 사용자 ID
            transaction_type: 거래 유형 (EARN/USE)
            start_dt: 시작일 (yyyy-mm-dd)
            end_dt: 종료일 (yyyy-mm-dd)
            order_type: 정렬 방식 (latest/highest/lowest)
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            (items, total_count) 튜플
        """
        log = get_logger_with_request_id()

        # transaction_type에 따라 reference_type 결정
        # USE: 마일리지 상품 구매 (MILEAGE_PRODUCT)
        # EARN: 마일리지 적립 (MILEAGE)
        reference_type_value = (
            ReferenceType.MILEAGE_PRODUCT.value if transaction_type == TransactionType.USE
            else ReferenceType.MILEAGE.value
        )

        log.info(
            "Get mileage history",
            user_id=user_id,
            transaction_type=transaction_type.value,
            reference_type=reference_type_value,
            start_dt=start_dt,
            end_dt=end_dt,
            order_type=order_type,
            page=page,
            limit=limit
        )

        # 기본 쿼리 조건
        base_query = (
            select(PointTransaction)
            .where(PointTransaction.user_id == user_id)
            .where(PointTransaction.currency_type == CurrencyType.POINT.value)
            .where(PointTransaction.reference_type == reference_type_value)
            .where(PointTransaction.transaction_type == transaction_type.value)
        )

        # 날짜 범위 필터링
        if start_dt:
            start_datetime = datetime.strptime(start_dt, "%Y-%m-%d")
            base_query = base_query.where(PointTransaction.created_at >= start_datetime)

        if end_dt:
            end_datetime = datetime.strptime(end_dt, "%Y-%m-%d")
            # 종료일 포함하려면 다음날 00:00:00 전까지
            from datetime import timedelta
            end_datetime = end_datetime + timedelta(days=1)
            base_query = base_query.where(PointTransaction.created_at < end_datetime)

        # 전체 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 정렬 처리
        if order_type == "highest":
            order_clause = desc(PointTransaction.amount)
        elif order_type == "lowest":
            order_clause = PointTransaction.amount.asc()
        else:  # latest (기본값)
            order_clause = desc(PointTransaction.created_at)

        # 페이징 처리된 데이터 조회
        offset = (page - 1) * limit
        stmt = (
            base_query
            .order_by(order_clause)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        items = result.scalars().all()

        log.info(
            "Mileage history fetched",
            user_id=user_id,
            transaction_type=transaction_type.value,
            total=total,
            count=len(items)
        )

        return list(items), total