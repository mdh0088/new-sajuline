"""
데이터 마스킹 기능 테스트.

역할별 민감 데이터 마스킹을 검증합니다.

Stories: 3-3-sensitive-data-masking
FRs: FR-016, NFR-S4

수정: 2026-02-04 - import 에러 해결 및 edge case 추가
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock database imports to avoid aiomysql dependency
sys.modules["aiomysql"] = MagicMock()
sys.modules["src.core.database"] = MagicMock()

from src.services.ai.config.masking_rules import MaskingLevel, MaskingType
from src.services.ai.security.data_masking import DataMasker, MaskingResult
from src.services.ai.security.rbac import AIRole


class TestPhoneMasking:
    """전화번호 마스킹 테스트"""

    def test_mask_phone_partial_standard(self):
        """표준 전화번호 부분 마스킹"""
        result = DataMasker._mask_phone(
            "010-1234-5678", MaskingLevel.PARTIAL.value
        )
        assert result == "010-****-5678"

    def test_mask_phone_partial_no_dash(self):
        """하이픈 없는 전화번호 부분 마스킹"""
        result = DataMasker._mask_phone(
            "01012345678", MaskingLevel.PARTIAL.value
        )
        assert result == "010-****-5678"

    def test_mask_phone_full(self):
        """전화번호 완전 마스킹"""
        result = DataMasker._mask_phone("010-1234-5678", MaskingLevel.FULL.value)
        assert result == "***-****-****"

    def test_mask_phone_none(self):
        """전화번호 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_phone("010-1234-5678", MaskingLevel.NONE.value)
        assert result == "010-1234-5678"

    def test_mask_phone_invalid_short(self):
        """짧은 전화번호 (유효하지 않음)"""
        result = DataMasker._mask_phone("123", MaskingLevel.PARTIAL.value)
        assert result == "123"  # 원본 반환

        result = DataMasker._mask_phone("123", MaskingLevel.FULL.value)
        assert result == "***-****-****"

    def test_mask_phone_very_long(self):
        """매우 긴 전화번호 (Edge Case)"""
        result = DataMasker._mask_phone(
            "010-1234-5678-9999", MaskingLevel.PARTIAL.value
        )
        # 숫자만 추출 후 앞3자리-****-뒤4자리
        assert result == "010-****-9999"


class TestEmailMasking:
    """이메일 마스킹 테스트"""

    def test_mask_email_partial_normal(self):
        """일반 이메일 부분 마스킹"""
        result = DataMasker._mask_email(
            "kimuser@example.com", MaskingLevel.PARTIAL.value
        )
        assert result == "ki***@example.com"

    def test_mask_email_partial_short_local(self):
        """짧은 로컬 부분 이메일"""
        result = DataMasker._mask_email(
            "ab@example.com", MaskingLevel.PARTIAL.value
        )
        assert result == "a***@example.com"

    def test_mask_email_full(self):
        """이메일 완전 마스킹"""
        result = DataMasker._mask_email(
            "test@test.com", MaskingLevel.FULL.value
        )
        assert result == "****@****.***"

    def test_mask_email_none(self):
        """이메일 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_email(
            "test@test.com", MaskingLevel.NONE.value
        )
        assert result == "test@test.com"

    def test_mask_email_invalid_no_at(self):
        """@ 없는 잘못된 이메일"""
        result = DataMasker._mask_email("notanemail", MaskingLevel.PARTIAL.value)
        assert result == "notanemail"  # 원본 반환

        result = DataMasker._mask_email("notanemail", MaskingLevel.FULL.value)
        assert result == "****@****.***"

    def test_mask_email_with_unicode(self):
        """유니코드 포함 이메일 (Edge Case)"""
        result = DataMasker._mask_email(
            "test한글@example.com", MaskingLevel.PARTIAL.value
        )
        assert result.startswith("te***@")


class TestSSNMasking:
    """주민번호 마스킹 테스트"""

    def test_mask_ssn_always_full(self):
        """주민번호 완전 마스킹 (항상 전체 마스킹)"""
        result = DataMasker._mask_ssn(
            "123456-1234567", MaskingLevel.PARTIAL.value
        )
        assert result == "******-*******"

        result = DataMasker._mask_ssn("123456-1234567", MaskingLevel.FULL.value)
        assert result == "******-*******"

    def test_mask_ssn_none(self):
        """주민번호 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_ssn("123456-1234567", MaskingLevel.NONE.value)
        assert result == "123456-1234567"


class TestCardMasking:
    """카드번호 마스킹 테스트"""

    def test_mask_card_partial_standard(self):
        """표준 카드번호 부분 마스킹"""
        result = DataMasker._mask_card(
            "1234-5678-9012-3456", MaskingLevel.PARTIAL.value
        )
        assert result == "****-****-****-3456"

    def test_mask_card_partial_no_dash(self):
        """하이픈 없는 카드번호"""
        result = DataMasker._mask_card(
            "1234567890123456", MaskingLevel.PARTIAL.value
        )
        assert result == "****-****-****-3456"

    def test_mask_card_full(self):
        """카드번호 완전 마스킹"""
        result = DataMasker._mask_card(
            "1234-5678-9012-3456", MaskingLevel.FULL.value
        )
        assert result == "****-****-****-****"

    def test_mask_card_none(self):
        """카드번호 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_card(
            "1234-5678-9012-3456", MaskingLevel.NONE.value
        )
        assert result == "1234-5678-9012-3456"

    def test_mask_card_invalid_short(self):
        """짧은 카드번호 (유효하지 않음)"""
        result = DataMasker._mask_card("1234", MaskingLevel.PARTIAL.value)
        assert result == "****-****-****-****"


class TestAccountMasking:
    """계좌번호 마스킹 테스트"""

    def test_mask_account_partial(self):
        """계좌번호 부분 마스킹"""
        result = DataMasker._mask_account(
            "110-456-789012", MaskingLevel.PARTIAL.value
        )
        assert result == "***-**-***9012"

    def test_mask_account_full(self):
        """계좌번호 완전 마스킹"""
        result = DataMasker._mask_account(
            "110-456-789012", MaskingLevel.FULL.value
        )
        assert result == "***-**-******"

    def test_mask_account_none(self):
        """계좌번호 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_account(
            "110-456-789012", MaskingLevel.NONE.value
        )
        assert result == "110-456-789012"

    def test_mask_account_short(self):
        """짧은 계좌번호"""
        result = DataMasker._mask_account("123", MaskingLevel.PARTIAL.value)
        assert result == "***-**-******"


class TestNameMasking:
    """이름 마스킹 테스트"""

    def test_mask_name_partial_three_chars(self):
        """3자 이름 부분 마스킹"""
        result = DataMasker._mask_name("김철수", MaskingLevel.PARTIAL.value)
        assert result == "김*수"

    def test_mask_name_partial_two_chars(self):
        """2자 이름 부분 마스킹"""
        result = DataMasker._mask_name("김철", MaskingLevel.PARTIAL.value)
        assert result == "김*"

    def test_mask_name_full(self):
        """이름 완전 마스킹"""
        result = DataMasker._mask_name("김철수", MaskingLevel.FULL.value)
        assert result == "***"

    def test_mask_name_none(self):
        """이름 마스킹 안 함 (Super Admin)"""
        result = DataMasker._mask_name("김철수", MaskingLevel.NONE.value)
        assert result == "김철수"

    def test_mask_name_empty(self):
        """빈 이름"""
        result = DataMasker._mask_name("", MaskingLevel.PARTIAL.value)
        assert result == "***"

        result = DataMasker._mask_name(None, MaskingLevel.PARTIAL.value)
        assert result == "***"


class TestDataMaskerIntegration:
    """DataMasker 통합 테스트"""

    def test_mask_data_super_admin_no_masking(self):
        """Super Admin 역할 - 마스킹 안 함 (AC 5)"""
        data = [
            {
                "name": "김철수",
                "phone": "010-1234-5678",
                "email": "test@example.com",
                "age": 30,
            }
        ]
        columns = ["name", "phone", "email", "age"]

        result = DataMasker.mask_data(data, columns, AIRole.SUPER_ADMIN)

        # 마스킹 안 함
        assert result.data[0]["phone"] == "010-1234-5678"
        assert result.data[0]["email"] == "test@example.com"
        assert result.data[0]["name"] == "김철수"
        assert result.masked_columns == []
        assert result.mask_count == 0

    def test_mask_data_viewer_full_masking(self):
        """Viewer 역할 - 완전 마스킹"""
        data = [
            {
                "name": "김철수",
                "phone": "010-1234-5678",
                "email": "test@example.com",
                "age": 30,
            }
        ]
        columns = ["name", "phone", "email", "age"]

        result = DataMasker.mask_data(data, columns, AIRole.VIEWER)

        assert result.data[0]["phone"] == "***-****-****"
        assert result.data[0]["email"] == "****@****.***"
        assert result.data[0]["name"] == "***"
        assert result.data[0]["age"] == 30  # 민감하지 않은 필드는 유지
        assert "phone" in result.masked_columns
        assert "email" in result.masked_columns
        assert "name" in result.masked_columns
        assert result.mask_count == 3

    def test_mask_data_admin_partial_masking(self):
        """Admin 역할 - 부분 마스킹"""
        data = [
            {
                "phone": "010-1234-5678",
                "email": "kim@test.com",
            }
        ]
        columns = ["phone", "email"]

        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)

        assert result.data[0]["phone"] == "010-****-5678"
        assert result.data[0]["email"] == "ki***@test.com"
        assert result.mask_count == 2

    def test_mask_data_table_specific_rules(self):
        """테이블별 마스킹 규칙 적용 (AC 2)"""
        data = [
            {
                "phone": "010-1111-1111",
                "email": "user@test.com",
                "user_name": "김철수",
            }
        ]
        columns = ["phone", "email", "user_name"]

        # t_user 테이블 규칙 적용
        result = DataMasker.mask_data(
            data, columns, AIRole.ADMIN, table_name="t_user"
        )

        assert result.data[0]["phone"] == "010-****-1111"
        assert result.data[0]["email"] == "us***@test.com"
        assert result.data[0]["user_name"] == "김*수"
        assert result.mask_count == 3

    def test_mask_data_multiple_rows(self):
        """여러 행 마스킹"""
        data = [
            {"phone": "010-1111-1111", "name": "김철수"},
            {"phone": "010-2222-2222", "name": "이영희"},
            {"phone": "010-3333-3333", "name": "박민수"},
        ]
        columns = ["phone", "name"]

        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)

        assert len(result.data) == 3
        assert result.mask_count == 6  # 3명 * 2필드
        assert result.data[0]["phone"] == "010-****-1111"
        assert result.data[1]["phone"] == "010-****-2222"

    def test_mask_data_null_values(self):
        """NULL 값 처리"""
        data = [
            {"phone": None, "email": "test@test.com"},
            {"phone": "010-1234-5678", "email": None},
        ]
        columns = ["phone", "email"]

        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)

        assert result.data[0]["phone"] is None  # NULL 유지
        assert result.data[1]["email"] is None
        assert result.mask_count == 2  # NULL이 아닌 값만 카운트

    def test_mask_data_no_sensitive_columns(self):
        """민감하지 않은 데이터"""
        data = [{"id": 1, "age": 30, "city": "Seoul"}]
        columns = ["id", "age", "city"]

        result = DataMasker.mask_data(data, columns, AIRole.VIEWER)

        assert result.data[0] == data[0]  # 원본 유지
        assert result.masked_columns == []
        assert result.mask_count == 0

    def test_mask_data_korean_column_names(self):
        """한국어 컬럼명 처리"""
        data = [{"전화번호": "010-1234-5678", "이메일": "test@test.com"}]
        columns = ["전화번호", "이메일"]

        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)

        assert result.data[0]["전화번호"] == "010-****-5678"
        assert result.data[0]["이메일"] == "te***@test.com"
        assert "전화번호" in result.masked_columns
        assert "이메일" in result.masked_columns

    def test_mask_data_mixed_case_columns(self):
        """대소문자 혼합 컬럼명"""
        data = [{"Phone": "010-1234-5678", "EMAIL": "test@test.com"}]
        columns = ["Phone", "EMAIL"]

        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)

        # 컬럼명은 대소문자 무관하게 매칭되어야 함
        assert result.data[0]["Phone"] == "010-****-5678"
        assert result.data[0]["EMAIL"] == "te***@test.com"


class TestMaskingLevels:
    """역할별 마스킹 레벨 테스트"""

    @pytest.mark.parametrize(
        "role,expected_level",
        [
            (AIRole.SUPER_ADMIN, MaskingLevel.NONE),
            (AIRole.ADMIN, MaskingLevel.PARTIAL),
            (AIRole.VIEWER, MaskingLevel.FULL),
        ],
    )
    def test_masking_level_by_role(self, role, expected_level):
        """역할별 마스킹 레벨 검증"""
        level = DataMasker.MASKING_LEVELS.get(role)
        assert level == expected_level


class TestEdgeCases:
    """엣지 케이스 테스트 (개선)"""

    def test_empty_data(self):
        """빈 데이터"""
        result = DataMasker.mask_data([], [], AIRole.VIEWER)
        assert result.data == []
        assert result.masked_columns == []
        assert result.mask_count == 0

    def test_empty_row_dict(self):
        """빈 딕셔너리 행"""
        data = [{}]
        result = DataMasker.mask_data(data, [], AIRole.VIEWER)
        assert result.data == [{}]
        assert result.mask_count == 0

    def test_special_characters_in_data(self):
        """특수 문자 포함 데이터"""
        data = [{"phone": "010-1234-5678!@#"}]
        result = DataMasker.mask_data(data, ["phone"], AIRole.ADMIN)
        # 숫자만 추출하여 마스킹
        assert result.data[0]["phone"] == "010-****-5678"

    def test_very_long_email(self):
        """매우 긴 이메일"""
        long_email = "a" * 50 + "@example.com"
        result = DataMasker._mask_email(long_email, MaskingLevel.PARTIAL.value)
        # 앞 2자 + *** + 도메인
        assert result.startswith("aa***@")

    def test_sql_injection_pattern_in_data(self):
        """SQLi 패턴 포함 데이터 (Edge Case)"""
        data = [{"email": "test'; DROP TABLE users--@evil.com"}]
        result = DataMasker.mask_data(data, ["email"], AIRole.ADMIN)
        # 정상적으로 이메일 마스킹 처리
        assert "@" in result.data[0]["email"]
        assert "***" in result.data[0]["email"]

    def test_large_dataset_performance(self):
        """대용량 데이터셋 성능 테스트 (1000+ rows)"""
        import time

        data = [
            {
                "phone": f"010-{i:04d}-{i:04d}",
                "email": f"user{i}@test.com",
                "name": f"사용자{i}",
            }
            for i in range(1000)
        ]
        columns = ["phone", "email", "name"]

        start = time.time()
        result = DataMasker.mask_data(data, columns, AIRole.ADMIN)
        elapsed = time.time() - start

        # 성능 검증: 1000행 < 100ms
        assert elapsed < 0.1, f"Too slow: {elapsed:.3f}s"
        assert result.mask_count == 3000  # 1000행 * 3컬럼
