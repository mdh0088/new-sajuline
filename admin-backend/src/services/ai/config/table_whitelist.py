"""
MariaDB 테이블 화이트리스트 설정.

역할별로 접근 가능한 테이블 목록을 관리합니다.

Stories: 2-3
FRs: FR-012
"""

from src.services.ai.security.rbac import AIRole

# 기본 허용 테이블 (모든 역할이 접근 가능)
BASE_ALLOWED_TABLES: set[str] = {
    "t_payment",
    "t_user",
    "t_counselor",
    "t_order",
    "t_consultation",
    "t_mileage",
    "t_point_transaction",
    "t_notice",
    "t_banner",
    "t_grade",
    "t_grade_change_log",
    "t_inquiry",
    "t_consultation_review",
    "t_counselor_application",
    "t_mileage_product",
    "t_point_product",
    "t_event",
}

# 민감한 테이블 (접근 금지)
SENSITIVE_TABLES: set[str] = {
    "t_admin",
    "t_user_password",
    "t_payment_card",
    "t_user_identity",
    "t_admin_session",
    "t_admin_password_history",
}

# 역할별 추가 허용 테이블
ROLE_EXTRA_TABLES: dict[AIRole, set[str]] = {
    AIRole.SUPER_ADMIN: {
        # Super Admin은 추가로 관리자 관련 통계 테이블 접근 가능
        # (단, 민감한 정보는 제외)
        "t_admin_log",
        "t_system_config",
    },
    AIRole.ADMIN: set(),  # Admin은 BASE만 접근
    AIRole.VIEWER: set(),  # Viewer도 BASE만 접근
}


def get_allowed_tables(role: AIRole) -> set[str]:
    """역할별 허용 테이블 목록 반환

    Args:
        role: AI 역할 (SUPER_ADMIN, ADMIN, VIEWER)

    Returns:
        set[str]: 해당 역할이 접근 가능한 테이블 목록
    """
    tables = BASE_ALLOWED_TABLES.copy()
    tables.update(ROLE_EXTRA_TABLES.get(role, set()))
    return tables


def is_table_allowed(table_name: str, role: AIRole) -> bool:
    """특정 테이블이 허용되는지 확인

    Args:
        table_name: 테이블 이름
        role: AI 역할

    Returns:
        bool: 허용 여부
    """
    # 민감한 테이블은 무조건 차단
    if table_name.lower() in SENSITIVE_TABLES:
        return False

    allowed = get_allowed_tables(role)
    return table_name.lower() in allowed


def get_all_tables() -> set[str]:
    """시스템 내 모든 테이블 목록 반환 (참고용)

    Returns:
        set[str]: BASE + SENSITIVE + 모든 역할의 EXTRA 테이블
    """
    all_tables = BASE_ALLOWED_TABLES.copy()
    all_tables.update(SENSITIVE_TABLES)

    for extra_tables in ROLE_EXTRA_TABLES.values():
        all_tables.update(extra_tables)

    return all_tables
