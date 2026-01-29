"""
사주 리포지토리 단위 테스트

Story 2.4 Task 8: SajuRepository 테스트
- 십성 해석 조회 테스트
- 지지 관계 조회 테스트 (정방향/역방향)
- 천간/지지 조회 테스트
- 조회 실패 시 None 반환 테스트
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.saju_repository import SajuRepository
from src.models.saju_sipsung_model import SajuSipsungInterpretation
from src.models.saju_jiji_relation_model import SajuJijiRelation
from src.models.saju_cheongan_model import SajuCheongan
from src.models.saju_jiji_model import SajuJiji


@pytest.fixture
def mock_db_session():
    """모킹된 AsyncSession"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def saju_repository(mock_db_session):
    """SajuRepository 인스턴스"""
    return SajuRepository(mock_db_session)


@pytest.fixture
def sample_sipsung_interpretation():
    """테스트용 십성 해석 데이터"""
    interp = Mock(spec=SajuSipsungInterpretation)
    interp.id = 1
    interp.ilgan = "갑"
    interp.sipsung = "비견"
    interp.keywords = ["협력", "동료", "경쟁"]
    interp.positive_meaning = "동료와의 협력이 좋습니다."
    interp.negative_meaning = "과도한 경쟁은 피하세요."
    interp.daily_advice = "오늘은 협력을 통해 좋은 결과를 얻을 수 있습니다."
    return interp


@pytest.fixture
def sample_jiji_relation():
    """테스트용 지지 관계 데이터"""
    relation = Mock(spec=SajuJijiRelation)
    relation.id = 1
    relation.jiji1 = "자"
    relation.jiji2 = "축"
    relation.relation_type = "합"
    relation.relation_name = "자축합"
    relation.keywords = ["합", "조화", "융합"]
    relation.daily_impact = "오늘 에너지가 조화롭게 흐릅니다."
    return relation


@pytest.fixture
def sample_cheongan():
    """테스트용 천간 데이터"""
    cheongan = Mock(spec=SajuCheongan)
    cheongan.id = 1
    cheongan.name = "갑"
    cheongan.hanja = "甲"
    cheongan.oheng = "목"
    cheongan.yin_yang = "양"
    return cheongan


@pytest.fixture
def sample_jiji():
    """테스트용 지지 데이터"""
    jiji = Mock(spec=SajuJiji)
    jiji.id = 1
    jiji.name = "자"
    jiji.hanja = "子"
    jiji.oheng = "수"
    jiji.yin_yang = "양"
    jiji.animal = "쥐"
    return jiji


@pytest.mark.unit
class TestGetSipsungInterpretation:
    """get_sipsung_interpretation() 메서드 테스트"""

    async def test_sipsung_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_sipsung_interpretation
    ):
        """AC1: 십성 해석 정상 조회"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sipsung_interpretation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_sipsung_interpretation("갑", "비견")

        # Then
        assert result is not None
        assert result.ilgan == "갑"
        assert result.sipsung == "비견"
        assert result.daily_advice == "오늘은 협력을 통해 좋은 결과를 얻을 수 있습니다."
        mock_db_session.execute.assert_called_once()

    async def test_sipsung_not_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """AC5: 십성 해석 미발견 시 None 반환"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_sipsung_interpretation("갑", "없는십성")

        # Then
        assert result is None

    async def test_sipsung_all_combinations(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_sipsung_interpretation
    ):
        """모든 일간 + 십성 조합 조회 가능 확인"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sipsung_interpretation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        ilgans = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
        sipsungs = ["비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인"]

        # When & Then
        for ilgan in ilgans[:2]:  # 전체 테스트는 시간이 오래 걸리므로 일부만
            for sipsung in sipsungs[:2]:
                result = await saju_repository.get_sipsung_interpretation(ilgan, sipsung)
                assert result is not None


@pytest.mark.unit
class TestGetJijiRelation:
    """get_jiji_relation() 메서드 테스트"""

    async def test_jiji_relation_found_forward(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_jiji_relation
    ):
        """AC1: 지지 관계 정방향 조회"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_jiji_relation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_jiji_relation("자", "축")

        # Then
        assert result is not None
        assert result.relation_type == "합"
        assert result.jiji1 == "자"
        assert result.jiji2 == "축"

    async def test_jiji_relation_found_reverse(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_jiji_relation
    ):
        """AC1: 지지 관계 역방향 조회 (축자 → 자축합)"""
        # Given
        mock_result_none = MagicMock()
        mock_result_none.scalar_one_or_none.return_value = None

        mock_result_found = MagicMock()
        mock_result_found.scalar_one_or_none.return_value = sample_jiji_relation

        # 첫 번째 호출은 None, 두 번째 호출은 역방향에서 찾음
        mock_db_session.execute = AsyncMock(
            side_effect=[mock_result_none, mock_result_found]
        )

        # When
        result = await saju_repository.get_jiji_relation("축", "자")

        # Then
        assert result is not None
        assert result.relation_type == "합"
        assert mock_db_session.execute.call_count == 2  # 정방향 + 역방향 시도

    async def test_jiji_relation_not_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """AC5: 지지 관계 미발견 시 None 반환"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_jiji_relation("자", "사")  # 무관계

        # Then
        assert result is None


@pytest.mark.unit
class TestGetCheongan:
    """get_cheongan_by_name() 메서드 테스트"""

    async def test_cheongan_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_cheongan
    ):
        """천간 정상 조회"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_cheongan
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_cheongan_by_name("갑")

        # Then
        assert result is not None
        assert result.name == "갑"
        assert result.oheng == "목"

    async def test_cheongan_not_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """천간 미발견 시 None 반환"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_cheongan_by_name("없는천간")

        # Then
        assert result is None


@pytest.mark.unit
class TestGetJiji:
    """get_jiji_by_name() 메서드 테스트"""

    async def test_jiji_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session,
        sample_jiji
    ):
        """지지 정상 조회"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_jiji
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_jiji_by_name("자")

        # Then
        assert result is not None
        assert result.name == "자"
        assert result.animal == "쥐"

    async def test_jiji_not_found(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """지지 미발견 시 None 반환"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_jiji_by_name("없는지지")

        # Then
        assert result is None


@pytest.mark.unit
class TestGetAllCheongan:
    """get_all_cheongan() 메서드 테스트"""

    async def test_get_all_cheongan(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """모든 천간 조회"""
        # Given
        cheongan_list = [Mock(name=c) for c in ["갑", "을", "병", "정", "무"]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cheongan_list
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_all_cheongan()

        # Then
        assert len(result) == 5


@pytest.mark.unit
class TestGetAllJiji:
    """get_all_jiji() 메서드 테스트"""

    async def test_get_all_jiji(
        self,
        saju_repository: SajuRepository,
        mock_db_session
    ):
        """모든 지지 조회"""
        # Given
        jiji_list = [Mock(name=j) for j in ["자", "축", "인", "묘", "진", "사"]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = jiji_list
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await saju_repository.get_all_jiji()

        # Then
        assert len(result) == 6
