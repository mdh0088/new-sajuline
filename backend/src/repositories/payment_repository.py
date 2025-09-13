"""
결제 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.engine import Result

from src.models.payment_model import Payment
from src.models.point_product_model import PointProduct
from src.schemas.payment_schema import PaymentCreate, PaymentUpdate
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException


class PaymentRepository:
    """결제 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create(self, payment_data: PaymentCreate) -> Payment:
        """결제 생성"""
        payment = Payment(
            order_no=payment_data.order_no,
            user_id=payment_data.user_id,
            product_id=payment_data.product_id,
            payment_type=payment_data.payment_type,
            amount=payment_data.amount,
            point_amount=payment_data.point_amount,
            bonus_point=payment_data.bonus_point,
            mileage_used=payment_data.mileage_used,
            payment_method=payment_data.payment_method,
            pg_provider=payment_data.pg_provider,
            cid=payment_data.cid,
            pay_info=payment_data.pay_info,
            tax_amount=payment_data.tax_amount,
            domestic_flag=payment_data.domestic_flag
        )
        
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment
    
    @logger.catch(reraise=True)
    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """결제 ID로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up payment by ID", payment_id=payment_id)
        
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await self.db.execute(stmt)
        payment = result.scalar_one_or_none()
        
        log.info("Payment lookup completed", payment_id=payment_id, found=payment is not None)
        return payment
    
    @logger.catch(reraise=True)
    async def get_list_by_user_id(
        self,
        user_id: str,
        payment_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """사용자 ID별 결제 목록 조회"""
        log = get_logger_with_request_id()
        log.info("Getting payments by user ID", user_id=user_id, payment_status=payment_status)
        
        stmt = select(Payment).where(Payment.user_id == user_id)
        
        if payment_status:
            stmt = stmt.where(Payment.payment_status == payment_status)
        
        stmt = stmt.offset(skip).limit(limit).order_by(Payment.created_at.desc())
        
        result = await self.db.execute(stmt)
        payments = list(result.scalars().all())
        
        log.info("Payments lookup by user completed", user_id=user_id, count=len(payments))
        return payments
    
    @logger.catch(reraise=True)
    async def get_count_by_user_id(
        self,
        user_id: str,
        payment_status: Optional[str] = None
    ) -> int:
        """사용자 ID별 결제 총 개수"""
        stmt = select(func.count(Payment.payment_id)).where(
            Payment.user_id == user_id
        )
        
        if payment_status:
            stmt = stmt.where(Payment.payment_status == payment_status)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    @logger.catch(reraise=True)
    async def get_monthly_total_amount_by_user_id(self, user_id: str) -> Decimal:
        """사용자 ID별 이번 달 총 결제 금액 (SUCCESS 상태만)"""
        log = get_logger_with_request_id()
        log.info("Getting this month total payment amount by user ID", user_id=user_id)
        
        # 이번 달 시작일과 끝일 계산
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        if now.month == 12:
            end_of_month = datetime(now.year + 1, 1, 1)
        else:
            end_of_month = datetime(now.year, now.month + 1, 1)
        
        stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.user_id == user_id,
                Payment.payment_status == "SUCCESS",
                Payment.paid_at >= start_of_month,
                Payment.paid_at < end_of_month
            )
        )
        
        result = await self.db.execute(stmt)
        total_amount = result.scalar() or Decimal('0.00')
        
        log.info("This month total payment amount calculated", 
                user_id=user_id, 
                total_amount=total_amount,
                month=f"{now.year}-{now.month:02d}")
        return total_amount

    @logger.catch(reraise=True)
    async def get_point_charge_history(
        self,
        user_id: str,
        start_dt: datetime,
        end_dt: datetime,
        order_type: str,
        page: int,
        limit: int,
    ) -> Tuple[List[Tuple[Optional[datetime], Optional[str], int, int]], int]:
        """
        포인트 충전 내역 조회
        - t_payment 기준으로 t_point_product 조인하여 product_name 조회
        - 필드: paid_at, product_name, point_amount, amount
        - 기간: paid_at between [start_dt 00:00:00, end_dt 23:59:59]
        - 정렬: latest(paid_at desc), highest(amount desc), lowest(amount asc)
        - SUCCESS 상태만 포함
        Returns: list of tuple(paid_at, product_name, point_amount, amount)
        """
        log = get_logger_with_request_id()
        log.info("Getting point charge history", user_id=user_id, start=str(start_dt), end=str(end_dt), order_type=order_type)

        dt_start = datetime(start_dt.year, start_dt.month, start_dt.day)
        dt_end = datetime(end_dt.year, end_dt.month, end_dt.day, 23, 59, 59)

        order_clause = None
        if order_type == "latest":
            order_clause = Payment.paid_at.desc()
        elif order_type == "highest":
            order_clause = Payment.amount.desc()
        elif order_type == "lowest":
            order_clause = Payment.amount.asc()
        else:
            order_clause = Payment.paid_at.desc()

        # 기본 쿼리 (정렬/페이징 제외)
        base_stmt = (
            select(
                Payment.paid_at,
                PointProduct.product_name,
                Payment.point_amount,
                Payment.amount,
            )
            .join(PointProduct, Payment.product_id == PointProduct.product_id, isouter=True)
            .where(
                and_(
                    Payment.user_id == user_id,
                    Payment.payment_status == "SUCCESS",
                    Payment.paid_at >= dt_start,
                    Payment.paid_at <= dt_end,
                )
            )
        )

        # 총 개수
        count_stmt = select(func.count(Payment.payment_id)).where(
            and_(
                Payment.user_id == user_id,
                Payment.payment_status == "SUCCESS",
                Payment.paid_at >= dt_start,
                Payment.paid_at <= dt_end,
            )
        )
        count_result = await self.db.execute(count_stmt)
        total: int = int(count_result.scalar() or 0)

        # 페이징 적용 쿼리
        stmt = base_stmt.order_by(order_clause).offset(max(0, (page - 1) * limit)).limit(limit)

        result = await self.db.execute(stmt)
        rows: List[Tuple[Optional[datetime], Optional[str], int, int]] = list(result.all())
        log.info("Point charge history fetched", user_id=user_id, count=len(rows), total=total, page=page, limit=limit)
        return rows, total
    
    @logger.catch(reraise=True)
    async def update(self, payment_id: int, update_data: PaymentUpdate) -> bool:
        """결제 정보 수정"""
        log = get_logger_with_request_id()
        log.info("Updating payment", payment_id=payment_id)
        
        # None이 아닌 필드만 업데이트
        update_values = {}
        if update_data.payment_status is not None:
            update_values["payment_status"] = update_data.payment_status
        if update_data.pg_tid is not None:
            update_values["pg_tid"] = update_data.pg_tid
        if update_data.paid_at is not None:
            update_values["paid_at"] = update_data.paid_at
        if update_data.cancel_reason is not None:
            update_values["cancel_reason"] = update_data.cancel_reason
        if update_data.refund_amount is not None:
            update_values["refund_amount"] = update_data.refund_amount
        
        if not update_values:
            log.warning("No fields to update", payment_id=payment_id)
            return False
        
        update_values["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(Payment)
            .where(Payment.payment_id == payment_id)
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Payment update completed", payment_id=payment_id, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def update_status(self, payment_id: int, payment_status: str, pg_tid: Optional[str] = None) -> bool:
        """결제 상태 업데이트"""
        log = get_logger_with_request_id()
        log.info("Updating payment status", payment_id=payment_id, status=payment_status)
        
        update_values = {
            "payment_status": payment_status,
            "updated_at": datetime.utcnow()
        }
        
        if pg_tid:
            update_values["pg_tid"] = pg_tid
        
        # 결제 완료 시 paid_at 설정
        if payment_status == "SUCCESS":
            update_values["paid_at"] = datetime.utcnow()
        # 취소 시 cancelled_at 설정
        elif payment_status == "CANCELLED":
            update_values["cancelled_at"] = datetime.utcnow()
        
        stmt = (
            update(Payment)
            .where(Payment.payment_id == payment_id)
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Payment status update completed", payment_id=payment_id, status=payment_status, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def cancel_payment(self, payment_id: int, cancel_reason: str, refund_amount: Optional[Decimal] = None) -> bool:
        """결제 취소"""
        log = get_logger_with_request_id()
        log.info("Cancelling payment", payment_id=payment_id, reason=cancel_reason)
        
        update_values = {
            "payment_status": "CANCELLED",
            "cancelled_at": datetime.utcnow(),
            "cancel_reason": cancel_reason,
            "updated_at": datetime.utcnow()
        }
        
        if refund_amount is not None:
            update_values["refund_amount"] = refund_amount
        
        stmt = (
            update(Payment)
            .where(Payment.payment_id == payment_id)
            .values(**update_values)
            .execution_options(synchronize_session="evaluate")
        )
        
        result = await self.db.execute(stmt)
        success = result.rowcount > 0
        
        log.info("Payment cancellation completed", payment_id=payment_id, success=success)
        return success
    
    @logger.catch(reraise=True)
    async def exists_by_order_no(self, order_no: str) -> bool:
        """주문번호 존재 여부 확인"""
        stmt = select(Payment.payment_id).where(Payment.order_no == order_no)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None