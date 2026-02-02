"""
AI 어시스턴트 API 엔드포인트

Stories: 1-1, 1-2, 1-3
FRs: FR-011, FR-012, FR-013
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import redis.asyncio as redis
from openai import AsyncOpenAI

from src.config.settings import settings
from src.services.ai.utils import create_checkpointer
from src.services.ai.utils.auth_logger import log_ai_access
from src.common.utils.auth_utils import get_current_admin, get_optional_admin
from src.models.admin_model import Admin
from src.services.ai.security.rbac import check_ai_permission, AIPermission
from src.services.ai.security.rate_limiter import rate_limit_dependency
from src.services.ai.security.audit_logger import log_access_granted
from src.services.ai.config.table_permissions import can_access_table, extract_tables_from_sql

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class HealthCheckResponse(BaseModel):
    """Health check 응답 모델"""
    status: str
    redis_connected: bool
    openai_connected: bool
    message: Optional[str] = None


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    admin: Admin | None = Depends(get_optional_admin),
) -> HealthCheckResponse:
    """
    AI 어시스턴트 서비스 Health Check (선택적 인증)

    Args:
        admin: 인증된 관리자 (선택적)

    Returns:
        HealthCheckResponse: 서비스 상태 정보
    """
    redis_connected = False
    openai_connected = False
    message = None
    
    # Redis 연결 상태 확인
    try:
        redis_client = redis.from_url(
            settings.ai_redis_url,
            decode_responses=True,
            socket_timeout=5
        )
        await redis_client.ping()
        redis_connected = True
        await redis_client.close()
    except Exception as e:
        message = f"Redis 연결 실패: {str(e)}"
    
    # OpenAI API 연결 상태 확인
    if settings.openai_api_key:
        try:
            client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=5.0
            )
            # 간단한 모델 목록 조회로 연결 확인
            await client.models.list()
            openai_connected = True
        except Exception as e:
            if not message:
                message = f"OpenAI API 연결 실패: {str(e)}"
            else:
                message += f" | OpenAI API 연결 실패: {str(e)}"
    else:
        message = "OpenAI API 키가 설정되지 않았습니다"
    
    # 전체 상태 판단
    status = "healthy" if redis_connected and openai_connected else "unhealthy"
    
    return HealthCheckResponse(
        status=status,
        redis_connected=redis_connected,
        openai_connected=openai_connected,
        message=message
    )


class QueryRequest(BaseModel):
    """AI 질의 요청 스키마"""
    query: str


class QueryResponse(BaseModel):
    """AI 질의 응답 스키마"""
    answer: str
    session_id: str | None = None


@router.post("/query", response_model=QueryResponse)
async def ai_query(
    request: QueryRequest,
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: None = Depends(rate_limit_dependency),
) -> QueryResponse:
    """
    자연어 질의 (인증 필수, RBAC + Rate Limit 적용)

    Args:
        request: 질의 요청
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        QueryResponse: AI 응답
    """
    # 접근 허용 로깅
    log_access_granted(
        admin_id=permission["admin_id"],
        role=permission["role"],
        query=request.query
    )

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/query",
        status="success"
    )

    # TODO: Story 2-1에서 구현
    # TODO: SQL 생성 후 테이블 권한 체크 로직 추가
    return QueryResponse(
        answer="AI 질의 기능은 아직 구현되지 않았습니다.",
        session_id=None
    )


class FeedbackRequest(BaseModel):
    """피드백 요청 스키마"""
    session_id: str
    feedback: str
    rating: int | None = None


class FeedbackResponse(BaseModel):
    """피드백 응답 스키마"""
    success: bool
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: None = Depends(rate_limit_dependency),
) -> FeedbackResponse:
    """
    피드백 제출 (인증 필수, RBAC + Rate Limit 적용)

    Args:
        request: 피드백 요청
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        FeedbackResponse: 제출 결과
    """
    # 접근 허용 로깅
    log_access_granted(
        admin_id=permission["admin_id"],
        role=permission["role"]
    )

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/feedback",
        status="success"
    )

    # TODO: Story 5-1에서 구현
    return FeedbackResponse(
        success=True,
        message="피드백이 제출되었습니다. (기능 준비 중)"
    )


class HistoryResponse(BaseModel):
    """질의 히스토리 응답 스키마"""
    history: list[dict]


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: None = Depends(rate_limit_dependency),
) -> HistoryResponse:
    """
    질의 히스토리 조회 (인증 필수, RBAC + Rate Limit 적용)

    Args:
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        HistoryResponse: 질의 히스토리
    """
    # 접근 허용 로깅
    log_access_granted(
        admin_id=permission["admin_id"],
        role=permission["role"]
    )

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint="/api/v1/ai/history",
        status="success"
    )

    # TODO: Story 4-1에서 구현
    return HistoryResponse(
        history=[]
    )
