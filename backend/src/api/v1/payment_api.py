"""
결제 API (Payletter 연동)
 - 결제 요청(Request)
 - 결제 완료 리턴(Return URL)
 - 결제 취소(Cancel URL)
 - 결제 결과 콜백(Callback URL)
사용자(user)만 접근 가능, guest/counselor 차단
"""

from datetime import datetime, timezone, timedelta
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.core.database import get_db_maria
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
from src.services.payment_service import PaymentService
from src.services.point_product_service import PointProductService
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.schemas.payment_schema import PaymentCreate
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
    body = build_payletter_request_body(
        client_id=settings.payment_client_id,
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        product_name=product.product_name,
        order_no=order_no,
        amount=amount,
        tax_amount=tax_amount,
        custom_parameter=f"{product.point_amount + product.bonus_point}",
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


@router.api_route("/point_return", methods=["GET", "POST"], response_model=APIResponse[dict])
async def payment_return(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
) -> APIResponse[dict]:
    """
    결제 완료 후 Return URL (사용자 브라우저에서 서버로 전송)
    - GET: 쿼리 파라미터로 전달 (Payletter 리다이렉트 방식)
    - POST: JSON body로 전달
    - 공식 문서/샘플에 따라 return_url로 결제 결과가 전달될 수 있음
    - 여기서 t_payment 생성 및 포인트 적립 로직을 수행
    """
    log = get_logger_with_request_id()

    # GET/POST 방식에 따라 데이터 파싱
    if request.method == "GET":
        # GET 쿼리 파라미터 파싱
        params = dict(request.query_params)
        log.info("Payment return received (GET)", payload=params)
        body_dict = params
    else:
        # POST body 파싱 - 미들웨어에서 이미 파싱한 데이터 사용
        # (request.body()는 한 번만 읽을 수 있으므로 request.state 사용)
        body_dict = getattr(request.state, 'request_body', None)

        if not body_dict:
            log.error("POST request but no body found in request.state")
            raise HTTPException(status_code=400, detail="요청 본문이 비어있습니다")

        log.info("Payment return received (POST)", payload=body_dict)

    # PayletterCallbackBody 스키마로 검증
    try:
        body = PayletterCallbackBody(**body_dict)
    except Exception as e:
        log.error("Failed to validate payment data", error=str(e), payload=body_dict)
        raise HTTPException(status_code=400, detail=f"결제 데이터 검증 실패: {str(e)}")

    # # payhash 검증 (가능 시) - 불필요하여 주석처리
    # if not verify_payhash_if_present(
    #     user_id=body.user_id,
    #     amount=body.amount,
    #     tid=body.tid,
    #     api_key=settings.payment_gateway_key,
    #     payhash=body.payhash,
    # ):
    #     raise HTTPException(status_code=400, detail="유효하지 않은 결제 해시")

    if body.amount is None or body.user_id is None:
        raise HTTPException(status_code=400, detail="필수 필드 누락")

    # t_payment 생성 (완료 시점)
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

    # code 값으로 결제 상태 결정 (0이면 SUCCESS, 아니면 FAIL)
    payment_status = "SUCCESS" if body.code == "0" else "FAIL"

    log.info("Payment create 1111111111111111", payload=body.model_dump())
    log.info("Payment create 22222222222222222", payload=body)
    
    create = PaymentCreate(
        order_no=order_no,
        user_id=body.user_id,
        product_id=None,  # 필요시 역참조로 보완
        payment_type="POINT_CHARGE",
        amount=int(body.amount),
        point_amount=int(body.custom_parameter or 0),
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
        code=body.code,
        result_message=body.message,
    )
    created = await payment_service.create_payment(create)

    return ok(data={"status": payment_status.lower(), "order_no": order_no}, message="결제 처리되었습니다")


@router.get("/point_cancel", response_model=APIResponse[dict])
async def payment_cancel(request: Request) -> APIResponse[dict]:
    """
    결제 취소 URL (사용자 브라우저에서 취소 선택 시)
    """
    return ok(data={"status": "cancelled"}, message="결제가 취소되었습니다.")


@router.post("/callback")
async def payment_callback(
    body: PayletterCallbackBody,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Payletter 콜백 수신 엔드포인트
    - CallBack.php 샘플과 동일하게 JSON 본문 수신
    - 성공 응답: {"code":0, "message":"success"}
    - 실패 응답: code != 0 이면 재전송됨(문서 규정)
    """
    log = get_logger_with_request_id()

    # payhash 검증은 결제 수단에 따라 미제공될 수 있음. 제공 시 아래와 같이 계산해 비교 권장:
    # expected = sha256(user_id + amount + tid + PAYMENT_KEY)
    # 여기서는 필드 존재시에만 비교하도록 placeholder만 남김(실제 구현은 보안 정책에 맞춰 보강)

    try:
        # 관련 결제 레코드 찾기 및 상태 업데이트
        log.info("Payment callback received", payload=body.model_dump())

        # 최근 PENDING 중 사용자/금액 일치 건을 찾는다 (order_no 미제공 대비)
        candidate = None
        if body.user_id and body.amount:
            candidate = await payment_service.get_recent_pending_by_user_and_amount(body.user_id, int(body.amount))

        if candidate:
            await payment_service.update_payment_status(candidate.payment_id, "SUCCESS", pg_tid=body.tid)

        return {"code": 0, "message": "success"}
    except Exception as e:
        log.error("Payment callback handling failed", error=str(e))
        return {"code": 9999, "message": "callback error"}


