"""
이벤트 관련 데이터 액세스 클래스
"""
from typing import Optional, Tuple, List
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import logger, get_logger_with_request_id

KST = ZoneInfo("Asia/Seoul")
from src.models.event_model import Event
from src.models.event_participation_model import EventParticipationLog


class EventRepository:
    """이벤트 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def get_active_signup_event(self) -> Optional[Event]:
        """
        활성 상태인 신규가입 이벤트(EVT_1) 조회
        - event_code = 'EVT_1'
        - is_active = True
        - valid_from <= now <= valid_until
        """
        log = get_logger_with_request_id()
        log.info("Looking up active signup event EVT_1")
        
        now = datetime.now(KST)
        stmt = select(Event).where(
            Event.event_code == "EVT_1",
            Event.is_active == True,
            Event.valid_from <= now,
            Event.valid_until >= now
        )
        
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()
        
        log.info("Active signup event lookup completed", 
                found=event is not None,
                event_id=event.event_id if event else None,
                reward_value=event.reward_value if event else None)
        return event
    
    @logger.catch(reraise=True)
    async def get_public_list(self) -> list[Event]:
        """게스트 공개 목록: is_active=True, created_at DESC"""
        log = get_logger_with_request_id()
        log.info("Getting public events list")
        stmt = (
            select(Event)
            .where(Event.is_active.is_(True))
            .order_by(desc(Event.created_at))
        )
        result = await self.db.execute(stmt)
        events = list(result.scalars().all())
        log.info("Public events retrieved", count=len(events))
        return events

    @logger.catch(reraise=True)
    async def get_by_id(self, event_id: int) -> Optional[Event]:
        log = get_logger_with_request_id()
        log.info("Looking up event by ID", event_id=event_id)
        stmt = select(Event).where(Event.event_id == event_id)
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()
        log.info("Event lookup completed", event_id=event_id, found=event is not None)
        return event

    @logger.catch(reraise=True)
    async def get_adjacent_ids(self, event_id: int) -> Tuple[Optional[int], Optional[int]]:
        """현재 이벤트 기준 이전/다음 ID 반환 (is_active=True, created_at DESC 시퀀스)"""
        log = get_logger_with_request_id()
        log.info("Resolving adjacent event ids", event_id=event_id)

        # 현재 created_at 조회
        current_stmt = select(Event.created_at).where(Event.event_id == event_id)
        current_res = await self.db.execute(current_stmt)
        current_created_at = current_res.scalar_one_or_none()
        if not current_created_at:
            return None, None

        # 이전(before): 더 최신 (created_at > current)
        before_stmt = (
            select(Event.event_id)
            .where(
                and_(
                    Event.is_active.is_(True),
                    Event.created_at > current_created_at
                )
            )
            .order_by(desc(Event.created_at))
            .limit(1)
        )
        before_res = await self.db.execute(before_stmt)
        before_id = before_res.scalar_one_or_none()

        # 다음(after): 더 과거 (created_at < current)
        after_stmt = (
            select(Event.event_id)
            .where(
                and_(
                    Event.is_active.is_(True),
                    Event.created_at < current_created_at
                )
            )
            .order_by(desc(Event.created_at))
            .limit(1)
        )
        after_res = await self.db.execute(after_stmt)
        after_id = after_res.scalar_one_or_none()

        log.info("Adjacent event IDs resolved", before_event_id=before_id, after_event_id=after_id)
        return before_id, after_id

    # 조회수 필드 없음 → 관련 메서드 제거

    @logger.catch(reraise=True)
    async def get_event_by_code(self, event_code: str) -> Optional[Event]:
        """이벤트 코드로 이벤트 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up event by code", event_code=event_code)
        
        stmt = select(Event).where(Event.event_code == event_code)
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()
        
        log.info("Event lookup by code completed", 
                event_code=event_code, 
                found=event is not None)
        return event
    
    @logger.catch(reraise=True)
    async def has_user_participated(self, event_id: int, user_id: str) -> bool:
        """
        사용자의 이벤트 참여 여부 확인 (중복 방지)
        EventParticipationLog의 UniqueConstraint(event_id, user_id) 활용
        """
        log = get_logger_with_request_id()
        log.info("Checking user event participation", event_id=event_id, user_id=user_id)
        
        stmt = select(EventParticipationLog.log_id).where(
            EventParticipationLog.event_id == event_id,
            EventParticipationLog.user_id == user_id
        )
        
        result = await self.db.execute(stmt)
        participated = result.scalar_one_or_none() is not None
        
        log.info("User event participation check completed", 
                event_id=event_id, 
                user_id=user_id, 
                participated=participated)
        return participated
    
    @logger.catch(reraise=True)
    async def create_participation_log(
        self, 
        event_id: int, 
        user_id: str, 
        reward_type: str,
        reward_value: int,
        participation_data: Optional[dict] = None
    ) -> EventParticipationLog:
        """
        이벤트 참여 로그 생성
        - UniqueConstraint(event_id, user_id)로 중복 방지
        - 실패시 IntegrityError 발생
        """
        log = get_logger_with_request_id()
        log.info("Creating event participation log", 
                event_id=event_id, 
                user_id=user_id,
                reward_type=reward_type,
                reward_value=reward_value)
        
        participation_log = EventParticipationLog(
            event_id=event_id,
            user_id=user_id,
            reward_type=reward_type,
            reward_value=reward_value,
            participation_data=participation_data or {},
            created_at=datetime.now(KST)
        )
        
        self.db.add(participation_log)
        await self.db.flush()
        await self.db.refresh(participation_log)
        
        log.info("Event participation log created successfully", 
                log_id=participation_log.log_id,
                event_id=event_id,
                user_id=user_id,
                reward_value=reward_value)
        return participation_log
    
    @logger.catch(reraise=True)
    async def get_user_participation_logs(self, user_id: str, limit: int = 10) -> list[EventParticipationLog]:
        """사용자의 이벤트 참여 로그 조회"""
        log = get_logger_with_request_id()
        log.info("Getting user participation logs", user_id=user_id, limit=limit)
        
        stmt = (
            select(EventParticipationLog)
            .where(EventParticipationLog.user_id == user_id)
            .order_by(EventParticipationLog.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        logs = list(result.scalars().all())
        
        log.info("User participation logs retrieved", 
                user_id=user_id, 
                count=len(logs))
        return logs