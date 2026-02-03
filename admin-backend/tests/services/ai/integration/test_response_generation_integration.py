"""
응답 생성 통합 테스트

전체 플로우 (SQL 생성 → 실행 → 응답 생성) E2E 테스트

Stories: 2-4
FRs: FR-011, FR-013, NFR-P1
"""
import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.messages import AIMessage

from src.services.ai.agents.response_agent import ResponseGenerationAgent
from src.services.ai.utils.response_formatter import ResponseFormatter
from src.services.ai.config.column_mappings import COLUMN_MAPPINGS


@pytest.fixture
def mock_llm_response():
    """Mock LLM 응답"""
    def _create_response(content: str):
        mock_llm = Mock()
        # ChatPromptTemplate | LLM 체인을 mock
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=AIMessage(content=content))
        mock_llm.__or__ = Mock(return_value=mock_chain)
        return mock_llm
    return _create_response


@pytest.fixture
def mock_settings():
    """Mock Settings 인스턴스"""
    settings = Mock()
    settings.ai_llm_model = "gpt-4o-mini"
    settings.ai_llm_fallback_model = "gpt-3.5-turbo"
    settings.ai_llm_timeout = 10
    settings.openai_api_key = "test-api-key"
    settings.ai_llm_max_sample_rows = 10
    return settings


@pytest.mark.asyncio
async def test_full_response_generation_flow(mock_llm_response, mock_settings):
    """전체 응답 생성 플로우 통합 테스트"""
    # Given: 쿼리 결과 데이터
    question = "이번 달 총 매출은 얼마인가요?"
    sql = "SELECT SUM(amount) as total_sales FROM payments WHERE MONTH(created_at) = MONTH(NOW())"
    result_data = [{"total_sales": 120000000}]
    columns = ["total_sales"]

    # Given: LLM Mock 설정
    llm = mock_llm_response("이번 달 총 매출은 1억 2천만원입니다. 전월 대비 15% 증가했습니다.")

    # When: ResponseGenerationAgent로 자연어 응답 생성
    response_agent = ResponseGenerationAgent(llm=llm, settings=mock_settings)
    response_result = await response_agent.generate_response(
        question=question,
        sql=sql,
        result_data=result_data,
        columns=columns,
    )

    # Then: 응답 생성 성공
    assert response_result.success is True
    assert response_result.natural_language_response is not None
    assert "매출" in response_result.natural_language_response
    assert response_result.error_code is None

    # When: ResponseFormatter로 테이블 데이터 포맷팅
    formatted_data = ResponseFormatter.format_table_data(
        data=result_data,
        columns=columns,
        column_mappings=COLUMN_MAPPINGS,
    )

    # Then: 데이터 포맷팅 성공
    assert len(formatted_data) == 1
    assert "총 매출" in formatted_data[0]
    assert formatted_data[0]["총 매출"] == "1억 2천만원"


@pytest.mark.asyncio
async def test_response_generation_performance(mock_llm_response, mock_settings):
    """응답 생성 성능 테스트 (p95 < 3초)"""
    # Given: 샘플 데이터
    question = "오늘 가입한 사용자 수는?"
    sql = "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = CURDATE()"
    result_data = [{"count": 45}]
    columns = ["count"]

    llm = mock_llm_response("오늘 45명의 회원이 새로 가입했습니다.")

    # When: 응답 생성 실행 및 시간 측정
    start_time = time.time()

    response_agent = ResponseGenerationAgent(llm=llm, settings=mock_settings)
    response_result = await response_agent.generate_response(
        question=question,
        sql=sql,
        result_data=result_data,
        columns=columns,
    )

    execution_time = time.time() - start_time

    # Then: 성능 요구사항 만족 (3초 이내)
    assert response_result.success is True
    assert execution_time < 3.0, f"응답 생성 시간이 3초를 초과했습니다: {execution_time:.2f}초"
    assert response_result.execution_time_ms < 3000


@pytest.mark.asyncio
async def test_empty_result_handling(mock_llm_response, mock_settings):
    """빈 결과 처리 통합 테스트"""
    # Given: 빈 결과
    question = "작년 매출은 얼마인가요?"
    sql = "SELECT SUM(amount) as total_sales FROM payments WHERE YEAR(created_at) = 2023"
    result_data = []
    columns = ["total_sales"]

    llm = mock_llm_response("조회 결과가 없습니다. 다른 기간으로 조회해보시는 건 어떨까요?")

    # When: 빈 결과에 대한 응답 생성
    response_agent = ResponseGenerationAgent(llm=llm, settings=mock_settings)
    response_result = await response_agent.generate_response(
        question=question,
        sql=sql,
        result_data=result_data,
        columns=columns,
    )

    # Then: 빈 결과 메시지 생성 성공
    assert response_result.success is True
    assert "조회 결과가 없습니다" in response_result.natural_language_response


@pytest.mark.asyncio
async def test_multiple_rows_formatting(mock_llm_response, mock_settings):
    """다중 행 결과 포맷팅 통합 테스트"""
    # Given: 다중 행 데이터
    question = "상담사별 매출 상위 3명은?"
    sql = "SELECT counselor_name, SUM(amount) as total_sales FROM payments GROUP BY counselor_id ORDER BY total_sales DESC LIMIT 3"
    result_data = [
        {"counselor_name": "김철수", "total_sales": 5000000},
        {"counselor_name": "이영희", "total_sales": 4500000},
        {"counselor_name": "박민수", "total_sales": 4200000},
    ]
    columns = ["counselor_name", "total_sales"]

    llm = mock_llm_response(
        "상담사별 매출 상위 3명은 김철수님(500만원), 이영희님(450만원), 박민수님(420만원)입니다."
    )

    # When: 응답 생성 및 데이터 포맷팅
    response_agent = ResponseGenerationAgent(llm=llm, settings=mock_settings)
    response_result = await response_agent.generate_response(
        question=question,
        sql=sql,
        result_data=result_data,
        columns=columns,
    )

    formatted_data = ResponseFormatter.format_table_data(
        data=result_data,
        columns=columns,
        column_mappings=COLUMN_MAPPINGS,
    )

    # Then: 자연어 응답과 테이블 데이터 모두 제공
    assert response_result.success is True
    assert "김철수" in response_result.natural_language_response

    assert len(formatted_data) == 3
    assert formatted_data[0]["상담사명"] == "김철수"
    assert formatted_data[0]["총 매출"] == "500만원"
    assert formatted_data[1]["총 매출"] == "450만원"
    assert formatted_data[2]["총 매출"] == "420만원"


@pytest.mark.asyncio
async def test_error_recovery(mock_llm_response, mock_settings):
    """에러 발생 시 복구 메커니즘 테스트"""
    # Given: LLM 타임아웃 발생
    llm = Mock()
    llm.ainvoke = AsyncMock(side_effect=TimeoutError("LLM timeout"))

    # When: 에러 발생
    response_agent = ResponseGenerationAgent(llm=llm, settings=mock_settings)
    response_result = await response_agent.generate_response(
        question="테스트 질문",
        sql="SELECT * FROM test",
        result_data=[{"count": 10}],
        columns=["count"],
    )

    # Then: 에러 코드 반환 및 복구 실패 처리
    assert response_result.success is False
    assert response_result.error_code == "AIBI_RESPONSE_TIMEOUT"
    assert response_result.error_message is not None


@pytest.mark.asyncio
async def test_complex_data_formatting(mock_llm_response, mock_settings):
    """복잡한 데이터 타입 포맷팅 통합 테스트"""
    from datetime import date, datetime

    # Given: 다양한 데이터 타입
    result_data = [
        {
            "user_id": 1,
            "name": "홍길동",
            "total_amount": 15000000,
            "created_at": datetime(2024, 1, 15, 14, 30),
            "last_login": date(2024, 2, 1),
            "count": 150,
            "memo": None,
        }
    ]
    columns = ["user_id", "name", "total_amount", "created_at", "last_login", "count", "memo"]

    llm = mock_llm_response("사용자 홍길동님의 총 금액은 1,500만원입니다.")

    # When: 데이터 포맷팅
    formatted_data = ResponseFormatter.format_table_data(
        data=result_data,
        columns=columns,
        column_mappings=COLUMN_MAPPINGS,
    )

    # Then: 각 타입별 올바른 포맷팅
    row = formatted_data[0]
    assert row["사용자 ID"] == "1"
    assert row["이름"] == "홍길동"
    assert row["총 금액"] == "1천만원"  # 금액 컬럼
    assert row["생성일시"] == "2024-01-15 14:30"  # datetime with time
    assert row["마지막 로그인"] == "2024-02-01"  # date
    assert row["건수"] == "150"  # 일반 숫자
    assert row["메모"] == "-"  # NULL 값
