"""
AI 에러를 사용자 친화적으로 변환하는 핸들러.

기술적 에러를 사용자가 이해하기 쉬운 메시지로 변환하고,
관련된 대안 질문을 제안합니다.

Stories: STORY-4-2
FRs: FR20, AR16, AR17
"""

from dataclasses import dataclass

from ..config.error_messages import ERROR_MESSAGES, get_error_guide
from .suggestion_generator import SuggestionGenerator


@dataclass
class UserFriendlyError:
    """사용자 친화적 에러 정보."""

    user_message: str
    suggestions: list[str]
    error_code: str
    technical_message: str | None = None
    error_guide: dict | None = None


class AIErrorHandler:
    """AI 에러를 사용자 친화적으로 변환."""

    # 에러 코드별 대안 제안 템플릿 매핑
    # 사용자 메시지는 error_messages.py에서 관리 (Single Source of Truth)
    ERROR_MAPPINGS = {
        "AIBI_SQL_GEN_FAILED": {
            "suggestions_template": "rephrase",
        },
        "AIBI_TABLE_NOT_ALLOWED": {
            "suggestions_template": "alternative_data",
        },
        "AIBI_LLM_TIMEOUT": {
            "suggestions_template": "retry",
        },
        "AIBI_EMPTY_RESULT": {
            "suggestions_template": "broaden_scope",
        },
        "AIBI_TOO_MANY_RESULTS": {
            "suggestions_template": "narrow_scope",
        },
    }

    @classmethod
    def handle_error(
        cls,
        error_code: str,
        original_question: str,
        technical_message: str | None = None,
    ) -> UserFriendlyError:
        """
        에러를 사용자 친화적으로 변환.

        Args:
            error_code: 에러 코드 (예: AIBI_SQL_GEN_FAILED)
            original_question: 사용자의 원래 질문
            technical_message: 기술적 에러 메시지 (선택)

        Returns:
            UserFriendlyError: 사용자 친화적 에러 정보
        """
        # 에러 코드별 템플릿 매핑 가져오기 (없으면 기본값)
        mapping = cls.ERROR_MAPPINGS.get(
            error_code,
            {
                "suggestions_template": "general",
            },
        )

        # error_messages.py에서 정의된 메시지 사용 (Single Source of Truth)
        user_message = ERROR_MESSAGES.get(
            error_code, "문제가 발생했습니다. 잠시 후 다시 시도해주세요."
        )

        suggestions = SuggestionGenerator.generate(
            template=mapping["suggestions_template"],
            original_question=original_question,
        )

        # 에러 유형별 안내 정보 가져오기
        error_guide = get_error_guide(error_code)

        return UserFriendlyError(
            user_message=user_message,
            suggestions=suggestions,
            error_code=error_code,
            technical_message=technical_message,
            error_guide=error_guide,
        )
