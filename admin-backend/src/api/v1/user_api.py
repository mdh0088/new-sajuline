"""
사용자 관리 API (관리자 백엔드)

- 목록 조회: t_user 기준 필터/페이징
- 각 사용자별 MSSQL tm60_users를 user_id=u_id로 매칭하여 전체 목록 포함
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.common.response import APIResponse, APIResponseBuilder, ok
from src.schemas.user_schema import UserListParams, UserUpdateRequest, UserPointAdjustRequest
from src.services.user_service import UserService
from src.services.notification_service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.core.database import get_db as get_db_maria, get_db_mssql
from src.repositories.user_repository import UserRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.repositories.notification_repository import NotificationRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.schemas.point_transaction_schema import PointTransactionItem


router = APIRouter(prefix="/users", tags=["users"])


def _get_user_service(
    db: AsyncSession = Depends(get_db_maria),
    mssql: Session = Depends(get_db_mssql),
) -> UserService:
    return UserService(UserRepository(db), Tm60UsersRepository(mssql), pt_repo=PointTransactionRepository(db))


def _get_notification_service(
    db: AsyncSession = Depends(get_db_maria),
) -> NotificationService:
    return NotificationService(NotificationRepository(db))


@router.get("/list", response_model=APIResponse, summary="유저 목록 조회")
async def get_user_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    search_type: str = Query("all", description="검색 타입: all|nickname|email|phone"),
    search_name: Optional[str] = Query(None, description="검색 키워드"),
    join_type: Optional[str] = Query(None, description="가입 유형: COMMON|NAVER|KAKAO"),
    grade: Optional[str] = Query(None, description="등급코드"),
    start_dt: Optional[str] = Query(None, description="생성일 시작 yyyy-mm-dd"),
    end_dt: Optional[str] = Query(None, description="생성일 종료 yyyy-mm-dd"),
    service: UserService = Depends(_get_user_service),
):
    params = UserListParams(
        page=page,
        limit=limit,
        search_type=search_type,
        search_name=search_name,
        join_type=join_type,
        grade=grade,
        start_dt=start_dt,
        end_dt=end_dt,
    )
    items, page, limit, total = await service.get_user_list(params)
    return APIResponseBuilder.paginated(
        data=[i.model_dump() for i in items],
        page=page,
        limit=limit,
        total=total,
        message="유저 목록 조회 성공",
    )


@router.get("/detail", response_model=APIResponse, summary="회원 상세 조회")
async def get_user_detail(
    user_id: str = Query(..., description="회원 ID"),
    service: UserService = Depends(_get_user_service),
):
    data = await service.get_user_detail(user_id)
    return ok(data=data, message="회원 상세 조회 성공")


@router.get("/notification-logs", response_model=APIResponse, summary="회원 알리톡 로그 목록 조회")
async def get_user_notification_logs(
    user_id: str = Query(..., description="회원 ID"),
    service: NotificationService = Depends(_get_notification_service),
):
    logs = await service.get_user_logs(user_id)
    return ok(data={"logs": [l.model_dump() for l in logs]}, message="알리톡 로그 조회 성공")


@router.patch("/update", response_model=APIResponse, summary="회원 정보 수정")
async def update_user(
    payload: UserUpdateRequest,
    service: UserService = Depends(_get_user_service),
):
    data = await service.update_user(payload)
    return ok(data=data, message="회원 정보 수정 성공")


@router.post("/points/adjust", response_model=APIResponse, summary="회원 포인트 지급/차감")
async def adjust_points(
    payload: UserPointAdjustRequest,
    service: UserService = Depends(_get_user_service),
):
    data = await service.adjust_user_points(payload)
    return ok(data=data, message="포인트 조정 성공")


@router.get("/mileage/use-logs", response_model=APIResponse, summary="회원 마일리지 사용 내역")
async def get_mileage_use_logs(
    user_id: str = Query(..., description="회원 ID"),
    service: UserService = Depends(_get_user_service),
):
    items = await service.get_mileage_use_logs(user_id)
    return ok(data={"items": [i.model_dump() for i in items]}, message="마일리지 사용 내역 조회 성공")


@router.get("/mileage/earn-logs", response_model=APIResponse, summary="회원 마일리지 적립 내역")
async def get_mileage_earn_logs(
    user_id: str = Query(..., description="회원 ID"),
    service: UserService = Depends(_get_user_service),
):
    items = await service.get_mileage_earn_logs(user_id)
    return ok(data={"items": [i.model_dump() for i in items]}, message="마일리지 적립 내역 조회 성공")


