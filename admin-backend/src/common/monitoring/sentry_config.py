"""
Sentry 설정 및 초기화 모듈

현재 프로젝트 아키텍처에 최적화된 Sentry 통합:
- 환경별 설정 (개발/프로덕션)
- FastAPI + SQLAlchemy 통합 (Redis 제외)
- 민감 정보 필터링
- 성능 모니터링
"""

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from typing import Optional, Dict, Any

from src.config.settings import settings


def initialize_sentry() -> None:
    """
    Sentry 초기화 및 설정

    FastAPI 앱 생성 전에 호출되어야 함
    환경 변수 SENTRY_DSN이 설정되지 않은 경우 초기화하지 않음
    """
    if not settings.sentry_dsn or settings.sentry_dsn == "CHANGE_THIS_USE_ENV_VAR":
        print("⚠️ Sentry DSN이 설정되지 않았습니다. 모니터링이 비활성화됩니다.")
        return

    try:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            debug=settings.debug,

            # 통합 설정 - FastAPI 기반 프로젝트에 최적화
            integrations=[
                StarletteIntegration(
                    transaction_style="endpoint",
                ),
                FastApiIntegration(
                    transaction_style="endpoint",
                ),
                SqlalchemyIntegration(),  # MariaDB/MSSQL 쿼리 추적
            ],

            # 성능 모니터링 설정 (환경별 샘플링)
            traces_sample_rate=1.0 if settings.is_development else 0.1,

            # 데이터 보안 설정
            send_default_pii=False,  # 개인정보 제외

            # 릴리스 정보 (버전 추적)
            release=f"{settings.app_name}@{settings.app_version}",

            # 민감한 데이터 필터링
            before_send=filter_sensitive_data,
        )

        # 전역 태그 설정 (초기화 후 설정)
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("service", settings.app_name)
            scope.set_tag("environment", settings.sentry_environment)
            scope.set_tag("version", settings.app_version)

        # 초기화 성공 로그
        print(f"✅ Sentry 초기화 완료 - 환경: {settings.sentry_environment}, 릴리스: {settings.app_name}@{settings.app_version}")

    except Exception as e:
        print(f"❌ Sentry 초기화 실패: {e}")
        # Sentry 초기화 실패해도 앱 시작은 계속 진행


def filter_sensitive_data(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    민감한 데이터 필터링 함수

    비밀번호, 토큰, 암호화 키 등 민감한 정보를 자동으로 마스킹
    """
    # 민감한 키워드 목록
    sensitive_keys = {
        'password', 'passwd', 'pwd',
        'token', 'access_token', 'refresh_token', 'jwt',
        'secret', 'key', 'api_key',
        'authorization', 'auth',
        'ssn', 'social_security_number',
        'credit_card', 'card_number',
    }

    def mask_sensitive_value(obj: Any, key: str) -> Any:
        """민감한 값을 마스킹"""
        if isinstance(obj, dict):
            return {
                k: mask_sensitive_value(v, k) if k.lower() not in sensitive_keys else '[Filtered]'
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [mask_sensitive_value(item, key) for item in obj]
        else:
            return '[Filtered]' if key.lower() in sensitive_keys else obj

    try:
        # 요청 데이터 필터링
        if 'request' in event:
            if 'data' in event['request']:
                event['request']['data'] = mask_sensitive_value(event['request']['data'], 'data')

            # 헤더에서 Authorization 등 필터링
            if 'headers' in event['request']:
                headers = event['request']['headers']
                for key in list(headers.keys()):
                    if key.lower() in {'authorization', 'cookie', 'x-api-key'}:
                        headers[key] = '[Filtered]'

        # 추가 컨텍스트 데이터 필터링
        if 'extra' in event:
            event['extra'] = mask_sensitive_value(event['extra'], 'extra')

        return event

    except Exception as e:
        # 필터링 실패해도 이벤트는 전송
        print(f"⚠️ Sentry 데이터 필터링 오류: {e}")
        return event


def capture_custom_event(
    message: str,
    level: str = "info",
    extra: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
    user: Optional[Dict[str, Any]] = None
) -> None:
    """
    커스텀 이벤트 전송 헬퍼 함수

    Args:
        message: 이벤트 메시지
        level: 로그 레벨 (debug, info, warning, error, fatal)
        extra: 추가 컨텍스트 정보
        tags: 태그 정보
        user: 사용자 정보
    """
    if not sentry_sdk.Hub.current.client:
        return

    with sentry_sdk.configure_scope() as scope:
        # 사용자 컨텍스트 설정
        if user:
            scope.user = user

        # 태그 설정
        if tags:
            for key, value in tags.items():
                scope.set_tag(key, value)

        # 추가 컨텍스트 설정
        if extra:
            for key, value in extra.items():
                scope.set_context(key, value)

        # 이벤트 전송
        sentry_sdk.capture_message(message, level)


def capture_business_exception(
    message: str,
    exception_type: str,
    user_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    비즈니스 로직 예외 전송 헬퍼

    사용자 액션으로 인한 예외 (결제 실패, 권한 없음 등)를 추적
    """
    capture_custom_event(
        message=message,
        level="warning",
        extra={
            "exception_type": exception_type,
            "business_logic": True,
            **(extra_context or {})
        },
        user={"id": user_id} if user_id else None,
        tags={
            "category": "business_exception",
            "type": exception_type
        }
    )