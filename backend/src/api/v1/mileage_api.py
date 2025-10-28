"""
마일리지 상품 API
- 마일리지 상품 목록 조회 (게스트 접근 가능)
- 마일리지 상품 구매 (사용자만 접근 가능)
- 마일리지 적립/사용 내역 조회 (사용자만 접근 가능)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria, get_db_mssql
from src.services.auth_service import get_current_user, TokenPayload
from src.common.utils.auth_utils import verify_user_role
from src.common.response import APIResponse, ok, APIResponseBuilder
from src.common.logging import get_logger_with_request_id
from src.repositories.mileage_repository import MileageProductRepository
from src.repositories.user_repository import UserRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.mileage_service import MileageProductService
from src.services.user_service import UserService
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.auth_service import AuthService
from src.repositories.counselor_repository import CounselorRepository
from src.schemas.mileage_product_schema import MileageProductResponse, MileagePurchaseRequest, MileageHistoryResponse
from src.models.point_transaction_model import TransactionType


router = APIRouter(prefix="/mileage-products", tags=["mileage-products"])


# Dependency Injection
def get_mileage_repo(db: AsyncSession = Depends(get_db_maria)) -> MileageProductRepository:
    return MileageProductRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    return UserRepository(db)


def get_transaction_repo(db: AsyncSession = Depends(get_db_maria)) -> PointTransactionRepository:
    return PointTransactionRepository(db)


def get_tm60_users_service():
    """TM60 사용자 서비스 의존성 주입"""
    for mssql_session in get_db_mssql():
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)


def get_mileage_service(
    mileage_repo: MileageProductRepository = Depends(get_mileage_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    transaction_repo: PointTransactionRepository = Depends(get_transaction_repo),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> MileageProductService:
    return MileageProductService(mileage_repo, user_repo, transaction_repo, tm60_users_service)


def get_user_service(
    db: AsyncSession = Depends(get_db_maria)
) -> UserService:
    return UserService(UserRepository(db), CounselorRepository(db), AuthService())


@router.get("/list", response_model=APIResponse[list[MileageProductResponse]], summary="마일리지 상품 목록 조회")
async def list_mileage_products(
    service: MileageProductService = Depends(get_mileage_service)
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
    current_user: TokenPayload = Depends(get_current_user),
    service: MileageProductService = Depends(get_mileage_service),
    user_service: UserService = Depends(get_user_service)
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
    transaction_type: TransactionType = Query(..., description="거래 유형 (EARN: 적립, USE: 사용)"),
    start_dt: str = Query(None, description="시작일 (yyyy-mm-dd)"),
    end_dt: str = Query(None, description="종료일 (yyyy-mm-dd)"),
    order_type: str = Query("latest", description="정렬 방식 (latest: 최신순, highest: 높은순, lowest: 낮은순)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user),
    service: MileageProductService = Depends(get_mileage_service)
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
