"""
테이블 권한 설정

역할별 접근 가능한 테이블 정의 및 검증
"""

import re
from typing import Set

from src.services.ai.security.rbac import AIRole

# 민감 테이블 (Super Admin만 접근 가능)
SENSITIVE_TABLES: Set[str] = {
    "t_admin",
    "t_user_password",
    "t_payment_card",
    "t_user_identity",
}

# 역할별 허용 테이블
ROLE_TABLE_PERMISSIONS: dict[AIRole, Set[str]] = {
    # Super Admin: 모든 테이블
    AIRole.SUPER_ADMIN: {"*"},
    # Admin: 제한된 테이블 집합
    AIRole.ADMIN: {
        "t_payment",
        "t_user",
        "t_counselor",
        "t_order",
        "t_consultation",
        "t_mileage",
        "t_point_transaction",
    },
    # Viewer: 최소 접근 (집계만)
    AIRole.VIEWER: {
        "t_payment",
        "t_order",
    },
}


def can_access_table(role: AIRole, table_name: str) -> bool:
    """
    역할이 해당 테이블에 접근 가능한지 확인

    Args:
        role: AI 역할
        table_name: 테이블명 (소문자)

    Returns:
        bool: 접근 가능 여부
    """
    # Super Admin은 모든 테이블 접근 가능
    if role == AIRole.SUPER_ADMIN:
        return True

    # 민감 테이블은 Super Admin만 접근 가능
    if table_name.lower() in SENSITIVE_TABLES:
        return False

    # 역할별 허용 테이블 확인
    allowed_tables = ROLE_TABLE_PERMISSIONS.get(role, set())

    # 와일드카드 확인
    if "*" in allowed_tables:
        return True

    # 테이블명 매칭 (소문자로 비교)
    return table_name.lower() in allowed_tables


def extract_tables_from_sql(sql: str) -> Set[str]:
    """
    SQL 쿼리에서 테이블명 추출

    Args:
        sql: SQL 쿼리 문자열

    Returns:
        Set[str]: 추출된 테이블명 집합 (소문자)
    """
    if not sql:
        return set()

    # SQL을 소문자로 변환
    sql_lower = sql.lower()

    # FROM, JOIN 키워드 다음의 테이블명 추출
    # 패턴: FROM/JOIN 다음에 나오는 식별자 (스키마.테이블 형태 포함)
    pattern = r"(?:from|join)\s+(?:[\w]+\.)?(\w+)"

    matches = re.findall(pattern, sql_lower, re.IGNORECASE)

    # 스키마 접두사 제거하고 테이블명만 추출
    tables = set()
    for match in matches:
        # 테이블명이 t_로 시작하거나 알파벳으로 시작하는 경우만
        if match.startswith("t_") or match.isalpha():
            tables.add(match)

    return tables
