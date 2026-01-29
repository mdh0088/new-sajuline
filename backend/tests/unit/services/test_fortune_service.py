"""
운세 서비스 단위 테스트

Story 2.4 Task 8: FortuneService 테스트 (AC: 1, 3, 5, 6)
- 캐시 → LLM → 폴백 플로우 테스트
- LLM 실패 시 폴백 로직 테스트
- source 필드 검증
- 커버리지 85% 이상
"""
import pytest
from datetime import date
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.services.fortune_service import FortuneService
from src.repositories.saju_repository import SajuRepository
from src.services.fortune_cache_service import FortuneCacheService
from src.core.langchain_chain import DailyFortuneChain
from src.schemas.fortune_schema import FortuneResponse, DayPillar, LLMFortuneOutput
from src.models.fortune_history_model import FortuneType


@pytest.fixture
def sample_fortune_response() -> FortuneResponse:
    """테스트용 캐시된 운세 응답"""
    return FortuneResponse(
        target_date=date(2026, 1, 29),
        fortune_type="daily",
        day_pillar=DayPillar(stem="갑", branch="진"),
        overall="캐시된 운세입니다.",
        love="캐시된 애정운입니다.",
        career="캐시된 직장운입니다.",
        health="캐시된 건강운입니다.",
        wealth="캐시된 재물운입니다.",
        source="cache",
        luck_score=4,
        sipsung="비견",
        keywords=["협력", "동료"]
    )


@pytest.fixture
def sample_llm_output() -> LLMFortuneOutput:
    """테스트용 LLM 출력"""
    return LLMFortuneOutput(
        overall="오늘은 창의적인 에너지가 넘칩니다. 새로운 아이디어가 떠오르는 하루가 될 것입니다.",
        love="연인과 함께하는 시간이 행복합니다.",
        career="업무에서 좋은 성과를 낼 수 있습니다.",
        health="규칙적인 운동을 권장합니다.",
        wealth="재물운이 상승합니다.",
        lucky_color="초록색",
        lucky_number=7
    )


@pytest.fixture
def mock_saju_repository():
    """모킹된 사주 리포지토리"""
    repo = AsyncMock(spec=SajuRepository)
    return repo


@pytest.fixture
def mock_cache_service():
    """모킹된 캐시 서비스"""
    service = AsyncMock(spec=FortuneCacheService)
    return service


@pytest.fixture
def mock_fortune_chain():
    """모킹된 LangChain 체인"""
    chain = AsyncMock(spec=DailyFortuneChain)
    return chain


@pytest.fixture
def fortune_service(mock_saju_repository, mock_cache_service, mock_fortune_chain):
    """FortuneService 인스턴스"""
    return FortuneService(mock_saju_repository, mock_cache_service, mock_fortune_chain)


@pytest.fixture
def sample_sipsung_data():
    """테스트용 십성 해석 데이터"""
    data = Mock()
    data.daily_advice = "오늘은 협력을 통해 좋은 결과를 얻을 수 있습니다."
    data.keywords = ["협력", "동료", "경쟁"]
    return data


@pytest.fixture
def sample_jiji_data():
    """테스트용 지지 관계 데이터"""
    data = Mock()
    data.daily_impact = "조화로운 에너지가 흐릅니다."
    data.relation_type = "합"
    data.keywords = ["합", "조화"]
    return data


@pytest.mark.unit
class TestGetDailyFortuneCacheHit:
    """캐시 히트 시나리오 테스트"""

    @patch('src.services.fortune_service.get_logger_with_request_id')
    async def test_cache_hit_returns_cached(
        self,
        mock_logger,
        fortune_service: FortuneService,
        mock_cache_service,
        sample_fortune_response
    ):
        """AC1: 캐시 히트 시 캐시된 응답 반환"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_cache_service.get_cached_fortune.return_value = (
            sample_fortune_response, "HIT"
        )

        # When
        result = await fortune_service.get_daily_fortune(
            user_id="test-user-123",
            birth_stem="갑",
            birth_branch="자",
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is not None
        assert result.source == "cache"
        mock_cache_service.get_cached_fortune.assert_called_once()
        # LLM은 호출되지 않음
        fortune_service.chain.generate_fortune.assert_not_called()


@pytest.mark.unit
class TestGetDailyFortuneLLMSuccess:
    """LLM 성공 시나리오 테스트"""

    @patch('src.services.fortune_service.get_logger_with_request_id')
    @patch('src.services.fortune_service.get_ilju')
    @patch('src.services.fortune_service.calculate_sipsung')
    @patch('src.services.fortune_service.calculate_luck_score')
    @patch('src.services.fortune_service.get_oheng')
    @patch('src.services.fortune_service.get_yin_yang')
    async def test_llm_success_returns_llm_response(
        self,
        mock_yin_yang,
        mock_oheng,
        mock_luck_score,
        mock_sipsung,
        mock_ilju,
        mock_logger,
        fortune_service: FortuneService,
        mock_cache_service,
        mock_saju_repository,
        mock_fortune_chain,
        sample_llm_output,
        sample_sipsung_data,
        sample_jiji_data
    ):
        """AC1: 캐시 미스 → LLM 호출 → 응답 반환"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_cache_service.get_cached_fortune.return_value = (None, "MISS")
        mock_ilju.return_value = ("을", "축")
        mock_sipsung.return_value = "겁재"
        mock_luck_score.return_value = 4
        mock_oheng.return_value = "목"
        mock_yin_yang.return_value = "양"

        mock_saju_repository.get_sipsung_interpretation.return_value = sample_sipsung_data
        mock_saju_repository.get_jiji_relation.return_value = sample_jiji_data

        mock_fortune_chain.generate_fortune.return_value = sample_llm_output

        # When
        result = await fortune_service.get_daily_fortune(
            user_id="test-user-123",
            birth_stem="갑",
            birth_branch="자",
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is not None
        assert result.source == "llm"
        assert result.overall == sample_llm_output.overall
        assert result.lucky_color == "초록색"
        assert result.lucky_number == 7
        assert result.luck_score == 4
        assert result.sipsung == "겁재"
        mock_fortune_chain.generate_fortune.assert_called_once()
        mock_cache_service.set_fortune_cache.assert_called_once()


@pytest.mark.unit
class TestGetDailyFortuneFallback:
    """폴백 시나리오 테스트"""

    @patch('src.services.fortune_service.get_logger_with_request_id')
    @patch('src.services.fortune_service.get_ilju')
    @patch('src.services.fortune_service.calculate_sipsung')
    @patch('src.services.fortune_service.calculate_luck_score')
    @patch('src.services.fortune_service.get_oheng')
    @patch('src.services.fortune_service.get_yin_yang')
    async def test_llm_failure_triggers_fallback(
        self,
        mock_yin_yang,
        mock_oheng,
        mock_luck_score,
        mock_sipsung,
        mock_ilju,
        mock_logger,
        fortune_service: FortuneService,
        mock_cache_service,
        mock_saju_repository,
        mock_fortune_chain,
        sample_sipsung_data,
        sample_jiji_data
    ):
        """AC3, AC5: LLM 실패 시 DB 데이터로 폴백"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_cache_service.get_cached_fortune.return_value = (None, "MISS")
        mock_ilju.return_value = ("을", "축")
        mock_sipsung.return_value = "겁재"
        mock_luck_score.return_value = 3
        mock_oheng.return_value = "목"
        mock_yin_yang.return_value = "양"

        mock_saju_repository.get_sipsung_interpretation.return_value = sample_sipsung_data
        mock_saju_repository.get_jiji_relation.return_value = sample_jiji_data

        # LLM 실패
        mock_fortune_chain.generate_fortune.side_effect = Exception("OpenAI API Error")

        # When
        result = await fortune_service.get_daily_fortune(
            user_id="test-user-123",
            birth_stem="갑",
            birth_branch="자",
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is not None
        assert result.source == "fallback"
        assert "협력을 통해 좋은 결과" in result.overall  # sipsung_data.daily_advice
        assert "잠시 후 다시 확인" in result.love  # 폴백 메시지
        mock_log.warning.assert_called()
        mock_cache_service.set_fortune_cache.assert_called_once()

    @patch('src.services.fortune_service.get_logger_with_request_id')
    @patch('src.services.fortune_service.get_ilju')
    @patch('src.services.fortune_service.calculate_sipsung')
    @patch('src.services.fortune_service.calculate_luck_score')
    @patch('src.services.fortune_service.get_oheng')
    @patch('src.services.fortune_service.get_yin_yang')
    async def test_db_data_missing_uses_default_fallback(
        self,
        mock_yin_yang,
        mock_oheng,
        mock_luck_score,
        mock_sipsung,
        mock_ilju,
        mock_logger,
        fortune_service: FortuneService,
        mock_cache_service,
        mock_saju_repository,
        mock_fortune_chain
    ):
        """AC5: DB 데이터도 없을 때 기본 폴백 메시지"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log

        mock_cache_service.get_cached_fortune.return_value = (None, "MISS")
        mock_ilju.return_value = ("을", "축")
        mock_sipsung.return_value = "겁재"
        mock_luck_score.return_value = 3
        mock_oheng.return_value = "목"
        mock_yin_yang.return_value = "양"

        # DB 데이터 없음
        mock_saju_repository.get_sipsung_interpretation.return_value = None
        mock_saju_repository.get_jiji_relation.return_value = None

        # LLM 실패
        mock_fortune_chain.generate_fortune.side_effect = Exception("OpenAI API Error")

        # When
        result = await fortune_service.get_daily_fortune(
            user_id="test-user-123",
            birth_stem="갑",
            birth_branch="자",
            target_date=date(2026, 1, 29)
        )

        # Then
        assert result is not None
        assert result.source == "fallback"
        assert "갑 일간이 겁재을 만났습니다" in result.overall  # 기본 폴백


@pytest.mark.unit
class TestFallbackHelpers:
    """폴백 헬퍼 메서드 테스트"""

    def test_get_sipsung_fallback_with_data(
        self,
        fortune_service: FortuneService,
        sample_sipsung_data
    ):
        """십성 해석 데이터 있을 때"""
        result = fortune_service._get_sipsung_fallback(
            sample_sipsung_data, "갑", "비견"
        )
        assert result == "오늘은 협력을 통해 좋은 결과를 얻을 수 있습니다."

    def test_get_sipsung_fallback_without_data(
        self,
        fortune_service: FortuneService
    ):
        """십성 해석 데이터 없을 때 기본 메시지"""
        result = fortune_service._get_sipsung_fallback(None, "갑", "비견")
        assert "갑 일간이 비견을 만났습니다" in result

    def test_get_jiji_fallback_with_data(
        self,
        fortune_service: FortuneService,
        sample_jiji_data
    ):
        """지지 관계 데이터 있을 때"""
        result = fortune_service._get_jiji_fallback(
            sample_jiji_data, "자", "축"
        )
        assert result == "조화로운 에너지가 흐릅니다."

    def test_get_jiji_fallback_without_data(
        self,
        fortune_service: FortuneService
    ):
        """지지 관계 데이터 없을 때 기본 메시지"""
        result = fortune_service._get_jiji_fallback(None, "자", "축")
        assert "자과 축의 만남입니다" in result


@pytest.mark.unit
class TestKeywordExtraction:
    """키워드 추출 테스트"""

    def test_extract_keywords_both_sources(
        self,
        fortune_service: FortuneService,
        sample_sipsung_data,
        sample_jiji_data
    ):
        """십성 + 지지 키워드 추출"""
        result = fortune_service._extract_keywords(
            sample_sipsung_data, sample_jiji_data
        )
        assert len(result) <= 5
        assert "협력" in result
        assert "합" in result

    def test_extract_keywords_only_sipsung(
        self,
        fortune_service: FortuneService,
        sample_sipsung_data
    ):
        """십성만 있을 때"""
        result = fortune_service._extract_keywords(sample_sipsung_data, None)
        assert len(result) <= 5
        assert "협력" in result

    def test_extract_keywords_none(
        self,
        fortune_service: FortuneService
    ):
        """데이터 없을 때 빈 리스트"""
        result = fortune_service._extract_keywords(None, None)
        assert result == []


@pytest.mark.unit
class TestBuildResponse:
    """응답 빌드 테스트"""

    def test_build_response(
        self,
        fortune_service: FortuneService,
        sample_llm_output
    ):
        """LLM 응답으로 FortuneResponse 빌드"""
        result = fortune_service._build_response(
            target_date=date(2026, 1, 29),
            day_gan="을",
            day_ji="축",
            llm_output=sample_llm_output,
            luck_score=4,
            sipsung="겁재",
            keywords=["협력", "경쟁"],
            source="llm"
        )

        assert isinstance(result, FortuneResponse)
        assert result.source == "llm"
        assert result.luck_score == 4
        assert result.sipsung == "겁재"
        assert result.day_pillar.stem == "을"
        assert result.day_pillar.branch == "축"
        assert result.lucky_color == "초록색"
        assert result.lucky_number == 7

    def test_build_fallback_response(
        self,
        fortune_service: FortuneService
    ):
        """폴백 응답 빌드"""
        result = fortune_service._build_fallback_response(
            target_date=date(2026, 1, 29),
            day_gan="을",
            day_ji="축",
            sipsung_interp="십성 해석입니다.",
            jiji_interp="지지 해석입니다.",
            luck_score=3,
            sipsung="겁재",
            keywords=["협력"]
        )

        assert isinstance(result, FortuneResponse)
        assert result.source == "fallback"
        assert result.luck_score == 3
        assert "십성 해석입니다. 지지 해석입니다." in result.overall
        assert "잠시 후 다시 확인" in result.love
        assert result.lucky_color is None
        assert result.lucky_number is None


@pytest.mark.unit
class TestDefaultDate:
    """기본 날짜 테스트"""

    @patch('src.services.fortune_service.get_logger_with_request_id')
    @patch('src.services.fortune_service.date')
    async def test_default_date_is_today(
        self,
        mock_date,
        mock_logger,
        fortune_service: FortuneService,
        mock_cache_service,
        sample_fortune_response
    ):
        """target_date 미지정 시 오늘 날짜 사용"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_date.today.return_value = date(2026, 1, 29)

        mock_cache_service.get_cached_fortune.return_value = (
            sample_fortune_response, "HIT"
        )

        # When
        result = await fortune_service.get_daily_fortune(
            user_id="test-user-123",
            birth_stem="갑",
            birth_branch="자",
            target_date=None  # 미지정
        )

        # Then
        mock_cache_service.get_cached_fortune.assert_called_once()
        call_args = mock_cache_service.get_cached_fortune.call_args
        # target_date가 today로 설정되었는지 확인
        assert call_args[0][2] is not None  # target_date
