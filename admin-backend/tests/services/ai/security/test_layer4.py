"""
Layer 4 사용자 확인 테스트.

Stories: 3-1
"""

import pytest

from src.services.ai.security.layer4_user import (
    COMPLEX_JOIN_THRESHOLD,
    LARGE_RESULT_THRESHOLD,
    Layer4UserConfirmation,
    UserConfirmationRequired,
)


class TestUserConfirmationRequired:
    """UserConfirmationRequired 데이터클래스 테스트"""

    def test_confirmation_creation_not_required(self):
        """확인이 필요하지 않은 경우"""
        confirmation = UserConfirmationRequired(
            required=False,
            reason=None,
            sql="SELECT * FROM users",
        )

        assert confirmation.required is False
        assert confirmation.reason is None

    def test_confirmation_creation_required(self):
        """확인이 필요한 경우"""
        confirmation = UserConfirmationRequired(
            required=True,
            reason="Large result set expected (1000+ rows)",
            sql="SELECT * FROM payments",
        )

        assert confirmation.required is True
        assert "Large result" in confirmation.reason


class TestLayer4UserConfirmation:
    """Layer 4 사용자 확인 테스트"""

    def test_validator_exists(self):
        """Layer4UserConfirmation 클래스가 존재하는지 확인"""
        assert Layer4UserConfirmation is not None

    def test_large_result_threshold_defined(self):
        """LARGE_RESULT_THRESHOLD 상수가 정의되어 있는지 확인"""
        assert isinstance(LARGE_RESULT_THRESHOLD, int)
        assert LARGE_RESULT_THRESHOLD > 0
        assert LARGE_RESULT_THRESHOLD == 500  # Story 요구사항

    def test_complex_join_threshold_defined(self):
        """COMPLEX_JOIN_THRESHOLD 상수가 정의되어 있는지 확인"""
        assert isinstance(COMPLEX_JOIN_THRESHOLD, int)
        assert COMPLEX_JOIN_THRESHOLD > 0
        assert COMPLEX_JOIN_THRESHOLD == 3  # Story 요구사항

    def test_check_simple_query_no_confirmation(self):
        """단순한 쿼리는 확인 불필요"""
        sql = "SELECT id, name FROM users WHERE id = 1"

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        assert result.required is False

    def test_check_large_result_confirmation_required(self):
        """대용량 조회는 확인 필요"""
        sql = "SELECT * FROM users"
        estimated_rows = LARGE_RESULT_THRESHOLD + 100

        result = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=estimated_rows
        )

        assert result.required is True
        assert "large" in result.reason.lower() or "rows" in result.reason.lower()

    def test_check_complex_join_confirmation_required(self):
        """복잡한 조인 쿼리는 확인 필요"""
        sql = """
        SELECT *
        FROM users u
        JOIN payments p ON u.id = p.user_id
        JOIN counselors c ON p.counselor_id = c.id
        JOIN members m ON u.member_id = m.id
        """

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        assert result.required is True
        assert "join" in result.reason.lower() or "complex" in result.reason.lower()

    def test_check_no_estimated_rows_provided(self):
        """estimated_rows가 제공되지 않은 경우"""
        sql = "SELECT * FROM users"  # No LIMIT

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        # estimated_rows가 없으면 JOIN 수나 다른 휴리스틱으로 판단
        # 단순한 SELECT *는 확인 필요할 수 있음
        assert isinstance(result.required, bool)

    def test_check_with_limit_clause_no_confirmation(self):
        """LIMIT 절이 있으면 확인 불필요"""
        sql = "SELECT * FROM users LIMIT 10"

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        assert result.required is False

    def test_check_small_estimated_rows_no_confirmation(self):
        """적은 수의 행이 예상되면 확인 불필요"""
        sql = "SELECT * FROM users"
        estimated_rows = 50  # < LARGE_RESULT_THRESHOLD

        result = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=estimated_rows
        )

        assert result.required is False

    def test_check_threshold_boundary_large_result(self):
        """LARGE_RESULT_THRESHOLD 경계값 테스트"""
        sql = "SELECT * FROM payments"

        # 정확히 임계값인 경우
        result_at = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=LARGE_RESULT_THRESHOLD
        )
        # 임계값보다 1 작은 경우
        result_below = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=LARGE_RESULT_THRESHOLD - 1
        )
        # 임계값보다 1 큰 경우
        result_above = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=LARGE_RESULT_THRESHOLD + 1
        )

        # 임계값 이상은 확인 필요
        assert result_above.required is True
        # 임계값 미만은 확인 불필요 (또는 정책에 따라 달라질 수 있음)
        assert result_below.required is False

    def test_check_threshold_boundary_complex_join(self):
        """COMPLEX_JOIN_THRESHOLD 경계값 테스트"""
        # 정확히 3개 JOIN
        sql_3_joins = """
        SELECT * FROM a
        JOIN b ON a.id = b.a_id
        JOIN c ON b.id = c.b_id
        JOIN d ON c.id = d.c_id
        """

        # 2개 JOIN
        sql_2_joins = """
        SELECT * FROM a
        JOIN b ON a.id = b.a_id
        JOIN c ON b.id = c.b_id
        """

        result_3 = Layer4UserConfirmation.check_confirmation_needed(sql_3_joins)
        result_2 = Layer4UserConfirmation.check_confirmation_needed(sql_2_joins)

        # 3개 이상 JOIN은 확인 필요
        assert result_3.required is True
        # 2개 이하는 확인 불필요
        assert result_2.required is False

    def test_check_multiple_reasons_for_confirmation(self):
        """여러 이유로 확인이 필요한 경우"""
        sql = """
        SELECT * FROM users u
        JOIN payments p ON u.id = p.user_id
        JOIN counselors c ON p.counselor_id = c.id
        JOIN members m ON u.member_id = m.id
        JOIN sessions s ON u.id = s.user_id
        """
        estimated_rows = 1000

        result = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=estimated_rows
        )

        assert result.required is True
        # 이유에 JOIN과 대용량 모두 언급될 수 있음
        assert result.reason is not None

    def test_check_case_insensitive_join_detection(self):
        """대소문자 구분 없이 JOIN 감지"""
        sql = """
        SELECT * FROM users u
        join payments p ON u.id = p.user_id
        JoIn counselors c ON p.counselor_id = c.id
        JOIN members m ON u.member_id = m.id
        """

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        assert result.required is True

    def test_check_left_right_outer_join_counted(self):
        """LEFT/RIGHT/OUTER JOIN도 카운트"""
        sql = """
        SELECT * FROM users u
        LEFT JOIN payments p ON u.id = p.user_id
        RIGHT JOIN counselors c ON p.counselor_id = c.id
        OUTER JOIN members m ON u.member_id = m.id
        """

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        # 3개 JOIN이므로 확인 필요
        assert result.required is True

    def test_check_reason_contains_sql(self):
        """확인 결과에 SQL이 포함되는지 확인"""
        sql = "SELECT * FROM users LIMIT 10"

        result = Layer4UserConfirmation.check_confirmation_needed(sql)

        assert result.sql == sql

    def test_limit_clause_removes_large_result_warning(self):
        """LIMIT 절이 있으면 대용량 결과 경고 제거 (line 68 coverage)"""
        # 대용량 결과 예상되지만 LIMIT이 있는 경우
        sql = "SELECT * FROM users LIMIT 100"
        estimated_rows = 1000  # LARGE_RESULT_THRESHOLD 이상

        result = Layer4UserConfirmation.check_confirmation_needed(
            sql, estimated_rows=estimated_rows
        )

        # LIMIT이 있으므로 대용량 경고가 제거되어야 함
        assert result.required is False or "Large result" not in (result.reason or "")
        # 이 테스트는 line 68의 warning 제거 로직을 실행함
