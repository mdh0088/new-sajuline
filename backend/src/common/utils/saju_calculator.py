"""
사주 계산 유틸리티

일진(일주), 십성, luck_score 계산을 위한 순수 함수 모듈입니다.
외부 의존성 없이 상수와 계산 로직만 포함합니다.

Story: 2-2-saju-calculation-utility
"""

from datetime import date
from typing import Literal

# =============================================================================
# 상수 정의 (Task 1)
# =============================================================================

# 천간 (10개)
CHEONGAN: list[str] = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]

# 지지 (12개)
JIJI: list[str] = [
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

# 십성 (10개)
SIPSUNG: list[str] = [
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

# 천간 → 오행 매핑
CHEONGAN_OHENG: dict[str, str] = {
    "갑": "목",
    "을": "목",
    "병": "화",
    "정": "화",
    "무": "토",
    "기": "토",
    "경": "금",
    "신": "금",
    "임": "수",
    "계": "수",
}

# 천간 → 음양 매핑
CHEONGAN_YIN_YANG: dict[str, str] = {
    "갑": "양",
    "을": "음",
    "병": "양",
    "정": "음",
    "무": "양",
    "기": "음",
    "경": "양",
    "신": "음",
    "임": "양",
    "계": "음",
}

# 오행 상생: 목→화→토→금→수→목
OHENG_GENERATE: dict[str, str] = {
    "목": "화",
    "화": "토",
    "토": "금",
    "금": "수",
    "수": "목",
}

# 오행 상극: 목→토→수→화→금→목
OHENG_CONQUER: dict[str, str] = {
    "목": "토",
    "토": "수",
    "수": "화",
    "화": "금",
    "금": "목",
}

# 십성별 카테고리별 기본 점수 (Task 4)
SIPSUNG_SCORE: dict[str, dict[str, int]] = {
    "총운": {
        "비견": 3,
        "겁재": 2,
        "식신": 4,
        "상관": 3,
        "정재": 4,
        "편재": 3,
        "정관": 4,
        "편관": 3,
        "정인": 4,
        "편인": 3,
    },
    "재물": {
        "정재": 5,
        "편재": 4,
        "식신": 4,
        "상관": 3,
        "비견": 2,
        "겁재": 2,
        "정관": 3,
        "편관": 2,
        "정인": 3,
        "편인": 2,
    },
    "연애": {
        "정재": 4,
        "편재": 3,
        "정관": 5,
        "편관": 3,
        "식신": 4,
        "상관": 4,
        "비견": 2,
        "겁재": 2,
        "정인": 3,
        "편인": 2,
    },
    "건강": {
        "비견": 4,
        "겁재": 3,
        "식신": 5,
        "상관": 3,
        "정재": 3,
        "편재": 2,
        "정관": 3,
        "편관": 2,
        "정인": 4,
        "편인": 3,
    },
    "직장": {
        "정관": 5,
        "편관": 4,
        "정재": 4,
        "편재": 3,
        "식신": 3,
        "상관": 2,
        "비견": 3,
        "겁재": 2,
        "정인": 4,
        "편인": 3,
    },
}

# 60갑자 주기 상수
SEXAGENARY_CYCLE = 60

# 지지 관계 보정값 (Task 4)
JIJI_MODIFIER: dict[str, int] = {
    # 12운성 (긍정)
    "건록": 1,
    "제왕": 1,
    "장생": 1,
    "관대": 1,
    # 12운성 (중립)
    "목욕": 0,
    "양": 0,
    "쇠": 0,
    "태": 0,
    "절": 0,
    # 12운성 (부정)
    "병": -1,
    "사": -1,
    "묘": -1,
    # 지지 관계
    "합": 1,
    "충": -1,
    "형": -1,
    "파": 0,
    "해": 0,
}

# =============================================================================
# 일진(일주) 계산 (Task 2)
# =============================================================================

# 기준일: 2000년 1월 7일 = 갑자일 (甲子日, index 0)
# Julian Day 기반으로 검증된 날짜
_BASE_DATE = date(2000, 1, 7)
_BASE_INDEX = 0  # 갑자


def get_ilju(target_date: date) -> tuple[str, str]:
    """
    주어진 날짜의 일주(일간+일지)를 계산합니다.

    60갑자 순환 알고리즘을 사용하여 정확한 일진을 계산합니다.
    기준일: 2000년 1월 7일 = 갑자일 (Julian Day 검증)

    Args:
        target_date: 계산할 날짜

    Returns:
        tuple[str, str]: (천간, 지지) 예: ("무", "오")

    Raises:
        ValueError: 잘못된 날짜 형식

    Examples:
        >>> get_ilju(date(2000, 1, 1))
        ('무', '오')
        >>> get_ilju(date(2024, 2, 10))
        ('갑', '진')
    """
    if not isinstance(target_date, date):
        raise ValueError(f"잘못된 날짜 형식입니다: {target_date}")

    diff = (target_date - _BASE_DATE).days
    index = (_BASE_INDEX + diff) % SEXAGENARY_CYCLE

    cheongan = CHEONGAN[index % 10]
    jiji = JIJI[index % 12]

    return cheongan, jiji


def get_today_ilju() -> tuple[str, str]:
    """
    오늘의 일주(일간+일지)를 반환합니다.

    Returns:
        tuple[str, str]: (천간, 지지)
    """
    return get_ilju(date.today())


# =============================================================================
# 십성 계산 (Task 3)
# =============================================================================


def _get_relation(my_oheng: str, other_oheng: str) -> str:
    """
    두 오행 간의 관계를 반환합니다.

    Returns:
        str: "same" | "generate" | "conquer" | "generated_by" | "conquered_by"
    """
    if my_oheng == other_oheng:
        return "same"
    if OHENG_GENERATE.get(my_oheng) == other_oheng:
        return "generate"  # 내가 생하는
    if OHENG_CONQUER.get(my_oheng) == other_oheng:
        return "conquer"  # 내가 극하는
    if OHENG_GENERATE.get(other_oheng) == my_oheng:
        return "generated_by"  # 나를 생하는
    if OHENG_CONQUER.get(other_oheng) == my_oheng:
        return "conquered_by"  # 나를 극하는
    return "unknown"


def calculate_sipsung(day_stem: str, birth_stem: str) -> str:
    """
    일간과 태어난 천간을 비교하여 십성을 계산합니다.

    Args:
        day_stem: 해당일의 일간 (천간)
        birth_stem: 사용자의 태어난 일간 (천간)

    Returns:
        str: 십성 이름 (비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인)

    Raises:
        ValueError: 잘못된 천간 입력

    Examples:
        >>> calculate_sipsung("갑", "갑")
        '비견'
        >>> calculate_sipsung("갑", "을")
        '겁재'
    """
    if day_stem not in CHEONGAN:
        raise ValueError(f"잘못된 천간입니다: {day_stem}")
    if birth_stem not in CHEONGAN:
        raise ValueError(f"잘못된 천간입니다: {birth_stem}")

    # day_stem(일간)이 "나", birth_stem(상대방 천간)이 "상대방"
    my_oheng = CHEONGAN_OHENG[day_stem]
    other_oheng = CHEONGAN_OHENG[birth_stem]
    my_yin_yang = CHEONGAN_YIN_YANG[day_stem]
    other_yin_yang = CHEONGAN_YIN_YANG[birth_stem]

    same_yin_yang = my_yin_yang == other_yin_yang
    relation = _get_relation(my_oheng, other_oheng)

    # 십성 결정 로직
    if relation == "same":
        return "비견" if same_yin_yang else "겁재"
    elif relation == "generate":
        return "식신" if same_yin_yang else "상관"
    elif relation == "conquer":
        return "정재" if same_yin_yang else "편재"
    elif relation == "conquered_by":
        return "정관" if same_yin_yang else "편관"
    elif relation == "generated_by":
        return "정인" if same_yin_yang else "편인"

    # 이론상 도달하지 않음
    raise ValueError(f"십성 계산 오류: {day_stem}, {birth_stem}")


# =============================================================================
# luck_score 계산 (Task 4)
# =============================================================================

CategoryType = Literal["총운", "재물", "연애", "건강", "직장"]


def calculate_luck_score(
    sipsung: str, jiji_relation: str, category: CategoryType
) -> int:
    """
    십성, 지지관계, 카테고리를 기반으로 luck_score를 계산합니다.

    Args:
        sipsung: 십성 이름
        jiji_relation: 지지 관계 (합, 충, 형 등)
        category: 운세 카테고리 (총운, 재물, 연애, 건강, 직장)

    Returns:
        int: 1~5 범위의 luck_score

    Raises:
        ValueError: 잘못된 십성 또는 카테고리

    Examples:
        >>> calculate_luck_score("식신", "합", "총운")
        5
    """
    if sipsung not in SIPSUNG:
        raise ValueError(f"잘못된 십성입니다: {sipsung}")
    if category not in SIPSUNG_SCORE:
        raise ValueError(f"잘못된 카테고리입니다: {category}")

    base_score = SIPSUNG_SCORE[category][sipsung]

    # 지지 관계 유효성 검증
    if jiji_relation not in JIJI_MODIFIER:
        raise ValueError(f"잘못된 지지관계입니다: {jiji_relation}")

    modifier = JIJI_MODIFIER[jiji_relation]

    # 최종값 1~5 범위 제한
    return max(1, min(5, base_score + modifier))


# =============================================================================
# 보조 함수 (Task 5)
# =============================================================================


def get_oheng(stem: str) -> str:
    """
    천간의 오행을 반환합니다.

    Args:
        stem: 천간

    Returns:
        str: 오행 (목, 화, 토, 금, 수)

    Raises:
        ValueError: 잘못된 천간
    """
    if stem not in CHEONGAN_OHENG:
        raise ValueError(f"잘못된 천간입니다: {stem}")
    return CHEONGAN_OHENG[stem]


def get_yin_yang(stem: str) -> str:
    """
    천간의 음양을 반환합니다.

    Args:
        stem: 천간

    Returns:
        str: 음양 ("양" 또는 "음")

    Raises:
        ValueError: 잘못된 천간
    """
    if stem not in CHEONGAN_YIN_YANG:
        raise ValueError(f"잘못된 천간입니다: {stem}")
    return CHEONGAN_YIN_YANG[stem]


# =============================================================================
# 연주(年柱) 계산 (Story 2.6)
# =============================================================================

# 기준: 2000년 = 경진년 (庚辰年)
_YEAR_BASE = 2000
_YEAR_BASE_GAN_IDX = 6  # 경 (庚)
_YEAR_BASE_JI_IDX = 4   # 진 (辰)

# 월지 상수 (정월=인월 기준)
MONTH_JIJI: list[str] = ["인", "묘", "진", "사", "오", "미", "신", "유", "술", "해", "자", "축"]

# 월별 계절/기운
MONTH_ENERGY: dict[int, str] = {
    1: "새해의 시작, 새로운 기운이 움트는 시기",
    2: "봄의 기운이 깨어나는 시기",
    3: "만물이 소생하는 활기찬 시기",
    4: "생명력이 활발해지는 시기",
    5: "여름의 열기가 시작되는 시기",
    6: "풍요와 성장의 절정기",
    7: "가을의 기운이 시작되는 시기",
    8: "결실을 준비하는 시기",
    9: "수확과 정리의 시기",
    10: "겨울을 준비하는 시기",
    11: "내면을 돌아보는 시기",
    12: "한 해를 마무리하는 시기",
}

# 월 이름 (한글)
MONTH_NAME_KO: dict[int, str] = {
    1: "정월", 2: "이월", 3: "삼월", 4: "사월",
    5: "오월", 6: "유월", 7: "칠월", 8: "팔월",
    9: "구월", 10: "시월", 11: "십일월", 12: "십이월",
}


def get_year_pillar(target_date: date) -> tuple[str, str]:
    """
    연주(연간+연지)를 계산합니다.

    60갑자 순환 알고리즘을 사용합니다.
    기준: 2000년 = 경진년 (庚辰年)

    Args:
        target_date: 계산할 날짜

    Returns:
        tuple[str, str]: (연간, 연지) 예: ("병", "오")

    Examples:
        >>> get_year_pillar(date(2026, 1, 30))
        ('병', '오')
        >>> get_year_pillar(date(2000, 1, 1))
        ('경', '진')
    """
    diff = target_date.year - _YEAR_BASE
    gan_idx = (_YEAR_BASE_GAN_IDX + diff) % 10
    ji_idx = (_YEAR_BASE_JI_IDX + diff) % 12

    return CHEONGAN[gan_idx], JIJI[ji_idx]


def get_month_branch(target_date: date) -> str:
    """
    월지(月支)를 반환합니다.

    정월(1월) = 인월(寅月) 기준
    참고: 정확한 절입 시간 계산은 생략 (MVP)

    Args:
        target_date: 대상 날짜

    Returns:
        str: 월지 (인, 묘, 진, ...)

    Examples:
        >>> get_month_branch(date(2026, 1, 30))
        '인'
        >>> get_month_branch(date(2026, 6, 15))
        '오'
    """
    # 1월 = 인월(인덱스 0), 2월 = 묘월(인덱스 1), ...
    month_idx = (target_date.month - 1) % 12
    return MONTH_JIJI[month_idx]


def get_month_energy(target_date: date) -> str:
    """
    해당 월의 기운/특성을 반환합니다.

    Args:
        target_date: 대상 날짜

    Returns:
        str: 월의 에너지 설명
    """
    return MONTH_ENERGY.get(target_date.month, "안정적인 기운의 시기")


def get_month_name(month: int) -> str:
    """
    월의 한글 이름을 반환합니다.

    Args:
        month: 월 (1~12)

    Returns:
        str: 월 이름 (정월, 이월, ...)
    """
    return MONTH_NAME_KO.get(month, f"{month}월")


def get_year_energy(target_date: date) -> str:
    """
    해당 연도의 기운/특성을 반환합니다.

    연주(년간+년지)의 오행을 기반으로 설명합니다.

    Args:
        target_date: 대상 날짜

    Returns:
        str: 연도의 에너지 설명
    """
    year_gan, year_ji = get_year_pillar(target_date)
    gan_oheng = CHEONGAN_OHENG[year_gan]

    energy_desc = {
        "목": "성장과 발전의 에너지가 강한 해",
        "화": "열정과 확장의 에너지가 강한 해",
        "토": "안정과 중심의 에너지가 강한 해",
        "금": "수확과 결실의 에너지가 강한 해",
        "수": "지혜와 유연함의 에너지가 강한 해",
    }

    return energy_desc.get(gan_oheng, "다양한 에너지가 조화를 이루는 해")
