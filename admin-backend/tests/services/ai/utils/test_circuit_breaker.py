"""
Circuit Breaker 패턴 테스트.

Stories: STORY-6-1
FRs: FR29, NFR-R2, NFR-R3
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from src.services.ai.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerOpenError,
)


@pytest.fixture
def circuit_breaker_config():
    """테스트용 Circuit Breaker 설정"""
    return CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=1.0,  # 1초 (테스트 속도 향상)
        half_open_max_calls=2
    )


@pytest.fixture
def circuit_breaker(circuit_breaker_config):
    """Circuit Breaker 인스턴스"""
    return CircuitBreaker(
        name="test_breaker",
        config=circuit_breaker_config
    )


class TestCircuitBreakerStateTransitions:
    """Circuit Breaker 상태 전환 테스트"""

    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self, circuit_breaker):
        """초기 상태는 CLOSED"""
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_successful_call_keeps_closed_state(self, circuit_breaker):
        """성공한 호출은 CLOSED 상태 유지"""
        async def success_func():
            return "success"

        result = await circuit_breaker.call(success_func)

        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failure_threshold_opens_circuit(self, circuit_breaker):
        """실패 임계값 도달 시 OPEN 상태로 전환"""
        async def failing_func():
            raise Exception("Simulated failure")

        # 3번 실패 (threshold)
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        assert circuit_breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self, circuit_breaker):
        """OPEN 상태에서는 호출 거부"""
        async def failing_func():
            raise Exception("Simulated failure")

        # Circuit 열기
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        # OPEN 상태에서 호출 시도
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_timeout_transitions_to_half_open(self, circuit_breaker):
        """타임아웃 경과 후 HALF_OPEN으로 전환"""
        async def failing_func():
            raise Exception("Simulated failure")

        # Circuit 열기
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        assert circuit_breaker.state == CircuitState.OPEN

        # 타임아웃 대기 (1초)
        await asyncio.sleep(1.1)

        # 다음 호출 시 HALF_OPEN으로 전환
        async def success_func():
            return "success"

        result = await circuit_breaker.call(success_func)

        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_success_closes_circuit(self, circuit_breaker):
        """HALF_OPEN에서 성공 시 CLOSED로 전환"""
        async def failing_func():
            raise Exception("Simulated failure")

        # Circuit 열기
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        # 타임아웃 대기
        await asyncio.sleep(1.1)

        # HALF_OPEN으로 전환 및 성공 (2번 성공해야 CLOSED)
        async def success_func():
            return "success"

        await circuit_breaker.call(success_func)
        assert circuit_breaker.state == CircuitState.HALF_OPEN

        await circuit_breaker.call(success_func)
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self, circuit_breaker):
        """HALF_OPEN에서 실패 시 즉시 OPEN으로 재전환"""
        async def failing_func():
            raise Exception("Simulated failure")

        # Circuit 열기
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        # 타임아웃 대기
        await asyncio.sleep(1.1)

        # HALF_OPEN에서 실패
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_func)

        assert circuit_breaker.state == CircuitState.OPEN


class TestCircuitBreakerStatistics:
    """Circuit Breaker 통계 테스트"""

    @pytest.mark.asyncio
    async def test_get_stats_returns_correct_info(self, circuit_breaker):
        """통계 정보가 정확하게 반환됨"""
        stats = circuit_breaker.get_stats()

        assert stats["name"] == "test_breaker"
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["failure_count"] == 0
        assert stats["success_count"] == 0
        assert stats["last_failure_time"] is None

    @pytest.mark.asyncio
    async def test_failure_count_increments(self, circuit_breaker):
        """실패 횟수가 정확하게 증가"""
        async def failing_func():
            raise Exception("Simulated failure")

        # 2번 실패
        for _ in range(2):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_func)

        stats = circuit_breaker.get_stats()
        assert stats["failure_count"] == 2
        assert stats["last_failure_time"] is not None


class TestCircuitBreakerConcurrency:
    """Circuit Breaker 동시성 테스트"""

    @pytest.mark.asyncio
    async def test_concurrent_calls_handle_state_correctly(self, circuit_breaker):
        """동시 호출 시 상태가 올바르게 관리됨"""
        call_count = 0

        async def mixed_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise Exception("Fail")
            return "success"

        # 동시에 여러 호출 (일부 실패, 일부 성공)
        results = await asyncio.gather(
            *[circuit_breaker.call(mixed_func) for _ in range(5)],
            return_exceptions=True
        )

        # 실패와 CircuitBreakerOpenError 확인
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) >= 3


class TestCircuitBreakerConfiguration:
    """Circuit Breaker 설정 테스트"""

    @pytest.mark.asyncio
    async def test_custom_failure_threshold(self):
        """커스텀 실패 임계값 적용"""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = CircuitBreaker("test", config)

        async def failing_func():
            raise Exception("Fail")

        # 4번 실패해도 CLOSED
        for _ in range(4):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.CLOSED

        # 5번째 실패로 OPEN
        with pytest.raises(Exception):
            await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_custom_success_threshold(self):
        """커스텀 성공 임계값 적용"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=3,
            timeout=1.0
        )
        cb = CircuitBreaker("test", config)

        async def failing_func():
            raise Exception("Fail")

        # Circuit 열기
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        await asyncio.sleep(1.1)

        # 3번 성공해야 CLOSED
        async def success_func():
            return "ok"

        await cb.call(success_func)
        assert cb.state == CircuitState.HALF_OPEN

        await cb.call(success_func)
        assert cb.state == CircuitState.HALF_OPEN

        await cb.call(success_func)
        assert cb.state == CircuitState.CLOSED
