"""
사주 계산 유틸리티 단위 테스트

일진(일주) 계산, 십성 계산, luck_score 계산 기능을 테스트합니다.
Story: 2-2-saju-calculation-utility
"""

from datetime import date

import pytest

from src.common.utils.saju_calculator import (  # 상수; 함수
    CHEONGAN,
    CHEONGAN_OHENG,
    CHEONGAN_YIN_YANG,
    JIJI,
    JIJI_MODIFIER,
    OHENG_CONQUER,
    OHENG_GENERATE,
    SEXAGENARY_CYCLE,
    SIPSUNG,
    SIPSUNG_SCORE,
    calculate_luck_score,
    calculate_sipsung,
    get_ilju,
    get_oheng,
    get_today_ilju,
    get_yin_yang,
)


@pytest.mark.unit
class TestConstants:
    """상수 정의 테스트 (Task 1)"""

    def test_cheongan_count(self):
        """천간은 10개여야 한다"""
        assert len(CHEONGAN) == 10

    def test_cheongan_values(self):
        """천간 목록 확인"""
        expected = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
        assert CHEONGAN == expected

    def test_jiji_count(self):
        """지지는 12개여야 한다"""
        assert len(JIJI) == 12

    def test_jiji_values(self):
        """지지 목록 확인"""
        expected = [
            "자",
            "축",
            "인",
            "묘",
            "진",
            "사",
            "오",
            "미",
            "신",
            "유",
            "술",
            "해",
        ]
        assert JIJI == expected

    def test_sipsung_count(self):
        """십성은 10개여야 한다"""
        assert len(SIPSUNG) == 10

    def test_sipsung_values(self):
        """십성 목록 확인"""
        expected = [
            "비견",
            "겁재",
            "식신",
            "상관",
            "편재",
            "정재",
            "편관",
            "정관",
            "편인",
            "정인",
        ]
        assert SIPSUNG == expected

    def test_cheongan_oheng_mapping(self):
        """천간-오행 매핑 확인"""
        assert CHEONGAN_OHENG["갑"] == "목"
        assert CHEONGAN_OHENG["을"] == "목"
        assert CHEONGAN_OHENG["병"] == "화"
        assert CHEONGAN_OHENG["정"] == "화"
        assert CHEONGAN_OHENG["무"] == "토"
        assert CHEONGAN_OHENG["기"] == "토"
        assert CHEONGAN_OHENG["경"] == "금"
        assert CHEONGAN_OHENG["신"] == "금"
        assert CHEONGAN_OHENG["임"] == "수"
        assert CHEONGAN_OHENG["계"] == "수"

    def test_sexagenary_cycle_constant(self):
        """60갑자 주기 상수 확인"""
        assert SEXAGENARY_CYCLE == 60

    def test_cheongan_yin_yang_mapping(self):
        """천간-음양 매핑 확인"""
        # 양: 갑, 병, 무, 경, 임
        assert CHEONGAN_YIN_YANG["갑"] == "양"
        assert CHEONGAN_YIN_YANG["병"] == "양"
        assert CHEONGAN_YIN_YANG["무"] == "양"
        assert CHEONGAN_YIN_YANG["경"] == "양"
        assert CHEONGAN_YIN_YANG["임"] == "양"
        # 음: 을, 정, 기, 신, 계
        assert CHEONGAN_YIN_YANG["을"] == "음"
        assert CHEONGAN_YIN_YANG["정"] == "음"
        assert CHEONGAN_YIN_YANG["기"] == "음"
        assert CHEONGAN_YIN_YANG["신"] == "음"
        assert CHEONGAN_YIN_YANG["계"] == "음"


@pytest.mark.unit
class TestGetIlju:
    """일진(일주) 계산 테스트 (Task 2)"""

    @pytest.mark.parametrize(
        "date_str,expected_gan,expected_ji",
        [
            ("2000-01-01", "무", "오"),  # Julian Day 검증
            ("2000-01-07", "갑", "자"),  # 기준일 (갑자일)
            ("2020-01-01", "계", "묘"),  # Julian Day 검증
            ("2024-02-10", "갑", "진"),  # 60갑자 순환 검증
        ],
    )
    def test_verified_dates(self, date_str: str, expected_gan: str, expected_ji: str):
        """검증된 날짜의 일진 계산"""
        # Given
        target = date.fromisoformat(date_str)

        # When
        gan, ji = get_ilju(target)

        # Then
        assert gan == expected_gan
        assert ji == expected_ji

    def test_60_day_cycle(self):
        """60일 후 동일 일주 반환"""
        # Given
        base = date(2000, 1, 1)
        after_60 = date(2000, 3, 1)  # 60일 후

        # When
        base_ilju = get_ilju(base)
        after_60_ilju = get_ilju(after_60)

        # Then
        assert base_ilju == after_60_ilju

    def test_consecutive_days_different(self):
        """연속 날짜는 다른 일주"""
        # Given
        day1 = date(2000, 1, 1)
        day2 = date(2000, 1, 2)

        # When
        ilju1 = get_ilju(day1)
        ilju2 = get_ilju(day2)

        # Then
        assert ilju1 != ilju2

    def test_return_type(self):
        """반환 타입 확인"""
        # When
        result = get_ilju(date(2000, 1, 1))

        # Then
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] in CHEONGAN
        assert result[1] in JIJI


@pytest.mark.unit
class TestCalculateSipsung:
    """십성 계산 테스트 (Task 3)"""

    @pytest.mark.parametrize(
        "day_stem,birth_stem,expected",
        [
            # 비견: 같은 오행, 같은 음양
            ("갑", "갑", "비견"),
            ("을", "을", "비견"),
            # 겁재: 같은 오행, 다른 음양
            ("갑", "을", "겁재"),
            ("을", "갑", "겁재"),
            # 식신: 내가 생하는 오행, 같은 음양 (목→화)
            ("갑", "병", "식신"),
            ("을", "정", "식신"),
            # 상관: 내가 생하는 오행, 다른 음양
            ("갑", "정", "상관"),
            ("을", "병", "상관"),
            # 편재: 내가 극하는 오행, 다른 음양 (목→토)
            ("갑", "기", "편재"),
            # 정재: 내가 극하는 오행, 같은 음양
            ("갑", "무", "정재"),
            # 편관: 나를 극하는 오행, 다른 음양 (금→목)
            ("갑", "신", "편관"),
            # 정관: 나를 극하는 오행, 같은 음양
            ("갑", "경", "정관"),
            # 편인: 나를 생하는 오행, 다른 음양 (수→목)
            ("갑", "계", "편인"),
            # 정인: 나를 생하는 오행, 같은 음양
            ("갑", "임", "정인"),
        ],
    )
    def test_sipsung_calculation(self, day_stem: str, birth_stem: str, expected: str):
        """십성 계산 검증"""
        # When
        result = calculate_sipsung(day_stem, birth_stem)

        # Then
        assert result == expected

    def test_invalid_day_stem_raises_error(self):
        """잘못된 일간 입력 시 ValueError"""
        # When / Then
        with pytest.raises(ValueError, match="잘못된 천간"):
            calculate_sipsung("X", "갑")

    def test_invalid_birth_stem_raises_error(self):
        """잘못된 태어난 천간 입력 시 ValueError"""
        # When / Then
        with pytest.raises(ValueError, match="잘못된 천간"):
            calculate_sipsung("갑", "Z")

    def test_return_type(self):
        """반환 타입 확인"""
        # When
        result = calculate_sipsung("갑", "을")

        # Then
        assert isinstance(result, str)
        assert result in SIPSUNG


@pytest.mark.unit
class TestCalculateLuckScore:
    """luck_score 계산 테스트 (Task 4)"""

    def test_score_in_range(self):
        """점수는 1~5 범위"""
        # When
        score = calculate_luck_score("식신", "합", "총운")

        # Then
        assert 1 <= score <= 5

    def test_consistency(self):
        """동일 입력은 동일 결과"""
        # When
        score1 = calculate_luck_score("정관", "충", "직장")
        score2 = calculate_luck_score("정관", "충", "직장")

        # Then
        assert score1 == score2

    @pytest.mark.parametrize(
        "sipsung,jiji_relation,category,expected_min,expected_max",
        [
            # 정재 + 합 + 재물 = 높은 점수 기대 (5 + 1 = 6 → 5)
            ("정재", "합", "재물", 4, 5),
            # 편관 + 충 + 직장 = 낮은 점수 기대 (4 - 1 = 3)
            ("편관", "충", "직장", 2, 4),
            # 비견 + 중립 + 건강 = 중간 점수 (4 + 0 = 4)
            ("비견", "목욕", "건강", 3, 5),
        ],
    )
    def test_score_calculation_ranges(
        self,
        sipsung: str,
        jiji_relation: str,
        category: str,
        expected_min: int,
        expected_max: int,
    ):
        """점수 계산 범위 검증"""
        # When
        score = calculate_luck_score(sipsung, jiji_relation, category)

        # Then
        assert expected_min <= score <= expected_max

    def test_positive_modifier_increases_score(self):
        """긍정적 지지관계는 점수를 높인다"""
        # Given
        base_score = calculate_luck_score("비견", "목욕", "총운")  # 중립
        high_score = calculate_luck_score("비견", "합", "총운")  # 긍정 (+1)

        # Then
        assert high_score >= base_score

    def test_negative_modifier_decreases_score(self):
        """부정적 지지관계는 점수를 낮춘다"""
        # Given
        base_score = calculate_luck_score("비견", "목욕", "총운")  # 중립
        low_score = calculate_luck_score("비견", "충", "총운")  # 부정 (-1)

        # Then
        assert low_score <= base_score

    def test_all_categories_supported(self):
        """모든 카테고리 지원 확인"""
        categories = ["총운", "재물", "연애", "건강", "직장"]
        for category in categories:
            score = calculate_luck_score("비견", "합", category)
            assert 1 <= score <= 5

    def test_invalid_sipsung_raises_error(self):
        """잘못된 십성 입력 시 ValueError"""
        with pytest.raises(ValueError, match="잘못된 십성"):
            calculate_luck_score("없는십성", "합", "총운")

    def test_invalid_category_raises_error(self):
        """잘못된 카테고리 입력 시 ValueError"""
        with pytest.raises(ValueError, match="잘못된 카테고리"):
            calculate_luck_score("비견", "합", "없는카테고리")

    def test_invalid_jiji_relation_raises_error(self):
        """잘못된 지지관계 입력 시 ValueError"""
        with pytest.raises(ValueError, match="잘못된 지지관계"):
            calculate_luck_score("비견", "없는관계", "총운")


@pytest.mark.unit
class TestHelperFunctions:
    """보조 함수 테스트 (Task 5)"""

    @pytest.mark.parametrize(
        "stem,expected_oheng",
        [
            ("갑", "목"),
            ("을", "목"),
            ("병", "화"),
            ("정", "화"),
            ("무", "토"),
            ("기", "토"),
            ("경", "금"),
            ("신", "금"),
            ("임", "수"),
            ("계", "수"),
        ],
    )
    def test_get_oheng(self, stem: str, expected_oheng: str):
        """천간의 오행 반환"""
        assert get_oheng(stem) == expected_oheng

    def test_get_oheng_invalid_raises_error(self):
        """잘못된 천간 입력 시 ValueError"""
        with pytest.raises(ValueError, match="잘못된 천간"):
            get_oheng("X")

    @pytest.mark.parametrize(
        "stem,expected_yin_yang",
        [
            ("갑", "양"),
            ("병", "양"),
            ("무", "양"),
            ("경", "양"),
            ("임", "양"),
            ("을", "음"),
            ("정", "음"),
            ("기", "음"),
            ("신", "음"),
            ("계", "음"),
        ],
    )
    def test_get_yin_yang(self, stem: str, expected_yin_yang: str):
        """천간의 음양 반환"""
        assert get_yin_yang(stem) == expected_yin_yang

    def test_get_yin_yang_invalid_raises_error(self):
        """잘못된 천간 입력 시 ValueError"""
        with pytest.raises(ValueError, match="잘못된 천간"):
            get_yin_yang("Z")

    def test_get_today_ilju_returns_tuple(self):
        """오늘 일진 반환 타입 확인"""
        # When
        result = get_today_ilju()

        # Then
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] in CHEONGAN
        assert result[1] in JIJI

    def test_get_today_ilju_matches_get_ilju(self):
        """get_today_ilju는 get_ilju(today)와 동일"""
        # Given
        today = date.today()

        # When
        today_ilju = get_today_ilju()
        manual_ilju = get_ilju(today)

        # Then
        assert today_ilju == manual_ilju
