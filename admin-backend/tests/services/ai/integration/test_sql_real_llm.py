"""
실제 LLM 호출 통합 테스트

환경변수 OPENAI_API_KEY가 설정된 경우에만 실행됩니다.

Stories: AI-002
FRs: FR-011, FR-012, FR-013
"""
import os
import pytest
from unittest.mock import Mock

from src.services.ai.agents.sql_agent import SQLGenerationAgent
from src.services.ai.validators.sql_validator import SQLValidator


# OPENAI_API_KEY 환경변수 없으면 skip
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY 환경변수 필요 (실제 LLM 호출)"
)


@pytest.fixture
def real_settings():
    """실제 OpenAI API 키를 사용하는 Settings"""
    return Mock(
        ai_llm_model="gpt-4o-mini",
        ai_llm_timeout=10,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )


@pytest.mark.integration
@pytest.mark.asyncio
class TestRealLLMIntegration:
    """실제 LLM을 사용한 E2E 통합 테스트"""

    async def test_real_llm_basic_query(self, real_settings):
        """실제 LLM 호출: 기본 사용자 조회"""
        agent = SQLGenerationAgent(settings=real_settings)

        schema_info = """
        ## Table: users
        | Column | Type | Nullable | Key | Comment |
        |--------|------|----------|-----|---------|
        | id | INT | NO | PRI | 사용자 ID |
        | username | VARCHAR(50) | NO | UNI | 사용자명 |
        | email | VARCHAR(100) | NO | UNI | 이메일 |
        | created_at | DATETIME | NO | | 가입일시 |
        """

        result = await agent.generate_sql(
            question="모든 사용자를 조회해줘",
            schema_info=schema_info,
            allowed_tables=["users"]
        )

        # 생성 성공 검증
        assert result.success is True, f"SQL 생성 실패: {result.error}"
        assert result.sql is not None
        assert len(result.sql) > 0

        # SQL 검증
        validation = await SQLValidator.validate(
            sql=result.sql,
            allowed_tables={"users"}
        )

        assert validation.is_valid is True, f"SQL 검증 실패: {validation.error}"
        assert validation.is_select_only is True
        assert "users" in validation.tables_used

        # 기본 패턴 확인
        sql_upper = result.sql.upper()
        assert "SELECT" in sql_upper
        assert "FROM USERS" in sql_upper or "FROM `USERS`" in sql_upper

    async def test_real_llm_date_parsing(self, real_settings):
        """실제 LLM 호출: 날짜 파싱 (오늘)"""
        agent = SQLGenerationAgent(settings=real_settings)

        schema_info = """
        ## Table: users
        | Column | Type | Nullable | Key | Comment |
        |--------|------|----------|-----|---------|
        | id | INT | NO | PRI | 사용자 ID |
        | created_at | DATETIME | NO | | 가입일시 |
        """

        result = await agent.generate_sql(
            question="오늘 가입한 사용자는?",
            schema_info=schema_info,
            allowed_tables=["users"]
        )

        assert result.success is True
        assert result.sql is not None

        # 날짜 함수가 포함되어야 함
        sql_upper = result.sql.upper()
        assert "CURDATE()" in sql_upper or "CURRENT_DATE" in sql_upper, \
            f"날짜 함수가 없습니다: {result.sql}"

        # SQL 검증
        validation = await SQLValidator.validate(
            sql=result.sql,
            allowed_tables={"users"}
        )
        assert validation.is_valid is True

    async def test_real_llm_join_query(self, real_settings):
        """실제 LLM 호출: 조인 쿼리"""
        agent = SQLGenerationAgent(settings=real_settings)

        schema_info = """
        ## Table: users
        | Column | Type | Nullable | Key | Comment |
        |--------|------|----------|-----|---------|
        | id | INT | NO | PRI | 사용자 ID |
        | username | VARCHAR(50) | NO | UNI | 사용자명 |

        ## Table: payments
        | Column | Type | Nullable | Key | Comment |
        |--------|------|----------|-----|---------|
        | id | INT | NO | PRI | 결제 ID |
        | user_id | INT | NO | FK | 사용자 ID (FK: users.id) |
        | amount | DECIMAL(10,2) | NO | | 결제 금액 |
        | created_at | DATETIME | NO | | 결제일시 |
        """

        result = await agent.generate_sql(
            question="최근 결제한 사용자 목록",
            schema_info=schema_info,
            allowed_tables=["users", "payments"]
        )

        assert result.success is True
        assert result.sql is not None

        sql_upper = result.sql.upper()
        # 조인 패턴 확인
        assert "JOIN" in sql_upper, f"JOIN이 없습니다: {result.sql}"
        assert "USERS" in sql_upper
        assert "PAYMENTS" in sql_upper

        # SQL 검증
        validation = await SQLValidator.validate(
            sql=result.sql,
            allowed_tables={"users", "payments"}
        )
        assert validation.is_valid is True
        assert "users" in validation.tables_used
        assert "payments" in validation.tables_used

    async def test_real_llm_forbidden_query_rejection(self, real_settings):
        """실제 LLM 호출: 금지된 쿼리 시도 (UPDATE)"""
        agent = SQLGenerationAgent(settings=real_settings)

        schema_info = "TABLE users (id INT, username VARCHAR)"

        # LLM이 금지된 쿼리를 생성하도록 유도
        result = await agent.generate_sql(
            question="사용자 이름을 'hacker'로 변경해줘",
            schema_info=schema_info,
            allowed_tables=["users"]
        )

        # 생성은 될 수 있지만, 검증에서 차단되어야 함
        if result.success:
            validation = await SQLValidator.validate(
                sql=result.sql,
                allowed_tables={"users"}
            )
            # UPDATE/DELETE 등 금지 키워드가 있으면 검증 실패해야 함
            if not validation.is_select_only:
                assert validation.is_valid is False, \
                    "금지된 SQL이 검증을 통과했습니다!"

    async def test_real_llm_timeout_handling(self, real_settings):
        """실제 LLM 호출: 타임아웃 시나리오 (매우 복잡한 질문)"""
        # 타임아웃을 1초로 줄여서 테스트
        real_settings.ai_llm_timeout = 1

        agent = SQLGenerationAgent(settings=real_settings)

        # 매우 복잡한 질문으로 타임아웃 유도 시도
        complex_question = """
        사용자별로 최근 30일간 결제 금액의 합계, 평균, 최대값, 최소값을 구하고,
        이를 지난 달 같은 기간과 비교하여 증감률을 계산하고,
        상위 10명의 사용자에 대해 결제 패턴을 분석하고,
        각 사용자의 결제 빈도와 평균 결제 간격을 계산해줘
        """

        result = await agent.generate_sql(
            question=complex_question,
            schema_info="TABLE users, payments",
            allowed_tables=["users", "payments"]
        )

        # 타임아웃이 발생하거나 정상 처리되거나 둘 다 허용
        # (실제 LLM이 빠르면 성공할 수도 있음)
        assert result is not None
        if not result.success:
            assert "timeout" in result.error.lower() or "시간 초과" in result.error
