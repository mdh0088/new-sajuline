# Story 3.3: 민감 데이터 마스킹

Status: ready-for-dev

## Story

As a 시스템,
I want 질의 결과 내 민감 데이터를 마스킹하기를,
so that PII가 노출되지 않는다.

## Acceptance Criteria

1. 정의된 민감 필드가 마스킹된다
   - 전화번호: `010-****-1234`
   - 이메일: `ki***@example.com`
   - 주민번호: `******-*******`
   - 카드번호: `****-****-****-1234`
   - 계좌번호: `***-**-******`
2. 마스킹 규칙이 설정 파일로 관리된다
   - YAML 또는 Python dict 형태
   - 테이블-컬럼 매핑
   - 마스킹 패턴 정의
3. 마스킹된 필드가 로그에 표시된다
   - 어떤 필드가 마스킹되었는지 기록
4. 민감 데이터 마스킹율이 100%이다
5. 역할별 마스킹 수준이 다르게 적용된다
   - Super Admin: 전체 표시 (또는 부분 마스킹)
   - Admin: 부분 마스킹
   - Viewer: 완전 마스킹

## Tasks / Subtasks

- [ ] Task 1: 데이터 마스커 구현 (AC: 1, 4, 5)
  - [ ] `src/services/ai/security/data_masking.py` 생성
  - [ ] `DataMasker` 클래스 구현
  - [ ] `MaskingResult` 데이터클래스 정의
  - [ ] `MASKING_LEVELS` 역할별 레벨 정의
  - [ ] `mask_data()` 메서드 구현
  - [ ] 마스킹 타입별 메서드 구현
    - [ ] `_mask_phone()` 전화번호
    - [ ] `_mask_email()` 이메일
    - [ ] `_mask_ssn()` 주민번호
    - [ ] `_mask_card()` 카드번호
    - [ ] `_mask_account()` 계좌번호
    - [ ] `_mask_name()` 이름
- [ ] Task 2: 마스킹 규칙 설정 구현 (AC: 2)
  - [ ] `src/services/ai/config/masking_rules.py` 생성
  - [ ] `MASKING_RULES` 상수 정의
  - [ ] 컬럼 패턴별 마스킹 타입 매핑
  - [ ] `TABLE_SPECIFIC_RULES` 테이블별 규칙
- [ ] Task 3: Layer 3 통합 (AC: 3, 4)
  - [ ] `src/services/ai/security/layer3_result.py` 업데이트
  - [ ] `validate_and_sanitize()` 마스킹 통합
  - [ ] `masked_columns` 로깅 추가
- [ ] Task 4: 단위 테스트 작성 (≥95% 커버리지) (AC: 1-5)
  - [ ] `tests/services/ai/security/test_data_masking.py` 생성
  - [ ] 각 마스킹 타입 테스트
  - [ ] 역할별 마스킹 레벨 테스트
  - [ ] 엣지 케이스 테스트
- [ ] Task 5: 린팅/타입 체크 통과
  - [ ] `black src/services/ai/` 실행
  - [ ] `isort src/services/ai/` 실행
  - [ ] `flake8 src/services/ai/` 실행
  - [ ] `mypy src/services/ai/` 실행

## Dev Notes

### Background

데이터베이스 조회 결과에는 전화번호, 이메일, 주민번호 등 개인 식별 정보(PII)가 포함될 수 있습니다. 이러한 민감 정보는 역할에 따라 마스킹 처리하여 데이터 유출을 방지해야 합니다.

### Data Masking Module

```python
# src/services/ai/security/data_masking.py
from typing import List, Dict, Any
from dataclasses import dataclass
import re
from src.services.ai.security.rbac import AIRole

@dataclass
class MaskingResult:
    data: List[Dict[str, Any]]
    masked_columns: List[str]
    mask_count: int

class DataMasker:
    """민감 데이터 마스킹"""

    # 역할별 마스킹 레벨
    MASKING_LEVELS = {
        AIRole.SUPER_ADMIN: "partial",  # 부분 마스킹
        AIRole.ADMIN: "partial",  # 부분 마스킹
        AIRole.VIEWER: "full",  # 완전 마스킹
    }

    @classmethod
    def mask_data(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        role: AIRole
    ) -> MaskingResult:
        """데이터 마스킹 수행"""
        from src.services.ai.config.masking_rules import MASKING_RULES

        masking_level = cls.MASKING_LEVELS.get(role, "full")
        masked_columns = []
        mask_count = 0

        masked_data = []
        for row in data:
            masked_row = row.copy()
            for col, value in row.items():
                if value is None:
                    continue

                col_lower = col.lower()
                for rule in MASKING_RULES:
                    if cls._matches_rule(col_lower, rule):
                        original = str(value)
                        masked = cls._apply_mask(
                            original,
                            rule["type"],
                            masking_level
                        )
                        if masked != original:
                            masked_row[col] = masked
                            if col not in masked_columns:
                                masked_columns.append(col)
                            mask_count += 1
                        break

            masked_data.append(masked_row)

        return MaskingResult(
            data=masked_data,
            masked_columns=masked_columns,
            mask_count=mask_count
        )

    @staticmethod
    def _mask_phone(value: str, level: str) -> str:
        """전화번호 마스킹: 010-****-1234"""
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            return "***-****-****" if level == "full" else value

        if level == "full":
            return "***-****-****"
        else:  # partial
            return f"{digits[:3]}-****-{digits[-4:]}"

    @staticmethod
    def _mask_email(value: str, level: str) -> str:
        """이메일 마스킹: ki***@example.com"""
        if '@' not in value:
            return "****@****.***" if level == "full" else value

        local, domain = value.split('@', 1)

        if level == "full":
            return "****@****.***"
        else:  # partial
            if len(local) <= 2:
                masked_local = local[0] + "***"
            else:
                masked_local = local[:2] + "***"
            return f"{masked_local}@{domain}"

    @staticmethod
    def _mask_ssn(value: str, level: str) -> str:
        """주민번호 마스킹: ******-*******"""
        return "******-*******"

    @staticmethod
    def _mask_card(value: str, level: str) -> str:
        """카드번호 마스킹: ****-****-****-1234"""
        digits = re.sub(r'\D', '', value)
        if len(digits) < 16:
            return "****-****-****-****"

        if level == "full":
            return "****-****-****-****"
        else:  # partial
            return f"****-****-****-{digits[-4:]}"

    @staticmethod
    def _mask_account(value: str, level: str) -> str:
        """계좌번호 마스킹"""
        if level == "full":
            return "***-**-******"
        else:
            cleaned = re.sub(r'\D', '', value)
            if len(cleaned) > 4:
                return "***-**-***" + cleaned[-4:]
            return "***-**-******"

    @staticmethod
    def _mask_name(value: str, level: str) -> str:
        """이름 마스킹: 김*수"""
        if not value or len(value) < 2:
            return "***"

        if level == "full":
            return "***"
        else:  # partial
            if len(value) == 2:
                return value[0] + "*"
            else:
                return value[0] + "*" * (len(value) - 2) + value[-1]
```

### Masking Rules Configuration

```python
# src/services/ai/config/masking_rules.py

MASKING_RULES = [
    {
        "type": "phone",
        "column_patterns": [
            r"phone",
            r"mobile",
            r"tel",
            r"contact",
            r"휴대폰",
            r"전화",
        ],
        "description": "전화번호 마스킹"
    },
    {
        "type": "email",
        "column_patterns": [
            r"email",
            r"mail",
            r"이메일",
        ],
        "description": "이메일 마스킹"
    },
    {
        "type": "ssn",
        "column_patterns": [
            r"ssn",
            r"resident",
            r"jumin",
            r"주민",
            r"identity",
        ],
        "description": "주민번호 마스킹"
    },
    {
        "type": "card",
        "column_patterns": [
            r"card",
            r"credit",
            r"카드",
        ],
        "description": "카드번호 마스킹"
    },
    {
        "type": "account",
        "column_patterns": [
            r"account",
            r"bank",
            r"계좌",
        ],
        "description": "계좌번호 마스킹"
    },
]

# 테이블별 추가 마스킹 규칙
TABLE_SPECIFIC_RULES = {
    "t_user": {
        "phone": "phone",
        "email": "email",
    },
    "t_counselor": {
        "phone": "phone",
        "bank_account": "account",
    }
}
```

### Integration with Layer 3

```python
# src/services/ai/security/layer3_result.py 확장
from src.services.ai.security.data_masking import DataMasker
from src.services.ai.security.rbac import AIRole

class Layer3ResultValidator:
    @classmethod
    def validate_and_sanitize(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        role: AIRole
    ) -> tuple[List[Dict[str, Any]], ResultValidationResult]:
        """결과 검증 및 정제 (마스킹 포함)"""

        # 1. 행 수 제한
        truncated = len(data) > cls.MAX_ROWS
        if truncated:
            data = data[:cls.MAX_ROWS]

        # 2. 민감 데이터 마스킹
        masking_result = DataMasker.mask_data(data, columns, role)

        return masking_result.data, ResultValidationResult(
            is_safe=True,
            row_count=len(masking_result.data),
            truncated=truncated,
            masked_columns=masking_result.masked_columns,
            warnings=[]
        )
```

### 테스트 시나리오

```python
def test_phone_masking_partial():
    result = DataMasker._mask_phone("010-1234-5678", "partial")
    assert result == "010-****-5678"

def test_email_masking_partial():
    result = DataMasker._mask_email("kimuser@example.com", "partial")
    assert result == "ki***@example.com"

def test_viewer_full_masking():
    data = [{"phone": "010-1234-5678", "email": "test@test.com"}]
    result = DataMasker.mask_data(data, ["phone", "email"], AIRole.VIEWER)
    assert result.data[0]["phone"] == "***-****-****"
```

### Dependencies

**Prerequisite Stories:**
- Story 3-1: 4-Layer Security 프레임워크 (Layer 3 기반)

**Blocked Stories:**
- 없음

### Architecture Requirements

- **FR16**: 민감 데이터 마스킹 ✓
- **NFR-S4**: 민감 데이터 마스킹 100% ✓
- **AR8**: Layer 3 Result Validation ✓

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Privacy]
- [KISA 개인정보 마스킹 가이드](https://www.privacy.go.kr/)

## Dev Agent Record

### Agent Model Used

(작업 완료 시 기록)

### Debug Log References

(디버깅 이슈 발생 시 기록)

### Completion Notes List

(각 Task 완료 시 기록)

### File List

(생성/수정된 파일 목록)
