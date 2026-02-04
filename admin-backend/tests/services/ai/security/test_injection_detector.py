"""
SQL Injection 탐지기 테스트

Stories: 3-2
FRs: FR-014, NFR-S1
"""
import pytest
from src.services.ai.security.injection_detector import (
    SQLInjectionDetector,
    InjectionDetectionResult,
)


class TestSQLInjectionDetector:
    """SQL Injection 탐지기 테스트"""

    def test_detect_no_injection(self):
        """정상 SQL은 통과"""
        sql = "SELECT * FROM users WHERE age > 18"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is False
        assert len(result.patterns_detected) == 0
        assert result.risk_score == 0.0
        assert result.recommendation is None

    def test_detect_union_injection(self):
        """UNION Injection 탐지"""
        sql = "SELECT * FROM users UNION SELECT * FROM admin"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "union_injection" in result.patterns_detected
        assert result.risk_score > 0.0
        assert "차단" in result.recommendation

    def test_detect_union_null_injection(self):
        """UNION NULL Injection 탐지"""
        sql = "1 UNION SELECT NULL,NULL,NULL--"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "union_null" in result.patterns_detected

    def test_detect_tautology_numeric(self):
        """숫자 Tautology 탐지 (1=1)"""
        sql = "SELECT * FROM users WHERE 1=1"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "tautology_numeric" in result.patterns_detected

    def test_detect_tautology_string(self):
        """문자열 Tautology 탐지 ('a'='a')"""
        sql = "SELECT * FROM users WHERE 'a'='a'"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "tautology_string" in result.patterns_detected

    def test_detect_tautology_or(self):
        """OR 1=1 Tautology 탐지"""
        sql = "SELECT * FROM users WHERE id=1 OR 1=1"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "tautology_or" in result.patterns_detected

    def test_detect_comment_inline(self):
        """-- 주석 Injection 탐지"""
        sql = "SELECT * FROM users WHERE id=1-- AND active=1"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "comment_inline" in result.patterns_detected

    def test_detect_comment_block(self):
        """/* */ 블록 주석 Injection 탐지"""
        sql = "SELECT * FROM users /*comment*/ WHERE 1=1"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "comment_block" in result.patterns_detected

    def test_detect_stacked_query(self):
        """Stacked Query Injection 탐지"""
        sql = "SELECT * FROM users; DROP TABLE admin"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "stacked_query" in result.patterns_detected

    def test_detect_sleep_injection(self):
        """SLEEP Time-based Injection 탐지"""
        sql = "SELECT * FROM users WHERE id=1 AND SLEEP(10)"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "sleep_injection" in result.patterns_detected

    def test_detect_benchmark_injection(self):
        """BENCHMARK Time-based Injection 탐지"""
        sql = "SELECT * FROM users WHERE id=1 AND BENCHMARK(1000000,MD5('test'))"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "benchmark_injection" in result.patterns_detected

    def test_detect_load_file_injection(self):
        """LOAD_FILE Out-of-band Injection 탐지"""
        sql = "SELECT LOAD_FILE('/etc/passwd')"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "load_file" in result.patterns_detected

    def test_detect_into_outfile_injection(self):
        """INTO OUTFILE Injection 탐지"""
        sql = "SELECT * FROM users INTO OUTFILE '/tmp/dump.txt'"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "into_outfile" in result.patterns_detected

    def test_detect_multiple_patterns(self):
        """여러 패턴 동시 탐지 시 risk_score 누적"""
        sql = "SELECT * FROM users WHERE 1=1 UNION SELECT NULL-- "
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert len(result.patterns_detected) >= 2
        assert result.risk_score > 0.5

    def test_risk_score_high_patterns(self):
        """High risk 패턴은 0.5 가중치"""
        sql = "SELECT * FROM users UNION SELECT * FROM admin"
        result = SQLInjectionDetector.detect(sql)

        assert result.risk_score >= 0.5

    def test_risk_score_medium_patterns(self):
        """Medium risk 패턴은 0.3 가중치"""
        sql = "SELECT * FROM users WHERE 1=1 OR 1=1"
        result = SQLInjectionDetector.detect(sql)

        assert 0.3 <= result.risk_score < 0.5

    def test_risk_score_capped_at_1(self):
        """risk_score는 1.0을 초과하지 않음"""
        # 여러 high risk 패턴 조합
        sql = "SELECT * FROM users UNION SELECT * FROM admin; DROP TABLE users-- INTO OUTFILE '/tmp/hack'"
        result = SQLInjectionDetector.detect(sql)

        assert result.risk_score <= 1.0

    def test_detect_version_probe(self):
        """시스템 정보 수집 시도 탐지"""
        sql = "SELECT @@VERSION"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "version_probe" in result.patterns_detected

    def test_detect_database_probe(self):
        """DATABASE() 프로브 탐지"""
        sql = "SELECT DATABASE()"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "database_probe" in result.patterns_detected

    def test_detect_user_probe(self):
        """CURRENT_USER 프로브 탐지"""
        sql = "SELECT CURRENT_USER"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "user_probe" in result.patterns_detected

    def test_case_insensitive_detection(self):
        """대소문자 구분 없이 탐지"""
        sql_upper = "SELECT * FROM users UNION SELECT * FROM admin"
        sql_lower = "select * from users union select * from admin"

        result_upper = SQLInjectionDetector.detect(sql_upper)
        result_lower = SQLInjectionDetector.detect(sql_lower)

        assert result_upper.is_injection is True
        assert result_lower.is_injection is True
        assert result_upper.patterns_detected == result_lower.patterns_detected

    def test_legitimate_queries_with_similar_keywords(self):
        """정상 쿼리의 오탐 방지"""
        # UNION이 포함되지만 정상적인 형태는 아님
        sql = "SELECT user_id FROM employees"
        result = SQLInjectionDetector.detect(sql)

        # 이 경우 탐지되지 않아야 함
        assert result.is_injection is False

    def test_hex_encoding_detection(self):
        """Hex 인코딩 우회 시도 탐지"""
        sql = "SELECT 0x61646d696e"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "hex_encoding" in result.patterns_detected

    def test_char_encoding_detection(self):
        """CHAR 인코딩 우회 시도 탐지"""
        sql = "SELECT CHAR(97,100,109,105,110)"
        result = SQLInjectionDetector.detect(sql)

        assert result.is_injection is True
        assert "char_encoding" in result.patterns_detected
