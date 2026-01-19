"""
재시도/백오프 유틸 (T-068)

tenacity 기반의 표준 재시도 데코레이터/헬퍼 제공
서비스/리포지토리에서 import 하여 사용
"""

from __future__ import annotations

from typing import Callable, Type, Iterable

from tenacity import (
	retry,
	stop_after_attempt,
	wait_exponential_jitter,
	retry_if_exception_type,
)


def with_retry(
	*,
	attempts: int = 3,
	min_wait_seconds: float = 0.2,
	max_wait_seconds: float = 2.0,
	exceptions: Iterable[Type[BaseException]] = (Exception,),
) -> Callable:
	"""
	기본 재시도 정책 데코레이터
	- 지수 백오프 + 지터
	- 시도 횟수/대상 예외 지정 가능
	"""

	return retry(
		stop=stop_after_attempt(attempts),
		wait=wait_exponential_jitter(initial=min_wait_seconds, max=max_wait_seconds),
		retry=retry_if_exception_type(tuple(exceptions)),
	)


