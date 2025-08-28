from typing import Optional, Any
from src.common.config.settings import get_settings

_ai_client: Optional[Any] = None

def get_ai_client():
	global _ai_client
	if _ai_client is None:
		settings = get_settings()
		# 기본: OpenAI 최신 SDK(OpenAI) 사용
		try:
			from openai import OpenAI  # type: ignore
		except Exception as e:  # noqa: BLE001
			raise RuntimeError("openai package is not installed.") from e
		api_key = getattr(settings, "OPENAI_API_KEY", None)
		if not api_key:
			raise RuntimeError("OPENAI_API_KEY is not configured")
		base_url = getattr(settings, "OPENAI_BASE_URL", None)
		org = getattr(settings, "OPENAI_ORG", None)
		_ai_client = OpenAI(api_key=api_key, base_url=base_url, organization=org)
	return _ai_client
