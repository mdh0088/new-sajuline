from typing import Optional, Any
from src.common.config.settings import get_settings

_s3_client: Optional[Any] = None

def get_s3():
	global _s3_client
	if _s3_client is None:
		try:
			import boto3  # type: ignore
			from botocore.config import Config  # type: ignore
		except Exception as e:  # noqa: BLE001
			raise RuntimeError(
				"boto3 is not installed. Install boto3 to use S3 client."
			) from e
		settings = get_settings()
		config = Config(
			retries={"max_attempts": getattr(settings, "AWS_S3_MAX_RETRIES", 3), "mode": "standard"},
			read_timeout=getattr(settings, "AWS_S3_TIMEOUT", 30),
			connect_timeout=getattr(settings, "AWS_S3_TIMEOUT", 30),
			signature_version=getattr(settings, "AWS_S3_SIGNATURE_VERSION", None) or None,
		)
		_s3_client = boto3.client(
			"s3",
			aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
			aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
			region_name=getattr(settings, "AWS_REGION", None),
			endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
			config=config,
		)
	return _s3_client
