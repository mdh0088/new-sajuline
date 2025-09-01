"""
사용자 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, AuthenticationError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.user_model import User, UserStatus, JoinType
from src.schemas.user_schema import UserCreate, UserUpdate, UserResponse, UserListResponse, UserSignup, SignupResponse
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService


class UserService:
    """사용자 비즈니스 로직 서비스"""
    
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        사용자 생성 비즈니스 로직
        - 중복 검증
        - 비밀번호 해싱
        - 사용자 생성
        """
        log = get_logger_with_request_id()
        log.info("Creating new user", user_id=user_data.user_id, email=user_data.email)
        
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_data.user_id == "create_user_error_test":
            raise ValidationError("Service layer: 사용자 생성 비즈니스 로직 실패 테스트")
        
        # 중복 검증
        if await self.user_repo.exists_by_user_id(user_data.user_id):
            log.warning("User ID already exists", user_id=user_data.user_id)
            raise DuplicateError("이미 존재하는 사용자 ID입니다.")
        
        if await self.user_repo.exists_by_email(user_data.email):
            log.warning("Email already exists", email=user_data.email)
            raise DuplicateError("이미 존재하는 이메일입니다.")
        
        if await self.user_repo.exists_by_phone(user_data.phone):
            log.warning("Phone already exists", phone=user_data.phone)
            raise DuplicateError("이미 존재하는 전화번호입니다.")
        
        # 비밀번호 해싱 (소셜 로그인이 아닌 경우)
        password_hash = None
        if user_data.password and user_data.join_type.value == "COMMON":
            password_hash = self.auth_service.hash_password(user_data.password)
        
        # 사용자 생성
        user = await self.user_repo.create(user_data, password_hash)
        
        log.info("User created successfully", user_id=user.user_id, email=user.email)
        return UserResponse.model_validate(user)
    
    async def signup(self, signup_data: UserSignup) -> SignupResponse:
        """
        통합 회원가입 처리 (일반 + 소셜)
        - 가입 유형 자동 판별
        - 유효성 검사 (중복 체크, 약관 동의, 비밀번호 검증)
        - 사용자 생성
        """
        log = get_logger_with_request_id()
        log.info("Starting signup process", user_id=signup_data.user_id, email=signup_data.email)
        
        # 1. 가입 유형 판별
        is_social = bool(signup_data.social_provider and signup_data.social_id)
        
        if is_social:
            # 소셜 가입: social_provider를 JoinType으로 변환
            try:
                join_type = JoinType(signup_data.social_provider.upper())
            except ValueError:
                log.warning("Unsupported social provider", provider=signup_data.social_provider)
                raise ValidationError(f"지원하지 않는 소셜 제공자입니다: {signup_data.social_provider}")
            log.info("Social signup detected", provider=signup_data.social_provider)
        else:
            # 일반 가입: 비밀번호 필수 검증
            if not signup_data.password:
                log.warning("Password required for regular signup", user_id=signup_data.user_id)
                raise ValidationError("일반 회원가입은 비밀번호가 필수입니다.")
            join_type = JoinType.COMMON
            log.info("Regular signup detected", user_id=signup_data.user_id)
        
        # 2. 약관 동의 검증
        if not signup_data.agree_terms or not signup_data.agree_privacy:
            log.warning("Terms agreement required", 
                       user_id=signup_data.user_id, 
                       agree_terms=signup_data.agree_terms, 
                       agree_privacy=signup_data.agree_privacy)
            raise ValidationError("필수 약관에 동의해주세요.")
        
        # 3. 중복 검증
        if await self.user_repo.exists_by_user_id(signup_data.user_id):
            log.warning("User ID already exists", user_id=signup_data.user_id)
            raise DuplicateError("이미 존재하는 사용자 ID입니다.")
        
        if await self.user_repo.exists_by_email(signup_data.email):
            log.warning("Email already exists", email=signup_data.email)
            raise DuplicateError("이미 존재하는 이메일입니다.")
        
        if await self.user_repo.exists_by_phone(signup_data.phone):
            log.warning("Phone already exists", phone=signup_data.phone)
            raise DuplicateError("이미 존재하는 전화번호입니다.")
        
        # 4. UserCreate 스키마로 변환하여 기존 로직 재사용
        user_create_data = UserCreate(
            user_id=signup_data.user_id,
            email=signup_data.email,
            nickname=signup_data.nickname,
            phone=signup_data.phone,
            join_type=join_type,
            social_provider=signup_data.social_provider,
            social_id=signup_data.social_id,
            profile_image_url=signup_data.profile_image_url,
            birth_date=signup_data.birth_date,
            gender=signup_data.gender,
            is_marketing_agreed=signup_data.is_marketing_agreed,
            password=signup_data.password
        )
        
        # 5. 비밀번호 해싱 (일반 가입시에만)
        password_hash = None
        if signup_data.password and join_type == JoinType.COMMON:
            password_hash = self.auth_service.hash_password(signup_data.password)
        
        # 6. 사용자 생성
        user = await self.user_repo.create(user_create_data, password_hash)
        
        log.info("Signup completed successfully", 
                user_id=user.user_id, 
                email=user.email, 
                join_type=join_type.value,
                is_social=is_social)
        
        # 7. 응답 생성
        user_response = UserResponse.model_validate(user)
        return SignupResponse(
            user=user_response,
            message="회원가입이 완료되었습니다."
        )
    
    async def get_user(self, user_id: str) -> UserResponse:
        """사용자 조회"""
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_id == "get_user_error_test":
            raise ValidationError("Service layer: 사용자 조회 비즈니스 로직 실패 테스트")
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")
        
        return UserResponse.model_validate(user)
    
    async def get_user_by_email(self, email: str) -> UserResponse:
        """이메일로 사용자 조회"""
        # 테스트용 강제 서비스 레이어 오류 발생
        if email == "get_user_by_email_error_test@test.com":
            raise ValidationError("Service layer: 이메일 사용자 조회 비즈니스 로직 실패 테스트")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")
        
        return UserResponse.model_validate(user)
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        사용자 정보 수정 비즈니스 로직
        - 존재 여부 확인
        - 중복 검증 (닉네임, 전화번호 변경시)
        - 정보 수정
        """
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_id == "update_user_error_test":
            raise ValidationError("Service layer: 사용자 정보 수정 비즈니스 로직 실패 테스트")
        
        # 사용자 존재 여부 확인
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")
        
        # 전화번호 변경시 중복 검증
        if user_data.phone and user_data.phone != existing_user.phone:
            if await self.user_repo.exists_by_phone(user_data.phone):
                raise DuplicateError("이미 존재하는 전화번호입니다.")
        
        # 사용자 정보 수정
        updated_user = await self.user_repo.update(user_id, user_data)
        
        return UserResponse.model_validate(updated_user) if updated_user else None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제 비즈니스 로직
        - 존재 여부 확인
        - 삭제 처리
        """
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_id == "delete_user_error_test":
            raise ValidationError("Service layer: 사용자 삭제 비즈니스 로직 실패 테스트")
        
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")
        
        success = await self.user_repo.delete(user_id)
        
        return success
    
    async def get_user_list(
        self, 
        page: int = 1, 
        size: int = 20,
        user_status: Optional[str] = None
    ) -> UserListResponse:
        """
        사용자 목록 조회 비즈니스 로직
        - 페이징 처리
        - 상태별 필터링
        """
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_status == "get_user_list_error_test":
            raise ValidationError("Service layer: 사용자 목록 조회 비즈니스 로직 실패 테스트")
        
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        skip = (page - 1) * size
        
        # 상태 검증
        if user_status and user_status not in [status.value for status in UserStatus]:
            raise ValidationError("유효하지 않은 사용자 상태입니다.")
        
        users = await self.user_repo.get_list(skip, size, user_status)
        total = await self.user_repo.get_count(user_status)
        
        user_responses = [UserResponse.model_validate(user) for user in users]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            size=size
        )
    
    async def authenticate_user(self, user_id_or_email: str, password: str) -> UserResponse:
        """
        사용자 인증 비즈니스 로직
        - 사용자 ID 또는 이메일로 조회
        - 비밀번호 검증
        - 계정 잠금 확인
        """
        # 테스트용 강제 서비스 레이어 오류 발생
        if user_id_or_email == "service_error_test":
            raise ValidationError("Service layer: 비즈니스 로직 검증 실패 테스트")
        
        # 사용자 조회 (ID 또는 이메일)
        user = None
        if "@" in user_id_or_email:
            user = await self.user_repo.get_by_email(user_id_or_email)
        else:
            user = await self.user_repo.get_by_id(user_id_or_email)
        
        if not user:
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")
        
        # 계정 잠금 확인
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AuthenticationError(f"계정이 {user.locked_until}까지 잠겨있습니다.")
        
        # 비밀번호 검증
        if not user.password_hash or not self.auth_service.verify_password(password, user.password_hash):
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")
        
        return UserResponse.model_validate(user)
    
    async def login(self, user_id_or_email: str, password: str) -> Tuple[str, UserResponse]:
        """
        사용자 로그인 비즈니스 로직
        - 사용자 인증
        - JWT 토큰 생성
        - 로그인 실패 횟수 관리
        - 마지막 로그인 시간 업데이트
        """
        log = get_logger_with_request_id()
        log.info("Login attempt", identifier=user_id_or_email)
        
        # 사용자 인증
        try:
            user_response = await self.authenticate_user(user_id_or_email, password)
        except AuthenticationError as auth_error:
            # 실패 횟수 증가 (실제 사용자가 있는 경우)
            user = None
            if "@" in user_id_or_email:
                user = await self.user_repo.get_by_email(user_id_or_email)
            else:
                user = await self.user_repo.get_by_id(user_id_or_email)
            
            if user:
                await self.user_repo.increment_failed_login(user.user_id)
            
            log.warning("Authentication failed", identifier=user_id_or_email, reason=str(auth_error))
            raise  # 원래 예외 다시 발생
        
        # 계정 상태 확인
        user = await self.user_repo.get_by_id(user_response.user_id)
        if user.user_status != UserStatus.ACTIVE:
            log.warning("Login failed - inactive account", user_id=user.user_id, status=user.user_status.value)
            raise AuthenticationError("계정이 비활성화되었습니다")
        
        # 로그인 성공 시 실패 횟수 초기화
        await self.user_repo.reset_failed_login(user.user_id)
        
        # JWT 토큰 생성
        access_token = self.auth_service.create_access_token(
            user_id=user.user_id,
            email=user.email,
            role="user"
        )
        
        # 마지막 로그인 시간 업데이트
        await self.user_repo.update_last_login(user.user_id)
        
        log.info("Login successful", user_id=user.user_id, email=user.email)
        return access_token, user_response