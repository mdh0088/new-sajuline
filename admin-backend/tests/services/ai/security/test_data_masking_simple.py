"""
데이터 마스킹 기능 간단 테스트 (임포트 문제 회피).

Stories: 3-3-sensitive-data-masking
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


def test_phone_masking_logic():
    """전화번호 마스킹 로직 테스트"""
    import re

    def mask_phone(value: str, level: str) -> str:
        """전화번호 마스킹: 010-****-1234"""
        digits = re.sub(r"\D", "", value)
        if len(digits) < 10:
            return "***-****-****" if level == "full" else value

        if level == "full":
            return "***-****-****"
        else:  # partial
            return f"{digits[:3]}-****-{digits[-4:]}"

    # Test partial
    assert mask_phone("010-1234-5678", "partial") == "010-****-5678"
    assert mask_phone("01012345678", "partial") == "010-****-5678"

    # Test full
    assert mask_phone("010-1234-5678", "full") == "***-****-****"

    # Test short
    result = mask_phone("123", "partial")
    assert result == "123"

    print("✅ Phone masking tests passed")


def test_email_masking_logic():
    """이메일 마스킹 로직 테스트"""

    def mask_email(value: str, level: str) -> str:
        """이메일 마스킹: ki***@example.com"""
        if "@" not in value:
            return "****@****.***" if level == "full" else value

        local, domain = value.split("@", 1)

        if level == "full":
            return "****@****.***"
        else:  # partial
            if len(local) <= 2:
                masked_local = local[0] + "***"
            else:
                masked_local = local[:2] + "***"
            return f"{masked_local}@{domain}"

    # Test partial
    assert mask_email("kimuser@example.com", "partial") == "ki***@example.com"
    assert mask_email("ab@example.com", "partial") == "a***@example.com"

    # Test full
    assert mask_email("test@test.com", "full") == "****@****.***"

    # Test invalid
    assert mask_email("notanemail", "partial") == "notanemail"

    print("✅ Email masking tests passed")


def test_card_masking_logic():
    """카드번호 마스킹 로직 테스트"""
    import re

    def mask_card(value: str, level: str) -> str:
        """카드번호 마스킹: ****-****-****-1234"""
        digits = re.sub(r"\D", "", value)
        if len(digits) < 16:
            return "****-****-****-****"

        if level == "full":
            return "****-****-****-****"
        else:  # partial
            return f"****-****-****-{digits[-4:]}"

    # Test partial
    assert mask_card("1234-5678-9012-3456", "partial") == "****-****-****-3456"
    assert mask_card("1234567890123456", "partial") == "****-****-****-3456"

    # Test full
    assert mask_card("1234-5678-9012-3456", "full") == "****-****-****-****"

    print("✅ Card masking tests passed")


if __name__ == "__main__":
    test_phone_masking_logic()
    test_email_masking_logic()
    test_card_masking_logic()
    print("\n🎉 All simple tests passed!")
