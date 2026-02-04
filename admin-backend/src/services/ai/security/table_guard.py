"""
테이블 접근 제어

화이트리스트 및 블랙리스트 기반 테이블 접근 권한을 관리합니다.

Stories: 3-2
FRs: FR-015, NFR-S3
"""

import re
from dataclasses import dataclass
from typing import Set


@dataclass
class TableAccessResult:
    """테이블 접근 검사 결과"""

    allowed: bool
    blocked_tables: list[str]
    reason: str | None = None


class TableAccessGuard:
    """
    테이블 접근 제어

    화이트리스트에 있는 테이블만 접근 허용하며,
    블랙리스트 및 시스템 테이블은 절대 접근 불가합니다.
    """

    # 절대 접근 금지 테이블 (역할과 무관)
    BLACKLIST_TABLES = {
        # 시스템 테이블
        "information_schema",
        "mysql",
        "performance_schema",
        "sys",
        # 민감 테이블 (슈퍼 관리자 제외 전체 차단)
        "t_admin",
        "t_user_password",
        "t_payment_card",
        "t_user_identity",
        "t_api_keys",
        "t_sessions",
    }

    # 시스템 테이블 패턴
    SYSTEM_TABLE_PATTERNS = [
        r"^mysql\.",
        r"^information_schema\.",
        r"^performance_schema\.",
        r"^sys\.",
    ]

    @classmethod
    def check_access(
        cls,
        sql: str,
        allowed_tables: Set[str],
        is_super_admin: bool = False,
    ) -> TableAccessResult:
        """
        테이블 접근 권한 확인

        Args:
            sql: 검사할 SQL 쿼리
            allowed_tables: 접근 허용된 테이블 집합
            is_super_admin: 슈퍼 관리자 여부

        Returns:
            TableAccessResult: 접근 허용 여부 및 차단된 테이블 목록
        """
        tables_in_sql = cls._extract_all_tables(sql)
        blocked_tables = []

        for table in tables_in_sql:
            table_lower = table.lower()
            # 테이블명만 추출 (스키마 제외: dbo.users → users)
            table_name_only = table_lower.split(".")[-1]

            # 1. 시스템 테이블 패턴 체크
            for pattern in cls.SYSTEM_TABLE_PATTERNS:
                if re.match(pattern, table_lower):
                    blocked_tables.append(table)
                    break
            else:
                # 2. 블랙리스트 체크
                if table_name_only in cls.BLACKLIST_TABLES:
                    # 슈퍼 관리자도 절대 접근 불가 테이블
                    if table_name_only in {
                        "t_user_password",
                        "t_payment_card",
                        "t_user_identity",
                    }:
                        blocked_tables.append(table)
                    # 슈퍼 관리자는 접근 가능한 블랙리스트 테이블
                    elif not is_super_admin:
                        blocked_tables.append(table)

                # 3. 화이트리스트 체크 (블랙리스트가 아닌 경우에만)
                # 스키마 제외하고 테이블명만 비교
                elif table_name_only not in {
                    t.lower() for t in allowed_tables
                }:
                    blocked_tables.append(table)

        if blocked_tables:
            return TableAccessResult(
                allowed=False,
                blocked_tables=blocked_tables,
                reason=f"접근이 허용되지 않은 테이블: {', '.join(blocked_tables)}",
            )

        return TableAccessResult(allowed=True, blocked_tables=[])

    @staticmethod
    def _extract_all_tables(sql: str) -> Set[str]:
        """
        SQL에서 모든 테이블 참조 추출

        FROM 및 JOIN 절에서 테이블명을 추출합니다.
        백틱, 따옴표, 대괄호로 감싼 테이블명도 처리합니다.

        Args:
            sql: SQL 쿼리

        Returns:
            Set[str]: 테이블명 집합
        """
        tables = set()

        # FROM 절에서 테이블 추출
        from_matches = re.findall(
            r"FROM\s+([`\"\[]?\w+[`\"\]]?(?:\.[`\"\[]?\w+[`\"\]]?)?)",
            sql,
            re.IGNORECASE,
        )
        tables.update(from_matches)

        # JOIN 절에서 테이블 추출
        join_matches = re.findall(
            r"JOIN\s+([`\"\[]?\w+[`\"\]]?(?:\.[`\"\[]?\w+[`\"\]]?)?)",
            sql,
            re.IGNORECASE,
        )
        tables.update(join_matches)

        # 백틱, 따옴표, 대괄호 제거
        cleaned = set()
        for t in tables:
            cleaned.add(re.sub(r"[`\"\[\]]", "", t))

        return cleaned
