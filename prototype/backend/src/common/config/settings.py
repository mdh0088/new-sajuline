"""
애플리케이션 설정 관리

환경변수 및 설정값 통합 관리
python-dotenv를 활용한 안전한 환경 파일 로드
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_environment_files():
    """
    환경별 .env 파일을 안전하게 로드
    
    Docker 환경과 로컬 환경 모두 지원
    여러 환경 파일의 우선순위 처리
    """
    # 현재 파일의 위치에서 프로젝트 루트 찾기
    current_file = Path(__file__)  # /app/src/common/config/settings.py
    project_root = current_file.parent.parent.parent.parent  # /app (Docker) 또는 backend/
    
    # 환경 설정
    env = os.getenv("ENVIRONMENT", "development")
    
    # 로드할 환경 파일 목록 (우선순위 순)
    env_files_to_try = [
        project_root / f".env.{env}",      # .env.development, .env.production
        project_root / ".env.local",       # 로컬 오버라이드 (gitignore)
        project_root / ".env",             # 기본 환경 파일
    ]
    
    loaded_files = []
    
    # 각 파일을 순서대로 시도하여 로드
    for env_file in env_files_to_try:
        if env_file.exists():
            try:
                # override=False로 설정하여 기존 환경 변수 보존
                load_dotenv(env_file, override=False)
                loaded_files.append(str(env_file.name))
            except Exception as e:
                # 파일 로드 실패 시 경고만 출력하고 계속 진행
                print(f"⚠️  Failed to load {env_file}: {e}")
    
    # 로드 결과 출력 (개발 환경에서만)
    if env == "development":
        if loaded_files:
            print(f"✅ Environment files loaded: {', '.join(loaded_files)}")
        else:
            # 파일이 없어도 기본값으로 작동하므로 치명적이지 않음
            print(f"⚠️  No environment files found in {project_root}")
            print("📝 Using default configuration values")


# 모듈 로드 시 환경 파일 로드 (한 번만 실행)
load_environment_files()


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정
    
    환경변수에서 설정값을 로드하고 기본값 제공
    개발/스테이징/프로덕션 환경별 설정 분리
    """
    
    model_config = SettingsConfigDict(
        # env_file 제거 - 이미 load_dotenv로 환경변수에 로드됨
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # 기본 애플리케이션 설정
    ENVIRONMENT: str = Field(default="development", description="실행 환경")
    DEBUG: bool = Field(default=True, description="디버그 모드")
    HOST: str = Field(default="0.0.0.0", description="서버 호스트")
    PORT: int = Field(default=8000, description="서버 포트")
    LOG_LEVEL: str = Field(default="INFO", description="로그 레벨")
    
    # 보안 설정
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 서명용 비밀키"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="액세스 토큰 만료 시간(분)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="리프레시 토큰 만료 시간(일)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT 서명 알고리즘"
    )
    
    # CORS 설정
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://frontend:3000",  # Docker 환경용
            "https://sajuline.com",
            "https://www.sajuline.com",
            "https://dev.sajuline.com"
        ],
        description="CORS 허용 도메인"
    )
    
    # 프론트엔드 URL (소셜 로그인 리다이렉트 URI 생성용)
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="프론트엔드 기본 URL (OAuth 리다이렉트 URI 생성용)"
    )
    
    # 신뢰할 수 있는 호스트
    TRUSTED_HOSTS: Optional[List[str]] = Field(
        default=None,
        description="신뢰할 수 있는 호스트 목록"
    )
    
    # 데이터베이스 설정 (MariaDB)
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://user:password@localhost:3306/sajuline?charset=utf8mb4",
        description="MariaDB 데이터베이스 URL"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="SQLAlchemy SQL 로그 출력"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=10,
        description="데이터베이스 연결 풀 크기"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=20,
        description="최대 오버플로우 연결 수"
    )

    # MSSQL 연결 설정 (dev/prod 분기용)
    MSSQL_HOST: str = Field(default="mssql-ars", description="MSSQL 호스트")
    MSSQL_PORT: int = Field(default=1433, description="MSSQL 포트")
    MSSQL_DB: str = Field(default="ars", description="MSSQL 데이터베이스명")
    MSSQL_USER: str = Field(default="sa", description="MSSQL 사용자")
    MSSQL_PASSWORD: Optional[str] = Field(default=None, description="MSSQL 비밀번호")
    MSSQL_DEV_DRIVER: str = Field(default="pymssql", description="개발용 MSSQL 드라이버 (pymssql|pyodbc)")
    MSSQL_PROD_DRIVER: str = Field(default="pymssql", description="운영용 MSSQL 드라이버 (pymssql|pyodbc)")
    
    # Redis 설정
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis 서버 URL"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis 데이터베이스 번호"
    )
    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="Redis 패스워드"
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50,
        description="Redis 최대 커넥션 수"
    )
    REDIS_SOCKET_TIMEOUT: int = Field(
        default=5,
        description="Redis 소켓 타임아웃(초)"
    )
    REDIS_CONNECT_TIMEOUT: int = Field(
        default=5,
        description="Redis 연결 타임아웃(초)"
    )
    
    
    # 파일 업로드 설정
    UPLOAD_MAX_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="최대 업로드 파일 크기(바이트)"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf", "txt"],
        description="허용되는 파일 확장자"
    )
    
    # AWS S3 설정
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS 액세스 키"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS 시크릿 키"
    )
    AWS_REGION: str = Field(
        default="ap-northeast-2",
        description="AWS 리전"
    )
    S3_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="S3 버킷 이름"
    )
    AWS_S3_ENDPOINT_URL: Optional[str] = Field(
        default=None,
        description="S3 호환 엔드포인트 URL"
    )
    AWS_S3_SIGNATURE_VERSION: Optional[str] = Field(
        default=None,
        description="S3 서명 버전"
    )
    AWS_S3_MAX_RETRIES: int = Field(
        default=3,
        description="S3 최대 재시도 횟수"
    )
    AWS_S3_TIMEOUT: int = Field(
        default=30,
        description="S3 요청 타임아웃(초)"
    )
    
    # 소셜 로그인 설정
    KAKAO_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="카카오 클라이언트 ID"
    )
    KAKAO_AUTH_URL: str = Field(
        default="https://kauth.kakao.com/oauth/authorize",
        description="카카오 인증 URL"
    )
    KAKAO_TOKEN_URL: str = Field(
        default="https://kauth.kakao.com/oauth/token",
        description="카카오 토큰 URL"
    )
    KAKAO_USER_INFO_URL: str = Field(
        default="https://kapi.kakao.com/v2/user/me",
        description="카카오 사용자 정보 URL"
    )
    KAKAO_LOGOUT_URL: str = Field(
        default="https://kapi.kakao.com/v1/user/logout",
        description="카카오 로그아웃 URL"
    )
    
    NAVER_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="네이버 클라이언트 ID"
    )
    NAVER_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="네이버 클라이언트 시크릿"
    )
    NAVER_AUTH_URL: str = Field(
        default="https://nid.naver.com/oauth2.0/authorize",
        description="네이버 인증 URL"
    )
    NAVER_TOKEN_URL: str = Field(
        default="https://nid.naver.com/oauth2.0/token",
        description="네이버 토큰 URL"
    )
    NAVER_USER_INFO_URL: str = Field(
        default="https://openapi.naver.com/v1/nid/me",
        description="네이버 사용자 정보 URL"
    )
    
    # PG사 연동 설정
    PAYMENT_GATEWAY_URL: Optional[str] = Field(
        default=None,
        description="결제 게이트웨이 URL"
    )
    PAYMENT_GATEWAY_KEY: Optional[str] = Field(
        default=None,
        description="결제 게이트웨이 API 키"
    )
    
    # 모니터링 설정
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN"
    )
    
    # 레이트 리미터 설정
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="레이트 리미터 활성화"
    )
    RATE_LIMIT_CALLS: int = Field(
        default=100,
        description="레이트 리미터 호출 횟수"
    )
    RATE_LIMIT_PERIOD: int = Field(
        default=60,
        description="레이트 리미터 기간(초)"
    )
    
    # Docker 환경 설정
    DOCKER_ENV: bool = Field(
        default=False,
        description="Docker 환경 여부"
    )
    
    # 로깅 설정
    LOG_TO_STDOUT: bool = Field(
        default=True,
        description="로그를 stdout으로 출력"
    )
    LOG_TO_FILE: bool = Field(
        default=False,
        description="로그를 파일로 저장"
    )
    LOG_DIR: str = Field(
        default="/var/log/app" if os.name != "nt" else "C:/var/log/app",
        description="로그 파일 디렉토리"
    )
    LOG_FILE_NAME: str = Field(
        default="app.log",
        description="로그 파일 이름"
    )
    LOG_RETENTION_DAYS: int = Field(
        default=7,
        description="로그 파일 보관 일수"
    )
    LOG_JSON: bool = Field(
        default=False,
        description="JSON 포맷 로깅 사용"
    )
    SERVICE_NAME: str = Field(
        default="sajuline-api",
        description="서비스 이름"
    )
    SERVICE_VERSION: str = Field(
        default="1.0.0",
        description="서비스 버전"
    )
    
    # 외부 서비스 URL
    API_BASE_URL: str = Field(
        default="http://localhost:8000",
        description="API 베이스 URL"
    )
    EMAIL_SERVICE_URL: Optional[str] = Field(
        default=None,
        description="이메일 서비스 URL"
    )
    SMS_SERVICE_URL: Optional[str] = Field(
        default=None,
        description="SMS 서비스 URL"
    )
    WEBHOOK_BASE_URL: Optional[str] = Field(
        default=None,
        description="웹훅 기본 URL"
    )
    
    # 암호화 설정
    ENCRYPTION_KEY: Optional[str] = Field(
        default=None,
        description="데이터 암호화 키"
    )
    DATA_ENCRYPTION_ENABLED: bool = Field(
        default=False,
        description="데이터 암호화 활성화"
    )
    
    # 기능 플래그
    ENABLE_AI_FEATURES: bool = Field(
        default=True,
        description="AI 기능 활성화"
    )
    # OpenAI/AI 설정
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API Key"
    )
    OPENAI_BASE_URL: Optional[str] = Field(
        default=None,
        description="OpenAI Base URL"
    )
    OPENAI_ORG: Optional[str] = Field(
        default=None,
        description="OpenAI Organization ID"
    )
    ENABLE_SOCIAL_LOGIN: bool = Field(
        default=True,
        description="소셜 로그인 활성화"
    )
    ENABLE_WEBHOOKS: bool = Field(
        default=False,
        description="웹훅 활성화"
    )
    
    # 관리자 설정
    ADMIN_EMAIL: Optional[str] = Field(
        default=None,
        description="관리자 이메일"
    )
    ADMIN_PASSWORD: Optional[str] = Field(
        default=None,
        description="관리자 비밀번호"
    )
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """환경 설정 검증"""
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_envs}")
        return v
    
    @validator("DEBUG")
    def validate_debug_mode(cls, v, values):
        """디버그 모드 검증 - 프로덕션에서는 반드시 False여야 함"""
        env = values.get("ENVIRONMENT", "development")
        if env == "production" and v is True:
            raise ValueError("DEBUG must be False in production environment for security reasons")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """시크릿 키 검증"""
        env = values.get("ENVIRONMENT", "development")
        default_keys = [
            "your-secret-key-change-in-production",
            "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR",
            "MUST_SET_FROM_ENV_VAR_IN_PRODUCTION",
            "MUST_OVERRIDE_IN_ENV_LOCAL_FILE",
            "GENERATE_WITH_OPENSSL_RAND_HEX_32"
        ]
        
        # 프로덕션 환경에서 기본 키 사용 시 에러
        if env == "production" and v in default_keys:
            raise ValueError("SECRET_KEY must be changed in production environment")
        
        # 개발 환경에서도 기본 키 사용 시 경고
        if env == "development" and v in default_keys:
            import warnings
            warnings.warn(
                "Using default SECRET_KEY in development. "
                "Consider generating a secure key with: openssl rand -hex 32",
                UserWarning
            )
        
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v, values):
        """데이터베이스 URL 검증"""
        env = values.get("ENVIRONMENT", "development")
        default_urls = [
            "MUST_SET_FROM_ENV_VAR_IN_PRODUCTION",
            "CHANGE_THIS_PASSWORD"
        ]
        if env == "production":
            if "localhost" in v:
                raise ValueError("DATABASE_URL should not use localhost in production")
            for default in default_urls:
                if default in v:
                    raise ValueError("DATABASE_URL must be properly configured in production")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        """CORS origins 검증 및 파싱"""
        if isinstance(v, str):
            # 쉼표로 구분된 문자열을 리스트로 변환
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            # 기본값 반환
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "https://sajuline.com",
                "https://www.sajuline.com",
                "https://dev.sajuline.com"
            ]
    
    @validator("TRUSTED_HOSTS", pre=True)
    def validate_trusted_hosts(cls, v):
        """신뢰할 수 있는 호스트 검증 및 파싱"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        elif isinstance(v, list):
            return v
        else:
            return None
    
    def validate_required_settings(self) -> None:
        """
        필수 설정값 검증
        
        애플리케이션 시작 시 호출하여 필수 환경 변수가 설정되었는지 확인
        
        Raises:
            ValueError: 필수 설정값이 누락된 경우
        """
        required_fields = []
        
        # 프로덕션 환경에서만 필수인 설정들
        if self.is_production:
            # 보안 관련 필수 설정
            if self.SECRET_KEY == "your-secret-key-change-in-production" or not self.SECRET_KEY:
                required_fields.append("SECRET_KEY (강력한 랜덤 키)")
            
            # 데이터베이스
            if "localhost" in self.DATABASE_URL:
                required_fields.append("DATABASE_URL (프로덕션 데이터베이스)")
            
            # MSSQL 비밀번호
            if not self.MSSQL_PASSWORD:
                required_fields.append("MSSQL_PASSWORD")
            
            # 관리자 계정
            if not self.ADMIN_EMAIL:
                required_fields.append("ADMIN_EMAIL")
            if not self.ADMIN_PASSWORD or len(self.ADMIN_PASSWORD) < 12:
                required_fields.append("ADMIN_PASSWORD (최소 12자 이상)")
            
            # 소셜 로그인 API 키
            if not self.KAKAO_CLIENT_ID:
                required_fields.append("KAKAO_CLIENT_ID")
            if not self.NAVER_CLIENT_ID:
                required_fields.append("NAVER_CLIENT_ID")
            if not self.NAVER_CLIENT_SECRET:
                required_fields.append("NAVER_CLIENT_SECRET")
            
            # KCP 운영 키 (KCP_TEST_MODE가 False인 경우)
            if not self.KCP_TEST_MODE:
                if not os.getenv("KCP_PROD_SITE_CD"):
                    required_fields.append("KCP_PROD_SITE_CD")
                if not os.getenv("KCP_PROD_ENC_KEY"):
                    required_fields.append("KCP_PROD_ENC_KEY")
                if not os.getenv("KCP_WEB_SITEID"):
                    required_fields.append("KCP_WEB_SITEID")
        
        # 모든 환경에서 필수인 설정들
        if not self.DATABASE_URL or self.DATABASE_URL == "mysql+aiomysql://user:password@localhost:3306/sajuline?charset=utf8mb4":
            if self.ENVIRONMENT != "development":
                required_fields.append("DATABASE_URL")
        
        if required_fields:
            raise ValueError(
                f"Missing or invalid required environment variables for {self.ENVIRONMENT} environment: "
                f"{', '.join(required_fields)}"
            )
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_docker_environment(self) -> bool:
        """Docker 환경 여부"""
        return self.DOCKER_ENV
    
    @property
    def database_url_sync(self) -> str:
        """동기 데이터베이스 URL (Alembic용)"""
        # MariaDB/MySQL의 경우 aiomysql을 pymysql로 변경
        if "aiomysql" in self.DATABASE_URL:
            return self.DATABASE_URL.replace("+aiomysql", "+pymysql")
        # 기타 드라이버의 경우 그대로 반환
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """
    설정 인스턴스 반환 (캐시됨)
    
    Returns:
        Settings: 애플리케이션 설정 인스턴스
    """
    settings = Settings()
    
    # 애플리케이션 시작 시 필수 설정값 검증
    try:
        settings.validate_required_settings()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        if settings.is_production:
            # 프로덕션에서는 에러 발생 시 종료
            raise
        else:
            # 개발 환경에서는 경고만 출력
            print("⚠️  Using default values for development")
    
    return settings 