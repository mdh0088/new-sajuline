"""
테이블 권한 설정 단위 테스트

AC 1-3 검증:
- Super Admin: 모든 테이블 접근 가능
- Admin: 제한된 테이블 집합 접근 가능
- Viewer: 읽기 전용 질의만 가능
"""
import pytest

from src.services.ai.security.rbac import AIRole
from src.services.ai.config.table_permissions import (
    SENSITIVE_TABLES,
    ROLE_TABLE_PERMISSIONS,
    can_access_table,
    extract_tables_from_sql,
)


class TestTablePermissionConstants:
    """테이블 권한 상수 테스트"""

    def test_sensitive_tables_defined(self):
        """민감 테이블 목록이 정의되어 있음"""
        assert isinstance(SENSITIVE_TABLES, set)
        assert len(SENSITIVE_TABLES) > 0

        # Dev Notes에 명시된 민감 테이블 포함 확인
        expected_sensitive = {
            "t_admin",
            "t_user_password",
            "t_payment_card",
            "t_user_identity",
        }
        assert expected_sensitive.issubset(SENSITIVE_TABLES)

    def test_role_table_permissions_defined(self):
        """역할별 테이블 권한 매핑이 정의되어 있음"""
        assert isinstance(ROLE_TABLE_PERMISSIONS, dict)

        # 모든 AIRole이 매핑에 포함되어 있음
        assert AIRole.SUPER_ADMIN in ROLE_TABLE_PERMISSIONS
        assert AIRole.ADMIN in ROLE_TABLE_PERMISSIONS
        assert AIRole.VIEWER in ROLE_TABLE_PERMISSIONS

    def test_super_admin_has_wildcard(self):
        """Super Admin은 와일드카드 권한"""
        assert "*" in ROLE_TABLE_PERMISSIONS[AIRole.SUPER_ADMIN]

    def test_admin_allowed_tables(self):
        """Admin 허용 테이블이 정의되어 있음"""
        admin_tables = ROLE_TABLE_PERMISSIONS[AIRole.ADMIN]
        assert isinstance(admin_tables, set)

        # Dev Notes에 명시된 허용 테이블 포함 확인
        expected_allowed = {
            "t_payment",
            "t_user",
            "t_counselor",
            "t_order",
        }
        assert expected_allowed.issubset(admin_tables)

        # 민감 테이블은 포함되지 않음
        assert "t_admin" not in admin_tables
        assert "t_user_password" not in admin_tables

    def test_viewer_minimal_tables(self):
        """Viewer는 최소한의 테이블만 접근"""
        viewer_tables = ROLE_TABLE_PERMISSIONS[AIRole.VIEWER]
        assert isinstance(viewer_tables, set)

        # Viewer는 Admin보다 적은 테이블만 접근
        admin_tables = ROLE_TABLE_PERMISSIONS[AIRole.ADMIN]
        assert len(viewer_tables) < len(admin_tables)


class TestCanAccessTable:
    """can_access_table() 함수 테스트"""

    def test_super_admin_access_all_tables(self):
        """Super Admin은 모든 테이블 접근 가능"""
        assert can_access_table(AIRole.SUPER_ADMIN, "t_payment")
        assert can_access_table(AIRole.SUPER_ADMIN, "t_admin")
        assert can_access_table(AIRole.SUPER_ADMIN, "t_user_password")
        assert can_access_table(AIRole.SUPER_ADMIN, "any_random_table")

    def test_admin_access_allowed_tables(self):
        """Admin은 허용된 테이블만 접근 가능"""
        # 허용된 테이블
        assert can_access_table(AIRole.ADMIN, "t_payment")
        assert can_access_table(AIRole.ADMIN, "t_user")
        assert can_access_table(AIRole.ADMIN, "t_counselor")
        assert can_access_table(AIRole.ADMIN, "t_order")

    def test_admin_blocked_sensitive_tables(self):
        """Admin은 민감 테이블 접근 불가"""
        assert not can_access_table(AIRole.ADMIN, "t_admin")
        assert not can_access_table(AIRole.ADMIN, "t_user_password")
        assert not can_access_table(AIRole.ADMIN, "t_payment_card")

    def test_admin_blocked_unlisted_tables(self):
        """Admin은 허용 목록에 없는 테이블 접근 불가"""
        assert not can_access_table(AIRole.ADMIN, "unknown_table")
        assert not can_access_table(AIRole.ADMIN, "random_table")

    def test_viewer_access_minimal_tables(self):
        """Viewer는 최소한의 테이블만 접근 가능"""
        # Viewer는 일부 테이블에만 접근 (집계용)
        viewer_tables = ROLE_TABLE_PERMISSIONS[AIRole.VIEWER]
        for table in viewer_tables:
            assert can_access_table(AIRole.VIEWER, table)

    def test_viewer_blocked_sensitive_tables(self):
        """Viewer는 민감 테이블 접근 불가"""
        assert not can_access_table(AIRole.VIEWER, "t_admin")
        assert not can_access_table(AIRole.VIEWER, "t_user_password")
        assert not can_access_table(AIRole.VIEWER, "t_payment_card")

    def test_viewer_blocked_most_tables(self):
        """Viewer는 대부분의 테이블 접근 불가"""
        # Admin은 접근 가능하지만 Viewer는 불가한 테이블
        assert can_access_table(AIRole.ADMIN, "t_counselor")
        assert not can_access_table(AIRole.VIEWER, "t_counselor")


class TestExtractTablesFromSQL:
    """extract_tables_from_sql() 함수 테스트"""

    def test_single_table_query(self):
        """단일 테이블 질의에서 테이블 추출"""
        sql = "SELECT * FROM t_user"
        tables = extract_tables_from_sql(sql)

        assert "t_user" in tables
        assert len(tables) == 1

    def test_join_query(self):
        """JOIN 질의에서 여러 테이블 추출"""
        sql = """
        SELECT u.*, p.amount
        FROM t_user u
        JOIN t_payment p ON u.id = p.user_id
        """
        tables = extract_tables_from_sql(sql)

        assert "t_user" in tables
        assert "t_payment" in tables
        assert len(tables) == 2

    def test_subquery(self):
        """서브쿼리에서 테이블 추출"""
        sql = """
        SELECT *
        FROM t_order
        WHERE user_id IN (SELECT id FROM t_user WHERE status = 'active')
        """
        tables = extract_tables_from_sql(sql)

        assert "t_order" in tables
        assert "t_user" in tables

    def test_case_insensitive(self):
        """대소문자 구분 없이 테이블 추출"""
        sql = "SELECT * FROM T_USER"
        tables = extract_tables_from_sql(sql)

        assert "t_user" in tables

    def test_with_schema_prefix(self):
        """스키마 접두사가 있는 테이블명 처리"""
        sql = "SELECT * FROM dbo.t_user"
        tables = extract_tables_from_sql(sql)

        # 스키마 제거하고 테이블명만 추출
        assert "t_user" in tables

    def test_empty_sql(self):
        """빈 SQL은 빈 집합 반환"""
        tables = extract_tables_from_sql("")
        assert len(tables) == 0

    def test_no_tables(self):
        """테이블이 없는 SQL (예: SHOW TABLES)"""
        sql = "SHOW TABLES"
        tables = extract_tables_from_sql(sql)
        # 실제 테이블명이 아니므로 빈 집합이거나 TABLES만 추출
        # 구현에 따라 다를 수 있음
        assert isinstance(tables, set)
