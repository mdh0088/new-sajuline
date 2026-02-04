"""
Circuit Breaker 패턴 구현.

5회 실패 시 OPEN 상태로 전환하고, 30초 후 HALF_OPEN 상태로
복구를 시도합니다. HALF_OPEN에서 3회 성공 시 CLOSED로 전환됩니다.

Stories: STORY-6-1
FRs: FR29, NFR-R2, NFR-R3
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable, TypeVar, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit Breaker 상태"""
    CLOSED = "closed"       # 정상 작동
    OPEN = "open"           # 차단 상태
    HALF_OPEN = "half_open"  # 테스트 상태


@dataclass
class CircuitBreakerConfig:
    """Circuit Breaker 설정"""
    failure_threshold: int = 5       # Open 전환 실패 횟수
    success_threshold: int = 3       # Close 전환 성공 횟수
    timeout: float = 30.0            # Open 유지 시간 (초)
    half_open_max_calls: int = 3     # Half-Open 시 최대 테스트 호출


@dataclass
class CircuitBreakerState:
    """Circuit Breaker 상태 관리"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    last_state_change: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


T = TypeVar('T')


class CircuitBreaker:
    """
    Circuit Breaker 패턴 구현.

    서비스 장애 시 자동으로 요청을 차단하고, 일정 시간 후
    복구를 시도합니다.

    Example:
        >>> cb = CircuitBreaker("my_service")
        >>> result = await cb.call(my_async_function, arg1, arg2)
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None
    ):
        """
        Circuit Breaker 초기화.

        Args:
            name: Circuit Breaker 식별자
            config: 설정 (None이면 기본값 사용)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """현재 Circuit 상태"""
        return self._state.state

    async def call(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Circuit Breaker를 통한 함수 호출.

        Args:
            func: 호출할 async 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자

        Returns:
            함수 실행 결과

        Raises:
            CircuitBreakerOpenError: Circuit이 OPEN 상태일 때
            Exception: 함수 실행 중 발생한 예외
        """
        async with self._lock:
            await self._check_state_transition()

            if self._state.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN"
                )

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure(e)
            raise

    async def _check_state_transition(self):
        """상태 전환 확인"""
        if self._state.state == CircuitState.OPEN:
            # Timeout 경과 시 Half-Open으로 전환
            if self._state.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self._state.last_failure_time).total_seconds()
                if elapsed >= self.config.timeout:
                    await self._transition_to(CircuitState.HALF_OPEN)

    async def _on_success(self):
        """성공 처리"""
        async with self._lock:
            self._state.failure_count = 0

            if self._state.state == CircuitState.HALF_OPEN:
                self._state.success_count += 1
                if self._state.success_count >= self.config.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)

    async def _on_failure(self, error: Exception):
        """실패 처리"""
        async with self._lock:
            self._state.failure_count += 1
            self._state.last_failure_time = datetime.now(timezone.utc)
            self._state.success_count = 0

            if self._state.state == CircuitState.HALF_OPEN:
                # Half-Open에서 실패 시 즉시 Open
                await self._transition_to(CircuitState.OPEN)
            elif self._state.failure_count >= self.config.failure_threshold:
                await self._transition_to(CircuitState.OPEN)

    async def _transition_to(self, new_state: CircuitState):
        """상태 전환"""
        old_state = self._state.state
        self._state.state = new_state
        self._state.last_state_change = datetime.now(timezone.utc)

        if new_state == CircuitState.HALF_OPEN:
            self._state.success_count = 0

        logger.warning(
            f"Circuit breaker '{self.name}' state change: {old_state.value} -> {new_state.value} "
            f"(failures={self._state.failure_count}, timestamp={datetime.now(timezone.utc).isoformat()})"
        )

    def get_stats(self) -> dict:
        """
        현재 상태 통계.

        Returns:
            상태 정보 딕셔너리
        """
        return {
            "name": self.name,
            "state": self._state.state.value,
            "failure_count": self._state.failure_count,
            "success_count": self._state.success_count,
            "last_failure_time": (
                self._state.last_failure_time.isoformat()
                if self._state.last_failure_time else None
            ),
            "last_state_change": self._state.last_state_change.isoformat()
        }


class CircuitBreakerOpenError(Exception):
    """Circuit Breaker가 Open 상태일 때 발생하는 예외"""
    pass
