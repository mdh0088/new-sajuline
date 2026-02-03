"""
Layer 4: 사용자 확인 필요 여부 판단.

위험하거나 복잡한 쿼리 실행 시 사용자에게 확인을 요청합니다.

Stories: 3-1
FRs: FR-021 (4-Layer Security)
"""

import re
from dataclasses import dataclass

# 대용량 조회 임계값
LARGE_RESULT_THRESHOLD = 500

# 복잡한 조인 임계값
COMPLEX_JOIN_THRESHOLD = 3


@dataclass
class UserConfirmationRequired:
    """
    사용자 확인 필요 여부 결과.

    Attributes:
        required: 확인이 필요한지 여부
        reason: 확인이 필요한 이유 (required=True일 때)
        sql: 확인 대상 SQL 문자열
    """

    required: bool
    reason: str | None
    sql: str


class Layer4UserConfirmation:
    """Layer 4: 사용자 확인 필요 여부 판단"""

    @classmethod
    def check_confirmation_needed(
        cls, sql: str, estimated_rows: int | None = None
    ) -> UserConfirmationRequired:
        """
        사용자 확인 필요 여부 확인.

        Args:
            sql: 실행할 SQL 문자열
            estimated_rows: 예상 결과 행 수 (선택적)

        Returns:
            UserConfirmationRequired: 확인 필요 여부 및 이유
        """
        reasons = []

        # 1. 대용량 조회 확인 (estimated_rows 제공된 경우)
        if estimated_rows is not None and estimated_rows >= LARGE_RESULT_THRESHOLD:
            reasons.append(f"Large result set expected ({estimated_rows} rows)")

        # 2. 복잡한 JOIN 확인
        join_count = cls._count_joins(sql)
        if join_count >= COMPLEX_JOIN_THRESHOLD:
            reasons.append(f"Complex query with {join_count} joins")

        # 3. LIMIT 절이 있으면 LIMIT 값 확인 (작은 값만 안전)
        has_limit = cls._has_limit_clause(sql)
        limit_value = cls._get_limit_value(sql) if has_limit else None

        # LIMIT 값이 임계값보다 작으면 대용량 조회 경고 제거
        if (
            has_limit
            and limit_value
            and limit_value < LARGE_RESULT_THRESHOLD
            and "Large result" in " ".join(reasons)
        ):
            # LIMIT이 작으므로 대용량 조회 경고 제거
            reasons = [r for r in reasons if "Large result" not in r]

        # 4. 확인 필요 여부 결정
        if len(reasons) > 0:
            combined_reason = "; ".join(reasons)
            return UserConfirmationRequired(
                required=True, reason=combined_reason, sql=sql
            )
        else:
            return UserConfirmationRequired(required=False, reason=None, sql=sql)

    @staticmethod
    def _count_joins(sql: str) -> int:
        """
        SQL에서 JOIN 횟수 카운트.

        Args:
            sql: SQL 문자열

        Returns:
            int: JOIN 횟수
        """
        # JOIN, LEFT JOIN, RIGHT JOIN, OUTER JOIN 등 모두 카운트
        join_pattern = r"\b(?:LEFT\s+|RIGHT\s+|OUTER\s+|INNER\s+)?JOIN\b"
        matches = re.findall(join_pattern, sql, re.IGNORECASE)
        return len(matches)

    @staticmethod
    def _has_limit_clause(sql: str) -> bool:
        """
        SQL에 LIMIT 절이 있는지 확인.

        Args:
            sql: SQL 문자열

        Returns:
            bool: LIMIT 절 존재 여부
        """
        limit_pattern = r"\bLIMIT\s+\d+"
        return re.search(limit_pattern, sql, re.IGNORECASE) is not None

    @staticmethod
    def _get_limit_value(sql: str) -> int | None:
        """
        SQL에서 LIMIT 값을 추출.

        Args:
            sql: SQL 문자열

        Returns:
            int | None: LIMIT 값 (없으면 None)
        """
        limit_pattern = r"\bLIMIT\s+(\d+)"
        match = re.search(limit_pattern, sql, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
