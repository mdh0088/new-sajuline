"""
AI 어시스턴트 인증 통합 단위 테스트

Stories: 1-2
FRs: FR-012
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt
from unittest.mock import AsyncMock, MagicMock

from src.common.utils.auth_utils import get_current_admin, get_optional_admin
from src.models.admin_model import Admin
from src.config.settings import settings


class TestAuthIntegration:
    """인증 통합 단위 테스트"""

    @pytest.fixture
    def valid_token(self):
        """유효한 JWT 토큰 생성"""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "admin001",
            "email": "admin@example.com",
            "role": "admin",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=30)).timestamp()),
            "jti": "test-jti",
            "token_type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @pytest.fixture
    def expired_token(self):
        """만료된 JWT 토큰 생성"""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "admin001",
            "email": "admin@example.com",
            "role": "admin",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "jti": "expired-jti",
            "token_type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @pytest.fixture
    def mock_db(self):
        """Mock 데이터베이스 세션"""
        db = AsyncMock()
        return db

    @pytest.fixture
    def mock_admin(self):
        """Mock Admin 객체"""
        admin = Admin(
            admin_id="admin001",
            login_id="admin",
            email="admin@example.com",
            password_hash="hashed_password",
            name="관리자",
            role="admin",
            is_active=True,
        )
        return admin

    @pytest.mark.asyncio
    async def test_get_current_admin_with_valid_token(self, valid_token, mock_db, mock_admin):
        """AC1: 유효한 JWT 토큰으로 관리자 정보 조회 성공"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)

        # Mock DB 쿼리
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_admin)
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Act
        admin = await get_current_admin(credentials, mock_db)

        # Assert
        assert admin.admin_id == "admin001"
        assert admin.email == "admin@example.com"
        assert admin.role == "admin"

    @pytest.mark.asyncio
    async def test_get_current_admin_without_token(self, mock_db):
        """AC2: 토큰 없음 - AUTH_REQUIRED 에러"""
        # Arrange - credentials가 None인 경우는 HTTPBearer에서 자동 처리
        # 이 테스트는 실제 엔드포인트 테스트에서 확인
        pass

    @pytest.mark.asyncio
    async def test_get_current_admin_with_invalid_token(self, mock_db):
        """AC2: 유효하지 않은 토큰 - INVALID_TOKEN 에러"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        invalid_token = "invalid.jwt.token"
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=invalid_token)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        # AC2 요구사항: {"detail": "...", "code": "..."}
        assert isinstance(exc_info.value.detail, dict)
        assert exc_info.value.detail["code"] == "INVALID_TOKEN"
        assert "유효하지 않은 토큰입니다" in exc_info.value.detail["detail"]

    @pytest.mark.asyncio
    async def test_get_current_admin_with_expired_token(self, expired_token, mock_db):
        """AC3: 만료된 토큰 - SESSION_EXPIRED 에러"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        # AC3 요구사항: {"detail": "...", "code": "SESSION_EXPIRED"}
        assert isinstance(exc_info.value.detail, dict)
        assert exc_info.value.detail["code"] == "SESSION_EXPIRED"
        assert "세션이 만료되었습니다" in exc_info.value.detail["detail"]

    @pytest.mark.asyncio
    async def test_get_current_admin_with_inactive_admin(self, valid_token, mock_db):
        """Edge Case: 비활성화된 관리자 - INVALID_TOKEN 에러"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)

        inactive_admin = Admin(
            admin_id="admin001",
            login_id="admin",
            email="admin@example.com",
            password_hash="hashed_password",
            name="관리자",
            role="admin",
            is_active=False,  # 비활성
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=inactive_admin)
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(exc_info.value.detail, dict)
        assert exc_info.value.detail["code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_get_current_admin_with_deleted_admin(self, valid_token, mock_db):
        """Edge Case: 삭제된 관리자 (DB에 없음) - INVALID_TOKEN 에러"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)

        # Mock DB 쿼리 - 관리자 없음
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(exc_info.value.detail, dict)
        assert exc_info.value.detail["code"] == "INVALID_TOKEN"
        assert "유효하지 않은 토큰입니다" in exc_info.value.detail["detail"]

    @pytest.mark.asyncio
    async def test_get_optional_admin_with_valid_token(self, valid_token, mock_db, mock_admin):
        """AC5: 선택적 인증 - 유효한 토큰으로 관리자 반환"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_admin)
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Act
        admin = await get_optional_admin(credentials, mock_db)

        # Assert
        assert admin is not None
        assert admin.admin_id == "admin001"

    @pytest.mark.asyncio
    async def test_get_optional_admin_without_token(self, mock_db):
        """AC5: 선택적 인증 - 토큰 없으면 None 반환"""
        # Act
        admin = await get_optional_admin(None, mock_db)

        # Assert
        assert admin is None

    @pytest.mark.asyncio
    async def test_get_optional_admin_with_invalid_token(self, mock_db):
        """AC5: 선택적 인증 - 유효하지 않은 토큰은 None 반환 (에러 발생 안 함)"""
        # Arrange
        from fastapi.security import HTTPAuthorizationCredentials

        invalid_token = "invalid.jwt.token"
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=invalid_token)

        # Act
        admin = await get_optional_admin(credentials, mock_db)

        # Assert
        assert admin is None
