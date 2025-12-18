"""
이벤트 관련 비즈니스 로직 서비스
"""
from typing import Optional, Tuple, List
from datetime import datetime
from zoneinfo import ZoneInfo

from src.repositories.event_repository import EventRepository

KST = ZoneInfo("Asia/Seoul")
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.ars.tm60_users_service import Tm60UsersService
from src.services.point_transaction_service import PointTransactionService
from src.models.point_transaction_model import TransactionType, CurrencyType, ReferenceType
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException, ValidationError
from src.schemas.user_schema import SignupRewardInfo
from src.schemas.event_schema import EventResponse, EventDetailResponse


class EventService:
    """이벤트 비즈니스 로직 서비스"""
    
    def __init__(
        self,
        event_repo: EventRepository,
        point_transaction_service: PointTransactionService,
        tm60_users_service: Tm60UsersService,
    ):
        self.event_repo = event_repo
        self.point_transaction_service = point_transaction_service
        self.tm60_users_service = tm60_users_service
    
    async def process_signup_reward(self, user_id: str) -> Optional[SignupRewardInfo]:
        """
        회원가입 이벤트 포인트 지급 처리
        - EVT_1 이벤트 확인 및 포인트 지급
        - 중복 참여 방지
        - 포인트 지급 및 거래 내역 기록
        
        Returns:
            SignupRewardInfo: 포인트 지급 성공시 보상 정보
            None: 이벤트 없음 또는 이미 참여함
        """
        log = get_logger_with_request_id()
        log.info("Processing signup reward", user_id=user_id)
        
        try:
            # 1. 활성 신규가입 이벤트(EVT_1) 조회
            event = await self.event_repo.get_active_signup_event()
            if not event:
                log.info("No active signup event found", user_id=user_id)
                return None
            
            log.info("Active signup event found", 
                    user_id=user_id, 
                    event_id=event.event_id,
                    event_code=event.event_code,
                    reward_value=event.reward_value)
            
            # 2. 중복 참여 여부 확인
            already_participated = await self.event_repo.has_user_participated(event.event_id, user_id)
            if already_participated:
                log.info("User already participated in signup event", 
                        user_id=user_id, 
                        event_id=event.event_id)
                return None
            
            # 3. TM60(MSSQL)에 포인트 지급
            try:
                new_balance = await self.tm60_users_service.update_user_points(
                    user_id=user_id,
                    point_amount=event.reward_value
                )
            except BaseAppException as e:
                if "찾을 수 없습니다" in str(e) or e.status_code == 404:
                    log.warning("TM60 user not found for point update, skipping MSSQL point update", 
                              user_id=user_id)
                    # MSSQL 포인트 업데이트는 실패하지만 MariaDB 로그만 기록
                    new_balance = event.reward_value  # 초기 포인트로 설정
                else:
                    raise
            
            log.info("Points added to TM60 successfully", 
                    user_id=user_id,
                    added_points=event.reward_value,
                    new_balance=new_balance)
            
            # 4. MariaDB에 포인트 거래 내역 기록
            await self.point_transaction_service.create_transaction(
                user_id=user_id,
                transaction_type=TransactionType.EARN,
                currency_type=CurrencyType.POINT,
                amount=event.reward_value,
                balance_after=new_balance,
                reference_type=ReferenceType.EVENT,
                reference_id=event.event_code,
                description=f"{event.event_name} 참여 포인트 지급",
                expires_at=None  # 일반 포인트는 만료 없음
            )
            
            # 5. 이벤트 참여 로그 기록
            await self.event_repo.create_participation_log(
                event_id=event.event_id,
                user_id=user_id,
                reward_type=event.reward_type,
                reward_value=event.reward_value,
                participation_data={
                    "signup_date": datetime.now(KST).isoformat(),
                    "point_balance_after": new_balance
                }
            )
            
            # 6. 지급 결과 반환 (Frontend 표시용)
            reward_info = SignupRewardInfo(
                event_name=event.event_name,
                reward_value=event.reward_value,
                balance_after=new_balance,
                message=f"회원가입을 축하드립니다! {event.reward_value:,}P가 지급되었습니다."
            )
            
            log.info("Signup reward processing completed successfully", 
                    user_id=user_id,
                    event_code=event.event_code,
                    reward_value=event.reward_value,
                    balance_after=new_balance)
            
            return reward_info
            
        except Exception as e:
            log.warning("Signup reward processing failed", 
                      user_id=user_id, 
                      error=str(e))
            # 회원가입은 성공하되, 포인트 지급만 실패하는 것으로 처리
            # 심각한 오류가 아닌 경우 None 반환하여 회원가입 자체는 성공하도록 함
            if isinstance(e, (ValidationError, BaseAppException)):
                # 예상된 오류는 로깅만 하고 None 반환 (회원가입 성공)
                return None
            else:
                # 예상치 못한 오류는 재발생 (회원가입도 실패)
                raise BaseAppException(f"포인트 지급 처리 실패: {str(e)}", status_code=500)

    # ===== 공개 조회 API용 서비스 =====
    async def get_public_event_list(self) -> List[EventResponse]:
        """게스트 공개 이벤트 목록 (is_active=True, created_at DESC)"""
        log = get_logger_with_request_id()
        log.info("Service: get_public_event_list")
        events = await self.event_repo.get_public_list()
        return [EventResponse.model_validate(e) for e in events]

    async def get_event_detail_with_adjacent(self, event_id: int) -> EventDetailResponse:
        """
        이벤트 상세 조회 + 이전/다음 event_id 포함
        - 스키마에 after_event_id, before_event_id 필드를 추가하여 반환
        """
        log = get_logger_with_request_id()
        log.info("Service: get_event_detail_with_adjacent", event_id=event_id)
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise ValidationError(f"이벤트를 찾을 수 없습니다. (ID: {event_id})")

        before_id, after_id = await self.event_repo.get_adjacent_ids(event_id)
        base = EventDetailResponse.model_validate(event)
        base.before_event_id = before_id
        base.after_event_id = after_id
        return base

    # 조회수 기능 없음 (t_event에 view_count 미존재)