"""
KCP Configuration

KCP 인증 서비스 설정
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class KCPSettings(BaseSettings):
    """KCP 설정 (환경변수에서 로드)"""
    
    # 테스트/운영 모드
    KCP_TEST_MODE: bool = Field(True, description="테스트 모드 여부")
    
    # 테스트 환경 설정
    KCP_TEST_SITE_CD: str = Field(default=None, description="테스트 사이트 코드")
    KCP_TEST_ENC_KEY: str = Field(default=None, description="테스트 암호화 키")
    KCP_TEST_GATEWAY_URL: str = Field(
        "https://testcert.kcp.co.kr/kcp_cert/cert_view.jsp",
        description="테스트 게이트웨이 URL"
    )
    
    # 운영 환경 설정
    KCP_PROD_SITE_CD: str = Field(default=None, description="운영 사이트 코드")
    KCP_PROD_ENC_KEY: str = Field(default=None, description="운영 암호화 키")
    KCP_PROD_GATEWAY_URL: str = Field(
        "https://cert.kcp.co.kr/kcp_cert/cert_view.jsp",
        description="운영 게이트웨이 URL"
    )
    
    # 공통 설정
    KCP_WEB_SITEID: str = Field(default=None, description="웹사이트 ID")
    KCP_BASE_DIR: str = Field(
        "/app/kcp_binaries",  # Docker 환경 기본값
        description="KCP 바이너리 파일 기본 디렉토리"
    )
    KCP_RETURN_URL: str = Field(
        "https://www.sajuline.com/config/kcp/SMART_ENC/smartcert_proc_res.php",
        description="인증 결과 리턴 URL (운영 환경 기본값)"
    )
    KCP_CERT_OTP_USE: str = Field("Y", description="OTP 사용 여부")
    KCP_CERT_ENC_USE_EXT: str = Field("Y", description="암호화 고도화 사용")
    
    # 환경별 자동 선택
    @property
    def site_cd(self) -> str:
        """현재 환경의 사이트 코드"""
        return self.KCP_TEST_SITE_CD if self.KCP_TEST_MODE else self.KCP_PROD_SITE_CD
    
    @property
    def enc_key(self) -> str:
        """현재 환경의 암호화 키"""
        return self.KCP_TEST_ENC_KEY if self.KCP_TEST_MODE else self.KCP_PROD_ENC_KEY
    
    @property
    def gateway_url(self) -> str:
        """현재 환경의 게이트웨이 URL"""
        return self.KCP_TEST_GATEWAY_URL if self.KCP_TEST_MODE else self.KCP_PROD_GATEWAY_URL
    
    @property
    def return_url(self) -> str:
        """인증 결과 리턴 URL"""
        if self.KCP_TEST_MODE:
            # 테스트 환경에서는 로컬 API로 설정
            from src.common.config.settings import get_settings
            settings = get_settings()
            return f"{settings.API_BASE_URL}/phone-verification/callback"
        else:
            # 운영 환경에서는 기본값 사용
            return self.KCP_RETURN_URL
    
    @property
    def home_dir(self) -> str:
        """시스템 아키텍처에 맞는 KCP 바이너리 디렉토리"""
        import platform
        
        # 시스템 아키텍처 감지
        machine = platform.machine().lower()
        
        if machine in ['x86_64', 'amd64']:
            # 64bit 시스템
            arch_dir = "64bit"
        elif machine in ['i386', 'i686', 'x86']:
            # 32bit 시스템
            arch_dir = "32bit"
        else:
            # 기본값으로 64bit 사용
            arch_dir = "64bit"
        
        return os.path.join(self.KCP_BASE_DIR, arch_dir)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 싱글톤 인스턴스
kcp_settings = KCPSettings()


def get_kcp_configuration():
    """KCP 설정 객체 반환"""
    from ..domain.entities import KCPConfiguration
    
    return KCPConfiguration(
        site_cd=kcp_settings.site_cd,
        site_key=kcp_settings.enc_key,  # site_key는 실제로 암호화 키임
        web_siteid=kcp_settings.KCP_WEB_SITEID,
        gateway_url=kcp_settings.gateway_url,
        return_url=kcp_settings.return_url,
        home_dir=kcp_settings.home_dir,
        enc_key=kcp_settings.enc_key,
        cert_otp_use=kcp_settings.KCP_CERT_OTP_USE,
        cert_enc_use_ext=kcp_settings.KCP_CERT_ENC_USE_EXT,
        is_test_mode=kcp_settings.KCP_TEST_MODE
    )