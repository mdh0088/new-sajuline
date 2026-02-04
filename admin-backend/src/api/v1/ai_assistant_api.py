"""
AI 어시스턴트 API 엔드포인트

Stories: 1-1, 1-2, 1-3, 2-1, 3-4, 4-1, 4-3, 5-1, 5-3, 6-3
FRs: FR-011, FR-012, FR-013, FR-015, FR17, FR18, FR19, FR22, FR24, FR26, FR27, FR28, FR32
"""

import json
import time
import uuid
from datetime import date
from typing import Optional

import redis.asyncio as redis
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path, Query, Request
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse, StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import get_logger
from src.common.utils.auth_utils import get_current_admin, get_optional_admin
from src.config.settings import settings
from src.core.database import get_db
from src.models.admin_model import Admin
from src.api.v1.dependencies.redis_dep import get_redis_client  # Story 6-2
from src.schemas.ai.error_schema import AIErrorCode, AIErrorResponse
from src.schemas.ai.feedback_analytics_schema import (  # Story 5-3
    FeedbackStatsResponse,
    FeedbackTrendsResponse,
    LowScoreFeedbackResponse,
)
from src.schemas.ai.history_schema import (  # Story 4-1
    ExampleQuestionsResponse,
    QueryHistoryResponse,
)
from src.schemas.ai.autocomplete_schema import (  # Story 4-3
    AutocompleteResponse,
    CacheHitRateResponse,
)
from src.schemas.ai.correction_schema import (  # Story 5-2
    CorrectionRequest,
    CorrectionResponse,
    CorrectionHistoryResponse,
)
from src.services.ai.services.correction_service import AICorrectionService  # Story 5-2
from src.schemas.ai.monitoring_schema import (  # Story 6-3
    SLAStatusResponse,
    MetricsResponse,
    ViolationItem,
    ResponseTimeMetrics,
    LLMCostMetrics,
)
from src.schemas.ai.query_schema import AIQueryMetadata, AIQueryRequest, AIQueryResponse
from src.services.ai.config.table_permissions import extract_tables_from_sql
from src.services.ai.security import SecurityPipeline  # Story 3-1: 4-Layer Security
from src.services.ai.security.rbac import AIPermission, check_ai_permission
from src.services.ai.services.example_service import ExampleQuestionService  # Story 4-1
from src.services.ai.services.feedback_analytics_service import (  # Story 5-3
    FeedbackAnalyticsService,
)
from src.services.ai.services.feedback_service import AIFeedbackService  # Story 5-1
from src.schemas.ai.feedback_schema import AIFeedbackRequest, AIFeedbackResponse  # Story 5-1
from src.services.ai.services.autocomplete_service import AutocompleteService  # Story 4-3
from src.services.ai.services.history_service import AIHistoryService  # Story 4-1
from src.services.ai.utils.auth_logger import log_ai_access
from src.services.ai.validators.input_validator import validate_query_input

# Story 3-4: Rate Limiting 및 감사 로깅
from src.api.v1.dependencies.rate_limit import rate_limit_dependency
from src.services.ai.audit.audit_logger import AIAuditLogger, AIQueryAuditLog
from src.services.ai.audit.log_config import configure_ai_audit_logging

# Story 4-2: 사용자 친화적 에러 및 대안 제안
from src.services.ai.utils.error_handler import AIErrorHandler

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


def create_ai_error_response(
    error_code: str,
    message: str | None = None,
    suggestions: list[str] | None = None,
    original_question: str = "",
    error_guide: dict | None = None,
) -> dict:
    """AI 에러 응답 생성 helper 함수 (Story 4-2: 에러 핸들러 통합)

    Args:
        error_code: 에러 코드 (AIErrorCode 상수)
        message: 사용자 친화적 에러 메시지 (선택, 없으면 error_handler에서 생성)
        suggestions: 해결 방법 제안 (선택, 없으면 error_handler에서 생성)
        original_question: 사용자의 원래 질문 (대안 제안 생성용)
        error_guide: 에러 유형별 안내 정보 (선택, 없으면 error_handler에서 생성)

    Returns:
        dict: AIErrorResponse 형태의 딕셔너리
    """
    # Story 4-2: AIErrorHandler 사용
    if not message or not suggestions or error_guide is None:
        friendly_error = AIErrorHandler.handle_error(
            error_code=error_code,
            original_question=original_question,
        )
        message = message or friendly_error.user_message
        suggestions = suggestions or friendly_error.suggestions
        error_guide = error_guide if error_guide is not None else friendly_error.error_guide

    return AIErrorResponse(
        error_code=error_code,
        message=message,
        suggestions=suggestions or [],
        error_guide=error_guide,
    ).model_dump()


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
        429: {"model": AIErrorResponse},
        500: {"model": AIErrorResponse},
        503: {"model": AIErrorResponse},
        504: {"model": AIErrorResponse},
    },
)
async def ai_query(
    request: AIQueryRequest,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(lambda: None),  # TODO: Implement proper Redis dependency
    _rate_limit: Admin = Depends(rate_limit_dependency),
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
                    detail=create_ai_error_response(
                        error_code=validation_result.error_code,
                        message=validation_result.message,
                        suggestions=validation_result.suggestions,
                    ),
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
                detail=create_ai_error_response(
                    error_code=AIErrorCode.INTERNAL_ERROR,
                    message="내부 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    suggestions=["잠시 후 다시 시도해주세요."],
                ),
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

        # Story 2-5: 접근성 모드
        from src.schemas.ai.query_schema import AccessibilityHints
        from src.services.ai.utils.accessibility_formatter import (
            AccessibilityFormatter,
        )

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
                detail=create_ai_error_response(
                    error_code="AIBI_SQL_GEN_FAILED",  # Story 4-2: 에러 코드
                    original_question=request.question,  # Story 4-2: 대안 제안용
                ),
            )

        # Story 3-1: Layer 2 SQL 보안 검증
        security_validation = SecurityPipeline.validate_sql(
            sql_result.sql, allowed_tables
        )
        if not security_validation.is_safe:
            # Story 3-4: 차단 감사 로그
            await AIAuditLogger.log_query(
                AIQueryAuditLog(
                    request_id=query_id,
                    admin_id=admin.admin_id,
                    admin_role=permission["role"].value,
                    question=request.question,
                    db_scope=request.db_scope,
                    generated_sql=sql_result.sql,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    row_count=0,
                    status="blocked",
                    error_code=AIErrorCode.SECURITY_VIOLATION,
                    error_message=f"보안 위반: {', '.join(security_validation.violations)}",
                )
            )
            logger.warning(
                f"SQL security validation failed: {security_validation.violations}"
            )
            raise HTTPException(
                status_code=400,
                detail=create_ai_error_response(
                    error_code=AIErrorCode.SECURITY_VIOLATION,
                    message="생성된 SQL이 보안 정책을 위반했습니다.",
                    suggestions=[
                        "질문을 더 안전하게 표현해주세요.",
                        f"위반 사항: {', '.join(security_validation.violations[:2])}",
                    ],
                ),
            )

        # Story 3-1: Layer 4 사용자 확인 필요 여부 체크
        confirmation_check = SecurityPipeline.check_user_confirmation(
            sql_result.sql, estimated_rows=request.max_rows
        )
        if confirmation_check.required:
            logger.info(
                f"User confirmation required for SQL: {confirmation_check.reason}"
            )
            # Note: 실제 UI에서는 확인 다이얼로그 표시 필요
            # 현재는 경고 로그만 기록하고 진행
            # TODO: Frontend에서 confirmation_required 플래그 처리

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
                detail=create_ai_error_response(
                    error_code=query_result.error_code or AIErrorCode.DATABASE_ERROR,
                    message=query_result.error_message
                    or "데이터베이스 조회에 실패했습니다.",
                    suggestions=["잠시 후 다시 시도해주세요."],
                ),
            )

        # Story 3-1: Layer 3 결과 보안 검증 및 정제 (PII 마스킹, 행 수 제한)
        sanitized_data, result_validation = SecurityPipeline.sanitize_result(
            query_result.data or [], query_result.columns or []
        )
        if result_validation.was_truncated:
            logger.info(
                f"Result truncated: {result_validation.row_count} → 500 rows (MAX_ROWS)"
            )
        if result_validation.masked_columns:
            logger.info(
                f"Sensitive data masked: {', '.join(result_validation.masked_columns)}"
            )

        # 정제된 데이터로 query_result 업데이트
        query_result.data = sanitized_data

        # 3. 자연어 응답 생성 (Story 2-4)
        llm = ChatOpenAI(
            model=settings.ai_llm_model,
            temperature=0.3,
            timeout=settings.ai_llm_timeout,
            api_key=settings.openai_api_key,
        )
        response_agent = ResponseGenerationAgent(
            llm=llm,
            settings=settings,
            max_sample_rows=settings.ai_llm_max_sample_rows,
        )

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

        # 5. 접근성 모드 처리 (Story 2-5)
        answer_summary = None
        accessibility_hints_data = None

        if request.accessibility_mode:
            # 접근성 모드: 테이블 대신 상세 텍스트 요약 생성
            answer_summary = AccessibilityFormatter.format_for_screen_reader(
                answer=natural_language_answer,
                data=query_result.data or [],
                columns=query_result.columns or [],
            )

            # 접근성 힌트 생성
            question_preview = request.question[:47]
            if len(request.question) > 47:
                question_preview += "..."

            accessibility_hints_data = AccessibilityHints(
                aria_label=f"AI 분석 결과: {question_preview}",
                aria_live="polite",
                row_count=query_result.row_count,
                column_count=len(query_result.columns or []),
            )

            # 접근성 모드에서는 테이블 데이터를 빈 배열로 반환 (AC 4 준수)
            formatted_data = []

            logger.info(
                "ai_accessibility_mode_activated",
                extra={
                    "event": "ai_accessibility_mode_activated",
                    "admin_id": admin.admin_id,
                    "query_id": query_id,
                    "row_count": query_result.row_count,
                },
            )

        # 실행 시간 계산 (밀리초)
        execution_time_ms = int((time.time() - start_time) * 1000)

        # 테이블 목록 추출
        tables_accessed = list(
            allowed_tables & set(extract_tables_from_sql(sql_result.sql))
        )

        # Story 3-4: 감사 로깅 (AC 1-2 충족)
        await AIAuditLogger.log_query(
            AIQueryAuditLog(
                request_id=query_id,
                admin_id=admin.admin_id,
                admin_role=permission["role"].value,
                question=request.question,
                db_scope=request.db_scope,
                generated_sql=sql_result.sql,
                execution_time_ms=execution_time_ms,
                row_count=query_result.row_count,
                status="success",
                tables_accessed=tables_accessed,
                masked_columns=list(result_validation.masked_columns)
                if result_validation.masked_columns
                else [],
            )
        )

        # 기존 로깅 (프로젝트 컨텍스트 규칙 준수)
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
                "natural_language_answer_preview": (
                    natural_language_answer[: settings.ai_log_preview_length]
                    if natural_language_answer
                    else None
                ),
                "response_generation_success": response_result.success,
            },
        )

        # Story 4-1: 질의 히스토리 저장 (Issue #1 수정)
        try:
            from src.models.ai.ai_query_history_model import AIQueryHistory

            history = AIQueryHistory(
                admin_id=admin.admin_id,
                query_id=query_id,
                question=request.question,
                answer_summary=natural_language_answer[:500] if natural_language_answer else None,
                db_scope=request.db_scope,
                execution_time_ms=execution_time_ms,
                row_count=query_result.row_count,
                status="success"
            )
            history_service = AIHistoryService(db=db)
            await history_service.save_query(history)
            logger.info(f"질의 히스토리 저장 완료: query_id={query_id}")
        except Exception as e:
            # 히스토리 저장 실패는 전체 요청 실패로 이어지지 않도록 처리
            logger.error(f"질의 히스토리 저장 실패: {e}", exc_info=True)

        # Story 4-3: 자동완성을 위한 질문 인덱싱 (Issue #2 수정)
        try:
            redis_autocomplete = redis.from_url(
                settings.ai_redis_url, encoding="utf-8", decode_responses=True
            )
            autocomplete_service = AutocompleteService(
                redis_client=redis_autocomplete, encoding="utf-8"
            )
            await autocomplete_service.index_question(request.question)
            await redis_autocomplete.close()
            logger.info(f"자동완성 질문 인덱싱 완료: {request.question}")
        except Exception as e:
            # 인덱싱 실패는 전체 요청 실패로 이어지지 않음
            logger.warning(f"자동완성 질문 인덱싱 실패: {e}")

        # 응답 반환 (Story 2-2, 2-3, 2-4, 2-5 통합 완료)
        return AIQueryResponse(
            success=True,
            query_id=query_id,
            answer=natural_language_answer,
            answer_summary=answer_summary,  # Story 2-5
            data=formatted_data,
            generated_sql=sql_result.sql if request.include_sql else None,  # Story 2-5
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
            accessibility_hints=accessibility_hints_data,  # Story 2-5
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
            detail=create_ai_error_response(
                error_code=AIErrorCode.SERVICE_UNAVAILABLE,
                message="AI 서비스가 일시적으로 사용 불가능합니다. 관리자에게 문의하세요.",
                suggestions=["잠시 후 다시 시도해주세요.", "관리자에게 문의하세요."],
            ),
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
            detail=create_ai_error_response(
                error_code="AIBI_LLM_TIMEOUT",  # Story 4-2: 에러 코드
                original_question=request.question,  # Story 4-2: 대안 제안용
            ),
        )
    except Exception as e:
        # Story 3-4: 에러 감사 로그
        await AIAuditLogger.log_query(
            AIQueryAuditLog(
                request_id=query_id,
                admin_id=admin.admin_id,
                admin_role=permission["role"].value if "permission" in locals() else "unknown",
                question=request.question,
                db_scope=request.db_scope,
                generated_sql=None,
                execution_time_ms=int((time.time() - start_time) * 1000),
                row_count=0,
                status="error",
                error_code=AIErrorCode.INTERNAL_ERROR,
                error_message=str(e),
            )
        )
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
            detail=create_ai_error_response(
                error_code=AIErrorCode.INTERNAL_ERROR,
                message="요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                suggestions=["잠시 후 다시 시도해주세요."],
            ),
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
    redis_client=Depends(lambda: None),  # TODO: Implement proper Redis dependency
    _rate_limit: Admin = Depends(rate_limit_dependency),
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
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/feedback", status="success"
    )

    # TODO: Story 5-1에서 구현
    return FeedbackResponse(
        success=True, message="피드백이 제출되었습니다. (기능 준비 중)"
    )


# ==================== Story 5-2: 답변 수정 기능 ====================


@router.put("/feedback/{query_id}/correction", response_model=CorrectionResponse)
async def submit_correction(
    query_id: str = Path(
        ...,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
        description="질의 ID (UUID 형식)"
    ),
    request: CorrectionRequest = Body(...),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: Admin = Depends(rate_limit_dependency),
    db: AsyncSession = Depends(get_db),
) -> CorrectionResponse:
    """
    AI 응답 수정 제출 (AC1, AC2, AC3, AC5)

    AC1: "답변 수정" 버튼이 각 응답에 제공된다 (프론트엔드)
    AC2: 수정 모드에서 자연어 답변을 편집할 수 있다
    AC3: 수정된 답변이 원본과 함께 저장된다
    AC5: 수정된 답변이 향후 학습 데이터로 표시된다

    Args:
        query_id: 질의 ID
        request: 수정 요청 데이터
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크
        db: 데이터베이스 세션

    Returns:
        CorrectionResponse: 수정 제출 결과

    Raises:
        HTTPException: 질의를 찾을 수 없거나 저장 실패 시
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint=f"/api/v1/ai/feedback/{query_id}/correction",
        status="success",
    )

    try:
        # Story 5-2: 수정 서비스 사용
        service = AICorrectionService(db)
        correction = await service.save_correction(
            admin_id=admin.admin_id, query_id=query_id, correction=request
        )

        logger.info(
            "ai_correction_submitted",
            extra={
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "correction_id": correction.id,
                "is_training_data": correction.is_training_data,
            },
        )

        return CorrectionResponse(
            success=True,
            correction_id=correction.id,
            message="답변 수정이 제출되었습니다. 검토 후 반영됩니다.",
        )

    except ValueError as e:
        logger.error(
            "ai_correction_failed",
            extra={"admin_id": admin.admin_id, "query_id": query_id, "error": str(e)},
        )
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError as e:
        logger.error(
            "ai_correction_integrity_error",
            extra={"admin_id": admin.admin_id, "query_id": query_id, "error": str(e)},
        )
        raise HTTPException(status_code=409, detail="데이터 무결성 오류가 발생했습니다")
    except Exception as e:
        logger.error(
            "ai_correction_error",
            extra={
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        # 개발 환경에서는 상세 에러 포함
        detail = str(e) if settings.ENVIRONMENT == "development" else "수정 저장 중 오류가 발생했습니다"
        raise HTTPException(status_code=500, detail=detail)


@router.get("/feedback/{query_id}/corrections", response_model=CorrectionHistoryResponse)
async def get_correction_history(
    query_id: str = Path(
        ...,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
        description="질의 ID (UUID 형식)"
    ),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: Admin = Depends(rate_limit_dependency),
    db: AsyncSession = Depends(get_db),
) -> CorrectionHistoryResponse:
    """
    특정 질의의 수정 이력 조회 (AC4)

    AC4: 수정 이력이 관리된다

    Args:
        query_id: 질의 ID
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크
        db: 데이터베이스 세션

    Returns:
        CorrectionHistoryResponse: 수정 이력 목록

    Raises:
        HTTPException: 조회 실패 시
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id,
        endpoint=f"/api/v1/ai/feedback/{query_id}/corrections",
        status="success",
    )

    try:
        # Story 5-2: 수정 서비스 사용
        from src.schemas.ai.correction_schema import CorrectionItem

        service = AICorrectionService(db)
        corrections = await service.get_corrections(query_id)

        # 모델을 스키마로 변환
        correction_items = [
            CorrectionItem(
                id=c.id,
                admin_id=c.admin_id,
                original_answer=c.original_answer,
                corrected_answer=c.corrected_answer,
                correction_reason=c.correction_reason,
                is_training_data=c.is_training_data,
                created_at=c.created_at,
            )
            for c in corrections
        ]

        return CorrectionHistoryResponse(
            query_id=query_id,
            corrections=correction_items,
            total_count=len(correction_items),
        )

    except Exception as e:
        logger.error(
            "ai_correction_history_error",
            extra={
                "admin_id": admin.admin_id,
                "query_id": query_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(status_code=500, detail="수정 이력 조회 중 오류가 발생했습니다")


# ==================== Story 4-1: 예시 질문 및 히스토리 ====================


@router.get("/examples", response_model=ExampleQuestionsResponse)
async def get_example_questions(
    category: str | None = Query(default=None, description="카테고리 필터"),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> ExampleQuestionsResponse:
    """
    예시 질문 목록 조회 (AC1, AC6 - Redis 캐시)

    AC1: 도메인별 예시 질문 목록 표시 (최소 10개)
    AC2: 예시 질문 클릭 시 입력 필드 자동 입력 (프론트엔드 처리)
    AC6: Redis 캐시 적용 (TTL: 1시간)

    Args:
        category: 카테고리 필터 (None이면 전체)
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        ExampleQuestionsResponse: 카테고리별 예시 질문 목록
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/examples", status="success"
    )

    # AC6: Redis 캐시 적용 (TTL: 1시간 = 3600초) - Issue #5: Redis 연결 관리 수정
    cache_key = f"ai:examples:{category if category else 'all'}"
    redis_client = None

    # 캐시 조회
    try:
        redis_client = redis.from_url(
            settings.ai_redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        cached = await redis_client.get(cache_key)
        if cached:
            result = json.loads(cached)
            logger.info(f"예시 질문 캐시 히트: {cache_key}")
            return ExampleQuestionsResponse(**result)
    except Exception as e:
        logger.warning(f"Redis 캐시 조회 실패: {e}")
    finally:
        if redis_client:
            await redis_client.close()

    # 예시 질문 서비스 (캐시 미스 또는 캐시 실패)
    service = ExampleQuestionService()
    result = service.get_examples(category=category)

    # 캐시 저장 (새 Redis 연결)
    try:
        redis_client = redis.from_url(
            settings.ai_redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.setex(cache_key, 3600, json.dumps(result))
        logger.info(f"예시 질문 캐시 저장: {cache_key}")
        await redis_client.close()
    except Exception as e:
        logger.warning(f"Redis 캐시 저장 실패: {e}")

    return ExampleQuestionsResponse(**result)


@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    limit: int = Query(default=20, le=50, description="조회 개수 (최대 50)"),
    search: str | None = Query(default=None, description="검색어 (질문 내용)"),
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    db: AsyncSession = Depends(get_db),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> QueryHistoryResponse:
    """
    질의 히스토리 조회 (AC3, AC4, AC5)

    AC3: 최근 질의 히스토리 표시 (최대 20개)
    AC4: 히스토리 항목 클릭 시 재실행 (프론트엔드 처리)
    AC5: 히스토리 검색 기능

    Args:
        limit: 조회할 최대 개수 (기본값: 20, 최대: 50)
        search: 검색어 (question 필드 검색)
        admin: 인증된 관리자
        permission: AI 권한 정보
        db: 데이터베이스 세션
        _rate_limit: Rate Limit 체크 (의존성)

    Returns:
        QueryHistoryResponse: 질의 히스토리 목록
    """
    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/history", status="success"
    )

    # 히스토리 서비스
    service = AIHistoryService(db=db)
    history_list = await service.get_history(
        admin_id=admin.admin_id, limit=limit, search=search
    )

    return QueryHistoryResponse(
        history=history_list,
        total_count=len(history_list),
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=2, max_length=100, description="검색 쿼리 (최소 2자)"),
    limit: int = Query(default=5, le=10, description="제안 개수 (최대 10개)"),
    request: Request,
    admin: Admin = Depends(get_current_admin),
    permission: AIPermission = Depends(check_ai_permission),
    _rate_limit: Admin = Depends(rate_limit_dependency),
) -> AutocompleteResponse:
    """
    자동완성 제안 (AC1, AC2, AC3, AC4)

    Stories: 4-3
    AC1: 입력 중 실시간 자동완성 제안이 표시된다
    AC2: 자주 사용된 질문이 우선 제안된다 (점수 기반 정렬)
    AC3: 테이블/컬럼 이름이 자동완성에 포함된다
    AC4: 키보드로 자동완성 항목을 선택할 수 있다 (프론트엔드 처리)
    AC5: 캐시 히트율이 30% 이상이다 (Redis 사용)

    Rate Limiting: 분당 60회 (rate_limit_dependency)

    Args:
        q: 검색 쿼리 (최소 2자)
        limit: 최대 제안 개수 (기본값: 5, 최대: 10)
        request: HTTP 요청 (request_id 추출용)
        admin: 인증된 관리자
        permission: AI 권한 정보
        _rate_limit: Rate Limit 체크 (분당 60회)

    Returns:
        AutocompleteResponse: 자동완성 제안 목록
    """
    # request_id 추출 (디버깅용, Issue #9 수정)
    request_id = getattr(request.state, "request_id", None) if request else None

    # 인증 성공 로깅
    await log_ai_access(
        admin_id=admin.admin_id, endpoint="/api/v1/ai/autocomplete", status="success"
    )

    # Redis 연결
    # TODO (Issue #4): Connection Pool 사용으로 개선 필요 (app lifespan dependency)
    redis_client = None
    try:
        redis_client = redis.from_url(
            settings.ai_redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        # 자동완성 서비스 (AC1, AC2, AC3, AC5)
        # Issue #11 수정: encoding 파라미터 추가
        service = AutocompleteService(redis_client=redis_client, encoding="utf-8")
        suggestions = await service.suggest(q, limit=limit, request_id=request_id)

        logger.info(
            "autocomplete_request",
            extra={
                "event": "autocomplete_request",
                "admin_id": admin.admin_id,
                "query": q,
                "suggestion_count": len(suggestions),
                "request_id": request_id,  # Issue #9 수정
            }
        )

        return AutocompleteResponse(
            suggestions=suggestions,
            query=q,
            count=len(suggestions),
        )

    except Exception as e:
        logger.error(
            "autocomplete_error",
            extra={
                "event": "autocomplete_error",
                "admin_id": admin.admin_id,
                "query": q,
                "error": str(e),
                "request_id": request_id,  # Issue #9 수정
            }
        )
        # 에러 시 빈 결과 반환
        return AutocompleteResponse(
            suggestions=[],
            query=q,
            count=0,
        )
    finally:
        if redis_client:
            await redis_client.close()

# ==================== Story 6-3: SLA 모니터링 및 알림 ====================

@router.get("/monitoring/sla", response_model=SLAStatusResponse)
async def get_sla_status(
    send_alerts: bool = Query(default=False, description="알림 발송 여부"),
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis | None = Depends(get_redis_client),
):
    """현재 SLA 상태 조회

    Args:
        send_alerts: 알림 발송 여부 (기본: False - 조회만)
        current_admin: 인증된 관리자
        redis_client: Redis 클라이언트 (메트릭 저장소)

    Returns:
        SLAStatusResponse: SLA 상태 및 위반 목록
    """
    from src.services.ai.monitoring import (
        MetricsCollector,
        AlertService,
        AlertConfig,
        SLAMonitor,
    )

    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis unavailable")

    # 모니터링 서비스 초기화
    metrics = MetricsCollector(redis_client)
    alerts = AlertService(AlertConfig(
        slack_webhook_url=settings.slack_webhook_url if send_alerts else None,
        sentry_dsn=settings.sentry_dsn if send_alerts else None,
    ))
    monitor = SLAMonitor(metrics, alerts)

    # SLA 상태 확인
    status = await monitor.check_sla()

    logger.info(
        "sla_status_check",
        extra={
            "event": "sla_status_check",
            "admin_id": current_admin.admin_id,
            "healthy": status.healthy,
            "violations_count": len(status.violations),
            "send_alerts": send_alerts,
        }
    )

    return SLAStatusResponse(
        healthy=status.healthy,
        response_time_p95=status.response_time_p95,
        response_time_p99=status.response_time_p99,
        error_rate=status.error_rate * 100,  # 백분율로 변환
        llm_cost_month=status.llm_cost_month,
        llm_cost_pct=status.llm_cost_pct * 100,  # 백분율로 변환
        violations=[
            ViolationItem(
                metric=v.metric_name,
                severity=v.severity.value,
                message=v.message
            )
            for v in status.violations
        ]
    )


@router.get("/monitoring/metrics", response_model=MetricsResponse)
async def get_metrics(
    window_minutes: int = Query(default=60, le=1440),
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis | None = Depends(get_redis_client),
):
    """상세 메트릭 조회

    Args:
        window_minutes: 조회 시간 범위 (분, 최대 1440분 = 24시간)
        current_admin: 인증된 관리자
        redis_client: Redis 클라이언트

    Returns:
        MetricsResponse: 응답 시간, 에러율, LLM 비용 상세 메트릭
    """
    from src.services.ai.monitoring import MetricsCollector

    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis unavailable")

    metrics = MetricsCollector(redis_client)

    # 메트릭 수집
    response_time = await metrics.get_response_time_percentiles(window_minutes)
    error_rate = await metrics.get_error_rate(window_minutes)
    llm_cost_total = await metrics.get_monthly_llm_cost()
    llm_cost_by_model = await metrics.get_llm_cost_by_model()

    logger.info(
        "metrics_query",
        extra={
            "event": "metrics_query",
            "admin_id": current_admin.admin_id,
            "window_minutes": window_minutes,
        }
    )

    return MetricsResponse(
        response_time=ResponseTimeMetrics(**response_time),
        error_rate=error_rate,
        llm_cost=LLMCostMetrics(
            total=llm_cost_total,
            by_model=llm_cost_by_model
        )
    )


# ============================================================================
# Story 5-1: 피드백 제출 인터페이스 (Feedback Submission Interface)
# ============================================================================


@router.post(
    "/feedback",
    response_model=AIFeedbackResponse,
    status_code=201,
    summary="AI 응답 피드백 제출",
    description="AI 응답에 대한 별점(1-5)과 선택적 텍스트 피드백을 제출합니다.",
    responses={
        201: {"description": "피드백이 성공적으로 제출되었습니다"},
        401: {"description": "인증되지 않은 요청"},
        422: {"description": "잘못된 피드백 데이터"},
    }
)
async def submit_feedback(
    request: AIFeedbackRequest,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """AI 응답 피드백 제출 (Story 5-1)

    피드백은 BackgroundTasks를 통해 비동기로 처리되어 사용자 경험을 방해하지 않습니다.

    Args:
        request: 피드백 요청 데이터 (query_id, rating, comment)
        background_tasks: FastAPI BackgroundTasks
        current_admin: 인증된 관리자
        db: 데이터베이스 세션

    Returns:
        AIFeedbackResponse: 성공 여부와 메시지
    """
    # 비동기 처리를 위한 내부 함수
    async def save_feedback_task():
        """Background task로 피드백 저장

        중요: FastAPI 요청 종료 후 실행되므로 독립적인 DB 세션을 생성해야 함
        """
        from src.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as task_db:
            try:
                service = AIFeedbackService(db=task_db)
                await service.save_feedback(
                    admin_id=current_admin.admin_id,
                    feedback=request
                )
                await task_db.commit()

                logger.info(
                    "feedback_submitted",
                    extra={
                        "event": "feedback_submitted",
                        "admin_id": current_admin.admin_id,
                        "query_id": request.query_id,
                        "rating": request.rating,
                        "has_comment": request.comment is not None,
                    }
                )
            except Exception as e:
                await task_db.rollback()
                logger.error(
                    "feedback_submission_failed",
                    extra={
                        "event": "feedback_submission_failed",
                        "admin_id": current_admin.admin_id,
                        "query_id": request.query_id,
                        "error": str(e),
                    }
                )

    # BackgroundTasks에 피드백 저장 작업 추가
    background_tasks.add_task(save_feedback_task)

    # 즉시 성공 응답 반환 (UX 방해 없음)
    return AIFeedbackResponse(
        success=True,
        message="피드백이 제출되었습니다. 감사합니다!"
    )


# ============================================================================
# Story 6-2: 응답 캐싱 시스템 API
# ============================================================================

@router.get("/cache/stats", response_model=dict)
async def get_cache_stats(
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis | None = Depends(get_redis_client),
):
    """캐시 통계 조회
    
    Args:
        current_admin: 인증된 관리자
        redis_client: Redis 클라이언트
        
    Returns:
        dict: 캐시 통계 (히트율, 응답 시간 등)
    """
    from src.services.ai.utils.cache_manager import AICacheManager
    
    # Redis 클라이언트 생성
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
        )
    
    try:
        cache_manager = AICacheManager(redis_client)
        stats = await cache_manager.get_stats()
        
        logger.info(
            "cache_stats_query",
            extra={
                "event": "cache_stats_query",
                "admin_id": current_admin.admin_id,
                "hit_rate": stats.hit_rate,
            }
        )
        
        return {
            "total_requests": stats.total_requests,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_rate": stats.hit_rate,
            "avg_response_time_cached": stats.avg_response_time_cached,
            "avg_response_time_uncached": stats.avg_response_time_uncached,
        }
    finally:
        if redis_client:
            await redis_client.close()


@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: str = Query(default="", description="무효화 패턴 (비어있으면 전체)"),
    current_admin: Admin = Depends(get_current_admin),
    redis_client: redis.Redis = Depends(lambda: None),
):
    """캐시 무효화 (Super Admin 전용)
    
    Args:
        pattern: 무효화할 캐시 패턴 (예: "query:", 비어있으면 전체 무효화)
        current_admin: 인증된 관리자
        redis_client: Redis 클라이언트
        
    Returns:
        dict: 삭제된 캐시 개수
        
    Raises:
        HTTPException: Super Admin이 아닌 경우 403
    """
    from src.services.ai.utils.cache_manager import AICacheManager
    
    # Super Admin 권한 확인
    if current_admin.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admin 권한 필요")
    
    # Redis 클라이언트 생성
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
        )
    
    try:
        cache_manager = AICacheManager(redis_client)
        
        if pattern:
            deleted = await cache_manager.invalidate_by_pattern(pattern)
        else:
            deleted = await cache_manager.invalidate_all()
        
        logger.info(
            "cache_invalidated",
            extra={
                "event": "cache_invalidated",
                "admin_id": current_admin.admin_id,
                "pattern": pattern or "all",
                "deleted_count": deleted,
            }
        )
        
        return {"deleted_count": deleted}
    finally:
        if redis_client:
            await redis_client.close()
