"""
등급 관리 API (관리자 백엔드)

- 등록 목록 조회: 페이징 없이 전체를 grade_level DESC로 반환
- 등급 상세 조회: grade_code로 단건 조회
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.response import APIResponse, ok
from src.core.database import get_db as get_db_maria
from src.repositories.grade_repository import GradeRepository
from src.repositories.user_repository import UserRepository
from src.services.grade_service import GradeService
from src.schemas.grade_schema import (
    GradeListResponse,
    GradeDetailResponse,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradeDeleteResponse,
    UsersByGradeResponse,
)


router = APIRouter(prefix="/grades", tags=["grades"])


def _get_grade_service(db: AsyncSession = Depends(get_db_maria)) -> GradeService:
    return GradeService(GradeRepository(db), user_repo=UserRepository(db))


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


