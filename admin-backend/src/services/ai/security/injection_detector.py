"""
SQL Injection 탐지기

OWASP 기반 SQL Injection 패턴을 탐지하여 악의적인 SQL 실행을 차단합니다.

Stories: 3-2
FRs: FR-014, NFR-S1
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class InjectionDetectionResult:
    """SQL Injection 탐지 결과"""

    is_injection: bool
    patterns_detected: List[str]
    risk_score: float  # 0.0 ~ 1.0
    recommendation: str | None = None


class SQLInjectionDetector:
    """
    SQL Injection 탐지기

    OWASP Top 10 SQL Injection 패턴을 기반으로 악의적인 SQL을 탐지합니다.
    각 패턴은 위험도에 따라 가중치를 가지며, 총 risk_score를 계산합니다.
    """

    # OWASP 기반 Injection 패턴
    INJECTION_PATTERNS = {
        # Union-based
        "union_injection": r"UNION\s+(ALL\s+)?SELECT",
        "union_null": r"UNION\s+SELECT\s+NULL",
        # Tautology
        "tautology_numeric": r"(\d+)\s*=\s*\1",  # 1=1
        "tautology_string": r"'([^']+)'\s*=\s*'\1'",  # 'a'='a'
        "tautology_or": r"OR\s+1\s*=\s*1",
        "tautology_always_true": r"OR\s+'[^']*'\s*=\s*'[^']*'",
        "tautology_quote": r"'\s*OR\s+'",  # ' OR '
        # Comment injection
        "comment_inline": r"--[^\n]*",
        "comment_hash": r"#",
        "comment_block": r"/\*.*\*/",
        # Stacked queries
        "stacked_query": r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)",
        # Time-based
        "sleep_injection": r"SLEEP\s*\(\s*\d+\s*\)",
        "benchmark_injection": r"BENCHMARK\s*\(",
        "waitfor_injection": r"WAITFOR\s+DELAY",
        "pg_sleep": r"PG_SLEEP\s*\(",
        # Error-based
        "extractvalue": r"EXTRACTVALUE\s*\(",
        "updatexml": r"UPDATEXML\s*\(",
        # Out-of-band
        "load_file": r"LOAD_FILE\s*\(",
        "into_outfile": r"INTO\s+OUTFILE",
        "into_dumpfile": r"INTO\s+DUMPFILE",
        # Blind injection patterns
        "substring_blind": r"SUBSTRING\s*\([^,]+,\s*\d+,\s*1\s*\)",
        "ascii_blind": r"ASCII\s*\(\s*SUBSTRING",
        "if_blind": r"IF\s*\([^,]+,\s*(SLEEP|BENCHMARK)",
        # System info gathering
        "version_probe": r"@@VERSION|VERSION\s*\(\)",
        "database_probe": r"DATABASE\s*\(\)|SCHEMA\s*\(\)",
        "user_probe": r"CURRENT_USER|SESSION_USER|SYSTEM_USER",
        "system_table_mysql": r"\bmysql\.",
        "system_table_info_schema": r"\binformation_schema\.",
        # Hex encoding bypass
        "hex_encoding": r"0x[0-9a-fA-F]+",
        "char_encoding": r"CHAR\s*\(\s*\d+",
    }

    @classmethod
    def detect(cls, sql: str) -> InjectionDetectionResult:
        """
        SQL Injection 패턴 탐지

        Args:
            sql: 검사할 SQL 쿼리

        Returns:
            InjectionDetectionResult: 탐지 결과 (패턴, 위험도, 권장사항)
        """
        detected_patterns = []
        risk_score = 0.0

        for name, pattern in cls.INJECTION_PATTERNS.items():
            if re.search(pattern, sql, re.IGNORECASE | re.DOTALL):
                detected_patterns.append(name)
                risk_score += cls._get_pattern_weight(name)

        # risk_score는 1.0을 초과하지 않음
        risk_score = min(risk_score, 1.0)

        is_injection = len(detected_patterns) > 0

        recommendation = None
        if is_injection:
            recommendation = "SQL Injection 패턴이 감지되었습니다. 요청이 차단됩니다."

        return InjectionDetectionResult(
            is_injection=is_injection,
            patterns_detected=detected_patterns,
            risk_score=risk_score,
            recommendation=recommendation,
        )

    @staticmethod
    def _get_pattern_weight(pattern_name: str) -> float:
        """
        패턴별 위험도 가중치

        High risk (0.5): UNION, Stacked Query, File Operations
        Medium risk (0.3): Time-based, Tautology, Comments
        Low risk (0.1): 기타 패턴

        Args:
            pattern_name: 패턴 이름

        Returns:
            float: 위험도 가중치 (0.1 ~ 0.5)
        """
        high_risk = {
            "union_injection",
            "stacked_query",
            "load_file",
            "into_outfile",
            "into_dumpfile",
        }
        medium_risk = {
            "sleep_injection",
            "benchmark_injection",
            "tautology_or",
            "comment_inline",
            "comment_block",
        }

        if pattern_name in high_risk:
            return 0.5
        elif pattern_name in medium_risk:
            return 0.3
        return 0.1
