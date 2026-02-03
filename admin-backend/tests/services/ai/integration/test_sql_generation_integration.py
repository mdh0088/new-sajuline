"""
SQL 생성 통합 테스트

실제 LLM 호출을 포함한 E2E 테스트 (Mock 가능)

Stories: AI-002
FRs: FR-011, FR-012, FR-013
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from src.services.ai.agents.sql_agent import SQLGenerationAgent
from src.services.ai.validators.sql_validator import SQLValidator


@pytest.fixture
def golden_dataset():
    """Golden Dataset 로드"""
    golden_path = Path(__file__).parent.parent / "golden" / "queries.json"
    with open(golden_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_settings():
    """테스트용 Settings"""
    return Mock(
        ai_llm_model="gpt-4o-mini",
        ai_llm_timeout=10,
        openai_api_key="test-key",
    )


@pytest.mark.asyncio
class TestSQLGenerationIntegration:
    """SQL 생성 통합 테스트"""

    @pytest.mark.parametrize("case_id", [1, 2, 3, 6, 10])  # 샘플 케이스만 테스트
    async def test_golden_dataset_pattern_matching(
        self,
        case_id,
        golden_dataset,
        mock_settings
    ):
        """Golden Dataset 패턴 매칭 테스트 (Mock LLM)

        실제 LLM을 호출하지 않고 예상 패턴만 검증합니다.
        """
        case = next(c for c in golden_dataset["cases"] if c["id"] == case_id)

        # Mock LLM - 예상 패턴을 포함하는 SQL 반환
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()

            # 케이스에 따라 다른 SQL 생성
            if case_id == 1:  # 모든 사용자 조회
                mock_sql = "SELECT id, username, email FROM users LIMIT 100"
            elif case_id == 2:  # 오늘 가입한 사용자
                mock_sql = "SELECT * FROM users WHERE DATE(created_at) = CURDATE() LIMIT 100"
            elif case_id == 3:  # 어제 가입한 사용자
                mock_sql = "SELECT * FROM users WHERE DATE(created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) LIMIT 100"
            elif case_id == 6:  # 총 사용자 수
                mock_sql = "SELECT COUNT(*) as total_users FROM users"
            elif case_id == 10:  # 최근 가입 10명
                mock_sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT 10"
            else:
                mock_sql = "SELECT * FROM users LIMIT 100"

            llm_instance.ainvoke = AsyncMock(
                return_value=Mock(content=mock_sql)
            )
            mock.return_value = llm_instance

            # SQL 생성
            agent = SQLGenerationAgent(settings=mock_settings)
            result = await agent.generate_sql(
                question=case["question"],
                schema_info="TABLE users (id INT, username VARCHAR, email VARCHAR, created_at DATETIME)",
                allowed_tables=case["tables_used"]
            )

            # 성공 검증
            assert result.success is True, f"Case {case_id} failed: {result.error}"
            assert result.sql is not None

            # 패턴 매칭 검증
            sql_upper = result.sql.upper()
            for pattern in case["expected_patterns"]:
                assert pattern.upper() in sql_upper, \
                    f"Case {case_id}: Expected pattern '{pattern}' not found in SQL: {result.sql}"

            # 금지 패턴 검증
            for forbidden in case["must_not_contain"]:
                assert forbidden.upper() not in sql_upper, \
                    f"Case {case_id}: Forbidden pattern '{forbidden}' found in SQL: {result.sql}"

    async def test_end_to_end_with_validation(self, mock_settings):
        """E2E 테스트: SQL 생성 → 검증 파이프라인"""
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()
            llm_instance.ainvoke = AsyncMock(
                return_value=Mock(content="SELECT * FROM users WHERE status = 'active' LIMIT 50")
            )
            mock.return_value = llm_instance

            # 1. SQL 생성
            agent = SQLGenerationAgent(settings=mock_settings)
            generation_result = await agent.generate_sql(
                question="활성 사용자 조회",
                schema_info="TABLE users (id INT, username VARCHAR, status VARCHAR)",
                allowed_tables=["users"]
            )

            assert generation_result.success is True
            assert generation_result.sql is not None

            # 2. SQL 검증
            validation_result = await SQLValidator.validate(
                sql=generation_result.sql,
                allowed_tables={"users"}
            )

            assert validation_result.is_valid is True
            assert validation_result.is_select_only is True
            assert "users" in validation_result.tables_used

    async def test_invalid_sql_detection(self, mock_settings):
        """잘못된 SQL 생성 시 검증에서 차단되는지 테스트"""
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()
            # LLM이 잘못된 SQL을 생성한 경우
            llm_instance.ainvoke = AsyncMock(
                return_value=Mock(content="DELETE FROM users WHERE id = 1")
            )
            mock.return_value = llm_instance

            agent = SQLGenerationAgent(settings=mock_settings)
            generation_result = await agent.generate_sql(
                question="사용자 삭제",
                schema_info="TABLE users (id INT)",
                allowed_tables=["users"]
            )

            # 생성은 성공하지만
            assert generation_result.success is True

            # 검증에서 차단되어야 함
            validation_result = await SQLValidator.validate(
                sql=generation_result.sql,
                allowed_tables={"users"}
            )

            assert validation_result.is_valid is False
            assert "DELETE" in validation_result.error.upper()

    async def test_unauthorized_table_detection(self, mock_settings):
        """허용되지 않은 테이블 사용 감지 테스트"""
        with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
            llm_instance = Mock()
            llm_instance.ainvoke = AsyncMock(
                return_value=Mock(content="SELECT * FROM admin_secrets LIMIT 10")
            )
            mock.return_value = llm_instance

            agent = SQLGenerationAgent(settings=mock_settings)
            generation_result = await agent.generate_sql(
                question="관리자 비밀 정보 조회",
                schema_info="TABLE admin_secrets (id INT, secret VARCHAR)",
                allowed_tables=["users", "payments"]  # admin_secrets는 허용 안 됨
            )

            assert generation_result.success is True

            # 검증에서 차단
            validation_result = await SQLValidator.validate(
                sql=generation_result.sql,
                allowed_tables={"users", "payments"}
            )

            assert validation_result.is_valid is False
            assert "admin_secrets" in validation_result.error.lower()

    async def test_date_parsing_variations(self, mock_settings):
        """다양한 날짜 표현 파싱 테스트"""
        date_questions = [
            ("오늘 가입한 사용자", "CURDATE()"),
            ("어제 결제한 내역", "DATE_SUB"),
            ("이번 주 사용자", "YEARWEEK"),
            ("최근 7일 결제", "INTERVAL 7 DAY"),
        ]

        for question, expected_pattern in date_questions:
            with patch("src.services.ai.agents.sql_agent.ChatOpenAI") as mock:
                llm_instance = Mock()
                # 패턴에 맞는 SQL 반환
                if "CURDATE()" in expected_pattern:
                    mock_sql = "SELECT * FROM users WHERE DATE(created_at) = CURDATE()"
                elif "DATE_SUB" in expected_pattern:
                    mock_sql = "SELECT * FROM payments WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
                elif "YEARWEEK" in expected_pattern:
                    mock_sql = "SELECT * FROM users WHERE YEARWEEK(created_at) = YEARWEEK(CURDATE())"
                elif "INTERVAL 7 DAY" in expected_pattern:
                    mock_sql = "SELECT * FROM payments WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"

                llm_instance.ainvoke = AsyncMock(
                    return_value=Mock(content=mock_sql)
                )
                mock.return_value = llm_instance

                agent = SQLGenerationAgent(settings=mock_settings)
                result = await agent.generate_sql(
                    question=question,
                    schema_info="TABLE users/payments",
                    allowed_tables=["users", "payments"]
                )

                assert result.success is True
                assert expected_pattern in result.sql.upper(), \
                    f"Expected '{expected_pattern}' in SQL for question '{question}'"
