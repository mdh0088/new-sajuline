"""
공지사항 관련 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria
from src.repositories.notice_repository import NoticeRepository
from src.services.notice_service import NoticeService
from src.schemas.notice_schema import NoticeResponse, NoticeListParams, NoticeDetailResponse
from src.models.notice_model import NoticeType, TargetAudience
from src.common.response import APIResponse, APIResponseBuilder, ok
from src.common.logging import get_logger_with_request_id
# 공지 API는 게스트 접근 허용 → 권한 검사 미사용

router = APIRouter(prefix="/notices", tags=["notices"])


# Dependency injection functions
def get_notice_repository(db: AsyncSession = Depends(get_db_maria)) -> NoticeRepository:
    """공지사항 리포지토리 의존성 주입"""
    return NoticeRepository(db)


def get_notice_service(notice_repo: NoticeRepository = Depends(get_notice_repository)) -> NoticeService:
    """공지사항 서비스 의존성 주입"""
    return NoticeService(notice_repo)


@router.get("/", response_model=APIResponse, summary="공지사항 목록 조회")
async def get_notice_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    notice_type: Optional[NoticeType] = Query(None, description="공지 타입 필터"),
    target_audience: Optional[TargetAudience] = Query(None, description="대상 필터"),
    is_active: Optional[bool] = Query(None, description="활성화 상태 필터"),
    is_important: Optional[bool] = Query(None, description="중요 공지 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색어"),
    notice_service: NoticeService = Depends(get_notice_service)
) -> APIResponse:
    """
    공지사항 목록을 조회합니다.
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 10, 최대: 100)
    - **notice_type**: 공지 타입 필터 (GENERAL, EVENT, UPDATE)
    - **target_audience**: 대상 필터 (ALL, USER, COUNSELOR)
    - **is_active**: 활성화 상태 필터
    - **is_important**: 중요 공지 필터
    - **search**: 제목/내용 검색어
    """
    log = get_logger_with_request_id()
    log.info("API: Getting notice list", 
            page=page, 
            limit=limit, 
            notice_type=notice_type,
            target_audience=target_audience,
            is_active=is_active,
            is_important=is_important,
            search=search)
    
    params = NoticeListParams(
        page=page,
        limit=limit,
        notice_type=notice_type,
        target_audience=target_audience,
        is_active=is_active,
        is_important=is_important,
        search=search
    )
    
    notices, page, limit, total = await notice_service.get_notice_list(params)
    
    log.info("API: Notice list retrieved successfully", 
            count=len(notices), 
            total=total, 
            page=page, 
            limit=limit)
    
    return APIResponseBuilder.paginated(
        data=notices,
        page=page,
        limit=limit,
        total=total,
        message="공지사항 목록 조회 성공"
    )


@router.get("/public", response_model=APIResponse, summary="공지사항 목록 조회 (게스트)")
async def get_public_notices(
    notice_service: NoticeService = Depends(get_notice_service)
) -> APIResponse:
    """
    게스트도 접근 가능한 공지 목록 조회
    - 필터 고정: is_active=True, target_audience='ALL'
    - 정렬: is_important DESC, created_at DESC
    - 페이지네이션 없음 (요구사항에 page/limit 없음)
    """
    log = get_logger_with_request_id()
    log.info("API: Getting public notice list")
    notices = await notice_service.get_public_notice_list()
    return ok(data=notices, message="공지사항 목록 조회 성공")


@router.get("/{notice_id}", response_model=APIResponse[NoticeDetailResponse], summary="공지사항 단일 조회")
async def get_notice(
    notice_id: int,
    notice_service: NoticeService = Depends(get_notice_service)
) -> APIResponse[NoticeDetailResponse]:
    """
    공지사항 단일 항목을 조회합니다.
    
    - **notice_id**: 조회할 공지사항 ID
    """
    log = get_logger_with_request_id()
    log.info("API: Getting notice by ID", notice_id=notice_id)
    notice = await notice_service.get_notice_detail_with_adjacent(notice_id)
    log.info("API: Notice retrieved successfully", notice_id=notice_id, title=notice.title)
    return ok(data=notice, message="공지사항 조회 성공")


@router.post("/{notice_id}/views", response_model=APIResponse, summary="공지 조회수 증가")
async def increase_notice_view(
    notice_id: int,
    notice_service: NoticeService = Depends(get_notice_service)
) -> APIResponse:
    """공지 접속 시 view_count +1"""
    log = get_logger_with_request_id()
    log.info("API: Increase view count", notice_id=notice_id)
    await notice_service.increase_view_count(notice_id)
    return ok(data={"notice_id": notice_id}, message="조회수 증가")