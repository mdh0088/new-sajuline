"""
Graceful Degradation Manager.

4단계 점진적 서비스 저하를 관리합니다:
1. FULL - 모든 기능 사용 가능
2. FALLBACK - Fallback 모델 사용, 일부 기능 제한
3. CACHED - 캐시된 응답만 제공
4. UNAVAILABLE - 서비스 이용 불가

Stories: STORY-6-1
FRs: AR19
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """4단계 Graceful Degradation 레벨"""
    FULL = 1         # 완전 기능: gpt-4o-mini
    FALLBACK = 2     # Fallback: gpt-3.5-turbo
    CACHED = 3       # 캐시 응답만
    UNAVAILABLE = 4  # 서비스 불가


@dataclass
class DegradationStatus:
    """Degradation 상태 정보"""
    level: DegradationLevel
    message: str
    available_features: list[str]
    unavailable_features: list[str]


class GracefulDegradationManager:
    """
    4단계 Graceful Degradation 관리자.

    LLM 장애 시 점진적으로 서비스를 저하시켜 최소한의 기능을 유지합니다.

    Example:
        >>> manager = GracefulDegradationManager()
        >>> manager.set_level(DegradationLevel.FALLBACK)
        >>> status = manager.get_status()
        >>> print(status.message)
    """

    LEVEL_FEATURES = {
        DegradationLevel.FULL: {
            "available": [
                "자연어 질의",
                "SQL 생성",
                "자연어 응답",
                "자동완성",
                "히스토리"
            ],
            "unavailable": []
        },
        DegradationLevel.FALLBACK: {
            "available": [
                "자연어 질의",
                "SQL 생성 (단순화)",
                "자연어 응답 (기본)",
                "히스토리"
            ],
            "unavailable": ["자동완성 (일부 제한)"]
        },
        DegradationLevel.CACHED: {
            "available": [
                "캐시된 응답 조회",
                "히스토리",
                "예시 질문"
            ],
            "unavailable": [
                "새 질의 생성",
                "자동완성"
            ]
        },
        DegradationLevel.UNAVAILABLE: {
            "available": [],
            "unavailable": ["모든 AI 기능"]
        }
    }

    LEVEL_MESSAGES = {
        DegradationLevel.FULL: "정상 운영 중",
        DegradationLevel.FALLBACK: "일부 기능이 제한된 모드로 운영 중입니다",
        DegradationLevel.CACHED: "새 질의가 제한됩니다. 캐시된 응답만 제공됩니다",
        DegradationLevel.UNAVAILABLE: "AI 서비스를 일시적으로 이용할 수 없습니다"
    }

    def __init__(self):
        """Graceful Degradation Manager 초기화"""
        self._current_level = DegradationLevel.FULL
        self._manual_override: Optional[DegradationLevel] = None

    @property
    def current_level(self) -> DegradationLevel:
        """
        현재 Degradation 레벨.

        수동 오버라이드가 있으면 우선, 없으면 자동 레벨 반환.
        """
        return self._manual_override or self._current_level

    def set_level(self, level: DegradationLevel, manual: bool = False):
        """
        Degradation 레벨 설정.

        Args:
            level: 설정할 레벨
            manual: 수동 오버라이드 여부
        """
        if manual:
            self._manual_override = level
        else:
            self._current_level = level

        logger.warning(
            f"Degradation level changed to {level.name} (manual={manual})"
        )

    def clear_manual_override(self):
        """수동 오버라이드 해제"""
        self._manual_override = None
        logger.info("Degradation manual override cleared")

    def get_status(self) -> DegradationStatus:
        """
        현재 Degradation 상태 조회.

        Returns:
            DegradationStatus 객체
        """
        level = self.current_level
        features = self.LEVEL_FEATURES[level]

        return DegradationStatus(
            level=level,
            message=self.LEVEL_MESSAGES[level],
            available_features=features["available"],
            unavailable_features=features["unavailable"]
        )

    def is_feature_available(self, feature: str) -> bool:
        """
        특정 기능 사용 가능 여부 확인.

        Args:
            feature: 확인할 기능 이름

        Returns:
            사용 가능 여부
        """
        level = self.current_level
        return feature in self.LEVEL_FEATURES[level]["available"]

    def determine_level_from_errors(
        self,
        primary_healthy: bool,
        fallback_healthy: bool,
        cache_available: bool
    ) -> DegradationLevel:
        """
        에러 상태로부터 적절한 Degradation 레벨 결정.

        Args:
            primary_healthy: Primary LLM 정상 여부
            fallback_healthy: Fallback LLM 정상 여부
            cache_available: 캐시 사용 가능 여부

        Returns:
            결정된 Degradation 레벨
        """
        if primary_healthy:
            return DegradationLevel.FULL
        elif fallback_healthy:
            return DegradationLevel.FALLBACK
        elif cache_available:
            return DegradationLevel.CACHED
        else:
            return DegradationLevel.UNAVAILABLE
