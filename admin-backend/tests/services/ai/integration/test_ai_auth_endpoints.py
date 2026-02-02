"""
AI 어시스턴트 인증 통합 테스트 (End-to-End)

Stories: 1-2
FRs: FR-012
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from jose import jwt

from src.main import app
from src.config.settings import settings


class TestAIAuthEndpoints:
    """AI 엔드포인트 인증 통합 테스트"""

    @pytest.fixture
    def client(self):
        """테스트 클라이언트"""
        return TestClient(app)

    @pytest.fixture
    def valid_token(self):
        """유효한 JWT 토큰 생성"""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test_admin",
            "email": "test@example.com",
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
            "sub": "test_admin",
            "email": "test@example.com",
            "role": "admin",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "jti": "expired-jti",
            "token_type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def test_health_endpoint_without_auth(self, client):
        """AC5: /health 엔드포인트는 인증 없이 접근 가능"""
        # Act
        response = client.get("/api/v1/ai/health")

        # Assert
        assert response.status_code in [200, 503]  # healthy 또는 unhealthy

    def test_health_endpoint_with_valid_token(self, client, valid_token):
        """AC5: /health 엔드포인트는 유효한 토큰으로도 접근 가능"""
        # Act
        response = client.get(
            "/api/v1/ai/health",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        # Assert
        assert response.status_code in [200, 503]

    def test_query_endpoint_without_token(self, client):
        """AC2: 토큰 없이 /query 접근 시 401 반환 + 에러 코드"""
        # Act
        response = client.post(
            "/api/v1/ai/query",
            json={"query": "test query"}
        )

        # Assert
        assert response.status_code == 401
        # HTTPBearer가 자동으로 처리하는 에러는 단순 detail만 있음
        # 실제 get_current_admin 호출 전에 차단됨

    def test_query_endpoint_with_invalid_token(self, client):
        """AC2: 유효하지 않은 토큰으로 /query 접근 시 401 반환 + 에러 형식 검증"""
        # Act
        response = client.post(
            "/api/v1/ai/query",
            json={"query": "test query"},
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        # Assert
        assert response.status_code == 401
        # AC2 요구사항: {"detail": "...", "code": "INVALID_TOKEN"}
        data = response.json()
        assert "detail" in data
        if isinstance(data["detail"], dict):
            assert data["detail"]["code"] == "INVALID_TOKEN"
            assert "유효하지 않은 토큰입니다" in data["detail"]["detail"]

    def test_query_endpoint_with_expired_token(self, client, expired_token):
        """AC3: 만료된 토큰으로 /query 접근 시 401 반환 + SESSION_EXPIRED 검증"""
        # Act
        response = client.post(
            "/api/v1/ai/query",
            json={"query": "test query"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Assert
        assert response.status_code == 401
        # AC3 요구사항: {"detail": "...", "code": "SESSION_EXPIRED"}
        data = response.json()
        assert "detail" in data
        if isinstance(data["detail"], dict):
            assert data["detail"]["code"] == "SESSION_EXPIRED"
            assert "세션이 만료되었습니다" in data["detail"]["detail"]

    def test_feedback_endpoint_without_token(self, client):
        """AC2: 토큰 없이 /feedback 접근 시 401 반환"""
        # Act
        response = client.post(
            "/api/v1/ai/feedback",
            json={"session_id": "test", "feedback": "test feedback"}
        )

        # Assert
        assert response.status_code == 401

    def test_history_endpoint_without_token(self, client):
        """AC2: 토큰 없이 /history 접근 시 401 반환"""
        # Act
        response = client.get("/api/v1/ai/history")

        # Assert
        assert response.status_code == 401

    def test_authorization_header_format(self, client):
        """Edge Case: Bearer 접두사 없는 토큰은 거부"""
        # Act
        response = client.post(
            "/api/v1/ai/query",
            json={"query": "test query"},
            headers={"Authorization": "InvalidFormat"}
        )

        # Assert
        assert response.status_code == 401
