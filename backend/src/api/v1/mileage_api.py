"""
마일리지 상품 API
- 마일리지 상품 목록 조회 (게스트 접근 가능)
- 마일리지 상품 구매 (사용자만 접근 가능)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria, get_db_mssql
from src.services.auth_service import get_current_user, TokenPayload
from src.common.utils.auth_utils import verify_user_role
from src.common.response import APIResponse, ok
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
from src.schemas.mileage_product_schema import MileageProductResponse, MileagePurchaseRequest


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
