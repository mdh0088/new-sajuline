"""
등급 관리 API (관리자 백엔드)

- 등록 목록 조회: 페이징 없이 전체를 grade_level DESC로 반환
- 등급 상세 조회: grade_code로 단건 조회
- 월별 등급 업데이트: 전월 결제 금액 기준으로 사용자 등급 갱신
- 등급 변경 로그 조회: 사용자별 등급 변경 이력 조회
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.grade_repository import GradeRepository
from src.repositories.user_repository import UserRepository
from src.repositories.grade_change_log_repository import GradeChangeLogRepository
from src.services.grade_service import GradeService
from src.schemas.grade_schema import (
    GradeListResponse,
    GradeDetailResponse,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradeDeleteResponse,
    UsersByGradeResponse,
    MonthlyGradeUpdateRequest,
    MonthlyGradeUpdateResponse,
    GradeChangeLogListResponse,
)


router = APIRouter(prefix="/grades", tags=["grades"])


def _get_grade_service(db: AsyncSession = Depends(get_db_maria)) -> GradeService:
    """기본 등급 서비스 (CRUD 용)"""
    return GradeService(GradeRepository(db), user_repo=UserRepository(db))


def _get_grade_service_with_batch(db: AsyncSession = Depends(get_db_maria)) -> GradeService:
    """배치 처리용 등급 서비스 (등급 변경 로그 포함)"""
    return GradeService(
        grade_repo=GradeRepository(db),
        user_repo=UserRepository(db),
        grade_change_log_repo=GradeChangeLogRepository(db)
    )


@router.get("/list", response_model=APIResponse[GradeListResponse], summary="등급 목록 조회 (전체, 내림차순)")
async def get_grade_list(service: GradeService = Depends(_get_grade_service)):
    data = await service.get_all()
    return ok(data=data, message="등급 목록 조회 성공")


@router.get("/detail", response_model=APIResponse[GradeDetailResponse], summary="등급 상세 조회")
async def get_grade_detail(
    grade_code: str = Query(..., description="등급 코드"),
    service: GradeService = Depends(_get_grade_service),
):
    data = await service.get_detail(grade_code)
    return ok(data=data, message="등급 상세 조회 성공")


@router.delete("/delete", response_model=APIResponse[GradeDeleteResponse], summary="등급 삭제")
async def delete_grade(
    grade_code: str = Query(..., description="등급 코드"),
    service: GradeService = Depends(_get_grade_service),
):
    data = await service.delete(grade_code)
    return ok(data=data, message="등급 삭제 결과")


@router.get("/users", response_model=APIResponse[UsersByGradeResponse], summary="등급별 유저 목록")
async def get_users_by_grade(
    grade_code: str = Query(..., description="등급 코드"),
    service: GradeService = Depends(_get_grade_service),
):
    data = await service.get_users_by_grade(grade_code)
    return ok(data=data, message="등급별 유저 조회 성공")


@router.post("/create", response_model=APIResponse[GradeDetailResponse], summary="등급 등록 (이미지 업로드 지원)", description="multipart/form-data로 텍스트 필드와 이미지 파일을 전송합니다.")
async def create_grade(
    grade_code: str = Form(...),
    grade_name: str = Form(...),
    grade_level: int = Form(...),
    min_purchase_amount: int = Form(...),
    point_earn_rate: float = Form(...),
    discount_rate: float = Form(...),
    benefits: str | None = Form(default=None, description="JSON 문자열 또는 비움"),
    description: str | None = Form(default=None),
    is_active: bool = Form(default=True),
    grade_image: UploadFile | None = File(default=None),
    service: GradeService = Depends(_get_grade_service),
):
    # benefits 문자열을 JSON으로 전달할 수 있게 허용. 서비스에서는 그대로 dict 기대.
    import json
    benefits_obj = None
    if benefits:
        try:
            benefits_obj = json.loads(benefits)
        except Exception:
            benefits_obj = None

    payload = GradeCreateRequest(
        grade_code=grade_code,
        grade_name=grade_name,
        grade_level=grade_level,
        min_purchase_amount=min_purchase_amount,
        point_earn_rate=point_earn_rate,
        discount_rate=discount_rate,
        benefits=benefits_obj,
        description=description,
        is_active=is_active,
    )
    data = await service.create_with_image(payload=payload, image=grade_image)
    return ok(data=data, message="등급 등록 성공")


@router.post("/update", response_model=APIResponse[GradeDetailResponse], summary="등급 수정 (이미지 업로드 지원)", description="multipart/form-data로 텍스트 필드와 이미지 파일을 전송합니다.")
async def update_grade(
    grade_code: str = Form(...),
    grade_name: str | None = Form(default=None),
    grade_level: int | None = Form(default=None),
    min_purchase_amount: int | None = Form(default=None),
    point_earn_rate: float | None = Form(default=None),
    discount_rate: float | None = Form(default=None),
    benefits: str | None = Form(default=None, description="JSON 문자열 또는 비움"),
    description: str | None = Form(default=None),
    is_active: bool | None = Form(default=None),
    grade_image: UploadFile | None = File(default=None),
    service: GradeService = Depends(_get_grade_service),
):
    import json
    benefits_obj = None
    if benefits:
        try:
            benefits_obj = json.loads(benefits)
        except Exception:
            benefits_obj = None

    payload = GradeUpdateRequest(
        grade_code=grade_code,
        grade_name=grade_name,
        grade_level=grade_level,
        min_purchase_amount=min_purchase_amount,
        point_earn_rate=point_earn_rate,
        discount_rate=discount_rate,
        benefits=benefits_obj,
        description=description,
        is_active=is_active,
    )
    data = await service.update_with_image(payload=payload, image=grade_image)
    return ok(data=data, message="등급 수정 성공")


# =====================================================
# 월별 등급 업데이트 배치 API
# =====================================================

@router.post(
    "/monthly-update",
    response_model=APIResponse[MonthlyGradeUpdateResponse],
    summary="월별 등급 업데이트 실행",
    description="""
전월 결제 금액을 기준으로 ACTIVE 상태 사용자들의 등급을 업데이트합니다.

**처리 로직:**
1. t_user 테이블에서 ACTIVE 상태 사용자 조회
2. t_payment에서 전월 결제 금액 합산 (payment_status='SUCCESS')
3. t_grade의 min_purchase_amount 기준으로 등급 결정
4. t_grade_change_log에 변경 내역 기록
5. t_user의 grade_code 업데이트

**dry_run 옵션:**
- True: 실제 업데이트 없이 결과만 미리보기
- False: 실제 업데이트 수행
"""
)
async def execute_monthly_grade_update(
    request: MonthlyGradeUpdateRequest = Body(...),
    service: GradeService = Depends(_get_grade_service_with_batch),
):
    data = await service.execute_monthly_grade_update(
        target_year=request.target_year,
        target_month=request.target_month,
        dry_run=request.dry_run
    )
    message = "월별 등급 업데이트 테스트 완료" if request.dry_run else "월별 등급 업데이트 완료"
    return ok(data=data, message=message)


@router.get(
    "/change-logs",
    response_model=APIResponse[GradeChangeLogListResponse],
    summary="등급 변경 로그 조회",
    description="사용자별 등급 변경 이력을 조회합니다. user_id 미입력시 전체 로그를 조회합니다."
)
async def get_grade_change_logs(
    user_id: Optional[str] = Query(default=None, description="사용자 ID (선택)"),
    limit: int = Query(default=100, ge=1, le=500, description="조회 건수"),
    service: GradeService = Depends(_get_grade_service_with_batch),
):
    data = await service.get_grade_change_logs(user_id=user_id, limit=limit)
    return ok(data=data, message="등급 변경 로그 조회 성공")


@router.get(
    "/change-logs/list",
    response_model=APIResponse[GradeChangeLogListResponse],
    summary="등급 변경 로그 목록 조회 (페이지네이션, 월별 검색)",
    description="""
등급 변경 이력을 페이지네이션과 월별 검색 기능과 함께 조회합니다.

**검색 조건:**
- year, month: 특정 연월 검색 (예: 2024년 12월)
- user_id: 특정 사용자 검색
- change_reason: 변경 사유 검색 (AUTO_BATCH, MANUAL 등)

**페이지네이션:**
- page: 페이지 번호 (기본값: 1)
- size: 페이지 당 개수 (기본값: 20)
"""
)
async def get_grade_change_logs_list(
    year: Optional[int] = Query(default=None, description="대상 연도 (선택)"),
    month: Optional[int] = Query(default=None, ge=1, le=12, description="대상 월 (선택, 1-12)"),
    user_id: Optional[str] = Query(default=None, description="사용자 ID (선택)"),
    change_reason: Optional[str] = Query(default=None, description="변경 사유 (선택)"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=20, ge=1, le=100, description="페이지 당 개수"),
    service: GradeService = Depends(_get_grade_service_with_batch),
):
    data = await service.get_grade_change_logs_with_pagination(
        year=year,
        month=month,
        user_id=user_id,
        change_reason=change_reason,
        page=page,
        size=size
    )
    return ok(data=data, message="등급 변경 로그 목록 조회 성공")


