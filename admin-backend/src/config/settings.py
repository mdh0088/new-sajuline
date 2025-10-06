"""
관리자 백엔드 애플리케이션 설정 관리
"""
import os
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경 변수 기반 관리자 설정"""

    # 애플리케이션 기본 설정
    app_name: str = Field(..., env="APP_NAME")
    app_version: str = Field(..., env="APP_VERSION")
    app_env: str = Field(..., env="APP_ENV")
    debug: bool = Field(..., env="DEBUG")
    port: int = Field(..., env="PORT")

    # 보안 설정
    secret_key: str = Field(..., env="SECRET_KEY")
    admin_secret_key: str = Field(..., env="ADMIN_SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(..., env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS 설정
    cors_origins: str = Field(..., env="CORS_ORIGINS")

    # MariaDB 설정 (Primary Database)
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(..., env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(..., env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(..., env="DATABASE_POOL_TIMEOUT")

    # MSSQL 설정 (외부 연동)
    mssql_server: str = Field(..., env="MSSQL_SERVER")
    mssql_port: int = Field(..., env="MSSQL_PORT")
    mssql_database: str = Field(..., env="MSSQL_DATABASE")
    mssql_username: str = Field(..., env="MSSQL_USERNAME")
    mssql_password: str = Field(..., env="MSSQL_PASSWORD")
    mssql_driver: str = Field(..., env="MSSQL_DRIVER")
    mssql_timeout: int = Field(..., env="MSSQL_TIMEOUT")

    # 로깅 설정
    log_level: str = Field(..., env="LOG_LEVEL")
    log_format: str = Field(..., env="LOG_FORMAT")
    log_file: str = Field(..., env="LOG_FILE")

    # Sentry (에러 추적)
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    sentry_environment: str = Field(..., env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(..., env="SENTRY_TRACES_SAMPLE_RATE")

    # AWS S3 (파일 저장)
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(..., env="AWS_REGION")
    s3_bucket_name: str = Field(..., env="S3_BUCKET_NAME")
    s3_directory: str = Field(..., env="S3_DIRECTORY")

    # 관리자 권한 설정
    admin_roles: str = Field(..., env="ADMIN_ROLES")
    super_admin_email: str = Field(..., env="SUPER_ADMIN_EMAIL")

    # 이중 인증 설정
    enable_2fa: bool = Field(..., env="ENABLE_2FA")
    otp_issuer: str = Field(..., env="OTP_ISSUER")

    # 감사 로그 설정
    enable_audit_log: bool = Field(..., env="ENABLE_AUDIT_LOG")
    audit_log_retention_days: int = Field(..., env="AUDIT_LOG_RETENTION_DAYS")

    # 백업 설정
    backup_enabled: bool = Field(..., env="BACKUP_ENABLED")
    backup_schedule: str = Field(..., env="BACKUP_SCHEDULE")
    backup_retention_days: int = Field(..., env="BACKUP_RETENTION_DAYS")

    # 세션 설정
    session_timeout_minutes: int = Field(..., env="SESSION_TIMEOUT_MINUTES")
    session_extend_on_activity: bool = Field(..., env="SESSION_EXTEND_ON_ACTIVITY")

    # API 문서 설정
    docs_url: str = Field(..., env="DOCS_URL")
    redoc_url: str = Field(..., env="REDOC_URL")
    openapi_url: str = Field(..., env="OPENAPI_URL")

    # 외부 서비스 API URL
    main_backend_url: str = Field(..., env="MAIN_BACKEND_URL")
    main_frontend_url: str = Field(..., env="MAIN_FRONTEND_URL")

    # 통계 및 분석
    enable_analytics: bool = Field(..., env="ENABLE_ANALYTICS")
    analytics_batch_size: int = Field(..., env="ANALYTICS_BATCH_SIZE")
    analytics_flush_interval: int = Field(..., env="ANALYTICS_FLUSH_INTERVAL")

    # 알림 설정
    slack_webhook_url: Optional[str] = Field(None, env="SLACK_WEBHOOK_URL")
    email_notification_enabled: bool = Field(..., env="EMAIL_NOTIFICATION_ENABLED")
    email_smtp_host: Optional[str] = Field(None, env="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(..., env="EMAIL_SMTP_PORT")
    email_smtp_user: Optional[str] = Field(None, env="EMAIL_SMTP_USER")
    email_smtp_password: Optional[str] = Field(None, env="EMAIL_SMTP_PASSWORD")
    email_from: str = Field(..., env="EMAIL_FROM")

    # 기타 설정
    timezone: str = Field(..., env="TIMEZONE")
    max_upload_size: int = Field(..., env="MAX_UPLOAD_SIZE")
    allowed_upload_extensions: str = Field(..., env="ALLOWED_UPLOAD_EXTENSIONS")
    pagination_default_limit: int = Field(..., env="PAGINATION_DEFAULT_LIMIT")
    pagination_max_limit: int = Field(..., env="PAGINATION_MAX_LIMIT")

    # 결제 설정
    payment_gateway_url: str = Field(..., env="PAYMENT_GATEWAY_URL")
    payment_gateway_key: str = Field(..., env="PAYMENT_GATEWAY_KEY")
    payment_client_id: str = Field(..., env="PAYMENT_CLIENT_ID")

    class Config:
        # 환경에 따라 자동으로 env 파일 선택
        env_file = ".env.development" if os.getenv("APP_ENV", "development") == "development" else ".env.production"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins 문자열을 리스트로 변환"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def admin_roles_list(self) -> List[str]:
        """관리자 권한 문자열을 리스트로 변환"""
        return [role.strip() for role in self.admin_roles.split(",")]

    @property
    def allowed_upload_extensions_list(self) -> List[str]:
        """허용된 업로드 확장자 문자열을 리스트로 변환"""
        return [ext.strip() for ext in self.allowed_upload_extensions.split(",")]

    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.app_env == "production"

    @property
    def mariadb_url(self) -> str:
        """MariaDB 연결 URL 생성"""
        # DATABASE_URL을 파싱하여 컴포넌트 추출
        parsed = urlparse(self.database_url)

        # 쿼리 파라미터 파싱
        query_params = parse_qs(parsed.query)
        charset = query_params.get('charset', ['utf8mb4'])[0]

        # MariaDB 연결 정보 추출
        mariadb_user = parsed.username or 'root'
        mariadb_password = parsed.password or ''
        mariadb_host = parsed.hostname or 'localhost'
        mariadb_port = parsed.port or 3306
        mariadb_db = parsed.path.lstrip('/') if parsed.path else 'sajuline_db'

        # 기존: 시간대 설정 없음 (UTC로 저장)
        # return f"mysql+aiomysql://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_db}?charset={charset}"

        # aiomysql에서는 time_zone 파라미터 직접 지원하지 않음 - SQLAlchemy engine에서 connect_args로 처리
        return f"mysql+aiomysql://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_db}?charset={charset}"


# 전역 설정 인스턴스
settings = Settings()