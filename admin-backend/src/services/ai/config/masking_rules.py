"""
민감 데이터 마스킹 규칙 설정.

컬럼 패턴별 마스킹 타입 매핑을 정의합니다.

Stories: 3-3-sensitive-data-masking
FRs: FR-016

## 새로운 마스킹 타입 추가 방법:
1. MaskingType enum에 새 타입 추가
2. MASKING_RULES에 규칙 추가 (type, column_patterns, description)
3. DataMasker에 _mask_{type}() 메서드 구현
4. 테이블별 커스텀 규칙이 필요하면 TABLE_SPECIFIC_RULES에 추가
"""

import re
from enum import Enum
from typing import List, TypedDict


class MaskingType(str, Enum):
    """마스킹 타입"""

    PHONE = "phone"
    EMAIL = "email"
    SSN = "ssn"
    CARD = "card"
    ACCOUNT = "account"
    NAME = "name"


class MaskingLevel(str, Enum):
    """마스킹 레벨"""

    NONE = "none"  # 마스킹 안 함 (Super Admin)
    PARTIAL = "partial"  # 부분 마스킹 (Admin)
    FULL = "full"  # 완전 마스킹 (Viewer)


class MaskingRule(TypedDict):
    """마스킹 규칙 타입"""

    type: str
    column_patterns: List[str]
    description: str


# 마스킹 규칙 정의 (컴파일된 정규식으로 성능 개선)
_MASKING_RULES_RAW: List[MaskingRule] = [
    {
        "type": MaskingType.PHONE.value,
        "column_patterns": [
            r"phone",
            r"mobile",
            r"tel",
            r"contact",
            r"휴대폰",
            r"전화",
        ],
        "description": "전화번호 마스킹",
    },
    {
        "type": MaskingType.EMAIL.value,
        "column_patterns": [
            r"email",
            r"mail",
            r"이메일",
        ],
        "description": "이메일 마스킹",
    },
    {
        "type": MaskingType.SSN.value,
        "column_patterns": [
            r"ssn",
            r"resident",
            r"jumin",
            r"주민",
            r"identity",
        ],
        "description": "주민번호 마스킹",
    },
    {
        "type": MaskingType.CARD.value,
        "column_patterns": [
            r"card",
            r"credit",
            r"카드",
        ],
        "description": "카드번호 마스킹",
    },
    {
        "type": MaskingType.ACCOUNT.value,
        "column_patterns": [
            r"account",
            r"bank",
            r"계좌",
        ],
        "description": "계좌번호 마스킹",
    },
    {
        "type": MaskingType.NAME.value,
        "column_patterns": [
            r"name",
            r"이름",
            r"성명",
        ],
        "description": "이름 마스킹",
    },
]


class _CompiledMaskingRules:
    """성능 최적화를 위한 컴파일된 마스킹 규칙 (ReDoS 방지)"""

    def __init__(self):
        self.rules: List[tuple[str, List[re.Pattern], str]] = []
        for rule in _MASKING_RULES_RAW:
            compiled_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in rule["column_patterns"]
            ]
            self.rules.append(
                (rule["type"], compiled_patterns, rule["description"])
            )

    def find_mask_type(self, column_name: str) -> str | None:
        """
        컬럼명에 매칭되는 마스킹 타입 반환.

        Args:
            column_name: 컬럼명 (소문자 변환됨)

        Returns:
            매칭된 마스킹 타입 또는 None
        """
        col_lower = column_name.lower()
        for mask_type, patterns, _ in self.rules:
            for pattern in patterns:
                try:
                    # timeout 없이 안전한 매칭 (단순 패턴만 사용)
                    if pattern.search(col_lower):
                        return mask_type
                except re.error:
                    # 정규식 에러 시 무시하고 계속
                    continue
        return None


# 전역 인스턴스 (모듈 로드 시 한 번만 컴파일)
MASKING_RULES = _CompiledMaskingRules()


# 테이블별 추가 마스킹 규칙 (AC 2: 테이블-컬럼 매핑)
TABLE_SPECIFIC_RULES: dict[str, dict[str, str]] = {
    "t_user": {
        "phone": MaskingType.PHONE.value,
        "email": MaskingType.EMAIL.value,
        "user_name": MaskingType.NAME.value,
    },
    "t_counselor": {
        "phone": MaskingType.PHONE.value,
        "bank_account": MaskingType.ACCOUNT.value,
        "counselor_name": MaskingType.NAME.value,
    },
    "t_admin": {
        "phone": MaskingType.PHONE.value,
        "email": MaskingType.EMAIL.value,
    },
}
