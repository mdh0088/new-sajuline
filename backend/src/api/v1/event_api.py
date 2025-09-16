"""
이벤트 관련 공개 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria, get_db_mssql
from src.repositories.event_repository import EventRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.point_transaction_service import PointTransactionService
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.event_service import EventService
from src.schemas.event_schema import EventResponse, EventDetailResponse
from src.common.response import APIResponse, ok
from src.common.logging import get_logger_with_request_id


router = APIRouter(prefix="/events", tags=["events"])


# Dependency injection functions
def get_event_repository(db: AsyncSession = Depends(get_db_maria)) -> EventRepository:
    return EventRepository(db)


def get_point_transaction_service(db: AsyncSession = Depends(get_db_maria)) -> PointTransactionService:
    repo = PointTransactionRepository(db)
    return PointTransactionService(repo)


def get_tm60_users_service():
    for mssql_session in get_db_mssql():
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)


def get_event_service(
    event_repo: EventRepository = Depends(get_event_repository),
    point_transaction_service: PointTransactionService = Depends(get_point_transaction_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> EventService:
    return EventService(event_repo, point_transaction_service, tm60_users_service)


@router.get("/public", response_model=APIResponse, summary="이벤트 목록 조회 (게스트)")
async def get_public_events(
    event_service: EventService = Depends(get_event_service)
) -> APIResponse:
    """
    게스트도 접근 가능한 이벤트 목록 조회
    - 필터 고정: is_active=True
    - 정렬: created_at DESC
    - 페이지네이션 없음
    """
    log = get_logger_with_request_id()
    log.info("API: Getting public event list")
    events = await event_service.get_public_event_list()
    return ok(data=events, message="이벤트 목록 조회 성공")


@router.get("/{event_id}", response_model=APIResponse[EventDetailResponse], summary="이벤트 단일 조회")
async def get_event_detail(
    event_id: int,
    event_service: EventService = Depends(get_event_service)
) -> APIResponse[EventDetailResponse]:
    """
    이벤트 단일 항목을 조회합니다. 이전/다음 event_id 포함
    """
    log = get_logger_with_request_id()
    log.info("API: Getting event by ID", event_id=event_id)
    event = await event_service.get_event_detail_with_adjacent(event_id)
    return ok(data=event, message="이벤트 조회 성공")


# view_count 기능 없음


