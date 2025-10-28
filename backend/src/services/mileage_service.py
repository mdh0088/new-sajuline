"""
마일리지 상품 서비스 클래스
비즈니스 로직과 DTO 매핑
"""
from fastapi import HTTPException
from src.common.logging import get_logger_with_request_id
from src.repositories.mileage_repository import MileageProductRepository
from src.repositories.user_repository import UserRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.services.ars.tm60_users_service import Tm60UsersService
from src.schemas.mileage_product_schema import MileageProductResponse, MileageHistoryResponse
from src.models.point_transaction_model import TransactionType, CurrencyType, ReferenceType


class MileageProductService:
    """마일리지 상품 비즈니스 로직 서비스"""

    def __init__(
        self,
        mileage_repo: MileageProductRepository,
        user_repo: UserRepository,
        transaction_repo: PointTransactionRepository,
        tm60_users_service: Tm60UsersService
    ):
        self.mileage_repo = mileage_repo
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo
        self.tm60_users_service = tm60_users_service

    async def list_active_products(self) -> list[MileageProductResponse]:
        """활성 마일리지 상품 목록 조회"""
        log = get_logger_with_request_id()
        log.info("Service: list active mileage products")
        items = await self.mileage_repo.list_active_products()
        return [MileageProductResponse.model_validate(x) for x in items]

    async def purchase_mileage_product(self, user_id: str, mileage_id: int) -> dict:
        """
        마일리지 상품 구매 비즈니스 로직
        1. 유저 조회
        2. 마일리지 상품 조회
        3. 마일리지 포인트 검증
        4. tm60_users u_point 증가
        5. user mileage_point 차감
        6. t_point_transaction 로그 생성
        """
        log = get_logger_with_request_id()
        log.info("Service: purchase mileage product", user_id=user_id, mileage_id=mileage_id)

        # 1. 유저 조회
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            log.warning("User not found", user_id=user_id)
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 2. 마일리지 상품 조회
        product = await self.mileage_repo.get_by_id(mileage_id)
        if not product:
            log.warning("Mileage product not found", mileage_id=mileage_id)
            raise HTTPException(status_code=404, detail="마일리지 상품을 찾을 수 없습니다.")

        if not product.is_active:
            log.warning("Mileage product is not active", mileage_id=mileage_id)
            raise HTTPException(status_code=400, detail="비활성화된 상품입니다.")

        # 3. 마일리지 포인트 검증
        if user.mileage_point < product.m_product_value:
            log.warning(
                "Insufficient mileage points",
                user_id=user_id,
                user_mileage=user.mileage_point,
                product_value=product.m_product_value
            )
            raise HTTPException(status_code=400, detail="마일리지 포인트가 부족합니다.")

        # 4. tm60_users u_point 증가
        try:
            new_u_point = await self.tm60_users_service.update_user_points(user_id, product.charge_point)
            log.info(
                "TM60 user points updated",
                user_id=user_id,
                charge_point=product.charge_point,
                new_u_point=new_u_point
            )
        except Exception as e:
            log.error("Failed to update tm60 user points", user_id=user_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"포인트 충전 실패: {str(e)}")

        # 5. user mileage_point 차감
        try:
            new_mileage_point = user.mileage_point - product.m_product_value
            await self.user_repo.update_mileage_point(user_id, new_mileage_point)
            log.info(
                "User mileage point updated",
                user_id=user_id,
                old_mileage=user.mileage_point,
                product_value=product.m_product_value,
                new_mileage=new_mileage_point
            )
        except Exception as e:
            log.error("Failed to update user mileage point", user_id=user_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"마일리지 차감 실패: {str(e)}")

        # 6. t_point_transaction 로그 생성
        try:
            transaction = await self.transaction_repo.create_transaction(
                user_id=user_id,
                transaction_type=TransactionType.USE,
                currency_type=CurrencyType.POINT,
                amount=product.charge_point,
                balance_after=new_u_point,
                reference_type=ReferenceType.MILEAGE_PRODUCT,
                reference_id=str(mileage_id),
                description="포인트 상품 구매"
            )
            log.info(
                "Point transaction created",
                transaction_id=transaction.transaction_id,
                user_id=user_id,
                amount=product.charge_point
            )
        except Exception as e:
            log.error("Failed to create point transaction", user_id=user_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"거래 내역 생성 실패: {str(e)}")

        return {
            "message": "마일리지 상품 구매 완료",
            "charged_point": product.charge_point,
            "new_u_point": new_u_point,
            "used_mileage": product.m_product_value,
            "new_mileage_point": new_mileage_point
        }

    async def get_mileage_history(
        self,
        user_id: str,
        transaction_type: TransactionType,
        start_dt: str = None,
        end_dt: str = None,
        order_type: str = "latest",
        page: int = 1,
        limit: int = 20
    ) -> tuple[list[MileageHistoryResponse], int]:
        """
        마일리지 내역 조회 (페이징, 날짜 필터, 정렬)
        - 적립 내역 (EARN) 또는 사용 내역 (USE)
        - transaction_type을 파라미터로 받아 필터링
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
            (response_list, total_count) 튜플
        """
        log = get_logger_with_request_id()
        log.info(
            "Service: get mileage history",
            user_id=user_id,
            transaction_type=transaction_type.value,
            start_dt=start_dt,
            end_dt=end_dt,
            order_type=order_type,
            page=page,
            limit=limit
        )

        # Repository에서 데이터 조회
        items, total = await self.transaction_repo.get_mileage_history(
            user_id=user_id,
            transaction_type=transaction_type,
            start_dt=start_dt,
            end_dt=end_dt,
            order_type=order_type,
            page=page,
            limit=limit
        )

        # DTO 변환
        response_list = [MileageHistoryResponse.model_validate(item) for item in items]

        log.info(
            "Mileage history retrieved",
            user_id=user_id,
            transaction_type=transaction_type.value,
            total=total,
            count=len(response_list)
        )

        return response_list, total
