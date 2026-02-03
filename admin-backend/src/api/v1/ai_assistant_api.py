"""
AI 어시스턴트 API 엔드포인트

Stories: 1-1, 1-2, 1-3, 2-1
FRs: FR-011, FR-012, FR-013, FR-015
"""

import time
import uuid
from typing import Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

from src.common.logging import get_logger
from src.common.utils.auth_utils import get_current_admin, get_optional_admin
from src.config.settings import settings
from src.models.admin_model import Admin
from src.schemas.ai.error_schema import AIErrorCode, AIErrorResponse
from src.schemas.ai.query_schema import AIQueryMetadata, AIQueryRequest, AIQueryResponse
from src.services.ai.config.table_permissions import extract_tables_from_sql
from src.services.ai.security.audit_logger import log_access_granted
from src.services.ai.security.rate_limiter import rate_limit_dependency
from src.services.ai.security.rbac import AIPermission, check_ai_permission
from src.services.ai.utils.auth_logger import log_ai_access
from src.services.ai.validators.input_validator import validate_query_input

logger = get_logger(__name__)

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
            settings.ai_redis_url, decode_responses=True, socket_timeout=5
        )
        await redis_client.ping()
        redis_connected = True
        await redis_client.close()
    except Exception as e:
        message = f"Redis 연결 실패: {str(e)}"

    # OpenAI API 연결 상태 확인
    if settings.openai_api_key:
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=5.0)
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
        message=message,
    )


@router.post(
    "/query",
    response_model=AIQueryResponse,
    responses={
        400: {"model": AIErrorResponse},
        422: {"model": AIErrorResponse},
        500: {"model": AIErrorResponse},
        503: {"model": AIErrorResponse},
        504: {"model": AIErrorResponse},
    },
)
async def ai_query(
    request: AIQueryRequest,
    admin: Admin = Depends(get_current_admin),
    _rate_limit: None = Depends(rate_limit_dependency),
) -> AIQueryResponse:
    """
    자연어 질의 (인증 필수, RBAC + Rate Limit 적용)

    Stories: 2-1, 1-2, 1-3
    FRs: FR-011, FR-012, FR-015

    Args:
        request: 질의 요청 (AIQueryRequest)
        admin: 인증된 관리자
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        AIQueryResponse: AI 응답

    Raises:
        HTTPException: 유효성 검사 실패 시 400 에러, 서버 에러 시 500
    """
    # 시작 시간 측정
    start_time = time.time()

    # UUID 기반 query_id 및 session_id 생성
    query_id = str(uuid.uuid4())
    # session_id는 사용자 세션 단위로 관리 (현재는 query_id와 동일하게 설정)
    # TODO: Story 4-1에서 실제 세션 관리 구현 시 수정
    session_id = query_id

    try:
        # RBAC 권한 확인
        permission = check_ai_permission(admin)

        # 접근 허용 로깅
        log_access_granted(
            admin_id=permission["admin_id"],
            role=permission["role"],
            query=request.question,
        )

        # 인증 성공 로깅
        await log_ai_access(
            admin_id=admin.admin_id, endpoint="/api/v1/ai/query", status="success"
        )

        # 추가 유효성 검사 (비즈니스 로직) with error handling
        try:
            validation_result = await validate_query_input(request.question)
            if not validation_result.is_valid:
                logger.warning(
                    "query_validation_failed",
                    extra={
                        "event": "query_validation_failed",
                        "admin_id": admin.admin_id,
                        "query_id": query_id,
                        "error_code": validation_result.error_code,
                        "message": validation_result.message,
                    },
                )
                raise HTTPException(
                    status_code=400,
                    detail=AIErrorResponse(
                        error_code=validation_result.error_code,
                        message=validation_result.message,
                        suggestions=validation_result.suggestions,
                    ).model_dump(),
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "validation_error",
                extra={
                    "event": "validation_error",
                    "admin_id": admin.admin_id,
                    "query_id": query_id,
                    "error": str(e),
                },
            )
            raise HTTPException(
                status_code=500,
                detail=AIErrorResponse(
                    error_code=AIErrorCode.INTERNAL_ERROR,
                    message="내부 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    suggestions=["잠시 후 다시 시도해주세요."],
                ).model_dump(),
            )

        # Story 2-2: SQL 생성
        from langchain_openai import ChatOpenAI

        from src.core.database import get_aiomysql_pool

        # Story 2-3: MariaDB 실행
        from src.services.ai.agents.mariadb_agent import MariaDBAgent

        # Story 2-4: 응답 생성
        from src.services.ai.agents.response_agent import ResponseGenerationAgent
        from src.services.ai.agents.sql_agent import SQLGenerationAgent
        from src.services.ai.config.column_mappings import COLUMN_MAPPINGS
        from src.services.ai.config.table_permissions import get_role_allowed_tables
        from src.services.ai.tools.schema_loader import SchemaLoader
        from src.services.ai.utils.response_formatter import ResponseFormatter

        # 1. SQL 생성
        sql_agent = SQLGenerationAgent(settings)
        schema_loader = SchemaLoader()
        allowed_tables = get_role_allowed_tables(permission["role"])
        schema_info = await schema_loader.load_schema(allowed_tables)

        sql_result = await sql_agent.generate_sql(
            question=request.question,
            schema_info=schema_info,
            allowed_tables=list(allowed_tables),
        )

        if not sql_result.success or not sql_result.sql:
            raise HTTPException(
                status_code=400,
                detail=AIErrorResponse(
                    error_code=AIErrorCode.INVALID_QUERY,
                    message=sql_result.error or "SQL 생성에 실패했습니다.",
                    suggestions=["질문을 더 명확하게 표현해주세요."],
                ).model_dump(),
            )

        # 2. MariaDB 쿼리 실행
        pool = await get_aiomysql_pool()
        mariadb_agent = MariaDBAgent(pool)

        query_result = await mariadb_agent.execute_query(
            sql=sql_result.sql,
            allowed_tables=allowed_tables,
            max_rows=request.max_rows,
            user_id=admin.admin_id,
            session_id=session_id,
        )

        if not query_result.success:
            raise HTTPException(
                status_code=500,
                detail=AIErrorResponse(
                    error_code=query_result.error_code or AIErrorCode.DATABASE_ERROR,
                    message=query_result.error_message
                    or "데이터베이스 조회에 실패했습니다.",
                    suggestions=["잠시 후 다시 시도해주세요."],
                ).model_dump(),
            )

        # 3. 자연어 응답 생성 (Story 2-4)
        llm = ChatOpenAI(
            model=settings.ai_llm_model,
            temperature=0.3,
            timeout=settings.ai_llm_timeout,
            api_key=settings.openai_api_key,
        )
        response_agent = ResponseGenerationAgent(llm=llm)

        response_result = await response_agent.generate_response(
            question=request.question,
            sql=sql_result.sql,
            result_data=query_result.data or [],
            columns=query_result.columns or [],
        )

        if not response_result.success:
            # 응답 생성 실패 시 폴백: 간단한 데이터 요약 제공
            if query_result.row_count > 0 and query_result.data:
                first_row = query_result.data[0]
                # 첫 번째 row의 주요 값 표시
                preview = ", ".join(
                    [f"{k}: {v}" for k, v in list(first_row.items())[:3]]
                )
                natural_language_answer = f"조회 결과 {query_result.row_count}건을 찾았습니다. 첫 번째 결과: {preview}"
            else:
                natural_language_answer = (
                    f"조회 결과 {query_result.row_count}건을 찾았습니다."
                )

            logger.warning(
                "response_generation_fallback",
                extra={
                    "event": "response_generation_fallback",
                    "error_code": response_result.error_code,
                    "query_id": query_id,
                },
            )
        else:
            natural_language_answer = response_result.natural_language_response

        # 4. 테이블 데이터 포맷팅 (Story 2-4)
        formatted_data = None
        if query_result.data and len(query_result.data) > 0:
            formatted_data = ResponseFormatter.format_table_data(
                data=query_result.data,
                columns=query_result.columns or [],
                column_mappings=COLUMN_MAPPINGS,
            )

        # 실행 시간 계산 (밀리초)
        execution_time_ms = int((time.time() - start_time) * 1000)

        # 테이블 목록 추출
        tables_accessed = list(
            allowed_tables & set(extract_tables_from_sql(sql_result.sql))
        )

        # 성공 로깅 (프로젝트 컨텍스트 규칙 준수)
        logger.info(
            "ai_query_completed",
            extra={
                "event": "ai_query_completed",
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "session_id": session_id,
                "question": request.question,
                "db_scope": request.db_scope,
                "execution_time_ms": execution_time_ms,
                "tables_accessed": tables_accessed,
                "row_count": query_result.row_count,
                "answer_preview": (
                    natural_language_answer[:100] if natural_language_answer else None
                ),
                "response_generation_success": response_result.success,
            },
        )

        # 응답 반환 (Story 2-2, 2-3, 2-4 통합 완료)
        return AIQueryResponse(
            success=True,
            query_id=query_id,
            answer=natural_language_answer,
            data=formatted_data,
            generated_sql=sql_result.sql if request.include_sql else None,
            execution_time_ms=execution_time_ms,
            suggestions=[
                "더 자세한 분석이 필요하신가요?",
                "다른 기간으로 조회해보시겠어요?",
            ],
            metadata=AIQueryMetadata(
                query_complexity="simple",
                db_scope_detected=request.db_scope,
                tables_accessed=tables_accessed,
                agents_used=[
                    "sql_generation",
                    "mariadb_execution",
                    "response_generation",
                ],
            ),
        )

    except HTTPException:
        # HTTPException은 FastAPI가 처리하도록 re-raise
        raise
    except ImportError as e:
        # Story 2-2/2-3/2-4 모듈 누락 (서비스 일시 중단)
        logger.error(
            "ai_service_unavailable",
            extra={
                "event": "ai_service_unavailable",
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=503,
            detail=AIErrorResponse(
                error_code=AIErrorCode.SERVICE_UNAVAILABLE,
                message="AI 서비스가 일시적으로 사용 불가능합니다. 관리자에게 문의하세요.",
                suggestions=["잠시 후 다시 시도해주세요.", "관리자에게 문의하세요."],
            ).model_dump(),
        )
    except TimeoutError as e:
        # LLM 타임아웃
        logger.error(
            "ai_query_timeout",
            extra={
                "event": "ai_query_timeout",
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=504,
            detail=AIErrorResponse(
                error_code=AIErrorCode.LLM_TIMEOUT,
                message="요청 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
                suggestions=[
                    "질문을 더 간단하게 표현해주세요.",
                    "잠시 후 다시 시도해주세요.",
                ],
            ).model_dump(),
        )
    except Exception as e:
        # 예상치 못한 에러 처리
        logger.error(
            "ai_query_internal_error",
            extra={
                "event": "ai_query_internal_error",
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=AIErrorResponse(
                error_code=AIErrorCode.INTERNAL_ERROR,
                message="요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                suggestions=["잠시 후 다시 시도해주세요."],
            ).model_dump(),
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
    log_access_granted(admin_id=permission["admin_id"], role=permission["role"])

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/feedback", status="success"
    )

    # TODO: Story 5-1에서 구현
    return FeedbackResponse(
        success=True, message="피드백이 제출되었습니다. (기능 준비 중)"
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
    log_access_granted(admin_id=permission["admin_id"], role=permission["role"])

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/history", status="success"
    )

    # TODO: Story 4-1에서 구현
    return HistoryResponse(history=[])
