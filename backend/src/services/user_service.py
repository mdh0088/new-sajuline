"""
사용자 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime
import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, AuthenticationError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.user_model import User, UserStatus, JoinType
from src.schemas.user_schema import (
    UserResponse,
    UserSignup,
    PointHistoryResponse,
    PointChargeHistoryItem,
    PointUseHistoryItem,
    FindIdResponse,
    FindPasswordRequest,
    FindPasswordResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    WithdrawRequest,
    UserOutResponse,
)
from src.common.utils.email_service import email_service
from src.repositories.user_repository import UserRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.ars.tm60_users_service import Tm60UsersService
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
        event_service: Optional["EventService"] = None,
        tm60_users_service: Optional[Tm60UsersService] = None
    ):
        self.user_repo = user_repo
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
        self.activity_log_service = activity_log_service
        self.event_service = event_service
        self.tm60_users_service = tm60_users_service
        # Note: 아래 두 레포지토리는 포인트 내역 API에서 필요하므로 DI에서 주입받는 대신 메서드 인자로 받을 수 있도록 설계할 수도 있음

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """사용자 단건 조회 (닉네임/이메일 등 기본 정보 용도)"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")
        return UserResponse.model_validate(user)
    
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

        # 3. 탈퇴 후 재가입 제한 검사 (2개월)
        withdrawal_result = await self.user_repo.get_recent_withdrawal_by_phone(
            phone=signup_data.phone,
            months=2
        )
        if withdrawal_result:
            user_out, remaining_days = withdrawal_result
            log.warning("Signup blocked - recent withdrawal",
                       phone=signup_data.phone,
                       withdrawal_date=user_out.created_at,
                       remaining_days=remaining_days)
            raise ValidationError(
                f"탈퇴 후 2개월 이내에는 재가입이 불가능합니다. "
                f"약 {remaining_days}일 후에 가입이 가능합니다."
            )

        # 4. 중복 검증
        if await self.user_repo.exists_by_user_id(signup_data.user_id):
            log.warning("User ID already exists", user_id=signup_data.user_id)
            raise DuplicateError("이미 존재하는 사용자 ID입니다.")

        if await self.user_repo.exists_by_email(signup_data.email):
            log.warning("Email already exists", email=signup_data.email)
            raise DuplicateError("이미 존재하는 이메일입니다.")

        if await self.user_repo.exists_by_phone(signup_data.phone):
            log.warning("Phone already exists", phone=signup_data.phone)
            raise DuplicateError("이미 존재하는 전화번호입니다.")

        # 5. 비밀번호 해싱 (일반 가입시에만)
        password_hash = None
        if signup_data.password and join_type == JoinType.COMMON:
            password_hash = self.auth_service.hash_password(signup_data.password)

        # 6. 단순한 이중 DB 저장 (MariaDB 먼저 커밋 → MSSQL 저장 → 실패시 보상)
        user = None
        try:
            # 6-1. MariaDB에 사용자 생성 및 즉시 커밋
            user = await self.user_repo.create_from_signup(signup_data, password_hash, join_type)
            await self.user_repo.db.commit()
            log.info("MariaDB user created and committed", user_id=user.user_id)

            # 6-2. MSSQL(TM60)에 사용자 생성 시도 (주입된 서비스 사용)
            if not self.tm60_users_service:
                raise ValidationError("외부 시스템 연동 서비스가 초기화되지 않았습니다.")
            tm60_success = await self.tm60_users_service.create_user(
                user_id=user.user_id,
                phone=user.phone,
                nickname=user.nickname
            )
            if not tm60_success:
                # 6-3. MSSQL 실패시 MariaDB에서 사용자 완전 삭제 (보상 트랜잭션)
                await self.user_repo.delete_by_user_id(user.user_id)
                log.warning("TM60 user creation failed, deleted MariaDB user", user_id=user.user_id)
                raise ValidationError("외부 시스템 연동 오류로 회원가입에 실패했습니다.")

            log.info("Both databases updated successfully", user_id=user.user_id)

        except ValidationError:
            # ValidationError는 그대로 재발생
            raise
        except Exception as e:
            # 기타 예외시 보상 트랜잭션 실행 (MariaDB 사용자가 생성된 경우)
            if user:
                await self.user_repo.delete_by_user_id(user.user_id)
                log.warning("User creation failed, deleted MariaDB user", user_id=user.user_id, error=str(e))
            raise ValidationError(f"회원가입 처리 중 오류가 발생했습니다: {str(e)}")

        log.info("Signup completed successfully",
                user_id=user.user_id,
                email=user.email,
                join_type=join_type.value,
                is_social=is_social)

        # 7. 회원가입 이벤트 포인트 지급 처리 (실패해도 회원가입은 성공)
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

        # 8. 응답 생성 (포인트 지급 정보 포함)
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
            log.warning("Login failed - inactive account", user_id=user.user_id, status=user.user_status)
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

    async def get_point_history(
        self,
        *,
        user_id: str,
        start_dt: str,
        end_dt: str,
        search_type: str,
        order_type: str,
        payment_repo: PaymentRepository,
        chatlog_repo: Tm60ChatlogRepository,
        counselor_repo: CounselorRepository,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[PointHistoryResponse, int]:
        """사용자 포인트 내역 조회 (도메인: 사용자)"""
        log = get_logger_with_request_id()
        log.info(
            "Point history request",
            user_id=user_id,
            start_dt=start_dt,
            end_dt=end_dt,
            search_type=search_type,
            order_type=order_type,
        )

        # 입력 검증
        if not start_dt or not end_dt:
            raise ValidationError("start_dt와 end_dt는 필수입니다.")
        if search_type not in ("point_charge", "point_use"):
            raise ValidationError("search_type은 'point_charge' 또는 'point_use'여야 합니다.")
        if order_type not in ("latest", "highest", "lowest"):
            raise ValidationError("order_type은 'latest' | 'highest' | 'lowest'여야 합니다.")

        # 날짜 파싱
        try:
            start_date = datetime.strptime(start_dt, "%Y-%m-%d")
            end_date = datetime.strptime(end_dt, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("날짜 형식은 yyyy-mm-dd 여야 합니다.")

        if search_type == "point_charge":
            rows, total = await payment_repo.get_point_charge_history(
                user_id=user_id,
                start_dt=start_date,
                end_dt=end_date,
                order_type=order_type,
                page=page,
                limit=limit,
            )
            items = [
                PointChargeHistoryItem(
                    paid_at=paid_at,
                    product_name=product_name,
                    point_amount=int(point_amount or 0),
                )
                for (paid_at, product_name, point_amount, amount) in rows
            ]
            return PointHistoryResponse(search_type="point_charge", items_charge=items), total

        # point_use
        logs, total = await chatlog_repo.get_usage_logs(
            user_id=user_id,
            start_dt_str=start_dt,
            end_dt_str=end_dt,
            order_type=order_type,
            page=page,
            limit=limit,
        )

        unique_codes = sorted({log.m_code for log in logs if log.m_code})
        code_to_counselor = await counselor_repo.get_by_counselor_codes(unique_codes)

        items_use: list[PointUseHistoryItem] = []
        for log_row in logs:
            counselor = code_to_counselor.get(log_row.m_code)
            items_use.append(
                PointUseHistoryItem(
                    chatstart=log_row.chatstart,
                    chatend=log_row.chatend,
                    realchattm=log_row.realchattm,
                    counselor=(
                        None
                        if not counselor
                        else {
                            "counselor_code": counselor.counselor_code,
                            "nickname": counselor.nickname,
                            "name": counselor.name,
                            "profile_image_url": counselor.profile_image_url,
                        }
                    ),
                    usepoint=int(log_row.usepoint or 0),
                )
            )

        return PointHistoryResponse(search_type="point_use", items_use=items_use), total
    
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

    async def find_user_id(self, phone: str) -> FindIdResponse:
        """
        전화번호로 사용자 ID 찾기

        Args:
            phone: 본인인증된 전화번호

        Returns:
            FindIdResponse: 사용자 ID와 가입일시

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
        """
        log = get_logger_with_request_id()
        log.info("Finding user by phone", phone=phone)

        user = await self.user_repo.get_by_phone(phone)

        if not user:
            log.warning("User not found for phone", phone=phone)
            raise NotFoundError("해당 전화번호로 가입된 사용자를 찾을 수 없습니다.")

        log.info("User found", user_id=user.user_id)
        return FindIdResponse(
            user_id=user.user_id,
            created_at=user.created_at
        )

    def _generate_temporary_password(self, length: int = 12) -> str:
        """
        임시 비밀번호 생성 (영문 대소문자 + 숫자)

        Args:
            length: 비밀번호 길이 (기본 12자)

        Returns:
            str: 생성된 임시 비밀번호
        """
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    async def find_password(self, request: FindPasswordRequest) -> FindPasswordResponse:
        """
        비밀번호 찾기 (임시 비밀번호 발급 및 이메일 전송)

        Args:
            request: 비밀번호 찾기 요청 (user_id, phone)

        Returns:
            FindPasswordResponse: 처리 결과

        Raises:
            NotFoundError: 사용자를 찾을 수 없음 (user_id + phone 불일치 또는 SNS 가입자)
            ValidationError: 이메일 전송 실패
        """
        log = get_logger_with_request_id()
        log.info("Finding password", user_id=request.user_id, phone=request.phone)

        # 1. 사용자 조회 (user_id + phone + join_type='COMMON' 조건)
        user = await self.user_repo.get_by_user_id_and_phone_for_password_reset(
            request.user_id,
            request.phone
        )

        if not user:
            log.warning("User not found for password reset",
                       user_id=request.user_id,
                       phone=request.phone)
            raise NotFoundError(
                "입력하신 정보와 일치하는 사용자를 찾을 수 없습니다. "
                "아이디와 전화번호를 확인해주세요. "
                "(SNS 가입 회원은 비밀번호 찾기를 사용할 수 없습니다.)"
            )

        # 2. 임시 비밀번호 생성
        temporary_password = self._generate_temporary_password()
        log.info("Temporary password generated", user_id=user.user_id)

        # 3. 임시 비밀번호 해싱 (bcrypt)
        password_hash = self.auth_service.hash_password(temporary_password)
        log.info("Temporary password hashed", user_id=user.user_id)

        # 4. DB에 해시된 비밀번호 업데이트
        update_success = await self.user_repo.update_password(user.user_id, password_hash)

        if not update_success:
            log.error("Failed to update password in DB", user_id=user.user_id)
            raise ValidationError("비밀번호 업데이트에 실패했습니다. 다시 시도해주세요.")

        await self.user_repo.db.commit()
        log.info("Password updated in DB", user_id=user.user_id)

        # 5. 이메일로 평문 임시 비밀번호 전송
        try:
            await email_service.send_temporary_password(
                recipient_email=user.email,
                user_id=user.user_id,
                temporary_password=temporary_password
            )
            log.info("Temporary password email sent", user_id=user.user_id, email=user.email)
        except Exception as e:
            log.error("Failed to send temporary password email",
                     user_id=user.user_id,
                     email=user.email,
                     error=str(e))
            # 이메일 전송 실패해도 비밀번호는 이미 변경됨
            raise ValidationError(
                "임시 비밀번호가 발급되었으나 이메일 전송에 실패했습니다. "
                "잠시 후 다시 시도해주세요."
            )

        # 6. 이메일 마스킹 처리하여 응답
        masked_email = email_service.mask_email(user.email)

        log.info("Password reset completed successfully", user_id=user.user_id)
        return FindPasswordResponse(
            user_id=user.user_id,
            email=masked_email,
            message=f"임시 비밀번호가 {masked_email}로 전송되었습니다. 로그인 후 비밀번호를 변경해주세요."
        )

    async def change_password(self, user_id: str, request: PasswordChangeRequest) -> PasswordChangeResponse:
        """
        비밀번호 변경 처리

        프로세스:
        1. 사용자 존재 확인
        2. 소셜 로그인 사용자인 경우 변경 불가
        3. 현재 비밀번호 검증
        4. 새 비밀번호 해싱
        5. DB 업데이트

        Args:
            user_id: 사용자 ID (TokenPayload에서 추출)
            request: 비밀번호 변경 요청 데이터

        Returns:
            PasswordChangeResponse: 비밀번호 변경 정보

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
            AuthenticationError: 현재 비밀번호 불일치
            ValidationError: 소셜 로그인 사용자 또는 변경 실패
        """
        log = get_logger_with_request_id()
        log.info("Starting password change process", user_id=user_id)

        # 1. 사용자 존재 확인
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            log.warning("User not found for password change", user_id=user_id)
            raise NotFoundError("사용자를 찾을 수 없습니다.")

        # 2. 소셜 로그인 사용자인 경우 변경 불가
        if user.join_type != JoinType.COMMON:
            log.warning("Password change not allowed for social login user",
                       user_id=user_id,
                       join_type=user.join_type)
            raise ValidationError("소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다.")

        # 3. 현재 비밀번호 검증
        if not user.password_hash or not self.auth_service.verify_password(request.current_password, user.password_hash):
            log.warning("Current password verification failed", user_id=user_id)
            raise AuthenticationError("현재 비밀번호가 일치하지 않습니다.")

        log.info("Current password verified", user_id=user_id)

        # 4. 새 비밀번호 해싱
        new_password_hash = self.auth_service.hash_password(request.new_password)
        log.info("New password hashed", user_id=user_id)

        # 5. DB 업데이트
        update_success = await self.user_repo.update_password(user_id, new_password_hash)

        if not update_success:
            log.error("Failed to update password in DB", user_id=user_id)
            raise ValidationError("비밀번호 변경에 실패했습니다. 다시 시도해주세요.")

        await self.user_repo.db.commit()
        log.info("Password updated successfully", user_id=user_id)

        # 6. 응답 생성
        return PasswordChangeResponse(
            user_id=user_id,
            password_changed_at=datetime.utcnow(),
            message="비밀번호가 성공적으로 변경되었습니다."
        )

    async def withdraw_user(self, user_id: str, request: WithdrawRequest) -> UserOutResponse:
        """
        회원 탈퇴 처리

        프로세스:
        1. 사용자 존재 및 상태 확인
        2. 비밀번호 검증 (일반 가입자만)
        3. t_user_out 테이블에 탈퇴 정보 기록
        4. t_user 상태를 WITHDRAWN으로 변경
        5. tm60_users에서 전화번호로 삭제

        Args:
            user_id: 탈퇴 요청 사용자 ID (TokenPayload에서 추출)
            request: 탈퇴 요청 데이터 (비밀번호 포함, 소셜 로그인은 null)

        Returns:
            UserOutResponse: 탈퇴 정보

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
            AuthenticationError: 비밀번호 불일치
            ValidationError: 탈퇴 처리 실패
        """
        log = get_logger_with_request_id()
        log.info("Starting user withdrawal process", user_id=user_id)

        # 1. 사용자 존재 확인
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            log.warning("User not found for withdrawal", user_id=user_id)
            raise NotFoundError("사용자를 찾을 수 없습니다.")

        # 이미 탈퇴한 사용자인지 확인
        if user.user_status == UserStatus.WITHDRAWN:
            log.warning("User already withdrawn", user_id=user_id)
            raise ValidationError("이미 탈퇴한 사용자입니다.")

        # 2. 비밀번호 검증 (일반 가입자만)
        if user.join_type == JoinType.COMMON:
            if not request.password:
                log.warning("Password required for common user withdrawal", user_id=user_id)
                raise ValidationError("비밀번호를 입력해주세요.")

            if not user.password_hash or not self.auth_service.verify_password(request.password, user.password_hash):
                log.warning("Password verification failed for withdrawal", user_id=user_id)
                raise AuthenticationError("비밀번호가 일치하지 않습니다.")

            log.info("Password verified for common user withdrawal", user_id=user_id)
        else:
            log.info("Social login user withdrawal (no password verification)",
                    user_id=user_id,
                    join_type=user.join_type)

        # 3. 탈퇴 처리 (MSSQL 먼저 삭제 → MariaDB 처리, 실패시 보상 트랜잭션)
        # 전략: MSSQL 삭제가 반드시 성공해야 MariaDB 탈퇴 처리 진행
        user_out = None
        tm60_delete_success = False  # 보상 트랜잭션 판단용

        try:
            # 3-1. MSSQL(tm60_users) 먼저 삭제 시도
            if not self.tm60_users_service:
                raise ValidationError("외부 시스템 연동 서비스가 초기화되지 않았습니다.")

            tm60_delete_success = await self.tm60_users_service.delete_user_by_phone(user.phone)
            if not tm60_delete_success:
                log.error("TM60 user deletion failed, withdrawal aborted",
                         user_id=user_id,
                         phone=user.phone)
                raise ValidationError("외부 시스템 연동 오류로 회원 탈퇴에 실패했습니다. 잠시 후 다시 시도해주세요.")

            log.info("TM60 user deleted successfully", user_id=user_id, phone=user.phone)

            # 3-2. t_user_out에 탈퇴 정보 기록
            user_out = await self.user_repo.create_user_out(
                user_id=user.user_id,
                nickname=user.nickname,
                phone=user.phone,
                email=user.email
            )
            log.info("User out record created", user_id=user_id, out_idx=user_out.out_idx)

            # 3-3. t_user 상태를 WITHDRAWN으로 변경
            update_success = await self.user_repo.update_user_status_to_withdrawn(user_id)
            if not update_success:
                log.error("Failed to update user status to WITHDRAWN", user_id=user_id)
                # MariaDB 실패 시 MSSQL 복구 시도 (보상 트랜잭션)
                await self._rollback_tm60_user_deletion(user)
                raise ValidationError("회원 탈퇴 처리 중 오류가 발생했습니다.")

            log.info("User status updated to WITHDRAWN", user_id=user_id)

            # 3-4. MariaDB 커밋
            await self.user_repo.db.commit()
            log.info("Both databases updated successfully for withdrawal", user_id=user_id)

        except (NotFoundError, AuthenticationError, ValidationError):
            # 이미 알려진 예외는 그대로 재발생
            await self.user_repo.db.rollback()
            raise
        except Exception as e:
            # 기타 예외시 롤백
            await self.user_repo.db.rollback()
            # MSSQL이 이미 삭제된 경우 복구 시도
            if tm60_delete_success:
                await self._rollback_tm60_user_deletion(user)
            log.error("User withdrawal failed", user_id=user_id, error=str(e))
            raise ValidationError(f"회원 탈퇴 처리 중 오류가 발생했습니다: {str(e)}")

        log.info("User withdrawal completed successfully",
                user_id=user_id,
                out_idx=user_out.out_idx)

        return UserOutResponse.model_validate(user_out)

    async def _rollback_tm60_user_deletion(self, user: User) -> None:
        """
        MSSQL(tm60_users) 삭제 후 MariaDB 처리 실패 시 보상 트랜잭션
        삭제된 tm60_users 데이터를 다시 생성하여 복구

        Args:
            user: 복구할 사용자 정보

        Note:
            이 메서드는 최선의 노력(best-effort)으로 복구를 시도합니다.
            복구 실패 시에도 예외를 발생시키지 않고 경고 로그만 기록합니다.
            (이미 주요 예외가 발생한 상황이므로)
        """
        log = get_logger_with_request_id()
        log.warning("Attempting to rollback TM60 user deletion",
                   user_id=user.user_id,
                   phone=user.phone)

        try:
            if self.tm60_users_service:
                rollback_success = await self.tm60_users_service.create_user(
                    user_id=user.user_id,
                    phone=user.phone,
                    nickname=user.nickname
                )
                if rollback_success:
                    log.info("TM60 user rollback successful", user_id=user.user_id)
                else:
                    log.error("TM60 user rollback failed - create returned False",
                             user_id=user.user_id,
                             phone=user.phone)
            else:
                log.error("TM60 user rollback failed - service not available",
                         user_id=user.user_id)
        except Exception as rollback_error:
            # 복구 실패해도 원래 예외를 우선시
            log.error("TM60 user rollback exception",
                     user_id=user.user_id,
                     error=str(rollback_error))