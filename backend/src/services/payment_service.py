"""
결제 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.payment_model import Payment
from src.schemas.payment_schema import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentSummary,
    PaymentListResponse
)
from src.repositories.payment_repository import PaymentRepository


class PaymentService:
    """결제 비즈니스 로직 서비스"""
    
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo
    
    async def create_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """
        결제 생성
        - 주문번호 중복 검증
        - 결제 생성
        """
        log = get_logger_with_request_id()
        log.info("Creating payment", 
                user_id=payment_data.user_id, 
                order_no=payment_data.order_no,
                amount=payment_data.amount)
        
        # 주문번호 중복 검증
        if await self.payment_repo.exists_by_order_no(payment_data.order_no):
            log.warning("Order number already exists", order_no=payment_data.order_no)
            raise DuplicateError("이미 존재하는 주문번호입니다.")
        
        # 결제 금액 유효성 검증
        if payment_data.amount <= 0:
            log.warning("Invalid payment amount", amount=payment_data.amount)
            raise ValidationError("결제 금액은 0보다 커야 합니다.")
        
        # 결제 생성
        try:
            payment = await self.payment_repo.create(payment_data)
            await self.payment_repo.db.commit()
            
            log.info("Payment created successfully", 
                    payment_id=payment.payment_id,
                    order_no=payment.order_no,
                    amount=payment.amount)
            
            return PaymentResponse.model_validate(payment)
            
        except Exception as e:
            await self.payment_repo.db.rollback()
            log.warning("Payment creation failed", 
                       order_no=payment_data.order_no, 
                       error=str(e))
            raise ValidationError(f"결제 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_user_payment_history(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        payment_status: Optional[str] = None
    ) -> PaymentListResponse:
        """
        사용자별 결제 내역 조회 (요구사항)
        - 페이징 처리
        - 결제 상태별 필터링
        """
        log = get_logger_with_request_id()
        log.info("Getting user payment history", 
                user_id=user_id, 
                page=page, 
                size=size, 
                payment_status=payment_status)
        
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        skip = (page - 1) * size
        
        # 결제 목록 조회
        payments = await self.payment_repo.get_list_by_user_id(
            user_id=user_id,
            payment_status=payment_status,
            skip=skip,
            limit=size
        )
        
        # 전체 개수 조회
        total = await self.payment_repo.get_count_by_user_id(
            user_id=user_id,
            payment_status=payment_status
        )
        
        # 응답 데이터 변환
        payment_summaries = [
            PaymentSummary.model_validate(payment) 
            for payment in payments
        ]
        
        log.info("User payment history retrieved", 
                user_id=user_id, 
                count=len(payment_summaries), 
                total=total)
        
        return PaymentListResponse(
            payments=payment_summaries,
            total=total,
            page=page,
            size=size
        )
    
    async def get_user_monthly_total_payment_amount(self, user_id: str) -> Decimal:
        """
        사용자별 이번 달 총 결제 금액 조회 (요구사항)
        - payment_status가 SUCCESS이고 paid_at이 이번 달인 경우만 합계
        """
        log = get_logger_with_request_id()
        log.info("Getting user this month total payment amount", user_id=user_id)
        
        total_amount = await self.payment_repo.get_monthly_total_amount_by_user_id(user_id)
        
        log.info("User this month total payment amount calculated", 
                user_id=user_id, 
                total_amount=total_amount)
        
        return total_amount
    
    async def get_user_payment_stats(self, user_id: str) -> dict:
        """
        사용자 결제 통계 정보
        - 총 결제 건수
        - 성공 결제 건수  
        - 총 결제 금액 (SUCCESS만)
        """
        log = get_logger_with_request_id()
        log.info("Getting user payment stats", user_id=user_id)
        
        # 전체 결제 건수
        total_count = await self.payment_repo.get_count_by_user_id(user_id)
        
        # 성공 결제 건수
        success_count = await self.payment_repo.get_count_by_user_id(user_id, "SUCCESS")
        
        # 총 결제 금액 (SUCCESS만)
        total_amount = await self.payment_repo.get_monthly_total_amount_by_user_id(user_id)
        
        stats = {
            "user_id": user_id,
            "total_payment_count": total_count,
            "success_payment_count": success_count,
            "total_payment_amount": total_amount
        }
        
        log.info("User payment stats calculated", 
                user_id=user_id, 
                total_count=total_count,
                success_count=success_count,
                total_amount=total_amount)
        
        return stats
    
    async def update_payment_status(
        self,
        payment_id: int,
        payment_status: str,
        pg_tid: Optional[str] = None
    ) -> PaymentResponse:
        """
        결제 상태 업데이트
        - SUCCESS, FAILED, CANCELLED 등
        """
        log = get_logger_with_request_id()
        log.info("Updating payment status", 
                payment_id=payment_id, 
                status=payment_status)
        
        try:
            success = await self.payment_repo.update_status(
                payment_id=payment_id,
                payment_status=payment_status,
                pg_tid=pg_tid
            )
            
            if not success:
                log.warning("Payment not found for status update", payment_id=payment_id)
                raise NotFoundError("업데이트할 결제를 찾을 수 없습니다.")
            
            await self.payment_repo.db.commit()
            
            # 업데이트된 결제 조회하여 반환
            updated_payment = await self.payment_repo.get_by_id(payment_id)
            
            if not updated_payment:
                raise NotFoundError("업데이트된 결제를 찾을 수 없습니다.")
            
            log.info("Payment status updated successfully", 
                    payment_id=payment_id,
                    status=payment_status)
            
            return PaymentResponse.model_validate(updated_payment)
            
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except Exception as e:
            await self.payment_repo.db.rollback()
            log.warning("Payment status update failed", 
                       payment_id=payment_id,
                       error=str(e))
            raise ValidationError(f"결제 상태 업데이트 중 오류가 발생했습니다: {str(e)}")
    
    async def cancel_payment(
        self,
        payment_id: int,
        cancel_reason: str,
        refund_amount: Optional[Decimal] = None
    ) -> PaymentResponse:
        """
        결제 취소
        - 취소 사유 필수
        - 환불 금액 선택적
        """
        log = get_logger_with_request_id()
        log.info("Cancelling payment", 
                payment_id=payment_id, 
                reason=cancel_reason)
        
        if not cancel_reason.strip():
            log.warning("Cancel reason is required", payment_id=payment_id)
            raise ValidationError("취소 사유는 필수입니다.")
        
        try:
            success = await self.payment_repo.cancel_payment(
                payment_id=payment_id,
                cancel_reason=cancel_reason,
                refund_amount=refund_amount
            )
            
            if not success:
                log.warning("Payment not found for cancellation", payment_id=payment_id)
                raise NotFoundError("취소할 결제를 찾을 수 없습니다.")
            
            await self.payment_repo.db.commit()
            
            # 취소된 결제 조회하여 반환
            cancelled_payment = await self.payment_repo.get_by_id(payment_id)
            
            if not cancelled_payment:
                raise NotFoundError("취소된 결제를 찾을 수 없습니다.")
            
            log.info("Payment cancelled successfully", 
                    payment_id=payment_id,
                    refund_amount=refund_amount)
            
            return PaymentResponse.model_validate(cancelled_payment)
            
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except Exception as e:
            await self.payment_repo.db.rollback()
            log.warning("Payment cancellation failed", 
                       payment_id=payment_id,
                       error=str(e))
            raise ValidationError(f"결제 취소 중 오류가 발생했습니다: {str(e)}")
    
    async def get_payment_by_id(self, payment_id: int) -> PaymentResponse:
        """결제 상세 조회"""
        log = get_logger_with_request_id()
        log.info("Getting payment by ID", payment_id=payment_id)
        
        payment = await self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            log.warning("Payment not found", payment_id=payment_id)
            raise NotFoundError("결제 정보를 찾을 수 없습니다.")
        
        log.info("Payment retrieved successfully", payment_id=payment_id)
        return PaymentResponse.model_validate(payment)