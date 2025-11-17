"""
Notification API Endpoints
Kakao AlimTalk test API
"""
from typing import Optional
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria
from src.repositories.notification_repository import NotificationRepository
from src.services.notification_service import NotificationService
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id
from pydantic import BaseModel, Field

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Dependency injection functions
def get_notification_repository(db: AsyncSession = Depends(get_db_maria)) -> NotificationRepository:
    """알림 리포지토리 의존성 주입"""
    return NotificationRepository(db)


def get_notification_service(
    notification_repo: NotificationRepository = Depends(get_notification_repository)
) -> NotificationService:
    """알림 서비스 의존성 주입"""
    return NotificationService(notification_repo)


# ==========================================
# Request/Response Schemas
# ==========================================

class TestKakaoAlimTalkRequest(BaseModel):
    """카카오 알림톡 테스트 요청 스키마"""
    notification_type: str = Field(..., description="알림 유형: cs_login, cs_faq, user_faq, user_virtual, user_money_request, user_charge_confirm, user_join")
    phone: str = Field(..., description="수신자 전화번호")

    # 공통 파라미터
    user_nick_name: Optional[str] = Field(None, description="사용자 닉네임")
    nick_name: Optional[str] = Field(None, description="닉네임 (회원가입)")
    user_id: Optional[str] = Field(None, description="사용자 ID")

    # cs_login 파라미터
    cs_idx: Optional[int] = Field(None, description="상담사 인덱스")

    # user_virtual 파라미터
    regist_date: Optional[str] = Field(None, description="등록일")
    amount: Optional[int] = Field(None, description="금액")
    order_no: Optional[str] = Field(None, description="주문번호")
    product_name: Optional[str] = Field(None, description="상품명")

    # user_money_request 파라미터
    bank: Optional[str] = Field(None, description="은행")
    account: Optional[str] = Field(None, description="계좌번호")
    depositor: Optional[str] = Field(None, description="예금주")

    # user_charge_confirm 파라미터
    point: Optional[int] = Field(None, description="포인트")


# ==========================================
# API Endpoints
# ==========================================

@router.post(
    "/test/kakao-alimtalk",
    response_model=APIResponse,
    summary="카카오 알림톡 테스트 발송 (관리자용)",
    description="카카오 알림톡 7가지 유형 테스트 발송",
    status_code=status.HTTP_200_OK
)
async def test_send_kakao_alimtalk(
    request: TestKakaoAlimTalkRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    카카오 알림톡 테스트 발송

    - **notification_type**: 알림 유형 구분
      - cs_login: 상담사 접속 알림
      - cs_faq: 상담사 게시글 알림
      - user_faq: 사용자 게시글 알림
      - user_virtual: 무통장 입금 완료
      - user_money_request: 입금 요청
      - user_charge_confirm: 결제 완료
      - user_join: 회원 가입
    """
    log = get_logger_with_request_id()
    log.info("Test Kakao AlimTalk request", notification_type=request.notification_type, phone=request.phone)

    result = None

    # 알림 유형별 분기
    if request.notification_type == "cs_login":
        if not request.user_nick_name or not request.cs_idx:
            return ok(data=None, message="cs_login requires: user_nick_name, cs_idx")
        result = await notification_service.cs_login_alert(
            phone=request.phone,
            user_nick_name=request.user_nick_name,
            cs_idx=request.cs_idx
        )

    elif request.notification_type == "cs_faq":
        result = await notification_service.cs_faq_alert(phone=request.phone)

    elif request.notification_type == "user_faq":
        if not request.user_nick_name:
            return ok(data=None, message="user_faq requires: user_nick_name")
        result = await notification_service.user_faq_alert(
            phone=request.phone,
            user_nick_name=request.user_nick_name
        )

    elif request.notification_type == "user_virtual":
        if not all([request.user_nick_name, request.regist_date, request.amount, request.order_no, request.product_name]):
            return ok(data=None, message="user_virtual requires: user_nick_name, regist_date, amount, order_no, product_name")
        result = await notification_service.user_virtual_alert(
            phone=request.phone,
            user_nick_name=request.user_nick_name,
            regist_date=request.regist_date,
            amount=request.amount,
            order_no=request.order_no,
            product_name=request.product_name
        )

    elif request.notification_type == "user_money_request":
        if not all([request.user_nick_name, request.amount, request.bank, request.account, request.depositor, request.regist_date, request.product_name]):
            return ok(data=None, message="user_money_request requires: user_nick_name, amount, bank, account, depositor, regist_date, product_name")
        result = await notification_service.user_money_request_alert(
            phone=request.phone,
            user_nick_name=request.user_nick_name,
            amount=request.amount,
            bank=request.bank,
            account=request.account,
            depositor=request.depositor,
            regist_date=request.regist_date,
            product_name=request.product_name
        )

    elif request.notification_type == "user_charge_confirm":
        if not all([request.user_nick_name, request.order_no, request.product_name, request.amount, request.point]):
            return ok(data=None, message="user_charge_confirm requires: user_nick_name, order_no, product_name, amount, point")
        result = await notification_service.user_charge_confirm_alert(
            phone=request.phone,
            user_nick_name=request.user_nick_name,
            order_no=request.order_no,
            product_name=request.product_name,
            amount=request.amount,
            point=request.point
        )

    elif request.notification_type == "user_join":
        if not request.nick_name or not request.user_id:
            return ok(data=None, message="user_join requires: nick_name, user_id")
        result = await notification_service.user_join_alert(
            phone=request.phone,
            nick_name=request.nick_name,
            user_id=request.user_id
        )

    else:
        return ok(data=None, message="Invalid notification_type")

    log.info("Test Kakao AlimTalk completed", is_success=result.get("is_success"), code=result.get("code"))

    return ok(data=result, message="카카오 알림톡 테스트 발송 완료")
