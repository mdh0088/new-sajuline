"""
Layer 1: 프롬프트 엔지니어링 보안.

시스템 프롬프트에 보안 지침을 내장하여 LLM이 안전한 SQL만 생성하도록 유도합니다.

Stories: 3-1
FRs: FR-021 (4-Layer Security)
"""

from typing import Set

SECURITY_SYSTEM_PROMPT = """
You are a secure SQL query generator for MariaDB database.

**CRITICAL SECURITY CONSTRAINTS:**

1. **SELECT ONLY**: You MUST generate ONLY SELECT statements.
   - FORBIDDEN: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER,
     TRUNCATE, GRANT, REVOKE, EXEC, EXECUTE
   - FORBIDDEN: Any data modification or schema changes
   - FORBIDDEN: Administrative or system commands

2. **ALLOWED TABLES**: You can ONLY query from explicitly allowed tables.
   - The allowed tables will be provided in each request
   - Do NOT access any table not in the allowed list
   - Do NOT use information_schema or system tables

3. **FORBIDDEN PATTERNS**: You MUST NOT generate queries with:
   - UNION or UNION ALL (SQL injection risk)
   - Stacked queries (multiple statements with semicolons)
   - SQL comments (-- or /* */)
   - Subqueries accessing system tables
   - Time-based functions for injection (SLEEP, BENCHMARK)
   - File operations (LOAD_FILE, INTO OUTFILE, INTO DUMPFILE)

4. **RESPONSE FORMAT**: Generate clean, safe SQL queries only.
   - Use proper JOINs when needed
   - Apply appropriate WHERE clauses for filtering
   - Limit results when appropriate
   - Use clear column aliases for readability

**SECURITY PRINCIPLE**: When in doubt, refuse to generate the query
and explain why it's unsafe.
"""


def build_secure_prompt(user_query: str, allowed_tables: Set[str]) -> str:
    """
    사용자 쿼리와 허용 테이블 목록으로 보안이 강화된 프롬프트 생성.

    Args:
        user_query: 사용자의 자연어 질의
        allowed_tables: 접근 허용된 테이블 목록

    Returns:
        str: 보안 지침이 포함된 완전한 프롬프트

    Raises:
        ValueError: allowed_tables가 비어있을 경우
    """
    if not allowed_tables:
        raise ValueError("allowed_tables cannot be empty")

    # 허용 테이블 목록을 보기 좋게 포맷
    tables_list = ", ".join(sorted(allowed_tables))

    # 완전한 보안 프롬프트 생성
    prompt = f"""{SECURITY_SYSTEM_PROMPT}

**ALLOWED TABLES FOR THIS REQUEST:**
{tables_list}

**USER QUERY:**
{user_query}

Generate a safe SELECT query that answers the user's question using
ONLY the allowed tables listed above.
"""

    return prompt
