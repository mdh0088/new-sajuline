"""
S3 업로드 유틸리티

- settings.s3_directory 하위의 서브디렉토리(예: "counselor_applications")를 파라미터로 받아 업로드
- DB에는 파일명만 저장 (프론트/게이트웨이에서 CDN URL로 렌더)
"""
from __future__ import annotations

import hashlib
import os
import uuid
from typing import Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from src.config.settings import settings
from src.common.logging import get_logger_with_request_id


_s3_client = None


def get_s3_client():
    """S3 클라이언트 싱글톤"""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=BotoConfig(retries={"max_attempts": 3, "mode": "standard"}),
        )
    return _s3_client


def _safe_ext(filename: str) -> str:
    """안전한 파일 확장자 추출"""
    base, ext = os.path.splitext(filename or "")
    ext = (ext or "").lower().strip(".")
    if ext in {"jpg", "jpeg", "png", "gif", "webp"}:
        return "." + ext
    return ".png"


def _gen_filename(original_name: str, data_head: bytes | None = None) -> str:
    """고유한 파일명 생성 (UUID + 해시)"""
    hasher = hashlib.sha256()
    hasher.update(uuid.uuid4().hex.encode("utf-8"))
    if data_head:
        hasher.update(data_head)
    digest = hasher.hexdigest()
    return f"{digest}{_safe_ext(original_name)}"


def upload_public_image(*, subdirectory: str, content: bytes, original_name: str) -> str:
    """
    범용 이미지 업로드. 성공 시 저장된 파일명만 반환.
    - S3 Key: f"{settings.s3_directory}/{subdirectory}/{filename}"
    - Return: filename (예: "abcdef123.png")
    """
    log = get_logger_with_request_id()
    filename = _gen_filename(original_name, content[:64] if content else None)
    safe_subdir = (subdirectory or "").strip("/") or "misc"
    key = f"{settings.s3_directory.strip('/')}/{safe_subdir}/{filename}"

    try:
        client = get_s3_client()
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=content,
            ContentType=_guess_content_type(filename),
        )
        log.info("S3 upload success", key=key)
        return filename
    except (BotoCoreError, ClientError) as e:
        log.error("S3 upload failed", error=str(e))
        raise


def _guess_content_type(filename: str) -> str:
    """파일 확장자로 Content-Type 추정"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".gif":
        return "image/gif"
    if ext == ".webp":
        return "image/webp"
    return "application/octet-stream"
