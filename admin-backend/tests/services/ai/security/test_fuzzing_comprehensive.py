"""
SQL Injection 퍼징 종합 테스트

100+ OWASP 패턴을 사용하여 100% 차단율을 검증합니다.

Stories: 3-2
FRs: NFR-S1, NFR-S3
"""
import pytest
from src.services.ai.security.injection_detector import SQLInjectionDetector
from src.services.ai.security.table_guard import TableAccessGuard
from tests.services.ai.security.fuzzing_patterns import (
    INJECTION_FUZZING_PATTERNS,
    BLACKLIST_TABLE_PATTERNS,
)


class TestInjectionFuzzing:
    """SQL Injection 퍼징 테스트"""

    @pytest.mark.parametrize("malicious_sql", INJECTION_FUZZING_PATTERNS)
    def test_all_injection_patterns_detected(self, malicious_sql):
        """100+ SQL Injection 패턴 100% 탐지"""
        result = SQLInjectionDetector.detect(malicious_sql)

        assert result.is_injection is True, (
            f"Failed to detect injection: {malicious_sql[:100]}"
        )
        assert len(result.patterns_detected) > 0, (
            f"No patterns detected for: {malicious_sql[:100]}"
        )
        assert result.risk_score > 0.0, (
            f"Risk score should be > 0 for: {malicious_sql[:100]}"
        )

    def test_injection_detection_rate(self):
        """SQL Injection 차단율 100% 검증"""
        detected_count = 0
        total_count = len(INJECTION_FUZZING_PATTERNS)

        for malicious_sql in INJECTION_FUZZING_PATTERNS:
            result = SQLInjectionDetector.detect(malicious_sql)
            if result.is_injection:
                detected_count += 1

        detection_rate = (detected_count / total_count) * 100

        assert detection_rate == 100.0, (
            f"Detection rate: {detection_rate:.2f}% (expected 100%)"
        )
        assert detected_count == total_count, (
            f"Detected {detected_count}/{total_count} patterns"
        )


class TestTableAccessFuzzing:
    """테이블 접근 제어 퍼징 테스트"""

    @pytest.mark.parametrize("malicious_sql", BLACKLIST_TABLE_PATTERNS)
    def test_all_blacklist_tables_blocked(self, malicious_sql):
        """블랙리스트 테이블 100% 차단"""
        allowed_tables = {"t_member", "t_payment", "t_counselor"}

        result = TableAccessGuard.check_access(malicious_sql, allowed_tables)

        assert result.allowed is False, (
            f"Failed to block: {malicious_sql[:100]}"
        )
        assert len(result.blocked_tables) > 0, (
            f"No blocked tables for: {malicious_sql[:100]}"
        )

    def test_table_access_blocking_rate(self):
        """테이블 접근 차단율 100% 검증"""
        blocked_count = 0
        total_count = len(BLACKLIST_TABLE_PATTERNS)
        allowed_tables = {"t_member", "t_payment", "t_counselor"}

        for malicious_sql in BLACKLIST_TABLE_PATTERNS:
            result = TableAccessGuard.check_access(malicious_sql, allowed_tables)
            if not result.allowed:
                blocked_count += 1

        blocking_rate = (blocked_count / total_count) * 100

        assert blocking_rate == 100.0, (
            f"Blocking rate: {blocking_rate:.2f}% (expected 100%)"
        )
        assert blocked_count == total_count, (
            f"Blocked {blocked_count}/{total_count} attempts"
        )


class TestCombinedSecurityFuzzing:
    """통합 보안 퍼징 테스트"""

    @pytest.mark.parametrize("malicious_sql", INJECTION_FUZZING_PATTERNS[:20])
    def test_combined_security_layers(self, malicious_sql):
        """Injection + 테이블 접근 제어 통합 테스트 (샘플 20개)"""
        allowed_tables = {"t_member", "t_payment"}

        # Layer 1: Injection 탐지
        injection_result = SQLInjectionDetector.detect(malicious_sql)

        # Layer 2: 테이블 접근 제어
        table_result = TableAccessGuard.check_access(malicious_sql, allowed_tables)

        # 둘 중 하나라도 차단되어야 함
        assert (
            injection_result.is_injection or not table_result.allowed
        ), f"Neither layer blocked: {malicious_sql[:100]}"

    def test_legitimate_queries_pass_all_layers(self):
        """정상 쿼리는 모든 레이어 통과"""
        legitimate_queries = [
            "SELECT id, name FROM t_member WHERE active=1",
            "SELECT * FROM t_member WHERE age > 18 ORDER BY created_at DESC LIMIT 10",
            "SELECT COUNT(*) FROM t_payment WHERE status='completed'",
            "SELECT m.name, p.amount FROM t_member m JOIN t_payment p ON m.id = p.user_id WHERE p.status='pending'",
        ]
        allowed_tables = {"t_member", "t_payment"}

        for sql in legitimate_queries:
            injection_result = SQLInjectionDetector.detect(sql)
            table_result = TableAccessGuard.check_access(sql, allowed_tables)

            assert injection_result.is_injection is False, (
                f"False positive injection for: {sql}"
            )
            assert table_result.allowed is True, (
                f"False positive table block for: {sql}"
            )

    def test_pattern_coverage_statistics(self):
        """패턴 커버리지 통계"""
        injection_patterns_detected = set()

        for malicious_sql in INJECTION_FUZZING_PATTERNS:
            result = SQLInjectionDetector.detect(malicious_sql)
            injection_patterns_detected.update(result.patterns_detected)

        # 최소 15개 이상의 서로 다른 패턴 탐지되어야 함
        assert len(injection_patterns_detected) >= 15, (
            f"Pattern diversity: {len(injection_patterns_detected)} unique patterns detected"
        )
