"""
AI 운세 API 엔드포인트

Story 2.5: 일일 운세 API 엔드포인트
- GET /api/v1/fortune/daily - 일일 운세 조회
- 인증 필수, 사주 정보 필수
- 날짜 범위: 오늘 ~ 과거 7일
- 캐싱: Redis 24시간 + DB 영구 저장
"""

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from src.common.logging import get_logger_with_request_id
from src.common.middleware.rate_limit import limiter
from src.common.response import APIResponse, ok
from src.common.utils.saju_calculator import get_ilju
from src.core.dependencies import FortuneServiceDep, UserRepositoryDep
from src.schemas.fortune_schema import FortuneResponse
from src.services.auth_service import TokenPayload, get_current_user

router = APIRouter(prefix="/fortune", tags=["fortune"])


@router.get(
    "/daily",
    response_model=APIResponse[FortuneResponse],
    summary="일일 운세 조회",
    description="로그인한 사용자의 일일 AI 운세를 조회합니다.",
    responses={
        200: {"description": "운세 조회 성공"},
        400: {"description": "사주 정보 미등록 또는 날짜 범위 초과"},
        401: {"description": "인증 필요"},
        429: {"description": "요청 한도 초과"},
    },
)
@limiter.limit("100/minute")  # 분당 100회 제한 (일일 운세는 자주 조회될 수 있음)
async def get_daily_fortune(
    request: Request,
    response: Response,
    fortune_service: FortuneServiceDep,
    user_repo: UserRepositoryDep,
    current_user: TokenPayload = Depends(get_current_user),
    target_date: Optional[date] = Query(
        None,
        alias="date",
        description="조회할 날짜 (YYYY-MM-DD, 기본: 오늘, 과거 7일까지)",
    ),
) -> APIResponse[FortuneResponse]:
    """
    일일 운세 조회 API

    - **로그인 필수**: JWT 토큰 인증
    - **사주 정보 필수**: 사용자의 생년월일시 등록 필요
    - **날짜 범위**: 오늘 ~ 과거 7일
    - **캐싱**: Redis 24시간 + DB 영구 저장
    - **성능**: p95 < 300ms (캐시 히트), < 3초 (신규 생성)
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub

    log.info(
        "API: Daily fortune request",
        user_id=user_id,
        target_date=str(target_date) if target_date else "today",
    )

    # 1. 날짜 검증
    today = date.today()
    if target_date is None:
        target_date = today
    else:
        min_date = today - timedelta(days=7)
        if target_date < min_date or target_date > today:
            log.warning(
                "API: Invalid date range",
                user_id=user_id,
                target_date=str(target_date),
                min_date=str(min_date),
                max_date=str(today),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_DATE_RANGE",
                    "message": "조회 가능한 날짜 범위를 벗어났습니다 (오늘 ~ 과거 7일)",
                },
            )

    # 2. 사용자 정보 조회
    user = await user_repo.get_by_id(user_id)
    if not user:
        log.warning("API: User not found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "사용자 정보를 찾을 수 없습니다",
            },
        )

    # 3. 사주 정보 확인 (생년월일시에서 일간/일지 계산)
    if not user.birth_date:
        log.warning("API: Saju info not registered", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SAJU_INFO_REQUIRED",
                "message": "사주 정보를 먼저 등록해주세요",
            },
        )

    # 4. 생년월일시에서 일간/일지 계산
    try:
        # birth_date 형식: "YYYY-MM-DD HH:MM" 또는 "YYYY-MM-DD HH:MM:SS"
        birth_date_str = user.birth_date
        if len(birth_date_str) <= 16:  # "YYYY-MM-DD HH:MM"
            birth_datetime = datetime.strptime(birth_date_str, "%Y-%m-%d %H:%M")
        else:  # "YYYY-MM-DD HH:MM:SS"
            birth_datetime = datetime.strptime(birth_date_str, "%Y-%m-%d %H:%M:%S")

        # 일주 계산 (일간, 일지)
        birth_stem, birth_branch = get_ilju(birth_datetime.date())
    except (ValueError, TypeError) as e:
        log.warning(
            "API: Invalid birth_date format",
            user_id=user_id,
            birth_date=user.birth_date,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SAJU_INFO_REQUIRED",
                "message": "사주 정보 형식이 올바르지 않습니다. 다시 등록해주세요.",
            },
        )

    # 5. 운세 조회 (캐시 → LLM → 폴백)
    fortune = await fortune_service.get_daily_fortune(
        user_id=user_id,
        birth_stem=birth_stem,
        birth_branch=birth_branch,
        target_date=target_date,
    )

    # 6. X-Cache 헤더 설정 (source 기반)
    cache_status = "HIT" if fortune.source == "cache" else "MISS"
    if fortune.source == "fallback":
        cache_status = "MISS"
    response.headers["X-Cache"] = cache_status

    log.info(
        "API: Daily fortune retrieved",
        user_id=user_id,
        target_date=str(target_date),
        cache_status=cache_status,
        source=fortune.source,
    )

    return ok(data=fortune, message="일일 운세 조회 성공")
