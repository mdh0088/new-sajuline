"""
사용자 서비스 단위 테스트

UserService의 비즈니스 로직을 검증합니다.
외부 의존성(Repository, Auth Service)은 Mock으로 처리하여 순수한 비즈니스 로직만 테스트합니다.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.services.user_service import UserService
from src.exceptions.custom_exceptions import ValidationError, NotFoundError
from src.schemas.user_schema import UserResponse
from tests.fixtures.users import *  # 사용자 테스트 데이터 임포트


@pytest.mark.unit
class TestUserService:
    """사용자 서비스 단위 테스트 클래스"""

    @pytest.fixture
    def user_service(self, mock_user_repository, mock_auth_service):
        """UserService 인스턴스 픽스처"""
        return UserService(mock_user_repository, mock_auth_service)

    async def test_create_user_success(self, user_service, valid_user_create_data, mock_user_response):
        """사용자 생성 성공 테스트"""
        # Given
        user_service.user_repository.exists_by_email = AsyncMock(return_value=False)
        user_service.user_repository.exists_by_user_id = AsyncMock(return_value=False)
        user_service.user_repository.create = AsyncMock(return_value=mock_user_response)
        user_service.auth_service.hash_password = Mock(return_value="hashed_password")
        
        # When
        result = await user_service.create_user(valid_user_create_data)
        
        # Then
        assert result.email == valid_user_create_data.email
        assert result.nickname == valid_user_create_data.nickname
        assert result.user_id == valid_user_create_data.user_id
        
        # Mock 호출 검증
        user_service.auth_service.hash_password.assert_called_once_with(valid_user_create_data.password)
        user_service.user_repository.exists_by_email.assert_called_once_with(valid_user_create_data.email)
        user_service.user_repository.create.assert_called_once()

    async def test_create_user_duplicate_email(self, user_service, valid_user_create_data):
        """중복 이메일로 사용자 생성 실패 테스트"""
        # Given
        user_service.user_repository.exists_by_email = AsyncMock(return_value=True)
        
        # When & Then
        with pytest.raises(ValidationError, match="이미 사용 중인 이메일입니다"):
            await user_service.create_user(valid_user_create_data)
        
        # 중복 검사 후 더 이상 진행되지 않음을 확인
        user_service.user_repository.exists_by_email.assert_called_once()
        user_service.user_repository.create.assert_not_called()

    async def test_create_user_duplicate_user_id(self, user_service, valid_user_create_data):
        """중복 사용자 ID로 사용자 생성 실패 테스트"""
        # Given
        user_service.user_repository.exists_by_email = AsyncMock(return_value=False)
        user_service.user_repository.exists_by_user_id = AsyncMock(return_value=True)
        
        # When & Then
        with pytest.raises(ValidationError, match="이미 사용 중인 사용자 ID입니다"):
            await user_service.create_user(valid_user_create_data)

    async def test_get_user_success(self, user_service, mock_user_response):
        """사용자 조회 성공 테스트"""
        # Given
        user_id = "test_user_001"
        user_service.user_repository.get_by_id = AsyncMock(return_value=mock_user_response)
        
        # When
        result = await user_service.get_user(user_id)
        
        # Then
        assert result.user_id == user_id
        assert result.email == mock_user_response.email
        user_service.user_repository.get_by_id.assert_called_once_with(user_id)

    async def test_get_user_not_found(self, user_service):
        """존재하지 않는 사용자 조회 테스트"""
        # Given
        user_id = "nonexistent_user"
        user_service.user_repository.get_by_id = AsyncMock(return_value=None)
        
        # When & Then
        with pytest.raises(NotFoundError, match="사용자를 찾을 수 없습니다"):
            await user_service.get_user(user_id)

    async def test_authenticate_user_success(self, user_service, mock_user_response):
        """사용자 인증 성공 테스트"""
        # Given
        user_id = "test_user_001"
        password = "correct_password"
        
        # User exists and is active
        mock_user_response.status = "active"
        user_service.user_repository.get_by_id = AsyncMock(return_value=mock_user_response)
        user_service.auth_service.verify_password = Mock(return_value=True)
        
        # When
        result = await user_service.authenticate_user(user_id, password)
        
        # Then
        assert result.user_id == user_id
        user_service.auth_service.verify_password.assert_called_once()

    async def test_authenticate_user_wrong_password(self, user_service, mock_user_response):
        """잘못된 비밀번호로 인증 실패 테스트"""
        # Given
        user_id = "test_user_001"
        wrong_password = "wrong_password"
        
        mock_user_response.status = "active"
        user_service.user_repository.get_by_id = AsyncMock(return_value=mock_user_response)
        user_service.auth_service.verify_password = Mock(return_value=False)
        
        # When & Then
        with pytest.raises(ValidationError, match="비밀번호가 일치하지 않습니다"):
            await user_service.authenticate_user(user_id, wrong_password)

    async def test_authenticate_inactive_user(self, user_service, inactive_user_response):
        """비활성화된 사용자 인증 실패 테스트"""
        # Given
        user_id = "inactive_user"
        password = "any_password"
        
        user_service.user_repository.get_by_id = AsyncMock(return_value=inactive_user_response)
        
        # When & Then
        with pytest.raises(ValidationError, match="비활성화된 계정입니다"):
            await user_service.authenticate_user(user_id, password)
        
        # 비밀번호 검증까지 가지 않음을 확인
        user_service.auth_service.verify_password.assert_not_called()

    async def test_login_success(self, user_service, mock_user_response):
        """로그인 성공 테스트"""
        # Given
        user_id_or_email = "testuser@example.com"
        password = "correct_password"
        
        mock_user_response.status = "active"
        user_service.user_repository.get_by_email = AsyncMock(return_value=mock_user_response)
        user_service.auth_service.verify_password = Mock(return_value=True)
        user_service.auth_service.create_access_token = Mock(return_value="test_jwt_token")
        
        # When
        access_token, user_response = await user_service.login(user_id_or_email, password)
        
        # Then
        assert access_token == "test_jwt_token"
        assert user_response.email == mock_user_response.email
        user_service.auth_service.create_access_token.assert_called_once_with(
            mock_user_response.user_id, 
            mock_user_response.email, 
            "user"
        )

    async def test_update_user_success(self, user_service, user_update_data, mock_user_response):
        """사용자 정보 수정 성공 테스트"""
        # Given
        user_id = "test_user_001"
        updated_response = UserResponse(**mock_user_response.dict())
        updated_response.nickname = user_update_data.nickname
        updated_response.phone_number = user_update_data.phone_number
        
        user_service.user_repository.get_by_id = AsyncMock(return_value=mock_user_response)
        user_service.user_repository.update = AsyncMock(return_value=updated_response)
        
        # When
        result = await user_service.update_user(user_id, user_update_data)
        
        # Then
        assert result.nickname == user_update_data.nickname
        assert result.phone_number == user_update_data.phone_number
        user_service.user_repository.update.assert_called_once()

    async def test_delete_user_success(self, user_service, mock_user_response):
        """사용자 삭제 성공 테스트"""
        # Given
        user_id = "test_user_001"
        user_service.user_repository.get_by_id = AsyncMock(return_value=mock_user_response)
        user_service.user_repository.delete = AsyncMock(return_value=True)
        
        # When
        result = await user_service.delete_user(user_id)
        
        # Then
        assert result is True
        user_service.user_repository.delete.assert_called_once_with(user_id)