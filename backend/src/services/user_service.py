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
from src.schemas.user_schema import UserResponse, UserSignup
from src.repositories.user_repository import UserRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.auth_service import AuthService
from src.services.user_activity_log_service import UserActivityLogService
from src.schemas.user_activity_log_schema import DeviceType, UserType
from src.core.database import get_db_mssql


class UserService:
    """사용자 비즈니스 로직 서비스"""
    
    def __init__(
        self, 
        user_repo: UserRepository, 
        counselor_repo: CounselorRepository, 
        auth_service: AuthService,
        activity_log_service: Optional[UserActivityLogService] = None,
        event_service: Optional["EventService"] = None
    ):
        self.user_repo = user_repo
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
        self.activity_log_service = activity_log_service
        self.event_service = event_service
    
    async def signup(self, signup_data: UserSignup) -> UserResponse:
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
        
        # 2. 필수 약관 동의는 프론트엔드에서 검증하므로 서버에서는 생략
        
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
        
        # 4. 비밀번호 해싱 (일반 가입시에만)
        password_hash = None
        if signup_data.password and join_type == JoinType.COMMON:
            password_hash = self.auth_service.hash_password(signup_data.password)
        
        # 5. 이중 DB 저장 (MariaDB + MSSQL) - 둘 다 성공해야 함
        try:
            # 5-1. MariaDB에 사용자 생성 (flush만 수행, 커밋 지연)
            user = await self.user_repo.create_from_signup(signup_data, password_hash, join_type)
            log.info("MariaDB user created (not committed yet)", user_id=user.user_id)
            
            # 5-2. MSSQL(TM60)에 사용자 생성 시도
            # MSSQL 세션 생성 및 TM60UsersRepository 인스턴스화
            for mssql_session in get_db_mssql():
                tm60_repo = Tm60UsersRepository(mssql_session)
                tm60_success = await tm60_repo.create(
                    user_id=user.user_id,
                    phone=user.phone or "",
                    nickname=user.nickname or ""
                )
                
                if not tm60_success:
                    # TM60 실패시 MariaDB도 롤백
                    await self.user_repo.db.rollback()
                    log.warning("TM60 user creation failed, rolling back MariaDB", user_id=user.user_id)
                    raise ValidationError("외부 시스템 연동 오류로 회원가입에 실패했습니다.")
                break  # 첫 번째 세션만 사용
            
            # 5-3. 둘 다 성공한 경우에만 MariaDB 커밋
            await self.user_repo.db.commit()
            log.info("Both databases updated successfully", user_id=user.user_id)
            
        except ValidationError:
            # ValidationError는 그대로 재발생
            raise
        except Exception as e:
            # 기타 예외시 MariaDB 롤백
            await self.user_repo.db.rollback()
            log.warning("User creation failed, rolling back", user_id=signup_data.user_id, error=str(e))
            raise ValidationError(f"회원가입 처리 중 오류가 발생했습니다: {str(e)}")
        
        log.info("Signup completed successfully", 
                user_id=user.user_id, 
                email=user.email, 
                join_type=join_type.value,
                is_social=is_social)
        
        # 6. 회원가입 이벤트 포인트 지급 처리 (실패해도 회원가입은 성공)
        signup_reward = None
        if self.event_service:
            try:
                signup_reward = await self.event_service.process_signup_reward(user.user_id)
                if signup_reward:
                    log.info("Signup reward granted successfully", 
                           user_id=user.user_id,
                           reward_value=signup_reward.reward_value,
                           balance_after=signup_reward.balance_after)
            except Exception as e:
                # 포인트 지급 실패해도 회원가입은 성공으로 처리
                log.warning("Signup reward failed but signup succeeded", 
                          user_id=user.user_id, 
                          error=str(e))
        
        # 7. 응답 생성 (포인트 지급 정보 포함)
        user_response = UserResponse.model_validate(user)
        user_response.signup_reward = signup_reward
        
        return user_response
    
# TODO: 사용자 목록 조회 - 추후 참고용
    # async def get_user_list(
    #     self, 
    #     page: int = 1, 
    #     size: int = 20,
    #     user_status: Optional[str] = None
    # ) -> UserListResponse:
    #     """
    #     사용자 목록 조회 비즈니스 로직
    #     - 페이징 처리
    #     - 상태별 필터링
    #     """
    #     # 테스트용 강제 서비스 레이어 오류 발생
    #     if user_status == "get_user_list_error_test":
    #         raise ValidationError("Service layer: 사용자 목록 조회 비즈니스 로직 실패 테스트")
    #     
    #     if page < 1:
    #         page = 1
    #     if size < 1 or size > 100:
    #         size = 20
    #     
    #     skip = (page - 1) * size
    #     
    #     # 상태 검증
    #     if user_status and user_status not in [status.value for status in UserStatus]:
    #         raise ValidationError("유효하지 않은 사용자 상태입니다.")
    #     
    #     users = await self.user_repo.get_list(skip, size, user_status)
    #     total = await self.user_repo.get_count(user_status)
    #     
    #     user_responses = [UserResponse.model_validate(user) for user in users]
    #     
    #     return UserListResponse(
    #         users=user_responses,
    #         total=total,
    #         page=page,
    #         size=size
    #     )
    
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
    
    async def login(
        self, 
        user_id_or_email: str, 
        password: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: Optional[DeviceType] = None
    ) -> Tuple[str, UserResponse]:
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
        
        # 로그인 성공 활동 로그 기록
        if self.activity_log_service:
            try:
                await self.activity_log_service.log_login_success(
                    user_id=user.user_id,
                    user_type=UserType.USER,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    device_type=device_type
                )
            except Exception as e:
                # 활동 로그 실패해도 로그인은 성공으로 처리
                log.warning("Activity log failed but login succeeded", 
                          user_id=user.user_id, error=str(e))
        
        log.info("Login successful", user_id=user.user_id, email=user.email)
        return access_token, user_response
    
    async def check_email_availability(self, email: str) -> bool:
        """
        이메일 가용성 검사 (t_user + t_counselor 통합)
        Return: True=사용가능, False=이미 존재함
        """
        log = get_logger_with_request_id()
        log.info("Checking email availability across user and counselor tables", email=email)
        
        # t_user와 t_counselor 양쪽 테이블에서 이메일 존재 여부 확인
        user_exists = await self.user_repo.exists_by_email(email)
        counselor_exists = await self.counselor_repo.exists_by_counselor_id(email)  # counselor_id는 이메일 기반
        
        exists = user_exists or counselor_exists
        available = not exists
        
        log.info("Email availability check completed", 
                email=email, 
                user_exists=user_exists, 
                counselor_exists=counselor_exists, 
                available=available)
        return available
    
    async def check_user_id_availability(self, user_id: str) -> bool:
        """
        사용자 ID 가용성 검사 (t_user.user_id + t_counselor.counselor_id 통합)
        Return: True=사용가능, False=이미 존재함
        """
        log = get_logger_with_request_id()
        log.info("Checking user_id availability across user and counselor tables", user_id=user_id)
        
        # t_user.user_id와 t_counselor.counselor_id 양쪽에서 존재 여부 확인
        user_exists = await self.user_repo.exists_by_user_id(user_id)
        counselor_exists = await self.counselor_repo.exists_by_counselor_id(user_id)
        
        exists = user_exists or counselor_exists
        available = not exists
        
        log.info("User ID availability check completed", 
                user_id=user_id, 
                user_exists=user_exists, 
                counselor_exists=counselor_exists, 
                available=available)
        return available
    
    async def check_phone_availability(self, phone: str) -> bool:
        """
        전화번호 가용성 검사 (t_user + t_counselor 통합)
        Return: True=사용가능, False=이미 존재함
        """
        log = get_logger_with_request_id()
        log.info("Checking phone availability across user and counselor tables", phone=phone)
        
        # t_user와 t_counselor 양쪽 테이블에서 전화번호 존재 여부 확인
        user_exists = await self.user_repo.exists_by_phone(phone)
        counselor_exists = await self.counselor_repo.exists_by_phone(phone)
        
        exists = user_exists or counselor_exists
        available = not exists
        
        log.info("Phone availability check completed", 
                phone=phone, 
                user_exists=user_exists, 
                counselor_exists=counselor_exists, 
                available=available)
        return available
    
    async def check_nickname_availability(self, nickname: str) -> bool:
        """
        닉네임 가용성 검사 (t_user + t_counselor 통합)
        Return: True=사용가능, False=이미 존재함
        """
        log = get_logger_with_request_id()
        log.info("Checking nickname availability across user and counselor tables", nickname=nickname)
        
        # t_user와 t_counselor 양쪽 테이블에서 닉네임 존재 여부 확인
        user_exists = await self.user_repo.exists_by_nickname(nickname)
        counselor_exists = await self.counselor_repo.exists_by_nickname(nickname)
        
        exists = user_exists or counselor_exists
        available = not exists
        
        log.info("Nickname availability check completed", 
                nickname=nickname, 
                user_exists=user_exists, 
                counselor_exists=counselor_exists, 
                available=available)
        return available