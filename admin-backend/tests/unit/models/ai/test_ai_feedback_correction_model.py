"""
AIFeedbackCorrection 모델 테스트.

Stories: 5-2
FRs: FR25
"""


class TestAIFeedbackCorrectionModel:
    """AIFeedbackCorrection 모델 테스트."""

    def test_model_import(self):
        """모델을 import할 수 있는지 테스트."""
        # When
        from src.models.ai.ai_feedback_correction import AIFeedbackCorrection

        # Then
        assert AIFeedbackCorrection.__tablename__ == "t_ai_feedback_correction"

    def test_model_attributes(self):
        """모델 속성 존재 확인 테스트."""
        # When
        from src.models.ai.ai_feedback_correction import AIFeedbackCorrection

        # Then - 필수 컬럼 존재 확인
        assert hasattr(AIFeedbackCorrection, "id")
        assert hasattr(AIFeedbackCorrection, "admin_id")
        assert hasattr(AIFeedbackCorrection, "query_id")
        assert hasattr(AIFeedbackCorrection, "original_answer")
        assert hasattr(AIFeedbackCorrection, "corrected_answer")
        assert hasattr(AIFeedbackCorrection, "correction_reason")
        assert hasattr(AIFeedbackCorrection, "is_training_data")
        assert hasattr(AIFeedbackCorrection, "reviewed")
        assert hasattr(AIFeedbackCorrection, "reviewed_by")
        assert hasattr(AIFeedbackCorrection, "reviewed_at")
        assert hasattr(AIFeedbackCorrection, "created_at")

    def test_model_registered_in_init(self):
        """모델이 __init__.py에 등록되어 있는지 테스트."""
        # When
        from src.models.ai import AIFeedbackCorrection

        # Then
        assert AIFeedbackCorrection is not None
        assert AIFeedbackCorrection.__tablename__ == "t_ai_feedback_correction"


# 주의: 실제 DB 통합 테스트는 별도 환경 설정이 필요하므로
# 서비스 레이어 테스트에서 검증합니다.
