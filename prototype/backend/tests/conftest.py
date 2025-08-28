"""
Pytest Configuration and Fixtures

테스트 설정 및 픽스처
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi import FastAPI

from src.common.database.base import Base
from src.main import app
from src.phone_verification.domain.entities import (
    PhoneVerificationRequest,
    KCPConfiguration,
    VerificationStatus
)
from src.phone_verification.domain.models import PhoneVerification
from src.phone_verification.infrastructure.kcp_config import get_kcp_configuration


# 테스트 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """전체 테스트 세션용 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """테스트용 SQLAlchemy 엔진"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """테스트용 데이터베이스 세션"""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """테스트용 HTTP 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_kcp_config() -> KCPConfiguration:
    """테스트용 KCP 설정"""
    return KCPConfiguration(
        site_cd="S6186",  # 테스트 사이트 코드
        site_key="E66DCEB95BFBD45DF9DFAEEBCB092B5DC2EB3BF0",  # 테스트 암호화 키
        web_siteid="SITESKIN01",
        gateway_url="https://testcert.kcp.co.kr/kcp_cert/cert_view.jsp",
        return_url="http://localhost:8000/api/v1/phone-verification/callback",
        home_dir="/opt/kcp/cert",
        enc_key="E66DCEB95BFBD45DF9DFAEEBCB092B5DC2EB3BF0",  # 테스트 암호화 키
        cert_otp_use="Y",
        cert_enc_use_ext="Y",
        is_test_mode=True
    )


@pytest.fixture
def valid_phone_request() -> PhoneVerificationRequest:
    """유효한 핸드폰 인증 요청"""
    return PhoneVerificationRequest(
        phone_number="01012345678",
        user_name="홍길동",
        birth_date="19900101",
        carrier="SKT",
        gender="M",
        local_code="01",
        verification_method="sms"
    )


@pytest.fixture
def invalid_phone_request() -> PhoneVerificationRequest:
    """무효한 핸드폰 인증 요청"""
    return PhoneVerificationRequest(
        phone_number="012345",  # 잘못된 형식
        user_name="",
        birth_date="invalid",
        carrier="UNKNOWN",
        gender="X",
        local_code="99",
        verification_method="invalid"
    )


@pytest.fixture
def test_verification_session() -> PhoneVerification:
    """테스트용 인증 세션"""
    return PhoneVerification(
        session_id="TEST_SESSION_001",
        user_id="test_user_001",
        status=VerificationStatus.PENDING,
        user_name="홍길동",
        birth_date="19900101",
        phone_number="01012345678",
        carrier="SKT",
        gender="M",
        local_code="01",
        verification_method="sms",
        up_hash="TEST_UP_HASH",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )


@pytest.fixture
def completed_verification() -> PhoneVerification:
    """완료된 인증 세션"""
    verification = PhoneVerification(
        session_id="TEST_SESSION_COMPLETED",
        user_id="test_user_002",
        status=VerificationStatus.COMPLETED,
        user_name="홍길동",
        birth_date="19900101",
        phone_number="01012345678",
        carrier="SKT",
        gender="M",
        local_code="01",
        verification_method="sms",
        up_hash="TEST_UP_HASH",
        # 인증 완료 데이터
        cert_no="TEST_CERT_001",
        comm_id="SKT",
        phone_no="01012345678",
        verified_name="홍길동",
        verified_birth="19900101",
        sex_code="1",
        ci="TEST_CI_HASH",
        di="TEST_DI_HASH",
        res_cd="0000",
        res_msg="정상처리",
        verified_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    return verification


@pytest.fixture
def expired_verification() -> PhoneVerification:
    """만료된 인증 세션"""
    return PhoneVerification(
        session_id="TEST_SESSION_EXPIRED",
        user_id="test_user_003",
        status=VerificationStatus.PENDING,
        user_name="홍길동",
        birth_date="19900101",
        phone_number="01012345678",
        carrier="SKT",
        gender="M",
        local_code="01",
        verification_method="sms",
        up_hash="TEST_UP_HASH",
        expires_at=datetime.utcnow() - timedelta(minutes=1)  # 1분 전 만료
    )


@pytest.fixture
def test_callback_data():
    """테스트용 KCP 콜백 데이터"""
    return {
        "site_cd": "S6186",
        "ordr_idxx": "TEST_SESSION_001",
        "cert_no": "TEST_CERT_001",
        "enc_cert_data2": "TEST_ENCRYPTED_DATA",
        "dn_hash": "TEST_DN_HASH",
        "res_cd": "0000",
        "res_msg": "정상처리"
    }


@pytest.fixture
def failed_callback_data():
    """실패한 KCP 콜백 데이터"""
    return {
        "site_cd": "S6186",
        "ordr_idxx": "TEST_SESSION_001",
        "cert_no": "TEST_CERT_001",
        "enc_cert_data2": "TEST_ENCRYPTED_DATA",
        "dn_hash": "TEST_DN_HASH",
        "res_cd": "9999",
        "res_msg": "인증 실패"
    }


# 마크 정의
pytestmark = [
    pytest.mark.asyncio,
]