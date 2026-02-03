"""
AI 질의 스키마 단위 테스트.

Stories: 2-1
"""

import pytest
from pydantic import ValidationError
from src.schemas.ai.query_schema import AIQueryRequest, AIQueryResponse


class TestAIQueryRequest:
    """AIQueryRequest 스키마 테스트"""

    def test_valid_request_minimal(self):
        """최소 필수 필드만 - 성공"""
        request = AIQueryRequest(question="오늘 매출 얼마야?")
        assert request.question == "오늘 매출 얼마야?"
        assert request.db_scope == "mariadb"  # 기본값
        assert request.max_rows == 100  # 기본값
        assert request.include_sql is False
        assert request.stream is False
        assert request.accessibility_mode is False

    def test_valid_request_full(self):
        """모든 필드 지정 - 성공"""
        request = AIQueryRequest(
            question="이번 달 상담사별 상담 건수는?",
            db_scope="mssql",
            max_rows=500,
            include_sql=True,
            stream=False,
            accessibility_mode=True,
        )
        assert request.question == "이번 달 상담사별 상담 건수는?"
        assert request.db_scope == "mssql"
        assert request.max_rows == 500
        assert request.include_sql is True

    def test_question_too_short(self):
        """질문 너무 짧음 (5자 미만) - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="안녕")
        errors = exc_info.value.errors()
        assert any("at least 5 characters" in str(e) for e in errors)

    def test_question_too_long(self):
        """질문 너무 김 (500자 초과) - 실패"""
        long_question = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question=long_question)
        errors = exc_info.value.errors()
        assert any("at most 500 characters" in str(e) for e in errors)

    def test_question_with_sql_keyword_select(self):
        """SQL SELECT 키워드 포함 - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="SELECT * FROM users")
        errors = exc_info.value.errors()
        assert any("SQL 키워드" in str(e) for e in errors)

    def test_question_with_sql_keyword_drop(self):
        """SQL DROP 키워드 포함 - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="DROP TABLE payments")
        errors = exc_info.value.errors()
        assert any("SQL 키워드" in str(e) for e in errors)

    def test_question_with_sql_injection_pattern(self):
        """SQL Injection 패턴 (주석) - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="테스트; -- 주석")
        errors = exc_info.value.errors()
        assert any("SQL 키워드" in str(e) for e in errors)

    def test_question_with_union_select(self):
        """UNION SELECT 패턴 - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="test UNION SELECT password")
        errors = exc_info.value.errors()
        assert any("SQL 키워드" in str(e) for e in errors)

    def test_question_strips_whitespace(self):
        """공백 자동 제거"""
        request = AIQueryRequest(question="  오늘 매출은?  ")
        assert request.question == "오늘 매출은?"

    def test_max_rows_boundary_valid(self):
        """max_rows 경계값 테스트 - 유효"""
        request1 = AIQueryRequest(question="테스트 질문입니다", max_rows=1)
        assert request1.max_rows == 1

        request2 = AIQueryRequest(question="테스트 질문입니다", max_rows=5000)
        assert request2.max_rows == 5000

    def test_max_rows_below_minimum(self):
        """max_rows < 1 - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="테스트 질문입니다", max_rows=0)
        errors = exc_info.value.errors()
        assert any("greater than or equal to 1" in str(e) for e in errors)

    def test_max_rows_above_maximum(self):
        """max_rows > 5000 - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(question="테스트 질문입니다", max_rows=5001)
        errors = exc_info.value.errors()
        assert any("less than or equal to 5000" in str(e) for e in errors)

    def test_invalid_db_scope(self):
        """잘못된 db_scope - 실패"""
        with pytest.raises(ValidationError) as exc_info:
            AIQueryRequest(
                question="테스트 질문입니다",
                db_scope="postgresql"  # type: ignore
            )
        errors = exc_info.value.errors()
        assert any("db_scope" in str(e) for e in errors)


class TestAIQueryResponse:
    """AIQueryResponse 스키마 테스트"""

    def test_valid_response_minimal(self):
        """최소 필수 필드 - 성공"""
        response = AIQueryResponse(
            success=True,
            query_id="123e4567-e89b-12d3-a456-426614174000",
            answer="오늘 매출은 1,500만원입니다.",
            execution_time_ms=250,
        )
        assert response.success is True
        assert response.answer == "오늘 매출은 1,500만원입니다."
        assert response.data is None
        assert response.generated_sql is None
        assert response.suggestions == []

    def test_valid_response_with_data(self):
        """데이터 포함 응답 - 성공"""
        response = AIQueryResponse(
            success=True,
            query_id="123e4567-e89b-12d3-a456-426614174000",
            answer="검색 결과는 다음과 같습니다.",
            data=[
                {"date": "2024-01-01", "revenue": 10000},
                {"date": "2024-01-02", "revenue": 15000},
            ],
            execution_time_ms=450,
            suggestions=["어제 매출은?", "이번 달 평균 매출은?"],
        )
        assert len(response.data) == 2
        assert response.data[0]["revenue"] == 10000
        assert len(response.suggestions) == 2

    def test_valid_response_with_sql(self):
        """생성된 SQL 포함 - 성공"""
        response = AIQueryResponse(
            success=True,
            query_id="123e4567-e89b-12d3-a456-426614174000",
            answer="SQL을 실행했습니다.",
            generated_sql="SELECT SUM(amount) FROM payments WHERE date = CURDATE()",
            execution_time_ms=300,
        )
        assert response.generated_sql is not None
        assert "SELECT" in response.generated_sql

    def test_valid_response_accessibility_mode(self):
        """접근성 모드 응답 - 성공"""
        response = AIQueryResponse(
            success=True,
            query_id="123e4567-e89b-12d3-a456-426614174000",
            answer="오늘 매출은 1,500만원입니다.",
            answer_summary="총 150건의 결제가 발생했으며, 평균 금액은 10만원입니다.",
            execution_time_ms=200,
        )
        assert response.answer_summary is not None
