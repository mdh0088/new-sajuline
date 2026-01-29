"""
중앙화된 의존성 주입 모듈

모든 Repository/Service DI 함수와 Annotated 타입 alias를 관리합니다.
각 API 파일에서는 이 모듈에서 필요한 의존성만 import하여 사용합니다.

사용 예시:
    from src.core.dependencies import UserServiceDep, NotificationServiceDep

    @router.get("/users/{user_id}")
    async def get_user(user_id: int, user_service: UserServiceDep):
        return await user_service.get_user(user_id)
"""
from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# ==================== Database Sessions ====================
from src.core.database import get_db_maria, get_db_mssql
from src.core.redis import get_redis
import redis

# MariaDB Async Session - FastAPI가 생명주기 자동 관리
MariaSessionDep = Annotated[AsyncSession, Depends(get_db_maria)]

# MSSQL Sync Session - FastAPI가 생명주기 자동 관리 (for loop 패턴 사용 금지!)
MssqlSessionDep = Annotated[Session, Depends(get_db_mssql)]


# ==================== Repository Imports ====================
from src.repositories.user_repository import UserRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.notification_repository import NotificationRepository
from src.repositories.notification_wait_repository import NotificationWaitRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.point_product_repository import PointProductRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.grade_repository import GradeRepository
from src.repositories.event_repository import EventRepository
from src.repositories.banner_repository import BannerRepository
from src.repositories.notice_repository import NoticeRepository
from src.repositories.inquiry_repository import InquiryRepository
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.repositories.user_bookmark_repository import UserBookmarkRepository
from src.repositories.user_activity_log_repository import UserActivityLogRepository
from src.repositories.counselor_application_repository import CounselorApplicationRepository
from src.repositories.mileage_repository import MileageProductRepository
from src.repositories.fortune_repository import FortuneRepository
from src.repositories.saju_repository import SajuRepository

# MSSQL (ARS) Repositories
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.repositories.ars.tm60_mobile_repository import Tm60MobileRepository


# ==================== Service Imports ====================
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.counselor_service import CounselorService
from src.services.notification_service import NotificationService
from src.services.notification_wait_service import NotificationWaitService
from src.services.payment_service import PaymentService
from src.services.point_product_service import PointProductService
from src.services.point_transaction_service import PointTransactionService
from src.services.grade_service import GradeService
from src.services.event_service import EventService
from src.services.banner_service import BannerService
from src.services.notice_service import NoticeService
from src.services.inquiry_service import InquiryService
from src.services.consultation_review_service import ConsultationReviewService
from src.services.user_bookmark_service import UserBookmarkService
from src.services.user_activity_log_service import UserActivityLogService
from src.services.counselor_application_service import CounselorApplicationService
from src.services.mileage_service import MileageProductService

# MSSQL (ARS) Services
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.ars.tm60_member_service import Tm60MemberService
from src.services.ars.tm60_chatlog_service import Tm60ChatlogService
from src.services.ars.tm60_mobile_service import Tm60MobileService

# Other Services
from src.services.phone_verification_service import PhoneVerificationService
from src.services.social_auth_service import SocialAuthService
from src.services.fortune_cache_service import FortuneCacheService
from src.services.fortune_service import FortuneService

# LangChain
from src.core.langchain_chain import DailyFortuneChain


# ==================== MariaDB Repository DI Functions ====================

def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    """사용자 리포지토리 의존성 주입"""
    return UserRepository(db)


def get_counselor_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorRepository:
    """상담사 리포지토리 의존성 주입"""
    return CounselorRepository(db)


def get_notification_repository(db: AsyncSession = Depends(get_db_maria)) -> NotificationRepository:
    """알림 리포지토리 의존성 주입"""
    return NotificationRepository(db)


def get_notification_wait_repository(db: AsyncSession = Depends(get_db_maria)) -> NotificationWaitRepository:
    """알림 대기 리포지토리 의존성 주입"""
    return NotificationWaitRepository(db)


def get_payment_repository(db: AsyncSession = Depends(get_db_maria)) -> PaymentRepository:
    """결제 리포지토리 의존성 주입"""
    return PaymentRepository(db)


def get_point_product_repository(db: AsyncSession = Depends(get_db_maria)) -> PointProductRepository:
    """포인트 상품 리포지토리 의존성 주입"""
    return PointProductRepository(db)


def get_point_transaction_repository(db: AsyncSession = Depends(get_db_maria)) -> PointTransactionRepository:
    """포인트 거래 리포지토리 의존성 주입"""
    return PointTransactionRepository(db)


def get_grade_repository(db: AsyncSession = Depends(get_db_maria)) -> GradeRepository:
    """등급 리포지토리 의존성 주입"""
    return GradeRepository(db)


def get_event_repository(db: AsyncSession = Depends(get_db_maria)) -> EventRepository:
    """이벤트 리포지토리 의존성 주입"""
    return EventRepository(db)


def get_banner_repository(db: AsyncSession = Depends(get_db_maria)) -> BannerRepository:
    """배너 리포지토리 의존성 주입"""
    return BannerRepository(db)


def get_notice_repository(db: AsyncSession = Depends(get_db_maria)) -> NoticeRepository:
    """공지사항 리포지토리 의존성 주입"""
    return NoticeRepository(db)


def get_inquiry_repository(db: AsyncSession = Depends(get_db_maria)) -> InquiryRepository:
    """1:1 문의 리포지토리 의존성 주입"""
    return InquiryRepository(db)


def get_consultation_review_repository(db: AsyncSession = Depends(get_db_maria)) -> ConsultationReviewRepository:
    """상담 후기 리포지토리 의존성 주입"""
    return ConsultationReviewRepository(db)


def get_user_bookmark_repository(db: AsyncSession = Depends(get_db_maria)) -> UserBookmarkRepository:
    """사용자 북마크 리포지토리 의존성 주입"""
    return UserBookmarkRepository(db)


def get_user_activity_log_repository(db: AsyncSession = Depends(get_db_maria)) -> UserActivityLogRepository:
    """사용자 활동 로그 리포지토리 의존성 주입"""
    return UserActivityLogRepository(db)


def get_counselor_application_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorApplicationRepository:
    """상담사 신청 리포지토리 의존성 주입"""
    return CounselorApplicationRepository(db)


def get_mileage_repository(db: AsyncSession = Depends(get_db_maria)) -> MileageProductRepository:
    """마일리지 상품 리포지토리 의존성 주입"""
    return MileageProductRepository(db)


def get_fortune_repository(db: AsyncSession = Depends(get_db_maria)) -> FortuneRepository:
    """운세 이력 리포지토리 의존성 주입"""
    return FortuneRepository(db)


def get_saju_repository(db: AsyncSession = Depends(get_db_maria)) -> SajuRepository:
    """사주 지식 베이스 리포지토리 의존성 주입"""
    return SajuRepository(db)


# ==================== MSSQL Repository DI Functions ====================
# 중요: for loop 패턴 대신 Depends()를 사용하여 FastAPI가 세션 생명주기를 관리하도록 함

def get_tm60_users_repository(mssql_session: Session = Depends(get_db_mssql)) -> Tm60UsersRepository:
    """TM60 사용자 리포지토리 의존성 주입"""
    return Tm60UsersRepository(mssql_session)


def get_tm60_member_repository(mssql_session: Session = Depends(get_db_mssql)) -> Tm60MemberRepository:
    """TM60 멤버 리포지토리 의존성 주입"""
    return Tm60MemberRepository(mssql_session)


def get_tm60_chatlog_repository(mssql_session: Session = Depends(get_db_mssql)) -> Tm60ChatlogRepository:
    """TM60 채팅로그 리포지토리 의존성 주입"""
    return Tm60ChatlogRepository(mssql_session)


def get_tm60_mobile_repository(mssql_session: Session = Depends(get_db_mssql)) -> Tm60MobileRepository:
    """TM60 모바일 리포지토리 의존성 주입"""
    return Tm60MobileRepository(mssql_session)


# ==================== Repository Annotated Types ====================

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
CounselorRepositoryDep = Annotated[CounselorRepository, Depends(get_counselor_repository)]
NotificationRepositoryDep = Annotated[NotificationRepository, Depends(get_notification_repository)]
NotificationWaitRepositoryDep = Annotated[NotificationWaitRepository, Depends(get_notification_wait_repository)]
PaymentRepositoryDep = Annotated[PaymentRepository, Depends(get_payment_repository)]
PointProductRepositoryDep = Annotated[PointProductRepository, Depends(get_point_product_repository)]
PointTransactionRepositoryDep = Annotated[PointTransactionRepository, Depends(get_point_transaction_repository)]
GradeRepositoryDep = Annotated[GradeRepository, Depends(get_grade_repository)]
EventRepositoryDep = Annotated[EventRepository, Depends(get_event_repository)]
BannerRepositoryDep = Annotated[BannerRepository, Depends(get_banner_repository)]
NoticeRepositoryDep = Annotated[NoticeRepository, Depends(get_notice_repository)]
InquiryRepositoryDep = Annotated[InquiryRepository, Depends(get_inquiry_repository)]
ConsultationReviewRepositoryDep = Annotated[ConsultationReviewRepository, Depends(get_consultation_review_repository)]
UserBookmarkRepositoryDep = Annotated[UserBookmarkRepository, Depends(get_user_bookmark_repository)]
UserActivityLogRepositoryDep = Annotated[UserActivityLogRepository, Depends(get_user_activity_log_repository)]
CounselorApplicationRepositoryDep = Annotated[CounselorApplicationRepository, Depends(get_counselor_application_repository)]
MileageRepositoryDep = Annotated[MileageProductRepository, Depends(get_mileage_repository)]
FortuneRepositoryDep = Annotated[FortuneRepository, Depends(get_fortune_repository)]
SajuRepositoryDep = Annotated[SajuRepository, Depends(get_saju_repository)]

# MSSQL Repository Types
Tm60UsersRepositoryDep = Annotated[Tm60UsersRepository, Depends(get_tm60_users_repository)]
Tm60MemberRepositoryDep = Annotated[Tm60MemberRepository, Depends(get_tm60_member_repository)]
Tm60ChatlogRepositoryDep = Annotated[Tm60ChatlogRepository, Depends(get_tm60_chatlog_repository)]
Tm60MobileRepositoryDep = Annotated[Tm60MobileRepository, Depends(get_tm60_mobile_repository)]


# ==================== Stateless Service DI Functions ====================

def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입 (stateless)"""
    return AuthService()


def get_daily_fortune_chain() -> DailyFortuneChain:
    """LangChain 일일 운세 체인 의존성 주입 (stateless)"""
    return DailyFortuneChain()


# ==================== Simple Service DI Functions (1 dependency) ====================

def get_notification_service(
    notification_repo: NotificationRepository = Depends(get_notification_repository)
) -> NotificationService:
    """알림 서비스 의존성 주입"""
    return NotificationService(notification_repo)


def get_banner_service(
    banner_repo: BannerRepository = Depends(get_banner_repository)
) -> BannerService:
    """배너 서비스 의존성 주입"""
    return BannerService(banner_repo)


def get_notice_service(
    notice_repo: NoticeRepository = Depends(get_notice_repository)
) -> NoticeService:
    """공지사항 서비스 의존성 주입"""
    return NoticeService(notice_repo)


def get_grade_service(
    grade_repo: GradeRepository = Depends(get_grade_repository)
) -> GradeService:
    """등급 서비스 의존성 주입"""
    return GradeService(grade_repo)


def get_consultation_review_service(
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> ConsultationReviewService:
    """상담 후기 서비스 의존성 주입"""
    return ConsultationReviewService(review_repo)


def get_user_activity_log_service(
    activity_log_repo: UserActivityLogRepository = Depends(get_user_activity_log_repository)
) -> UserActivityLogService:
    """사용자 활동 로그 서비스 의존성 주입"""
    return UserActivityLogService(activity_log_repo)


def get_counselor_application_service(
    counselor_application_repo: CounselorApplicationRepository = Depends(get_counselor_application_repository)
) -> CounselorApplicationService:
    """상담사 신청 서비스 의존성 주입"""
    return CounselorApplicationService(counselor_application_repo)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repository)
) -> PaymentService:
    """결제 서비스 의존성 주입"""
    return PaymentService(payment_repo)


def get_point_product_service(
    point_product_repo: PointProductRepository = Depends(get_point_product_repository)
) -> PointProductService:
    """포인트 상품 서비스 의존성 주입"""
    return PointProductService(point_product_repo)


def get_fortune_cache_service(
    redis_client: redis.Redis = Depends(get_redis),
    fortune_repo: FortuneRepository = Depends(get_fortune_repository)
) -> FortuneCacheService:
    """운세 캐시 서비스 의존성 주입 (Redis + Repository)"""
    return FortuneCacheService(redis_client, fortune_repo)


# ==================== MSSQL Service DI Functions ====================

def get_tm60_users_service(
    tm60_users_repo: Tm60UsersRepository = Depends(get_tm60_users_repository)
) -> Tm60UsersService:
    """TM60 사용자 서비스 의존성 주입"""
    return Tm60UsersService(tm60_users_repo)


def get_tm60_member_service(
    tm60_member_repo: Tm60MemberRepository = Depends(get_tm60_member_repository)
) -> Tm60MemberService:
    """TM60 멤버 서비스 의존성 주입"""
    return Tm60MemberService(tm60_member_repo)


def get_tm60_chatlog_service(
    mssql_session: Session = Depends(get_db_mssql)
) -> Tm60ChatlogService:
    """TM60 채팅로그 서비스 의존성 주입"""
    # Tm60ChatlogService는 session을 직접 받음 (Repository가 아닌)
    return Tm60ChatlogService(mssql_session)


def get_tm60_mobile_service(
    tm60_mobile_repo: Tm60MobileRepository = Depends(get_tm60_mobile_repository)
) -> Tm60MobileService:
    """TM60 모바일 서비스 의존성 주입"""
    return Tm60MobileService(tm60_mobile_repo)


# ==================== Complex Service DI Functions (multiple dependencies) ====================

def get_mileage_service(
    mileage_repo: MileageProductRepository = Depends(get_mileage_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    transaction_repo: PointTransactionRepository = Depends(get_point_transaction_repository),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> MileageProductService:
    """마일리지 상품 서비스 의존성 주입 (4개 의존성)"""
    return MileageProductService(mileage_repo, user_repo, transaction_repo, tm60_users_service)


def get_user_bookmark_service(
    bookmark_repo: UserBookmarkRepository = Depends(get_user_bookmark_repository),
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> UserBookmarkService:
    """사용자 북마크 서비스 의존성 주입"""
    return UserBookmarkService(bookmark_repo, review_repo)


def get_point_transaction_service(
    point_transaction_repo: PointTransactionRepository = Depends(get_point_transaction_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    grade_repo: GradeRepository = Depends(get_grade_repository)
) -> PointTransactionService:
    """
    포인트 거래 서비스 의존성 주입 (표준 버전)
    - 마일리지 적립 기능을 위해 user_repo, grade_repo 포함
    """
    return PointTransactionService(point_transaction_repo, user_repo, grade_repo)


def get_event_service(
    event_repo: EventRepository = Depends(get_event_repository),
    point_transaction_service: PointTransactionService = Depends(get_point_transaction_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> EventService:
    """이벤트 서비스 의존성 주입"""
    return EventService(event_repo, point_transaction_service, tm60_users_service)


def get_notification_wait_service(
    notification_wait_repo: NotificationWaitRepository = Depends(get_notification_wait_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    notification_service: NotificationService = Depends(get_notification_service)
) -> NotificationWaitService:
    """알림 대기 서비스 의존성 주입"""
    return NotificationWaitService(
        notification_wait_repo=notification_wait_repo,
        user_repo=user_repo,
        counselor_repo=counselor_repo,
        notification_service=notification_service
    )


def get_inquiry_service(
    inquiry_repo: InquiryRepository = Depends(get_inquiry_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    notification_service: NotificationService = Depends(get_notification_service)
) -> InquiryService:
    """1:1 문의 서비스 의존성 주입 (사용자용)"""
    return InquiryService(
        inquiry_repo=inquiry_repo,
        counselor_repo=counselor_repo,
        notification_service=notification_service
    )


def get_inquiry_service_for_counselor(
    inquiry_repo: InquiryRepository = Depends(get_inquiry_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    notification_service: NotificationService = Depends(get_notification_service)
) -> InquiryService:
    """1:1 문의 서비스 의존성 주입 (상담사용)"""
    return InquiryService(
        inquiry_repo=inquiry_repo,
        user_repo=user_repo,
        notification_service=notification_service
    )


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
    event_service: EventService = Depends(get_event_service),
    activity_log_service: UserActivityLogService = Depends(get_user_activity_log_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> UserService:
    """
    사용자 서비스 의존성 주입 (표준 버전 - 6개 의존성)
    - 이벤트 포인트 지급: event_service
    - 활동 로그 기록: activity_log_service
    - ARS 시스템 연동: tm60_users_service
    """
    return UserService(
        user_repo, counselor_repo, auth_service,
        activity_log_service, event_service, tm60_users_service
    )


def get_counselor_service(
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
    tm60_member_service: Tm60MemberService = Depends(get_tm60_member_service),
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository),
    notification_wait_service: NotificationWaitService = Depends(get_notification_wait_service),
    chatlog_repo: Tm60ChatlogRepository = Depends(get_tm60_chatlog_repository)
) -> CounselorService:
    """상담사 서비스 의존성 주입"""
    return CounselorService(
        counselor_repo, auth_service, tm60_member_service,
        review_repo, notification_wait_service, chatlog_repo
    )


def get_phone_verification_service(
    redis_client: redis.Redis = Depends(get_redis)
) -> PhoneVerificationService:
    """휴대폰 본인인증 서비스 의존성 주입"""
    return PhoneVerificationService(redis_client)


def get_social_auth_service(
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository)
) -> SocialAuthService:
    """소셜 인증 서비스 의존성 주입"""
    return SocialAuthService(auth_service, user_repo)


def get_fortune_service(
    saju_repo: SajuRepository = Depends(get_saju_repository),
    cache_service: FortuneCacheService = Depends(get_fortune_cache_service),
    chain: DailyFortuneChain = Depends(get_daily_fortune_chain)
) -> FortuneService:
    """운세 서비스 의존성 주입 (3개 의존성: 사주 리포지토리 + 캐시 서비스 + LangChain)"""
    return FortuneService(saju_repo, cache_service, chain)


# ==================== Service Annotated Types ====================

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
NotificationWaitServiceDep = Annotated[NotificationWaitService, Depends(get_notification_wait_service)]
BannerServiceDep = Annotated[BannerService, Depends(get_banner_service)]
NoticeServiceDep = Annotated[NoticeService, Depends(get_notice_service)]
GradeServiceDep = Annotated[GradeService, Depends(get_grade_service)]
ConsultationReviewServiceDep = Annotated[ConsultationReviewService, Depends(get_consultation_review_service)]
UserActivityLogServiceDep = Annotated[UserActivityLogService, Depends(get_user_activity_log_service)]
CounselorApplicationServiceDep = Annotated[CounselorApplicationService, Depends(get_counselor_application_service)]
MileageServiceDep = Annotated[MileageProductService, Depends(get_mileage_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
PointProductServiceDep = Annotated[PointProductService, Depends(get_point_product_service)]
PointTransactionServiceDep = Annotated[PointTransactionService, Depends(get_point_transaction_service)]
EventServiceDep = Annotated[EventService, Depends(get_event_service)]
UserBookmarkServiceDep = Annotated[UserBookmarkService, Depends(get_user_bookmark_service)]
InquiryServiceDep = Annotated[InquiryService, Depends(get_inquiry_service)]
InquiryServiceForCounselorDep = Annotated[InquiryService, Depends(get_inquiry_service_for_counselor)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CounselorServiceDep = Annotated[CounselorService, Depends(get_counselor_service)]

# MSSQL Service Types
Tm60UsersServiceDep = Annotated[Tm60UsersService, Depends(get_tm60_users_service)]
Tm60MemberServiceDep = Annotated[Tm60MemberService, Depends(get_tm60_member_service)]
Tm60ChatlogServiceDep = Annotated[Tm60ChatlogService, Depends(get_tm60_chatlog_service)]
Tm60MobileServiceDep = Annotated[Tm60MobileService, Depends(get_tm60_mobile_service)]

# Other Service Types
PhoneVerificationServiceDep = Annotated[PhoneVerificationService, Depends(get_phone_verification_service)]
SocialAuthServiceDep = Annotated[SocialAuthService, Depends(get_social_auth_service)]
FortuneCacheServiceDep = Annotated[FortuneCacheService, Depends(get_fortune_cache_service)]
FortuneServiceDep = Annotated[FortuneService, Depends(get_fortune_service)]
DailyFortuneChainDep = Annotated[DailyFortuneChain, Depends(get_daily_fortune_chain)]
