"""
사용자 관련 테스트 데이터 픽스처

사용자 생성, 수정, 인증 등에 필요한 테스트 데이터를 제공합니다.
"""
import pytest
from datetime import datetime
from src.schemas.user_schema import UserCreate, UserUpdate, UserResponse, UserLogin
from src.schemas.auth_schema import LoginRequest


@pytest.fixture
def valid_user_create_data():
    """유효한 사용자 생성 데이터"""
    return UserCreate(
        user_id="test_user_001",
        email="testuser@example.com",
        password="SecurePassword123!",
        nickname="테스트유저",
        phone_number="01012345678",
        birth_date="19900515",
        gender="M"
    )


@pytest.fixture
def invalid_user_create_data():
    """무효한 사용자 생성 데이터 (검증 테스트용)"""
    return UserCreate(
        user_id="",  # 빈 사용자 ID
        email="invalid-email",  # 잘못된 이메일 형식
        password="123",  # 너무 짧은 비밀번호
        nickname="",  # 빈 닉네임
        phone_number="invalid",  # 잘못된 전화번호
        birth_date="invalid",  # 잘못된 생년월일
        gender="X"  # 잘못된 성별
    )


@pytest.fixture
def user_update_data():
    """사용자 정보 수정 데이터"""
    return UserUpdate(
        nickname="수정된닉네임",
        phone_number="01098765432"
    )


@pytest.fixture
def mock_user_response():
    """모킹된 사용자 응답 데이터"""
    return UserResponse(
        user_id="test_user_001",
        email="testuser@example.com",
        nickname="테스트유저",
        phone_number="01012345678",
        birth_date="19900515",
        gender="M",
        status="active",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0)
    )


@pytest.fixture
def user_login_data():
    """사용자 로그인 데이터"""
    return UserLogin(
        user_id="test_user_001",
        password="SecurePassword123!"
    )


@pytest.fixture
def login_request_data():
    """로그인 요청 데이터"""
    return LoginRequest(
        user_id="test_user_001",
        password="SecurePassword123!"
    )


@pytest.fixture
def duplicate_email_user():
    """중복 이메일 테스트용 사용자 데이터"""
    return UserCreate(
        user_id="duplicate_user",
        email="existing@example.com",  # 이미 존재하는 이메일
        password="AnotherPassword456!",
        nickname="중복테스트",
        phone_number="01087654321"
    )


@pytest.fixture
def test_users_list():
    """여러 사용자 데이터 리스트 (페이징 테스트용)"""
    users = []
    for i in range(1, 11):  # 10명의 사용자
        users.append(UserResponse(
            user_id=f"test_user_{i:03d}",
            email=f"user{i}@example.com",
            nickname=f"사용자{i}",
            phone_number=f"0101234{i:04d}",
            birth_date=f"199{i%10}0101",
            gender="M" if i % 2 == 1 else "F",
            status="active",
            created_at=datetime(2024, 1, i, 12, 0, 0),
            updated_at=datetime(2024, 1, i, 12, 0, 0)
        ))
    return users


@pytest.fixture
def inactive_user_response():
    """비활성화된 사용자 응답 데이터"""
    return UserResponse(
        user_id="inactive_user",
        email="inactive@example.com",
        nickname="비활성사용자",
        phone_number="01012345678",
        status="inactive",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0)
    )