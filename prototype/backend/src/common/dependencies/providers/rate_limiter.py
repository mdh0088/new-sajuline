from src.common.infrastructure.rate_limiter import rate_limiter as _rate_limiter
from src.common.infrastructure.rate_limiter import RateLimiter

def get_rate_limiter() -> RateLimiter:
	return _rate_limiter
