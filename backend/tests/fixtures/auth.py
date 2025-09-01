"""
인증 관련 테스트 데이터 픽스처

JWT 토큰, 인증 헤더, 인증 관련 테스트 데이터를 제공합니다.
"""
import pytest
from datetime import datetime, timedelta
from src.schemas.auth_schema import LoginData


@pytest.fixture
def valid_jwt_payload():
    """유효한 JWT 페이로드"""
    return {
        "sub": "test_user_001",
        "email": "testuser@example.com",
        "role": "user",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "jti": "test-jwt-id-123"
    }


@pytest.fixture
def expired_jwt_payload():
    """만료된 JWT 페이로드"""
    return {
        "sub": "test_user_001", 
        "email": "testuser@example.com",
        "role": "user",
        "exp": datetime.utcnow() - timedelta(minutes=1),  # 1분 전 만료
        "iat": datetime.utcnow() - timedelta(minutes=31),
        "jti": "expired-jwt-id-456"
    }


@pytest.fixture
def invalid_jwt_payload():
    """무효한 JWT 페이로드 (필수 필드 누락)"""
    return {
        # sub 필드 누락
        "email": "testuser@example.com",
        "role": "user",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow()
    }


@pytest.fixture
def test_access_token():
    """테스트용 액세스 토큰"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


@pytest.fixture
def test_auth_headers(test_access_token):
    """인증 헤더"""
    return {
        "Authorization": f"Bearer {test_access_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_cookies(test_access_token):
    """테스트용 HttpOnly 쿠키"""
    return {
        "access_token": test_access_token
    }


@pytest.fixture
def login_response_data():
    """로그인 응답 데이터"""
    return LoginData(
        user_id="test_user_001",
        email="testuser@example.com",
        nickname="테스트유저"
    )


@pytest.fixture
def password_hash():
    """해시된 비밀번호"""
    return "$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi"


@pytest.fixture
def wrong_password_hash():
    """잘못된 비밀번호 해시"""
    return "$2y$10$WRONG.HASH.VALUE.FOR.TESTING.PURPOSES.ONLY"


@pytest.fixture
def auth_test_scenarios():
    """다양한 인증 테스트 시나리오"""
    return {
        "valid_login": {
            "user_id": "valid_user",
            "password": "ValidPassword123!",
            "expected_success": True
        },
        "invalid_password": {
            "user_id": "valid_user", 
            "password": "WrongPassword",
            "expected_success": False,
            "expected_error": "비밀번호가 일치하지 않습니다"
        },
        "nonexistent_user": {
            "user_id": "nonexistent_user",
            "password": "AnyPassword",
            "expected_success": False,
            "expected_error": "사용자를 찾을 수 없습니다"
        },
        "inactive_user": {
            "user_id": "inactive_user",
            "password": "ValidPassword123!",
            "expected_success": False,
            "expected_error": "비활성화된 계정입니다"
        }
    }


@pytest.fixture
def token_verification_scenarios():
    """토큰 검증 테스트 시나리오"""
    return {
        "valid_token": {
            "token": "valid.jwt.token",
            "expected_success": True
        },
        "expired_token": {
            "token": "expired.jwt.token",
            "expected_success": False,
            "expected_error": "토큰이 만료되었습니다"
        },
        "invalid_token": {
            "token": "invalid.jwt.token",
            "expected_success": False,
            "expected_error": "토큰이 유효하지 않습니다"
        },
        "malformed_token": {
            "token": "malformed_token",
            "expected_success": False,
            "expected_error": "토큰 형식이 올바르지 않습니다"
        }
    }