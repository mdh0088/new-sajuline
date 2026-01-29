"""
일일 운세 API 단위 테스트

Story 2.5 Task 7: 단위 테스트 (AC: 7)
- 정상 응답 테스트 (캐시 히트/미스)
- 사주 정보 미등록 에러 테스트
- 인증 실패 테스트
- 날짜 범위 초과 테스트
- 커버리지 85% 이상
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from src.common.middleware.rate_limit import limiter
from src.core.dependencies import get_fortune_service, get_user_repository
from src.main import app
from src.schemas.fortune_schema import DayPillar, FortuneResponse
from src.services.auth_service import TokenPayload, get_current_user


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    """테스트 중 Rate Limiter 비활성화"""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def transport():
    """ASGI Transport for httpx"""
    return ASGITransport(app=app)


@pytest.fixture
async def client(transport):
    """비동기 테스트 클라이언트"""
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


@pytest.fixture
def mock_fortune_response():
    """FortuneResponse Mock"""
    return FortuneResponse(
        target_date=date.today(),
        fortune_type="daily",
        day_pillar=DayPillar(stem="갑", branch="진"),
        overall="오늘은 좋은 날입니다.",
        love="로맨틱한 하루가 될 것입니다.",
        career="승진의 기회가 보입니다.",
        health="건강 상태가 양호합니다.",
        wealth="재물운이 상승합니다.",
        lucky_color="파랑",
        lucky_number=7,
        source="llm",
        luck_score=4,
        sipsung="식신",
        keywords=["발전", "성장"],
    )


@pytest.fixture
def mock_token_payload():
    """인증된 사용자 Mock"""
    return TokenPayload(
        sub="user-123",
        email="test@example.com",
        role="user",
        exp=9999999999,
        iat=1609459200,
        jti="test-jti-123",
    )


@pytest.fixture
def mock_user_with_saju():
    """사주 정보가 있는 사용자 Mock"""
    user = MagicMock()
    user.user_id = "user-123"
    user.birth_date = "1990-01-15 08:30"  # 생년월일시
    return user


@pytest.fixture
def mock_user_without_saju():
    """사주 정보가 없는 사용자 Mock"""
    user = MagicMock()
    user.user_id = "user-123"
    user.birth_date = None
    return user


class TestDailyFortuneAPI:
    """일일 운세 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_daily_fortune_success_cache_miss(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """정상 운세 조회 - 캐시 미스"""
        # Mock 서비스/레포지토리 생성
        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        # FastAPI 의존성 override
        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 200
            json_data = response.json()
            assert json_data["success"] is True
            assert json_data["data"]["fortune_type"] == "daily"
            assert "x-cache" in response.headers
        finally:
            # Override 정리
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_success_cache_hit(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """정상 운세 조회 - 캐시 히트"""
        # 캐시에서 온 것처럼 source 변경
        mock_fortune_response.source = "cache"

        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 200
            json_data = response.json()
            assert json_data["success"] is True
            assert response.headers.get("x-cache") == "HIT"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_no_saju_info(
        self, client, mock_token_payload, mock_user_without_saju
    ):
        """사주 정보 미등록 시 400 에러"""
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_without_saju)

        # fortune_service도 mock 필요 (의존성 해결 시 Redis 연결 시도 방지)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 400
            json_data = response.json()
            # HTTPException의 detail이 dict로 반환됨
            assert json_data.get("detail", {}).get("code") == "SAJU_INFO_REQUIRED"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_unauthorized(self, client):
        """비로그인 시 401 에러"""

        # get_current_user가 HTTPException 발생하도록 설정
        def raise_unauthorized():
            raise HTTPException(status_code=401, detail="인증 토큰이 없습니다")

        # 의존성 해결 시 Redis 연결 시도 방지
        mock_fortune_service = AsyncMock()
        mock_user_repo = AsyncMock()

        app.dependency_overrides[get_current_user] = raise_unauthorized
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_invalid_date_range_past(
        self, client, mock_token_payload, mock_user_with_saju
    ):
        """과거 8일 이상 날짜 요청 시 400 에러"""
        old_date = (date.today() - timedelta(days=10)).isoformat()

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={old_date}")

            assert response.status_code == 400
            json_data = response.json()
            assert json_data.get("detail", {}).get("code") == "INVALID_DATE_RANGE"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_invalid_date_range_future(
        self, client, mock_token_payload, mock_user_with_saju
    ):
        """미래 날짜 요청 시 400 에러"""
        future_date = (date.today() + timedelta(days=1)).isoformat()

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={future_date}")

            assert response.status_code == 400
            json_data = response.json()
            assert json_data.get("detail", {}).get("code") == "INVALID_DATE_RANGE"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_with_valid_past_date(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """유효한 과거 날짜 (7일 이내) 요청"""
        valid_date = (date.today() - timedelta(days=3)).isoformat()
        mock_fortune_response.target_date = date.today() - timedelta(days=3)

        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={valid_date}")

            assert response.status_code == 200
            json_data = response.json()
            assert json_data["success"] is True
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_x_cache_header_present(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """X-Cache 헤더가 응답에 포함되는지 확인"""
        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 200
            # X-Cache 헤더 확인 (소문자로 변환됨)
            assert "x-cache" in response.headers
            assert response.headers["x-cache"] in ["HIT", "MISS"]
        finally:
            app.dependency_overrides.clear()


class TestDailyFortuneAPIEdgeCases:
    """일일 운세 API 엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_get_daily_fortune_exactly_7_days_ago(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """정확히 7일 전 날짜 요청 (유효)"""
        valid_date = (date.today() - timedelta(days=7)).isoformat()

        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={valid_date}")

            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_exactly_8_days_ago(
        self, client, mock_token_payload, mock_user_with_saju
    ):
        """정확히 8일 전 날짜 요청 (무효)"""
        invalid_date = (date.today() - timedelta(days=8)).isoformat()

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={invalid_date}")

            assert response.status_code == 400
            json_data = response.json()
            assert json_data.get("detail", {}).get("code") == "INVALID_DATE_RANGE"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_today(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """오늘 날짜 요청 (유효)"""
        today = date.today().isoformat()

        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get(f"/api/v1/fortune/daily?date={today}")

            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_no_date_param_uses_today(
        self, client, mock_fortune_response, mock_token_payload, mock_user_with_saju
    ):
        """date 파라미터 없으면 오늘 날짜 사용"""
        mock_fortune_service = AsyncMock()
        mock_fortune_service.get_daily_fortune = AsyncMock(
            return_value=mock_fortune_response
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user_with_saju)

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 200
            json_data = response.json()
            # FortuneResponse에서 alias가 "date"임
            assert json_data["data"]["date"] == date.today().isoformat()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_user_not_found(self, client, mock_token_payload):
        """사용자를 찾을 수 없을 때 404 에러"""
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=None)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 404
            json_data = response.json()
            assert json_data.get("detail", {}).get("code") == "USER_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_invalid_birth_date_format(
        self, client, mock_token_payload
    ):
        """생년월일 형식이 잘못된 경우 400 에러"""
        mock_user = MagicMock()
        mock_user.user_id = "user-123"
        mock_user.birth_date = "invalid-date-format"

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)
        mock_fortune_service = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: mock_token_payload
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
        app.dependency_overrides[get_fortune_service] = lambda: mock_fortune_service

        try:
            response = await client.get("/api/v1/fortune/daily")

            assert response.status_code == 400
            json_data = response.json()
            assert json_data.get("detail", {}).get("code") == "SAJU_INFO_REQUIRED"
        finally:
            app.dependency_overrides.clear()
