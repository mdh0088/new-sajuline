"""
Redis-based Phone Verification Service

Manages phone verification sessions in Redis with automatic TTL.
Implements industry-standard SMS verification pattern.
"""
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis.asyncio as redis
from src.common.config.settings import get_settings
from src.common.exceptions.custom import ValidationError, BusinessLogicError


class PhoneVerificationRedisService:
    """Redis를 사용한 핸드폰 인증 세션 관리"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
        # Configuration
        self.SESSION_TTL = 300  # 5 minutes
        self.VERIFIED_TOKEN_TTL = 86400  # 24 hours  
        self.MAX_ATTEMPTS = 3
        self.RATE_LIMIT_TTL = 3600  # 1 hour
        self.MAX_SENDS_PER_HOUR = 3
        
    async def connect(self):
        """Redis 연결"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _generate_session_id(self) -> str:
        """세션 ID 생성 (32자 랜덤)"""
        return secrets.token_hex(16)
    
    def _generate_verification_code(self) -> str:
        """6자리 인증 코드 생성"""
        return str(secrets.randbelow(900000) + 100000)
    
    def _generate_verification_token(self) -> str:
        """인증 완료 토큰 생성"""
        return secrets.token_urlsafe(32)
    
    async def check_rate_limit(self, phone: str) -> tuple[bool, int]:
        """
        SMS 발송 횟수 제한 확인
        
        Returns:
            (허용 여부, 남은 횟수)
        """
        await self.connect()
        
        rate_key = f"phone_verification:rate:{phone}"
        current_count = await self.redis_client.get(rate_key)
        
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        if current_count >= self.MAX_SENDS_PER_HOUR:
            return False, 0
        
        return True, self.MAX_SENDS_PER_HOUR - current_count
    
    async def increment_rate_limit(self, phone: str):
        """SMS 발송 횟수 증가"""
        await self.connect()
        
        rate_key = f"phone_verification:rate:{phone}"
        pipe = self.redis_client.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, self.RATE_LIMIT_TTL)
        await pipe.execute()
    
    async def create_verification_session(
        self,
        phone: str,
        name: str,
        birth_date: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str, datetime]:
        """
        인증 세션 생성
        
        Args:
            phone: 전화번호
            name: 이름
            birth_date: 생년월일
            extra_data: 추가 데이터
            
        Returns:
            (session_id, verification_code, expires_at)
        """
        await self.connect()
        
        # Generate session data
        session_id = self._generate_session_id()
        verification_code = self._generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(seconds=self.SESSION_TTL)
        
        session_data = {
            "phone": phone,
            "code": verification_code,
            "attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "user_info": {
                "name": name,
                "birth_date": birth_date
            }
        }
        
        if extra_data:
            session_data["extra"] = extra_data
        
        # Store in Redis
        session_key = f"phone_verification:{session_id}"
        await self.redis_client.setex(
            session_key,
            self.SESSION_TTL,
            json.dumps(session_data)
        )
        
        # Increment rate limit
        await self.increment_rate_limit(phone)
        
        return session_id, verification_code, expires_at
    
    async def get_verification_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        인증 세션 조회
        
        Args:
            session_id: 세션 ID
            
        Returns:
            세션 데이터 또는 None
        """
        await self.connect()
        
        session_key = f"phone_verification:{session_id}"
        session_data = await self.redis_client.get(session_key)
        
        if not session_data:
            return None
        
        return json.loads(session_data)
    
    async def verify_code(
        self,
        session_id: str,
        code: str
    ) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        인증 코드 검증
        
        Args:
            session_id: 세션 ID
            code: 인증 코드
            
        Returns:
            (성공 여부, 인증 토큰, 사용자 정보)
        """
        await self.connect()
        
        # Get session
        session_data = await self.get_verification_session(session_id)
        if not session_data:
            raise ValidationError("인증 세션이 만료되었거나 존재하지 않습니다.")
        
        # Check attempts
        if session_data["attempts"] >= self.MAX_ATTEMPTS:
            # Delete session after max attempts
            await self.delete_session(session_id)
            raise BusinessLogicError("인증 시도 횟수를 초과했습니다. 다시 시작해주세요.")
        
        # Increment attempts
        session_data["attempts"] += 1
        session_key = f"phone_verification:{session_id}"
        ttl = await self.redis_client.ttl(session_key)
        await self.redis_client.setex(
            session_key,
            ttl if ttl > 0 else self.SESSION_TTL,
            json.dumps(session_data)
        )
        
        # Verify code
        if session_data["code"] != code:
            remaining_attempts = self.MAX_ATTEMPTS - session_data["attempts"]
            if remaining_attempts > 0:
                raise ValidationError(
                    f"인증 코드가 일치하지 않습니다. (남은 시도: {remaining_attempts}회)"
                )
            else:
                await self.delete_session(session_id)
                raise ValidationError("인증 시도 횟수를 초과했습니다.")
        
        # Generate verification token
        verification_token = self._generate_verification_token()
        
        # Store verified token
        token_key = f"phone_verification:verified:{verification_token}"
        verified_data = {
            "phone": session_data["phone"],
            "verified_at": datetime.utcnow().isoformat(),
            "user_info": session_data["user_info"]
        }
        await self.redis_client.setex(
            token_key,
            self.VERIFIED_TOKEN_TTL,
            json.dumps(verified_data)
        )
        
        # Delete session after successful verification
        await self.delete_session(session_id)
        
        return True, verification_token, verified_data
    
    async def check_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        인증 토큰 확인
        
        Args:
            token: 인증 토큰
            
        Returns:
            인증 정보 또는 None
        """
        await self.connect()
        
        token_key = f"phone_verification:verified:{token}"
        verified_data = await self.redis_client.get(token_key)
        
        if not verified_data:
            return None
        
        return json.loads(verified_data)
    
    async def update_session_data(self, session_id: str, data: Dict[str, Any]):
        """
        세션 데이터 업데이트
        
        Args:
            session_id: 세션 ID
            data: 업데이트할 데이터
        """
        await self.connect()
        
        # Get existing session
        session_data = await self.get_verification_session(session_id)
        if not session_data:
            raise ValidationError("세션이 존재하지 않습니다.")
        
        # Update data
        session_data.update(data)
        
        # Save back to Redis with remaining TTL
        session_key = f"phone_verification:{session_id}"
        ttl = await self.redis_client.ttl(session_key)
        if ttl > 0:
            await self.redis_client.setex(
                session_key,
                ttl,
                json.dumps(session_data)
            )
    
    async def delete_session(self, session_id: str):
        """세션 삭제"""
        await self.connect()
        session_key = f"phone_verification:{session_id}"
        await self.redis_client.delete(session_key)
    
    async def cleanup_expired_sessions(self):
        """
        만료된 세션 정리 (Redis TTL이 자동 처리하지만 수동 정리가 필요한 경우)
        """
        # Redis TTL이 자동으로 처리하므로 일반적으로 필요 없음
        pass


# Singleton instance
phone_verification_redis = PhoneVerificationRedisService()