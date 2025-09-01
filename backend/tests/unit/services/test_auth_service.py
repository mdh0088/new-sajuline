"""
인증 서비스 단위 테스트

AuthService의 비밀번호 해싱, JWT 토큰 생성/검증 등의 기능을 테스트합니다.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.auth_service import AuthService
from src.exceptions.custom_exceptions import AuthenticationError, ValidationError
from tests.fixtures.auth import *  # 인증 테스트 데이터 임포트


@pytest.mark.unit
class TestAuthService:
    """인증 서비스 단위 테스트 클래스"""

    @pytest.fixture
    def auth_service(self):
        """AuthService 인스턴스 픽스처"""
        return AuthService()

    def test_hash_password_success(self, auth_service):
        """비밀번호 해싱 성공 테스트"""
        # Given
        plain_password = "SecurePassword123!"
        
        # When
        hashed = auth_service.hash_password(plain_password)
        
        # Then
        assert hashed is not None
        assert hashed != plain_password
        assert len(hashed) > 50  # bcrypt 해시는 일반적으로 60자
        assert hashed.startswith("$2y$")  # PHP 호환 bcrypt 식별자

    def test_hash_password_error_test_trigger(self, auth_service):
        """비밀번호 해싱 에러 테스트 (테스트용 트리거)"""
        # Given
        test_password = "password_hash_error_test"
        
        # When & Then
        with pytest.raises(ValidationError, match="Auth service layer: 비밀번호 해싱 처리 실패 테스트"):
            auth_service.hash_password(test_password)

    def test_verify_password_success(self, auth_service, password_hash):
        """비밀번호 검증 성공 테스트"""
        # Given
        plain_password = "secret"
        # bcrypt로 실제 해시 생성해서 테스트
        hashed_password = auth_service.hash_password(plain_password)
        
        # When
        result = auth_service.verify_password(plain_password, hashed_password)
        
        # Then
        assert result is True

    def test_verify_password_failure(self, auth_service, password_hash):
        """비밀번호 검증 실패 테스트"""
        # Given
        wrong_password = "wrong_password"
        correct_hash = auth_service.hash_password("correct_password")
        
        # When
        result = auth_service.verify_password(wrong_password, correct_hash)
        
        # Then
        assert result is False

    def test_verify_password_error_test_trigger(self, auth_service):
        """비밀번호 검증 에러 테스트 (테스트용 트리거)"""
        # Given
        test_password = "password_verify_error_test"
        any_hash = "$2y$10$test.hash"
        
        # When & Then
        with pytest.raises(ValidationError, match="Auth service layer: 비밀번호 검증 처리 실패 테스트"):
            auth_service.verify_password(test_password, any_hash)

    def test_create_access_token_success(self, auth_service):
        """JWT 액세스 토큰 생성 성공 테스트"""
        # Given
        user_id = "test_user"
        email = "test@example.com"
        role = "user"
        
        # When
        token = auth_service.create_access_token(user_id, email, role)
        
        # Then
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT는 header.payload.signature 형태

    def test_create_access_token_with_default_role(self, auth_service):
        """기본 역할로 JWT 토큰 생성 테스트"""
        # Given
        user_id = "test_user"
        email = "test@example.com"
        
        # When (role 파라미터 생략)
        token = auth_service.create_access_token(user_id, email)
        
        # Then
        assert token is not None
        # 토큰을 디코딩해서 기본 role이 "user"인지 확인
        payload = auth_service.verify_token(token)
        assert payload["role"] == "user"

    def test_create_access_token_error_test_trigger(self, auth_service):
        """토큰 생성 에러 테스트 (테스트용 트리거)"""
        # Given
        test_user_id = "token_create_error_test"
        email = "test@example.com"
        
        # When & Then
        with pytest.raises(ValidationError, match="Auth service layer: JWT 토큰 생성 실패 테스트"):
            auth_service.create_access_token(test_user_id, email)

    def test_verify_token_success(self, auth_service, valid_jwt_payload):
        """JWT 토큰 검증 성공 테스트"""
        # Given
        user_id = valid_jwt_payload["sub"]
        email = valid_jwt_payload["email"]
        role = valid_jwt_payload["role"]
        
        # 실제 토큰 생성
        token = auth_service.create_access_token(user_id, email, role)
        
        # When
        payload = auth_service.verify_token(token)
        
        # Then
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["role"] == role
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_verify_token_invalid_format(self, auth_service):
        """잘못된 형식의 토큰 검증 테스트"""
        # Given
        invalid_token = "invalid.token.format"
        
        # When & Then
        with pytest.raises(AuthenticationError, match="토큰이 유효하지 않습니다"):
            auth_service.verify_token(invalid_token)

    def test_verify_token_expired(self, auth_service):
        """만료된 토큰 검증 테스트"""
        # Given - 만료 시간을 과거로 설정해서 토큰 생성
        with patch('src.services.auth_service.datetime') as mock_datetime:
            # 과거 시간으로 설정
            past_time = datetime.utcnow() - timedelta(hours=1)
            mock_datetime.utcnow.return_value = past_time
            
            expired_token = auth_service.create_access_token("test_user", "test@example.com")
        
        # When & Then
        with pytest.raises(AuthenticationError, match="토큰이 유효하지 않습니다"):
            auth_service.verify_token(expired_token)

    def test_verify_token_missing_required_fields(self, auth_service):
        """필수 필드가 누락된 토큰 검증 테스트"""
        # Given - sub 필드가 없는 토큰을 직접 생성 (jose를 사용해서)
        from jose import jwt
        
        invalid_payload = {
            # "sub" 필드 누락
            "email": "test@example.com",
            "role": "user",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        }
        
        invalid_token = jwt.encode(invalid_payload, auth_service.secret_key, algorithm=auth_service.algorithm)
        
        # When & Then
        with pytest.raises(AuthenticationError, match="토큰이 유효하지 않습니다"):
            auth_service.verify_token(invalid_token)

    def test_verify_token_error_test_trigger(self, auth_service):
        """토큰 검증 에러 테스트 (테스트용 트리거)"""
        # Given
        test_token = "auth_service_error_test"
        
        # When & Then
        with pytest.raises(AuthenticationError, match="Auth service layer: JWT 토큰 검증 실패 테스트"):
            auth_service.verify_token(test_token)

    def test_password_hashing_and_verification_integration(self, auth_service):
        """비밀번호 해싱과 검증 통합 테스트"""
        # Given
        original_password = "MySecurePassword123!"
        
        # When
        hashed = auth_service.hash_password(original_password)
        is_valid = auth_service.verify_password(original_password, hashed)
        is_invalid = auth_service.verify_password("WrongPassword", hashed)
        
        # Then
        assert is_valid is True
        assert is_invalid is False

    def test_token_creation_and_verification_integration(self, auth_service):
        """토큰 생성과 검증 통합 테스트"""
        # Given
        user_id = "integration_test_user"
        email = "integration@example.com"
        role = "admin"
        
        # When
        token = auth_service.create_access_token(user_id, email, role)
        payload = auth_service.verify_token(token)
        
        # Then
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["role"] == role