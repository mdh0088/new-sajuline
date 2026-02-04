"""
Graceful Degradation Manager 테스트.

Stories: STORY-6-1
FRs: AR19
"""
import pytest

from src.services.ai.utils.graceful_degradation import (
    GracefulDegradationManager,
    DegradationLevel,
    DegradationStatus,
)


class TestDegradationLevels:
    """Degradation 레벨 정의 테스트"""

    def test_degradation_level_enum_values(self):
        """Degradation 레벨 Enum 값 확인"""
        assert DegradationLevel.FULL.value == 1
        assert DegradationLevel.FALLBACK.value == 2
        assert DegradationLevel.CACHED.value == 3
        assert DegradationLevel.UNAVAILABLE.value == 4


class TestGracefulDegradationManagerInitialization:
    """Graceful Degradation Manager 초기화 테스트"""

    def test_initial_level_is_full(self):
        """초기 레벨은 FULL"""
        manager = GracefulDegradationManager()
        assert manager.current_level == DegradationLevel.FULL

    def test_no_manual_override_initially(self):
        """초기에는 수동 오버라이드 없음"""
        manager = GracefulDegradationManager()
        assert manager._manual_override is None


class TestLevelManagement:
    """레벨 관리 테스트"""

    def test_set_level_changes_current_level(self):
        """레벨 설정이 현재 레벨 변경"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)

        assert manager.current_level == DegradationLevel.FALLBACK

    def test_manual_override_takes_precedence(self):
        """수동 오버라이드가 우선"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)
        manager.set_level(DegradationLevel.CACHED, manual=True)

        assert manager.current_level == DegradationLevel.CACHED

    def test_clear_manual_override_restores_automatic_level(self):
        """수동 오버라이드 해제 시 자동 레벨 복원"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)
        manager.set_level(DegradationLevel.UNAVAILABLE, manual=True)

        manager.clear_manual_override()

        assert manager.current_level == DegradationLevel.FALLBACK


class TestStatusRetrieval:
    """상태 조회 테스트"""

    def test_get_status_returns_correct_structure(self):
        """get_status가 올바른 구조 반환"""
        manager = GracefulDegradationManager()
        status = manager.get_status()

        assert isinstance(status, DegradationStatus)
        assert status.level == DegradationLevel.FULL
        assert isinstance(status.message, str)
        assert isinstance(status.available_features, list)
        assert isinstance(status.unavailable_features, list)

    def test_full_level_has_all_features(self):
        """FULL 레벨은 모든 기능 사용 가능"""
        manager = GracefulDegradationManager()
        status = manager.get_status()

        assert len(status.available_features) == 5
        assert len(status.unavailable_features) == 0

    def test_fallback_level_has_limited_features(self):
        """FALLBACK 레벨은 일부 기능 제한"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)
        status = manager.get_status()

        assert len(status.available_features) == 4
        assert len(status.unavailable_features) == 1

    def test_cached_level_has_minimal_features(self):
        """CACHED 레벨은 최소 기능만"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.CACHED)
        status = manager.get_status()

        assert len(status.available_features) == 3
        assert len(status.unavailable_features) == 2

    def test_unavailable_level_has_no_features(self):
        """UNAVAILABLE 레벨은 모든 기능 불가"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.UNAVAILABLE)
        status = manager.get_status()

        assert len(status.available_features) == 0
        assert len(status.unavailable_features) == 1


class TestFeatureAvailability:
    """기능 사용 가능 여부 테스트"""

    def test_is_feature_available_for_full_level(self):
        """FULL 레벨에서 모든 기능 사용 가능"""
        manager = GracefulDegradationManager()

        assert manager.is_feature_available("자연어 질의")
        assert manager.is_feature_available("SQL 생성")
        assert manager.is_feature_available("자연어 응답")
        assert manager.is_feature_available("자동완성")
        assert manager.is_feature_available("히스토리")

    def test_is_feature_available_for_fallback_level(self):
        """FALLBACK 레벨에서 일부 기능 사용 가능"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)

        assert manager.is_feature_available("자연어 질의")
        assert manager.is_feature_available("SQL 생성 (단순화)")
        assert manager.is_feature_available("자연어 응답 (기본)")
        assert manager.is_feature_available("히스토리")
        assert not manager.is_feature_available("자동완성")

    def test_is_feature_available_for_cached_level(self):
        """CACHED 레벨에서 캐시 기능만 사용 가능"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.CACHED)

        assert manager.is_feature_available("캐시된 응답 조회")
        assert manager.is_feature_available("히스토리")
        assert manager.is_feature_available("예시 질문")
        assert not manager.is_feature_available("새 질의 생성")

    def test_is_feature_available_for_unavailable_level(self):
        """UNAVAILABLE 레벨에서 모든 기능 사용 불가"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.UNAVAILABLE)

        assert not manager.is_feature_available("자연어 질의")
        assert not manager.is_feature_available("SQL 생성")


class TestLevelDetermination:
    """레벨 결정 로직 테스트"""

    def test_determine_level_returns_full_when_primary_healthy(self):
        """Primary 정상 시 FULL 레벨"""
        manager = GracefulDegradationManager()

        level = manager.determine_level_from_errors(
            primary_healthy=True,
            fallback_healthy=True,
            cache_available=True
        )

        assert level == DegradationLevel.FULL

    def test_determine_level_returns_fallback_when_primary_fails(self):
        """Primary 실패 시 FALLBACK 레벨"""
        manager = GracefulDegradationManager()

        level = manager.determine_level_from_errors(
            primary_healthy=False,
            fallback_healthy=True,
            cache_available=True
        )

        assert level == DegradationLevel.FALLBACK

    def test_determine_level_returns_cached_when_all_llms_fail(self):
        """모든 LLM 실패 시 CACHED 레벨"""
        manager = GracefulDegradationManager()

        level = manager.determine_level_from_errors(
            primary_healthy=False,
            fallback_healthy=False,
            cache_available=True
        )

        assert level == DegradationLevel.CACHED

    def test_determine_level_returns_unavailable_when_all_fail(self):
        """모든 시스템 실패 시 UNAVAILABLE 레벨"""
        manager = GracefulDegradationManager()

        level = manager.determine_level_from_errors(
            primary_healthy=False,
            fallback_healthy=False,
            cache_available=False
        )

        assert level == DegradationLevel.UNAVAILABLE


class TestStatusMessages:
    """상태 메시지 테스트"""

    def test_full_level_message(self):
        """FULL 레벨 메시지"""
        manager = GracefulDegradationManager()
        status = manager.get_status()

        assert "정상 운영 중" in status.message

    def test_fallback_level_message(self):
        """FALLBACK 레벨 메시지"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.FALLBACK)
        status = manager.get_status()

        assert "일부 기능이 제한" in status.message

    def test_cached_level_message(self):
        """CACHED 레벨 메시지"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.CACHED)
        status = manager.get_status()

        assert "새 질의가 제한" in status.message
        assert "캐시된 응답만" in status.message

    def test_unavailable_level_message(self):
        """UNAVAILABLE 레벨 메시지"""
        manager = GracefulDegradationManager()
        manager.set_level(DegradationLevel.UNAVAILABLE)
        status = manager.get_status()

        assert "일시적으로 이용할 수 없습니다" in status.message
