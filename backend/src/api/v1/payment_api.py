"""
결제 API (Payletter 연동)
 - 결제 요청(Request)
 - 결제 완료 리턴(Return URL)
 - 결제 취소(Cancel URL)
 - 결제 결과 콜백(Callback URL)
사용자(user)만 접근 가능, guest/counselor 차단
"""

from datetime import datetime, timezone, timedelta
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.core.database import get_db_maria, get_db_mssql
from src.services.auth_service import get_current_user, TokenPayload
from src.common.utils.auth_utils import verify_user_role
from src.common.response import ok, APIResponse
from src.common.logging import get_logger_with_request_id
from src.common.utils.payletter import (
    generate_order_no,
    calc_amounts,
    build_payletter_request_body,
)
from src.repositories.point_product_repository import PointProductRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.user_repository import UserRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.grade_repository import GradeRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.payment_service import PaymentService
from src.services.point_product_service import PointProductService
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.point_transaction_service import PointTransactionService
from src.schemas.payment_schema import PaymentCreate
from src.models.point_transaction_model import TransactionType, CurrencyType, ReferenceType
from decimal import Decimal
from src.schemas.payletter_schema import (
    PaymentRequestPayload,
    PayletterRequestResponse,
    PayletterCallbackBody,
)


router = APIRouter(prefix="/payment", tags=["payment"])


# Dependencies (align with grade_api style)
def get_point_product_repository(db: AsyncSession = Depends(get_db_maria)) -> PointProductRepository:
    return PointProductRepository(db)


def get_point_product_service(
    repo: PointProductRepository = Depends(get_point_product_repository)
) -> PointProductService:
    return PointProductService(repo)


def get_user_service(
    db: AsyncSession = Depends(get_db_maria)
) -> UserService:
    return UserService(UserRepository(db), CounselorRepository(db), AuthService())


def get_payment_service(
    db: AsyncSession = Depends(get_db_maria)
) -> PaymentService:
    return PaymentService(PaymentRepository(db))


def get_tm60_users_service():
    """TM60 사용자 서비스 의존성 주입"""
    for mssql_session in get_db_mssql():
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)


def get_grade_repository(db: AsyncSession = Depends(get_db_maria)) -> GradeRepository:
    return GradeRepository(db)


def get_point_transaction_repository(db: AsyncSession = Depends(get_db_maria)) -> PointTransactionRepository:
    return PointTransactionRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    return UserRepository(db)


def get_point_transaction_service(
    point_transaction_repo: PointTransactionRepository = Depends(get_point_transaction_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    grade_repo: GradeRepository = Depends(get_grade_repository)
) -> PointTransactionService:
    return PointTransactionService(point_transaction_repo, user_repo, grade_repo)


KST = timezone(timedelta(hours=9))


async def _get_product(repo: PointProductRepository, product_id: int):
    from sqlalchemy import select
    from src.models.point_product_model import PointProduct
    result = await repo.db.execute(select(PointProduct).where(PointProduct.product_id == product_id))
    return result.scalar_one_or_none()

@router.post("/request", response_model=APIResponse[PayletterRequestResponse])
async def request_payment(
    payload: PaymentRequestPayload,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    product_service: PointProductService = Depends(get_point_product_service),
    user_service: UserService = Depends(get_user_service),
) -> APIResponse[PayletterRequestResponse]:
    """
    결제 요청 API: Payletter 결제 토큰/URL 발급 요청 후 반환
    - 사용자(user)만 가능
    - guest/counselor 차단
    """
    log = get_logger_with_request_id()
    verify_user_role(current_user)

    # 상품 조회 (API -> Service -> Repository)
    product = await product_service.get_product(payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 금액 계산
    amount, tax_amount, discount_amount = calc_amounts(product.price, product.discount_rate)

    now = datetime.now(KST)
    order_no = generate_order_no(now)

    # 유저 정보 조회 (API -> Service -> Repository)
    user_id = current_user.sub
    user = await user_service.get_user_by_id(user_id)
    user_name = user.nickname or ""
    user_email = user.email or ""

    # 만료일/시간
    expire_date = (now + timedelta(days=1)).strftime("%Y%m%d")
    expire_time = now.strftime("%H%M")

    # Payletter 요청 페이로드 구성
    # payment_method는 프론트에서 pgcode(allthegate|virtualaccount|kakaopay)로 전달됨
    pgcode = payload.payment_method

    # custom_parameter를 JSON 객체로 구성
    custom_param_obj = {
        "point_amount": product.point_amount + product.bonus_point,
        "product_id": product.product_id
    }

    body = build_payletter_request_body(
        client_id=settings.payment_client_id,
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        product_name=product.product_name,
        order_no=order_no,
        amount=amount+tax_amount,
        tax_amount=tax_amount,
        custom_parameter=json.dumps(custom_param_obj),
        return_url=settings.payment_return_url,
        callback_url=settings.payment_callback_url,
        cancel_url=settings.payment_cancel_url,
        pgcode=pgcode,
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"PLKEY {settings.payment_gateway_key}",
    }

    # Payletter 결제 요청
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            if not settings.payment_gateway_url:
                raise HTTPException(status_code=500, detail="PAYMENT_GATEWAY_URL 미설정")
            endpoint = settings.payment_gateway_url.rstrip("/")
            if not endpoint.endswith("/v1.0/payments/request"):
                endpoint = f"{endpoint}/v1.0/payments/request"
            resp = await client.post(endpoint, json=body, headers=headers)
            if resp.status_code != 200:
                detail = resp.text or "PG 오류"
                raise HTTPException(status_code=resp.status_code, detail=detail)
            data = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        log.error("Payletter request failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"PG 연동 실패: {type(e).__name__}: {str(e)}")

    # 요청 단계에서는 DB 생성 금지 (결제 완료 후 처리)

    return ok(data=PayletterRequestResponse(**data), message="결제 요청 성공")


@router.post("/point_callback")
async def payment_callback(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service),
    point_transaction_service: PointTransactionService = Depends(get_point_transaction_service),
):
    """
    Payletter Callback URL (Server-to-Server)
    - 결제 성공 시에만 호출됨
    - JSON body로 전달
    - 주요 비즈니스 로직 처리: 결제 생성, 포인트 충전
    - 응답: {"code": 0, "message": "success"} (실패시 5분마다 20번 재전송)
    """
    log = get_logger_with_request_id()

    # POST body 파싱
    body_dict = getattr(request.state, 'request_body', None)
    if not body_dict:
        log.error("POST request but no body found in request.state")
        return {"code": 9999, "message": "요청 본문이 비어있습니다"}

    log.info("Payment callback received", payload=body_dict)

    # PayletterCallbackBody 스키마로 검증
    try:
        body = PayletterCallbackBody(**body_dict)
    except Exception as e:
        log.error("Failed to validate payment data", error=str(e), payload=body_dict)
        return {"code": 9999, "message": f"데이터 검증 실패: {str(e)}"}

    if body.amount is None or body.user_id is None:
        return {"code": 9999, "message": "필수 필드 누락"}

    # Callback은 성공시에만 호출되므로 payment_status는 항상 SUCCESS
    payment_status = "SUCCESS"
    
    # order_no는 body에서 전달된 값 사용, 없으면 현재 시간 기반 생성
    now = datetime.now(KST)
    order_no = body.order_no or generate_order_no(now)

    # transaction_date를 paid_at으로 변환
    paid_at = None
    if body.transaction_date:
        try:
            paid_at = datetime.strptime(body.transaction_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            log.warning("Failed to parse transaction_date", transaction_date=body.transaction_date)

    # custom_parameter JSON 파싱
    custom_param = {}
    product_id = None
    point_amount = 0

    if body.custom_parameter:
        try:
            custom_param = json.loads(body.custom_parameter)
            product_id = custom_param.get("product_id")
            point_amount = custom_param.get("point_amount", 0)
        except (json.JSONDecodeError, TypeError):
            # 구 버전 호환: 숫자 문자열인 경우
            try:
                point_amount = int(body.custom_parameter)
            except (ValueError, TypeError):
                point_amount = 0

    # t_payment 생성
    create = PaymentCreate(
        order_no=order_no,
        user_id=body.user_id,
        product_id=product_id,
        payment_type="POINT_CHARGE",
        amount=int(body.amount),
        point_amount=point_amount,
        mileage_used=0,
        payment_method=body.pgcode or "",
        payment_status=payment_status,
        pg_tid=body.tid,
        cid=body.cid or "",
        billkey=body.billkey,
        card_info=body.card_info,
        pay_info=body.pay_info or "",
        tax_amount=str(body.tax_amount) if body.tax_amount else str((int(body.amount) // 10) if body.amount else 0),
        domestic_flag=body.domestic_flag or "",
        install_month=body.install_month,
        pay_hash=body.payhash,
        taxfree_amount=str(body.taxfree_amount) if body.taxfree_amount else None,
        nonsettle_amount=None,
        discount_amount=None,
        point_use_flag=None,
        disposable_cup_deposit=str(body.disposable_cup_deposit) if body.disposable_cup_deposit else None,
        paid_at=paid_at,
        code="0",  # Callback은 성공시에만 호출
        result_message=body.message or "결제 성공",
    )
    
    try:
        created = await payment_service.create_payment(create)
        log.info("Payment created via callback", payment_id=created.payment_id, order_no=order_no)
    except Exception as e:
        log.error("Failed to create payment", error=str(e), order_no=order_no)
        return {"code": 9999, "message": f"결제 생성 실패: {str(e)}"}

    # 포인트 충전
    if point_amount > 0:
        try:
            new_points = await tm60_users_service.update_user_points(body.user_id, point_amount)
            log.info("User points increased", user_id=body.user_id, point_amount=point_amount, new_points=new_points)
        except Exception as e:
            log.error("Failed to increase user points", user_id=body.user_id, point_amount=point_amount, error=str(e))
            return {"code": 9999, "message": f"포인트 충전 실패: {str(e)}"}

        # 마일리지 적립
        try:
            mileage_result = await point_transaction_service.earn_mileage_from_payment(
                user_id=body.user_id,
                point_amount=point_amount,
                order_no=order_no
            )
            if mileage_result:
                log.info("Mileage earned successfully",
                        user_id=body.user_id,
                        earned_mileage=mileage_result["earned_mileage"],
                        balance_after=mileage_result["balance_after"],
                        earn_rate=mileage_result["earn_rate"])
            else:
                log.info("Mileage earning skipped", user_id=body.user_id, reason="earn_rate is 0 or user/grade not found")
        except Exception as e:
            # 마일리지 적립 실패해도 결제는 성공으로 처리 (포인트는 이미 충전됨)
            log.error("Mileage earning failed", user_id=body.user_id, error=str(e))

    # 성공 응답
    return {"code": 0, "message": "success"}


@router.get("/point_cancel", response_model=APIResponse[dict])
async def payment_cancel(request: Request) -> APIResponse[dict]:
    """
    결제 취소 URL (사용자 브라우저에서 취소 선택 시)
    """
    return ok(data={"status": "cancelled"}, message="결제가 취소되었습니다.")


@router.api_route("/point_return", methods=["GET", "POST"])
async def payment_return(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Payletter Return URL (사용자 브라우저 리다이렉트)
    - Callback 이후 호출됨
    - GET/POST 방식으로 전달
    - order_no로 결제 조회 후 실패시 상태 업데이트
    - 성공/실패 여부에 따라 HTML 응답 반환 (PC/모바일 분기)
    """
    log = get_logger_with_request_id()

    # GET/POST 방식에 따라 데이터 파싱
    if request.method == "GET":
        params = dict(request.query_params)
        log.info("Payment return received (GET)", payload=params)
        body_dict = params
    else:
        body_dict = getattr(request.state, 'request_body', None)
        if not body_dict:
            log.error("POST request but no body found in request.state")
            return HTMLResponse(content="<html><body><script>alert('요청 오류'); window.location.href='/point';</script></body></html>")
        log.info("Payment return received (POST)", payload=body_dict)

    # PayletterCallbackBody 스키마로 검증
    try:
        body = PayletterCallbackBody(**body_dict)
    except Exception as e:
        log.error("Failed to validate payment data", error=str(e), payload=body_dict)
        return HTMLResponse(content="<html><body><script>alert('데이터 검증 실패'); window.location.href='/point';</script></body></html>")

    order_no = body.order_no
    if not order_no:
        log.error("order_no is missing in return URL")
        return HTMLResponse(content="<html><body><script>alert('주문번호 누락'); window.location.href='/point';</script></body></html>")

    # order_no로 기존 결제 조회
    existing_payment = await payment_service.get_payment_by_order_no(order_no)
    
    if not existing_payment:
        log.warning("Payment not found for order_no", order_no=order_no)
        # Callback이 먼저 와야 하는데 없는 경우 (비정상)
        return HTMLResponse(content="<html><body><script>alert('결제 정보를 찾을 수 없습니다'); window.location.href='/point';</script></body></html>")

    # 가상계좌 체크: payment_method가 virtualaccount인 경우 입금 대기 상태
    payment_method = existing_payment.payment_method

    # code 값 확인: 0이 아니면 실패 (가상계좌 제외)
    return_code = body.code or ""

    if payment_method == "virtualaccount":
        # 가상계좌는 입금 대기 상태로 처리
        log.info("Virtual account payment pending", order_no=order_no)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>가상계좌 발급</title>
        </head>
        <body>
            <script>
                (function() {
                    const messageData = {type: 'payment_pending', message: '가상계좌가 발급되었습니다. 입금해주세요.'};
                    let sent = false;

                    // 1. iframe 케이스 (우선순위 높음)
                    try {
                        if (window.parent && window.parent !== window) {
                            console.log('[Payment] Sending postMessage to parent (iframe)');
                            window.parent.postMessage(messageData, '*');
                            sent = true;
                        }
                    } catch(e) {
                        console.error('[Payment] Failed to send to parent:', e);
                    }

                    // 2. 새 창 케이스
                    try {
                        if (window.opener && !window.opener.closed) {
                            console.log('[Payment] Sending postMessage to opener (popup)');
                            window.opener.postMessage(messageData, '*');
                            window.close();
                            sent = true;
                        }
                    } catch(e) {
                        console.error('[Payment] Failed to send to opener:', e);
                    }

                    // 3. Fallback: 단독 페이지
                    if (!sent) {
                        console.log('[Payment] Fallback: Full page redirect');
                        alert('가상계좌가 발급되었습니다. 입금해주세요.');
                        window.location.href = '/point';
                    }
                })();
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    if return_code != "0":
        # 실패 처리: payment_status, code, result_message, updated_at 업데이트
        from src.schemas.payment_schema import PaymentUpdate
        from datetime import datetime

        update_data = PaymentUpdate(
            payment_status="FAIL",
            code=return_code,
            result_message=body.message or "결제 실패",
        )

        await payment_service.update_payment(existing_payment.payment_id, update_data)
        log.info("Payment status updated to FAIL", order_no=order_no, code=return_code)

        # 실패 HTML 응답
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>결제 실패</title>
        </head>
        <body>
            <script>
                (function() {
                    const messageData = {type: 'payment_fail'};
                    let sent = false;

                    // 1. iframe 케이스 (우선순위 높음)
                    try {
                        if (window.parent && window.parent !== window) {
                            console.log('[Payment] Sending postMessage to parent (iframe)');
                            window.parent.postMessage(messageData, '*');
                            sent = true;
                        }
                    } catch(e) {
                        console.error('[Payment] Failed to send to parent:', e);
                    }

                    // 2. 새 창 케이스
                    try {
                        if (window.opener && !window.opener.closed) {
                            console.log('[Payment] Sending postMessage to opener (popup)');
                            window.opener.postMessage(messageData, '*');
                            window.close();
                            sent = true;
                        }
                    } catch(e) {
                        console.error('[Payment] Failed to send to opener:', e);
                    }

                    // 3. Fallback: 단독 페이지
                    if (!sent) {
                        console.log('[Payment] Fallback: Full page redirect');
                        alert('결제가 실패했습니다. 다시 시도해주세요.');
                        window.location.href = '/point';
                    }
                })();
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    # 성공 처리: Callback에서 이미 처리했으므로 HTML만 반환
    log.info("Payment return success", order_no=order_no)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>결제 성공</title>
    </head>
    <body>
        <script>
            (function() {
                const messageData = {type: 'payment_success'};
                let sent = false;

                // 1. iframe 케이스 (우선순위 높음)
                try {
                    if (window.parent && window.parent !== window) {
                        console.log('[Payment] Sending postMessage to parent (iframe)');
                        window.parent.postMessage(messageData, '*');
                        sent = true;
                    }
                } catch(e) {
                    console.error('[Payment] Failed to send to parent:', e);
                }

                // 2. 새 창 케이스
                try {
                    if (window.opener && !window.opener.closed) {
                        console.log('[Payment] Sending postMessage to opener (popup)');
                        window.opener.postMessage(messageData, '*');
                        window.close();
                        sent = true;
                    }
                } catch(e) {
                    console.error('[Payment] Failed to send to opener:', e);
                }

                // 3. Fallback: 단독 페이지
                if (!sent) {
                    console.log('[Payment] Fallback: Full page redirect');
                    alert('결제가 성공적으로 완료되었습니다.');
                    window.location.href = '/point';
                }
            })();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)



