"""
테이블 화이트리스트 설정 테스트.

Stories: 2-3
FRs: FR-012
"""
import pytest

from src.services.ai.config.table_whitelist import (
    BASE_ALLOWED_TABLES,
    SENSITIVE_TABLES,
    ROLE_EXTRA_TABLES,
    get_allowed_tables,
    is_table_allowed,
    get_all_tables,
)
from src.services.ai.security.rbac import AIRole


class TestTableWhitelist:
    """테이블 화이트리스트 테스트"""

    def test_base_allowed_tables_not_empty(self):
        """기본 허용 테이블이 정의되어 있음"""
        assert len(BASE_ALLOWED_TABLES) > 0
        assert "t_user" in BASE_ALLOWED_TABLES
        assert "t_payment" in BASE_ALLOWED_TABLES

    def test_sensitive_tables_not_empty(self):
        """민감한 테이블이 정의되어 있음"""
        assert len(SENSITIVE_TABLES) > 0
        assert "t_admin" in SENSITIVE_TABLES
        assert "t_user_password" in SENSITIVE_TABLES

    def test_base_and_sensitive_no_overlap(self):
        """BASE와 SENSITIVE 테이블이 겹치지 않음"""
        overlap = BASE_ALLOWED_TABLES & SENSITIVE_TABLES
        assert len(overlap) == 0, f"겹치는 테이블: {overlap}"

    def test_get_allowed_tables_super_admin(self):
        """SUPER_ADMIN은 BASE + EXTRA 테이블 접근 가능"""
        tables = get_allowed_tables(AIRole.SUPER_ADMIN)

        # BASE 테이블 포함
        assert "t_user" in tables
        assert "t_payment" in tables

        # EXTRA 테이블 포함
        extra = ROLE_EXTRA_TABLES.get(AIRole.SUPER_ADMIN, set())
        for table in extra:
            assert table in tables

    def test_get_allowed_tables_admin(self):
        """ADMIN은 BASE 테이블만 접근 가능"""
        tables = get_allowed_tables(AIRole.ADMIN)

        # BASE 테이블 포함
        assert "t_user" in tables
        assert "t_payment" in tables

        # SENSITIVE 테이블 제외
        assert "t_admin" not in tables
        assert "t_user_password" not in tables

    def test_get_allowed_tables_viewer(self):
        """VIEWER도 BASE 테이블 접근 가능"""
        tables = get_allowed_tables(AIRole.VIEWER)

        # BASE 테이블 포함
        assert "t_user" in tables
        assert "t_payment" in tables

    def test_is_table_allowed_base_table(self):
        """BASE 테이블은 모든 역할이 접근 가능"""
        assert is_table_allowed("t_user", AIRole.VIEWER)
        assert is_table_allowed("t_user", AIRole.ADMIN)
        assert is_table_allowed("t_user", AIRole.SUPER_ADMIN)

    def test_is_table_allowed_sensitive_table(self):
        """SENSITIVE 테이블은 모든 역할이 접근 불가"""
        assert not is_table_allowed("t_admin", AIRole.VIEWER)
        assert not is_table_allowed("t_admin", AIRole.ADMIN)
        assert not is_table_allowed("t_admin", AIRole.SUPER_ADMIN)

        assert not is_table_allowed("t_user_password", AIRole.SUPER_ADMIN)

    def test_is_table_allowed_extra_table(self):
        """EXTRA 테이블은 해당 역할만 접근 가능"""
        # SUPER_ADMIN EXTRA 테이블
        extra_tables = ROLE_EXTRA_TABLES.get(AIRole.SUPER_ADMIN, set())

        if extra_tables:
            extra_table = list(extra_tables)[0]
            assert is_table_allowed(extra_table, AIRole.SUPER_ADMIN)
            assert not is_table_allowed(extra_table, AIRole.ADMIN)
            assert not is_table_allowed(extra_table, AIRole.VIEWER)

    def test_is_table_allowed_case_insensitive(self):
        """테이블 이름은 대소문자 구분 없음"""
        assert is_table_allowed("T_USER", AIRole.VIEWER)
        assert is_table_allowed("t_User", AIRole.VIEWER)
        assert is_table_allowed("T_ADMIN", AIRole.VIEWER) is False

    def test_is_table_allowed_unknown_table(self):
        """정의되지 않은 테이블은 접근 불가"""
        assert not is_table_allowed("t_unknown_table", AIRole.SUPER_ADMIN)
        assert not is_table_allowed("t_hacker_table", AIRole.ADMIN)

    def test_get_all_tables(self):
        """모든 테이블 목록 반환"""
        all_tables = get_all_tables()

        # BASE 포함
        assert "t_user" in all_tables

        # SENSITIVE 포함
        assert "t_admin" in all_tables

        # EXTRA 포함
        for extra in ROLE_EXTRA_TABLES.values():
            for table in extra:
                assert table in all_tables

    def test_role_extra_tables_structure(self):
        """ROLE_EXTRA_TABLES 구조가 올바름"""
        assert AIRole.SUPER_ADMIN in ROLE_EXTRA_TABLES
        assert AIRole.ADMIN in ROLE_EXTRA_TABLES
        assert AIRole.VIEWER in ROLE_EXTRA_TABLES

        # 각 역할의 EXTRA는 set
        for role, tables in ROLE_EXTRA_TABLES.items():
            assert isinstance(tables, set)

    def test_super_admin_extra_not_in_sensitive(self):
        """SUPER_ADMIN EXTRA 테이블이 SENSITIVE에 없음"""
        extra = ROLE_EXTRA_TABLES.get(AIRole.SUPER_ADMIN, set())
        overlap = extra & SENSITIVE_TABLES
        assert len(overlap) == 0, f"SUPER_ADMIN EXTRA가 SENSITIVE와 겹침: {overlap}"
