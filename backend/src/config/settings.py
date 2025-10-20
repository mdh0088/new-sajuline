"""
애플리케이션 설정 관리
"""
import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경 변수 기반 설정"""
    
    # 애플리케이션 기본 설정
    environment: str = Field(..., env="ENVIRONMENT")
    debug: bool = Field(..., env="DEBUG")
    host: str = Field(..., env="HOST")
    port: int = Field(..., env="PORT")
    log_level: str = Field(..., env="LOG_LEVEL")
    
    # 보안 설정
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field(..., env="ALGORITHM")
    
    # CORS 설정
    cors_origins: str = Field(..., env="CORS_ORIGINS")
    frontend_url: str = Field(..., env="FRONTEND_URL")
    trusted_hosts: str = Field(..., env="TRUSTED_HOSTS")
    
    # MariaDB 설정 (Primary Database)
    mariadb_host: str = Field(..., env="MARIADB_HOST")
    mariadb_port: int = Field(..., env="MARIADB_PORT")
    mariadb_db: str = Field(..., env="MARIADB_DB")
    mariadb_user: str = Field(..., env="MARIADB_USER")
    mariadb_password: str = Field(..., env="MARIADB_PASSWORD")
    mariadb_charset: str = Field(..., env="MARIADB_CHARSET")
    mariadb_echo: bool = Field(..., env="MARIADB_ECHO")
    mariadb_pool_size: int = Field(..., env="MARIADB_POOL_SIZE")
    mariadb_max_overflow: int = Field(..., env="MARIADB_MAX_OVERFLOW")
    
    # MSSQL 설정 (ARS 연동)
    mssql_host: str = Field(..., env="MSSQL_HOST")
    mssql_port: int = Field(..., env="MSSQL_PORT")
    mssql_db: str = Field(..., env="MSSQL_DB")
    mssql_user: str = Field(..., env="MSSQL_USER")
    mssql_password: str = Field(..., env="MSSQL_PASSWORD")
    mssql_dev_driver: str = Field(..., env="MSSQL_DEV_DRIVER")
    mssql_prod_driver: str = Field(..., env="MSSQL_PROD_DRIVER")
    mssql_pool_size: int = Field(default=10, env="MSSQL_POOL_SIZE")
    mssql_max_overflow: int = Field(default=20, env="MSSQL_MAX_OVERFLOW")
    
    # Redis 설정
    redis_url: str = Field(..., env="REDIS_URL")
    redis_db: int = Field(..., env="REDIS_DB")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # AI 서비스 설정
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(..., env="OPENAI_MODEL")
    ai_cache_ttl: int = Field(..., env="AI_CACHE_TTL")
    
    # AWS S3 설정
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(..., env="AWS_REGION")
    s3_bucket_name: str = Field(..., env="S3_BUCKET_NAME")
    s3_directory: str = Field(..., env="S3_DIRECTORY")


    
    # 소셜 로그인 설정
    # Kakao OAuth
    kakao_client_id: str = Field(..., env="KAKAO_CLIENT_ID")
    kakao_auth_url: str = Field(..., env="KAKAO_AUTH_URL")
    kakao_token_url: str = Field(..., env="KAKAO_TOKEN_URL")
    kakao_user_info_url: str = Field(..., env="KAKAO_USER_INFO_URL")
    kakao_redirect_uri: str = Field(..., env="KAKAO_REDIRECT_URI")

    # Naver OAuth
    naver_client_id: str = Field(..., env="NAVER_CLIENT_ID")
    naver_client_secret: str = Field(..., env="NAVER_CLIENT_SECRET")
    naver_auth_url: str = Field(..., env="NAVER_AUTH_URL")
    naver_token_url: str = Field(..., env="NAVER_TOKEN_URL")
    naver_user_info_url: str = Field(..., env="NAVER_USER_INFO_URL")
    naver_redirect_uri: str = Field(..., env="NAVER_REDIRECT_URI")
    
    
    # 모니터링 설정
    sentry_dsn: str = Field(..., env="SENTRY_DSN")
    
    # 기능 플래그
    enable_ai_features: bool = Field(..., env="ENABLE_AI_FEATURES")
    enable_social_login: bool = Field(..., env="ENABLE_SOCIAL_LOGIN")
    enable_webhooks: bool = Field(..., env="ENABLE_WEBHOOKS")
    
    # Docker 환경
    docker_env: bool = Field(..., env="DOCKER_ENV")
    
    # KCP 설정
    kcp_base_dir: str = Field(..., env="KCP_BASE_DIR")
    kcp_test_mode: bool = Field(..., env="KCP_TEST_MODE")
    api_base_url: str = Field(..., env="API_BASE_URL")
    kcp_test_site_cd: str = Field(..., env="KCP_TEST_SITE_CD")
    kcp_test_enc_key: str = Field(..., env="KCP_TEST_ENC_KEY")
    kcp_web_siteid: str = Field(..., env="KCP_WEB_SITEID")
    kcp_prod_site_cd: Optional[str] = Field(None, env="KCP_PROD_SITE_CD")
    kcp_prod_enc_key: Optional[str] = Field(None, env="KCP_PROD_ENC_KEY")
    
    # 관리자 설정
    admin_email: str = Field(..., env="ADMIN_EMAIL")
    admin_password: str = Field(..., env="ADMIN_PASSWORD")
    
    # 로깅 설정
    log_json: bool = Field(..., env="LOG_JSON")
    log_to_stdout: bool = Field(..., env="LOG_TO_STDOUT")
    log_to_file: bool = Field(..., env="LOG_TO_FILE")
    service_name: str = Field(..., env="SERVICE_NAME")
    service_version: str = Field(..., env="SERVICE_VERSION")


    # payment 설정 (옵셔널로 완화: 서버 부팅시 ValidationError 방지, 사용시 검사)
    payment_gateway_url: Optional[str] = Field(None, env="PAYMENT_GATEWAY_URL")
    payment_gateway_key: Optional[str] = Field(None, env="PAYMENT_GATEWAY_KEY")
    payment_client_id: Optional[str] = Field(None, env="PAYMENT_CLIENT_ID")
    payment_naver_key: Optional[str] = Field(None, env="PAYMENT_NAVER_KEY")
    payment_naver_id: Optional[str] = Field(None, env="PAYMENT_NAVER_ID")
    payment_return_url: Optional[str] = Field(None, env="PAYMENT_RETURN_URL")
    payment_cancel_url: Optional[str] = Field(None, env="PAYMENT_CANCEL_URL")
    payment_callback_url: Optional[str] = Field(None, env="PAYMENT_CALLBACK_URL")
    payment_virtual_callback_url: Optional[str] = Field(None, env="PAYMENT_VIRTUAL_CALLBACK_URL")
    
    class Config:
        # 환경에 따라 자동으로 env 파일 선택
        env_file = ".env.development" if os.getenv("ENVIRONMENT", "development") == "development" else ".env.production"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins 문자열을 리스트로 변환"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def trusted_hosts_list(self) -> List[str]:
        """Trusted hosts 문자열을 리스트로 변환"""
        return [host.strip() for host in self.trusted_hosts.split(",")]
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment == "production"
    
    @property
    def mariadb_url(self) -> str:
        """MariaDB 연결 URL 생성"""
        # 기존: 시간대 설정 없음 (UTC로 저장)
        # return f"mysql+aiomysql://{self.mariadb_user}:{self.mariadb_password}@{self.mariadb_host}:{self.mariadb_port}/{self.mariadb_db}?charset={self.mariadb_charset}"
        
        # aiomysql에서는 time_zone 파라미터 직접 지원하지 않음 - SQLAlchemy engine에서 connect_args로 처리
        return f"mysql+aiomysql://{self.mariadb_user}:{self.mariadb_password}@{self.mariadb_host}:{self.mariadb_port}/{self.mariadb_db}?charset={self.mariadb_charset}"
    
    @property
    def redis_host(self) -> str:
        """Redis URL에서 host 추출"""
        # redis://redis:6379/0 -> redis
        if "://" in self.redis_url:
            host_port = self.redis_url.split("://")[1].split("/")[0]
            if ":" in host_port:
                return host_port.split(":")[0]
            return host_port
        return "localhost"  # fallback
    
    @property
    def redis_port(self) -> int:
        """Redis URL에서 port 추출"""  
        # redis://redis:6379/0 -> 6379
        if "://" in self.redis_url:
            host_port = self.redis_url.split("://")[1].split("/")[0]
            if ":" in host_port:
                return int(host_port.split(":")[1])
        return 6379  # default Redis port


# 전역 설정 인스턴스
settings = Settings()