"""
마일리지 상품 API
- 마일리지 상품 목록 조회 (게스트 접근 가능)
- 마일리지 상품 구매 (사용자만 접근 가능)
- 마일리지 적립/사용 내역 조회 (사용자만 접근 가능)
"""
from fastapi import APIRouter, Depends, Query

from src.core.dependencies import MileageServiceDep, UserServiceDep
from src.services.auth_service import get_current_user, TokenPayload
from src.common.utils.auth_utils import verify_user_role
from src.common.response import APIResponse, ok, APIResponseBuilder
from src.common.logging import get_logger_with_request_id
from src.schemas.mileage_product_schema import MileageProductResponse, MileagePurchaseRequest, MileageHistoryResponse
from src.models.point_transaction_model import TransactionType


router = APIRouter(prefix="/mileage-products", tags=["mileage-products"])


@router.get("/list", response_model=APIResponse[list[MileageProductResponse]], summary="마일리지 상품 목록 조회")
async def list_mileage_products(
    service: MileageServiceDep
) -> APIResponse[list[MileageProductResponse]]:
    """
    활성 마일리지 상품 목록 조회
    - 권한 체크 없음(게스트 가능)
    - is_active=True만 노출
    - created_at DESC 정렬
    """
    log = get_logger_with_request_id()
    log.info("API: list mileage products")
    items = await service.list_active_products()
    return ok(data=items, message="마일리지 상품 목록 조회 성공")


@router.post("/purchase", response_model=APIResponse[dict], summary="마일리지 상품 구매")
async def purchase_mileage_product(
    payload: MileagePurchaseRequest,
    service: MileageServiceDep,
    user_service: UserServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[dict]:
    """
    마일리지 상품 구매
    - 사용자(user)만 가능
    - 마일리지 포인트로 포인트 상품 구매
    """
    log = get_logger_with_request_id()
    verify_user_role(current_user)

    user_id = current_user.sub
    log.info("API: purchase mileage product", user_id=user_id, mileage_id=payload.mileage_id)

    # 유저 정보 조회 (존재 여부 확인)
    await user_service.get_user_by_id(user_id)

    # 구매 처리
    result = await service.purchase_mileage_product(user_id, payload.mileage_id)

    return ok(data=result, message="마일리지 상품 구매 완료")


@router.get("/history", response_model=APIResponse, summary="마일리지 적립/사용 내역 조회")
async def get_mileage_history(
    service: MileageServiceDep,
    transaction_type: TransactionType = Query(..., description="거래 유형 (EARN: 적립, USE: 사용)"),
    start_dt: str = Query(None, description="시작일 (yyyy-mm-dd)"),
    end_dt: str = Query(None, description="종료일 (yyyy-mm-dd)"),
    order_type: str = Query("latest", description="정렬 방식 (latest: 최신순, highest: 높은순, lowest: 낮은순)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse:
    """
    마일리지 적립/사용 내역 조회 (페이징, 날짜 필터, 정렬)
    - 사용자(user)만 가능
    - transaction_type으로 적립(EARN) 또는 사용(USE) 필터링
    - 날짜 범위 필터링 (start_dt ~ end_dt)
    - 정렬: latest(최신순), highest(높은순), lowest(낮은순)
    """
    log = get_logger_with_request_id()
    verify_user_role(current_user)

    user_id = current_user.sub
    log.info(
        "API: get mileage history",
        user_id=user_id,
        transaction_type=transaction_type.value,
        start_dt=start_dt,
        end_dt=end_dt,
        order_type=order_type,
        page=page,
        limit=limit
    )

    # 내역 조회
    data, total = await service.get_mileage_history(
        user_id=user_id,
        transaction_type=transaction_type,
        start_dt=start_dt,
        end_dt=end_dt,
        order_type=order_type,
        page=page,
        limit=limit
    )

    # 페이지네이션 응답
    return APIResponseBuilder.paginated(
        data=data,
        page=page,
        limit=limit,
        total=total,
        message=f"마일리지 {'적립' if transaction_type == TransactionType.EARN else '사용'} 내역 조회 성공"
    )
