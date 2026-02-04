"""
MetricsCollector 단위 테스트.

Stories: STORY-6-3
FRs: FR32
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio as redis

from src.services.ai.monitoring.metrics_collector import MetricsCollector


class TestMetricsCollector:
    """MetricsCollector 테스트"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis 클라이언트"""
        mock = AsyncMock(spec=redis.Redis)
        mock.lpush = AsyncMock(return_value=1)
        mock.expire = AsyncMock(return_value=True)
        mock.hincrby = AsyncMock(return_value=1)
        mock.hincrbyfloat = AsyncMock(return_value=1.0)
        mock.lrange = AsyncMock(return_value=[])
        mock.hgetall = AsyncMock(return_value={})
        mock.hget = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def collector(self, mock_redis):
        """MetricsCollector 인스턴스"""
        return MetricsCollector(mock_redis)

    @pytest.mark.asyncio
    async def test_record_response_time_success(self, collector, mock_redis):
        """응답 시간 기록 (성공)"""
        # When
        await collector.record_response_time(
            response_time_ms=1500.0, success=True, model="gpt-4o-mini"
        )

        # Then
        mock_redis.lpush.assert_called_once()
        assert mock_redis.lpush.call_args[0][1] == 1500.0
        assert mock_redis.expire.call_count == 2  # 응답 시간과 카운트 각각
        mock_redis.hincrby.assert_called_once()
        # hincrby 호출: (key, field, amount)
        assert mock_redis.hincrby.call_args[0][1] == "success"

    @pytest.mark.asyncio
    async def test_record_response_time_error(self, collector, mock_redis):
        """응답 시간 기록 (에러)"""
        # When
        await collector.record_response_time(
            response_time_ms=5000.0, success=False, model="gpt-4o-mini"
        )

        # Then
        mock_redis.hincrby.assert_called_once()
        # hincrby 호출: (key, field, amount)
        assert mock_redis.hincrby.call_args[0][1] == "error"

    @pytest.mark.asyncio
    async def test_record_llm_cost(self, collector, mock_redis):
        """LLM 비용 기록"""
        # When
        await collector.record_llm_cost(cost=0.05, model="gpt-4o-mini")

        # Then
        assert mock_redis.hincrbyfloat.call_count == 2
        calls = mock_redis.hincrbyfloat.call_args_list
        # 첫 번째 호출: total
        assert calls[0][0][1] == "total"
        assert calls[0][0][2] == 0.05
        # 두 번째 호출: model
        assert calls[1][0][1] == "gpt-4o-mini"
        assert calls[1][0][2] == 0.05

    @pytest.mark.asyncio
    async def test_get_response_time_percentiles_empty(self, collector, mock_redis):
        """응답 시간 백분위수 계산 (데이터 없음)"""
        # Given
        mock_redis.lrange.return_value = []

        # When
        result = await collector.get_response_time_percentiles(window_minutes=60)

        # Then
        assert result == {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0}

    @pytest.mark.asyncio
    async def test_get_response_time_percentiles_with_data(self, collector, mock_redis):
        """응답 시간 백분위수 계산 (데이터 있음)"""
        # Given - 100개의 샘플 데이터 (1000ms ~ 5000ms)
        sample_data = [str(1000 + i * 40).encode() for i in range(100)]
        mock_redis.lrange.return_value = sample_data

        # When
        result = await collector.get_response_time_percentiles(window_minutes=1)

        # Then
        assert result["count"] == 100
        assert result["p50"] > 0
        assert result["p95"] > result["p50"]
        assert result["p99"] > result["p95"]
        assert result["avg"] > 0

    @pytest.mark.asyncio
    async def test_get_error_rate_zero(self, collector, mock_redis):
        """에러율 계산 (요청 없음)"""
        # Given
        mock_redis.hgetall.return_value = {}

        # When
        result = await collector.get_error_rate(window_minutes=60)

        # Then
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_get_error_rate_with_errors(self, collector, mock_redis):
        """에러율 계산 (에러 있음)"""
        # Given - 80 성공, 20 에러
        mock_redis.hgetall.return_value = {b"success": b"80", b"error": b"20"}

        # When
        result = await collector.get_error_rate(window_minutes=1)

        # Then
        assert result == 0.2  # 20/100 = 0.2 (20%)

    @pytest.mark.asyncio
    async def test_get_monthly_llm_cost_zero(self, collector, mock_redis):
        """월간 LLM 비용 조회 (비용 없음)"""
        # Given
        mock_redis.hget.return_value = None

        # When
        result = await collector.get_monthly_llm_cost()

        # Then
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_get_monthly_llm_cost_with_data(self, collector, mock_redis):
        """월간 LLM 비용 조회 (비용 있음)"""
        # Given
        mock_redis.hget.return_value = b"150.50"

        # When
        result = await collector.get_monthly_llm_cost()

        # Then
        assert result == 150.50

    @pytest.mark.asyncio
    async def test_get_llm_cost_by_model(self, collector, mock_redis):
        """모델별 LLM 비용 조회"""
        # Given
        mock_redis.hgetall.return_value = {
            b"total": b"200.00",
            b"gpt-4o-mini": b"150.00",
            b"gpt-3.5-turbo": b"50.00",
        }

        # When
        result = await collector.get_llm_cost_by_model()

        # Then
        assert "gpt-4o-mini" in result
        assert "gpt-3.5-turbo" in result
        assert "total" not in result  # total은 제외
        assert result["gpt-4o-mini"] == 150.00
        assert result["gpt-3.5-turbo"] == 50.00
