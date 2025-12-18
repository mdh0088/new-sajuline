"""
결제 서비스 (관리자 백엔드)
"""
from __future__ import annotations

from typing import List, Tuple, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from sqlalchemy.orm import Session

from src.repositories.payment_repository import PaymentRepository

KST = ZoneInfo("Asia/Seoul")
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.schemas.payment_schema import (
    PaymentListParams,
    PaymentListResponse,
    PaymentWithUserItem,
    PaymentDetailResponse,
    PaymentCancelResponse,
)
from src.config.settings import settings
from src.common.logging import get_logger_with_request_id


class PaymentService:
    def __init__(self, payment_repo: PaymentRepository, mssql: Optional[Session] = None):
        self.payment_repo = payment_repo
        self.tm60_users_repo = Tm60UsersRepository(mssql) if mssql else None

    async def list_payments(self, params: PaymentListParams) -> PaymentListResponse:
        # 페이지/리밋 보정
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        # 날짜 파싱
        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        # search_name 빈 문자열 처리
        search_name_value = params.search_name.strip() if params.search_name else None
        if search_name_value == "":
            search_name_value = None

        rows, total = await self.payment_repo.get_list_with_user(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=search_name_value,
            amount=params.amount,
            payment_method=params.payment_method or None,
            payment_status=params.payment_status or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        items: List[PaymentWithUserItem] = []
        for payment, user in rows:
            # 모든 필드를 dict로 구성 (from_attributes 사용 없이 직접 매핑)
            payment_dict = {c.name: getattr(payment, c.name) for c in payment.__table__.columns}
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            items.append(PaymentWithUserItem(payment=payment_dict, user=user_dict))

        return PaymentListResponse(items=items, page=params.page, limit=params.limit, total=total)

    async def get_detail(self, payment_id: int) -> PaymentDetailResponse:
        row = await self.payment_repo.get_detail_with_user(payment_id)
        if not row:
            # 통일된 예외 클래스 파일 존재와 무관하게, FastAPI에서 404로 매핑되도록 ValueError 사용
            raise ValueError("결제를 찾을 수 없습니다")
        payment, user = row
        payment_dict = {c.name: getattr(payment, c.name) for c in payment.__table__.columns}
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return PaymentDetailResponse(payment=payment_dict, user=user_dict)

    async def cancel_payment(self, payment_id: int, ip_addr: str = "127.0.0.1") -> PaymentCancelResponse:
        """
        결제 취소 처리
        1. t_payment에서 결제 정보 조회
        2. tm60_users에서 포인트 잔액 확인
        3. Payletter API 호출
        4. 취소 성공 시 DB 업데이트 및 포인트 차감
        """
        log = get_logger_with_request_id()

        # 1. 결제 정보 조회
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"결제를 찾을 수 없습니다: payment_id={payment_id}")

        # 이미 취소된 결제인지 확인
        if payment.payment_status == "CANCEL":
            raise ValueError("이미 취소된 결제입니다")

        # 취소 가능한 상태인지 확인
        if payment.payment_status != "SUCCESS":
            raise ValueError(f"취소할 수 없는 결제 상태입니다: {payment.payment_status}")

        # 2. tm60_users 포인트 잔액 확인
        if self.tm60_users_repo and payment.point_amount and payment.point_amount > 0:
            users = await self.tm60_users_repo.find_all_by_user_id(str(payment.user_id))
            if not users:
                raise ValueError("ARS 사용자 정보를 찾을 수 없어 취소할 수 없습니다")

            user = users[0]
            if user.u_point < payment.point_amount:
                raise ValueError(f"포인트 잔액이 부족하여 취소할 수 없습니다 (필요: {payment.point_amount}, 보유: {user.u_point})")

            log.info("Point balance verified", user_id=payment.user_id, required=payment.point_amount, current=user.u_point)

        # 2. Payletter 취소 API 호출
        cancel_url = settings.payment_gateway_url.replace("/request", "/cancel")

        # payment_method 매핑 (CARD, BANK, VBANK, MOBILE, KAKAOPAY -> pgcode)
        pgcode_map = {
            "CARD": "card",
            "BANK": "transfer",
            "VBANK": "vaccount",
            "MOBILE": "mobile",
            "KAKAOPAY": "kakaopay",
        }
        pgcode = pgcode_map.get(payment.payment_method, "card")

        cancel_request = {
            "pgcode": pgcode,
            "client_id": settings.payment_client_id,
            "user_id": payment.user_id,
            "tid": payment.pg_tid,
            "ip_addr": ip_addr,
        }

        headers = {
            "Authorization": f"PLKEY {settings.payment_gateway_key}",
            "Content-Type": "application/json",
        }

        log.info("Payletter cancel request", payment_id=payment_id, tid=payment.pg_tid, pgcode=pgcode)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    cancel_url,
                    json=cancel_request,
                    headers=headers,
                )

                response_data = response.json()
                log.info("Payletter cancel response", payment_id=payment_id, response=response_data)

                # 3. 응답 처리 - cancel_date가 있으면 성공
                if "cancel_date" in response_data and response_data.get("cancel_date"):
                    # 취소 성공
                    cancelled_at = datetime.now(KST)
                    updated_payment = await self.payment_repo.update_cancel_info(
                        payment_id=payment_id,
                        cancel_amount=payment.amount,
                        cancelled_at=cancelled_at,
                        payment_status="CANCEL",
                    )

                    # 4. tm60_users 포인트 차감
                    if self.tm60_users_repo and payment.point_amount and payment.point_amount > 0:
                        try:
                            new_balance = await self.tm60_users_repo.adjust_points(
                                user_id=str(payment.user_id),
                                delta=-payment.point_amount
                            )
                            if new_balance == -1:
                                log.warning("User not found in tm60_users", user_id=payment.user_id, payment_id=payment_id)
                            elif new_balance == -2:
                                log.error("Insufficient points in tm60_users", user_id=payment.user_id, payment_id=payment_id, required=payment.point_amount)
                            else:
                                log.info("Points deducted from tm60_users", user_id=payment.user_id, payment_id=payment_id, deducted=payment.point_amount, new_balance=new_balance)
                        except Exception as point_error:
                            log.error("Failed to deduct points from tm60_users", user_id=payment.user_id, payment_id=payment_id, error=str(point_error))

                    log.info("Payment cancelled successfully", payment_id=payment_id, cancel_amount=payment.amount, payletter_cancel_date=response_data.get("cancel_date"))
                    return PaymentCancelResponse(
                        success=True,
                        payment_id=payment_id,
                        cancel_amount=payment.amount,
                        cancelled_at=cancelled_at,
                        message="결제 취소가 완료되었습니다",
                    )
                else:
                    # 취소 실패
                    error_message = response_data.get("message", "결제 취소 실패")
                    log.error("Payletter cancel failed", payment_id=payment_id, error=error_message, response=response_data)
                    raise ValueError(f"결제 취소 실패: {error_message}")

        except httpx.HTTPError as e:
            log.error("Payletter API call failed", payment_id=payment_id, error=str(e))
            raise ValueError(f"결제 취소 API 호출 실패: {str(e)}")
        except Exception as e:
            log.error("Payment cancel error", payment_id=payment_id, error=str(e))
            raise ValueError(f"결제 취소 처리 중 오류: {str(e)}")



