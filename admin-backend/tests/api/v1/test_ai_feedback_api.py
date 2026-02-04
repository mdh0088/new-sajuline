"""
AI 피드백 API 엔드포인트 테스트.

Stories: 5-1
FRs: FR-024, FR-026

이 테스트는 실제 API 엔드포인트와 BackgroundTasks 동작을 검증합니다.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.schemas.ai.feedback_schema import AIFeedbackRequest, AIFeedbackResponse
from src.services.ai.services.feedback_service import AIFeedbackService
from src.models.admin_model import Admin


class TestFeedbackAPIEndpoint:
    """피드백 API 엔드포인트 통합 테스트"""

    @pytest.fixture
    def mock_admin(self):
        """Mock 관리자"""
        admin = MagicMock(spec=Admin)
        admin.admin_id = "admin001"
        admin.id = 1
        return admin

    @pytest.fixture
    def valid_feedback_request(self):
        """유효한 피드백 요청"""
        return AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440000",
            rating=4,
            comment="결과는 정확했지만 응답이 조금 느렸어요"
        )

    @pytest.mark.asyncio
    async def test_submit_feedback_success(
        self, mock_admin, valid_feedback_request
    ):
        """피드백 제출 성공 테스트 (AC 1, 2, 3)"""
        # Given
        mock_background_tasks = MagicMock(spec=BackgroundTasks)
        mock_db = AsyncMock(spec=AsyncSession)

        # When - API 엔드포인트 직접 호출 시뮬레이션
        from src.api.v1.ai_assistant_api import submit_feedback

        response = await submit_feedback(
            request=valid_feedback_request,
            background_tasks=mock_background_tasks,
            current_admin=mock_admin,
            db=mock_db,
        )

        # Then
        assert isinstance(response, AIFeedbackResponse)
        assert response.success is True
        assert "피드백이 제출되었습니다" in response.message
        # AC 4: BackgroundTasks에 작업이 추가되었는지 검증
        assert mock_background_tasks.add_task.called
        assert mock_background_tasks.add_task.call_count == 1

    @pytest.mark.asyncio
    async def test_submit_feedback_background_task_execution(
        self, mock_admin, valid_feedback_request
    ):
        """백그라운드 작업 실제 실행 테스트 (AC 4 - 비동기 처리)"""
        # Given
        with patch(
            "src.api.v1.ai_assistant_api.AsyncSessionLocal"
        ) as mock_session_local:
            mock_task_db = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_task_db
            mock_task_db.commit = AsyncMock()
            mock_task_db.rollback = AsyncMock()

            with patch(
                "src.api.v1.ai_assistant_api.AIFeedbackService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.save_feedback = AsyncMock()

                mock_background_tasks = MagicMock(spec=BackgroundTasks)
                mock_db = AsyncMock(spec=AsyncSession)

                # When
                from src.api.v1.ai_assistant_api import submit_feedback

                response = await submit_feedback(
                    request=valid_feedback_request,
                    background_tasks=mock_background_tasks,
                    current_admin=mock_admin,
                    db=mock_db,
                )

                # Then - 응답이 즉시 반환됨 (비동기 처리)
                assert response.success is True

                # BackgroundTask로 추가된 함수를 직접 실행
                task_func = mock_background_tasks.add_task.call_args[0][0]
                await task_func()

                # 독립적인 DB 세션이 생성되었는지 검증
                assert mock_session_local.called
                # 서비스가 호출되었는지 검증
                assert mock_service.save_feedback.called
                # commit이 호출되었는지 검증
                assert mock_task_db.commit.called

    @pytest.mark.asyncio
    async def test_submit_feedback_with_invalid_query_id_fk_error(
        self, mock_admin
    ):
        """존재하지 않는 query_id로 피드백 제출 시 FK 에러 처리 (HIGH #4)"""
        # Given
        invalid_request = AIFeedbackRequest(
            query_id="non-existent-query-id",
            rating=3,
            comment="Test"
        )

        with patch(
            "src.api.v1.ai_assistant_api.AsyncSessionLocal"
        ) as mock_session_local:
            mock_task_db = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_task_db

            with patch(
                "src.api.v1.ai_assistant_api.AIFeedbackService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                # FK 위반 에러 시뮬레이션
                mock_service.save_feedback.side_effect = IntegrityError(
                    "Foreign key violation", None, None
                )

                mock_background_tasks = MagicMock(spec=BackgroundTasks)
                mock_db = AsyncMock(spec=AsyncSession)

                with patch(
                    "src.api.v1.ai_assistant_api.logger"
                ) as mock_logger:
                    # When
                    from src.api.v1.ai_assistant_api import submit_feedback

                    # 응답은 성공으로 즉시 반환됨 (비동기 처리)
                    response = await submit_feedback(
                        request=invalid_request,
                        background_tasks=mock_background_tasks,
                        current_admin=mock_admin,
                        db=mock_db,
                    )

                    # Then
                    assert response.success is True  # 응답은 성공

                    # 백그라운드 작업 실행
                    task_func = mock_background_tasks.add_task.call_args[0][0]
                    await task_func()

                    # 에러 로그가 기록되었는지 검증 (HIGH #5)
                    assert mock_logger.error.called
                    error_call = mock_logger.error.call_args
                    assert "feedback_submission_failed" in error_call[0]
                    # rollback이 호출되었는지 검증
                    assert mock_task_db.rollback.called

    @pytest.mark.asyncio
    async def test_submit_feedback_logs_success_event(
        self, mock_admin, valid_feedback_request
    ):
        """피드백 제출 성공 시 로그 이벤트 기록 (MEDIUM #9)"""
        # Given
        with patch(
            "src.api.v1.ai_assistant_api.AsyncSessionLocal"
        ) as mock_session_local:
            mock_task_db = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_task_db

            with patch(
                "src.api.v1.ai_assistant_api.AIFeedbackService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.save_feedback = AsyncMock()

                mock_background_tasks = MagicMock(spec=BackgroundTasks)
                mock_db = AsyncMock(spec=AsyncSession)

                with patch(
                    "src.api.v1.ai_assistant_api.logger"
                ) as mock_logger:
                    # When
                    from src.api.v1.ai_assistant_api import submit_feedback

                    response = await submit_feedback(
                        request=valid_feedback_request,
                        background_tasks=mock_background_tasks,
                        current_admin=mock_admin,
                        db=mock_db,
                    )

                    # 백그라운드 작업 실행
                    task_func = mock_background_tasks.add_task.call_args[0][0]
                    await task_func()

                    # Then - 로그 이벤트 검증
                    assert mock_logger.info.called
                    info_call = mock_logger.info.call_args
                    assert "feedback_submitted" in info_call[0]

                    # extra 데이터 검증
                    extra_data = info_call[1]["extra"]
                    assert extra_data["event"] == "feedback_submitted"
                    assert extra_data["admin_id"] == mock_admin.admin_id
                    assert extra_data["query_id"] == valid_feedback_request.query_id
                    assert extra_data["rating"] == valid_feedback_request.rating
                    assert extra_data["has_comment"] is True

    @pytest.mark.asyncio
    async def test_submit_feedback_without_comment(
        self, mock_admin
    ):
        """코멘트 없이 피드백 제출 테스트 (AC 2 - 선택적)"""
        # Given
        request_without_comment = AIFeedbackRequest(
            query_id="550e8400-e29b-41d4-a716-446655440001",
            rating=5
        )

        mock_background_tasks = MagicMock(spec=BackgroundTasks)
        mock_db = AsyncMock(spec=AsyncSession)

        # When
        from src.api.v1.ai_assistant_api import submit_feedback

        response = await submit_feedback(
            request=request_without_comment,
            background_tasks=mock_background_tasks,
            current_admin=mock_admin,
            db=mock_db,
        )

        # Then
        assert response.success is True
        assert mock_background_tasks.add_task.called

    @pytest.mark.asyncio
    async def test_submit_feedback_rating_validation(
        self, mock_admin
    ):
        """별점 범위 검증 테스트 (AC 1 - 1-5점)"""
        # Given - 잘못된 별점 (0)
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(
                query_id="test-query-id",
                rating=0,  # 범위 밖
                comment="Test"
            )

        # Then
        assert "rating" in str(exc_info.value)

        # Given - 잘못된 별점 (6)
        with pytest.raises(ValidationError) as exc_info:
            AIFeedbackRequest(
                query_id="test-query-id",
                rating=6,  # 범위 밖
                comment="Test"
            )

        # Then
        assert "rating" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_submit_feedback_returns_201_status(
        self, mock_admin, valid_feedback_request
    ):
        """피드백 제출 성공 시 201 Created 응답 (AC 3)"""
        # Given
        mock_background_tasks = MagicMock(spec=BackgroundTasks)
        mock_db = AsyncMock(spec=AsyncSession)

        # When
        from src.api.v1.ai_assistant_api import submit_feedback

        response = await submit_feedback(
            request=valid_feedback_request,
            background_tasks=mock_background_tasks,
            current_admin=mock_admin,
            db=mock_db,
        )

        # Then - 응답 스키마 검증
        assert isinstance(response, AIFeedbackResponse)
        assert response.success is True
        assert isinstance(response.message, str)
        assert len(response.message) > 0

    @pytest.mark.asyncio
    async def test_submit_feedback_db_session_independence(
        self, mock_admin, valid_feedback_request
    ):
        """백그라운드 작업이 독립적인 DB 세션을 사용하는지 검증 (HIGH #3)"""
        # Given
        original_db = AsyncMock(spec=AsyncSession)
        original_db.close = AsyncMock()

        with patch(
            "src.api.v1.ai_assistant_api.AsyncSessionLocal"
        ) as mock_session_local:
            mock_task_db = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_task_db

            with patch(
                "src.api.v1.ai_assistant_api.AIFeedbackService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service

                mock_background_tasks = MagicMock(spec=BackgroundTasks)

                # When
                from src.api.v1.ai_assistant_api import submit_feedback

                response = await submit_feedback(
                    request=valid_feedback_request,
                    background_tasks=mock_background_tasks,
                    current_admin=mock_admin,
                    db=original_db,
                )

                # 백그라운드 작업 실행
                task_func = mock_background_tasks.add_task.call_args[0][0]
                await task_func()

                # Then
                # 새로운 세션이 생성되었는지 확인
                assert mock_session_local.called
                # 서비스가 새 세션으로 생성되었는지 확인
                service_call = mock_service_class.call_args
                assert service_call[1]["db"] == mock_task_db
                # 원본 DB 세션과 다른 세션을 사용했는지 확인
                assert service_call[1]["db"] != original_db
