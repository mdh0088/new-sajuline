"""
Auth 인프라스트럭처 - 리포지토리 구현
"""
import asyncio
import aiohttp
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.common.exceptions.custom import DatabaseError, ExternalServiceException, ConflictException
from ...user.domain.models import User
from ..domain.entities import (
    SocialUserInfo, AuthProvider, KakaoOAuthConfig, NaverOAuthConfig
)
from ..domain.ports import AuthRepositoryPort as IAuthRepositoryPort


# Deprecated ABC 제거 (Protocol로 대체)


class MariaDBAuthRepository(IAuthRepositoryPort):
    """MariaDB Auth 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_session(self, session_data: Dict[str, Any]) -> None:
        """세션 생성"""
        try:
            # 세션 테이블이 없으므로 Redis에서 처리
            pass
        except SQLAlchemyError as e:
            raise DatabaseError(f"세션 생성 실패: {str(e)}")
    
    async def deactivate_user_sessions(self, user_id: str) -> None:
        """사용자 세션 비활성화"""
        try:
            # 세션 테이블이 없으므로 Redis에서 처리
            pass
        except SQLAlchemyError as e:
            raise DatabaseError(f"세션 비활성화 실패: {str(e)}")
    
    async def blacklist_token(self, token: str, expires_at: datetime) -> None:
        """토큰 블랙리스트 추가"""
        # Redis에서 처리
        pass
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """토큰 블랙리스트 확인"""
        # Redis에서 처리
        return False
    
    async def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None:
        """리프레시 토큰 저장"""
        # Redis에서 처리
        pass

    async def update_user_social_info(
        self,
        user_id: str,
        social_provider: str,
        social_id: str,
        profile_image_url: Optional[str]
    ) -> None:
        """사용자 소셜 정보 업데이트"""
        try:
            await self.session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(
                    social_provider=social_provider,
                    social_id=social_id,
                    profile_image_url=profile_image_url
                )
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"사용자 소셜 정보 업데이트 실패: {str(e)}")
    
    async def get_kakao_user_info(self, code: str) -> SocialUserInfo:
        """카카오 사용자 정보 조회"""
        # OAuth 클라이언트에서 처리
        pass
    
    async def get_naver_user_info(self, code: str) -> SocialUserInfo:
        """네이버 사용자 정보 조회"""
        # OAuth 클라이언트에서 처리
        pass


class RedisAuthRepository:
    """Redis Auth 리포지토리"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    async def create_session(self, session_data: Dict[str, Any]) -> None:
        """세션 생성"""
        try:
            session_id = session_data.get('session_id')
            session_json = json.dumps(session_data)
            
            # 세션 저장 (기본 TTL: 1일)
            await self.redis_client.setex(
                f"session:{session_id}",
                86400,  # 1일
                session_json
            )
            
            # 사용자별 세션 목록 저장
            user_id = session_data.get('user_id')
            if user_id:
                await self.redis_client.sadd(f"user_sessions:{user_id}", session_id)
                
        except Exception as e:
            raise DatabaseError(f"세션 생성 실패: {str(e)}")
    
    async def deactivate_user_sessions(self, user_id: str) -> None:
        """사용자 세션 비활성화"""
        try:
            # 사용자의 모든 세션 조회
            session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
            
            # 각 세션 삭제
            for session_id in session_ids:
                await self.redis_client.delete(f"session:{session_id}")
            
            # 사용자 세션 목록 삭제
            await self.redis_client.delete(f"user_sessions:{user_id}")
            
        except Exception as e:
            raise DatabaseError(f"세션 비활성화 실패: {str(e)}")
    
    async def blacklist_token(self, token: str, expires_at: datetime) -> None:
        """토큰 블랙리스트 추가"""
        try:
            # 토큰 해시값으로 키 생성
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # 만료 시간까지 블랙리스트 저장
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis_client.setex(f"blacklist:{token_hash}", ttl, "1")
                
        except Exception as e:
            raise DatabaseError(f"토큰 블랙리스트 추가 실패: {str(e)}")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """토큰 블랙리스트 확인"""
        try:
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            exists = await self.redis_client.exists(f"blacklist:{token_hash}")
            return bool(exists)
            
        except Exception as e:
            return False
    
    async def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None:
        """리프레시 토큰 저장"""
        try:
            # 기존 토큰 삭제
            await self.redis_client.delete(f"refresh_token:{user_id}")
            
            # 새 토큰 저장
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis_client.setex(f"refresh_token:{user_id}", ttl, token)
                
        except Exception as e:
            raise DatabaseError(f"리프레시 토큰 저장 실패: {str(e)}")


class HybridAuthRepository(IAuthRepositoryPort):
    """MariaDB + Redis 하이브리드 Auth 리포지토리"""
    
    def __init__(self, session: AsyncSession, redis_client=None):
        self.mariadb_repo = MariaDBAuthRepository(session)
        self.redis_repo = RedisAuthRepository(redis_client) if redis_client else None
    
    async def create_session(self, session_data: Dict[str, Any]) -> None:
        if self.redis_repo:
            await self.redis_repo.create_session(session_data)
    
    async def deactivate_user_sessions(self, user_id: str) -> None:
        if self.redis_repo:
            await self.redis_repo.deactivate_user_sessions(user_id)
    
    async def blacklist_token(self, token: str, expires_at: datetime) -> None:
        if self.redis_repo:
            await self.redis_repo.blacklist_token(token, expires_at)
    
    async def is_token_blacklisted(self, token: str) -> bool:
        if self.redis_repo:
            return await self.redis_repo.is_token_blacklisted(token)
        return False
    
    async def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None:
        if self.redis_repo:
            await self.redis_repo.store_refresh_token(user_id, token, expires_at)

    async def update_user_social_info(
        self,
        user_id: str,
        social_provider: str,
        social_id: str,
        profile_image_url: Optional[str]
    ) -> None:
        return await self.mariadb_repo.update_user_social_info(
            user_id, social_provider, social_id, profile_image_url
        )
    
    async def get_kakao_user_info(self, code: str) -> SocialUserInfo:
        """카카오 사용자 정보 조회"""
        from ...common.config.settings import settings
        
        config = KakaoOAuthConfig(
            client_id=settings.KAKAO_CLIENT_ID,
            redirect_uri=f"{settings.FRONTEND_URL}/auth/social/kakao/callback",
            auth_url=settings.KAKAO_AUTH_URL,
            token_url=settings.KAKAO_TOKEN_URL,
            user_info_url=settings.KAKAO_USER_INFO_URL,
            logout_url=settings.KAKAO_LOGOUT_URL
        )
        
        client = KakaoOAuthClient(config)
        try:
            # 1. 인증 코드로 액세스 토큰 획득
            token_response = await client.get_access_token(code)
            access_token = token_response.get('access_token')
            
            if not access_token:
                raise Exception("카카오 액세스 토큰 획득 실패")
            
            # 2. 액세스 토큰으로 사용자 정보 조회
            user_info = await client.get_user_info(access_token)
            return user_info
            
        finally:
            await client.close()
    
    async def get_naver_user_info(self, code: str) -> SocialUserInfo:
        """네이버 사용자 정보 조회"""
        from ...common.config.settings import settings
        
        config = NaverOAuthConfig(
            client_id=settings.NAVER_CLIENT_ID,
            client_secret=settings.NAVER_CLIENT_SECRET,
            redirect_uri=f"{settings.FRONTEND_URL}/auth/social/naver/callback",
            auth_url=settings.NAVER_AUTH_URL,
            token_url=settings.NAVER_TOKEN_URL,
            user_info_url=settings.NAVER_USER_INFO_URL
        )
        
        client = NaverOAuthClient(config)
        try:
            # 1. 인증 코드로 액세스 토큰 획득
            token_response = await client.get_access_token(code, state="STATE_VALUE")
            access_token = token_response.get('access_token')
            
            if not access_token:
                raise Exception("네이버 액세스 토큰 획득 실패")
            
            # 2. 액세스 토큰으로 사용자 정보 조회
            user_info = await client.get_user_info(access_token)
            return user_info
            
        finally:
            await client.close()


class SocialOAuthClient:
    """소셜 OAuth 클라이언트 베이스 클래스"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 생성"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """세션 정리"""
        if self.session and not self.session.closed:
            await self.session.close()


class KakaoOAuthClient(SocialOAuthClient):
    """카카오 OAuth 클라이언트"""
    
    def __init__(self, config: KakaoOAuthConfig):
        super().__init__()
        self.config = config
    
    async def get_access_token(self, code: str) -> Dict[str, Any]:
        """인증 코드로 액세스 토큰 획득"""
        try:
            session = await self._get_session()
            
            # old-docs/login/kakao_lib.php와 동일: client_secret 사용 안함
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.config.client_id,
                'redirect_uri': self.config.redirect_uri,
                'code': code
            }

            # 디버깅: 실제 요청 파라미터 로깅
            print(f"[DEBUG] 카카오 토큰 요청 URL: {self.config.token_url}")
            print(f"[DEBUG] 카카오 토큰 요청 파라미터: {data}")
            print(f"[DEBUG] Client ID: {self.config.client_id}")
            print(f"[DEBUG] Redirect URI: {self.config.redirect_uri}")
            print(f"[DEBUG] Code (앞 10자리): {code[:10]}...")
            print(f"[DEBUG] 카카오 API 호출 시작...")
            
            async with session.post(self.config.token_url, data=data) as response:
                print(f"[DEBUG] 카카오 API 응답 상태: {response.status}")
                
                # 응답 텍스트 먼저 받기
                response_text = await response.text()
                print(f"[DEBUG] 카카오 API 응답 텍스트: {response_text}")
                
                # JSON 파싱 시도
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 파싱 실패: {e}")
                    raise Exception(f"카카오 API 응답 JSON 파싱 실패: {response_text}")
                
                if response.status != 200:
                    print(f"[ERROR] 카카오 토큰 요청 실패 - 상태코드: {response.status}")
                    raise Exception(f"카카오 토큰 요청 실패: {result}")
                
                print(f"[DEBUG] 카카오 토큰 요청 성공: {result}")
                return result
                
        except Exception as e:
            print(f"[ERROR] 카카오 get_access_token 예외 발생: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR] 스택 트레이스: {traceback.format_exc()}")
            raise e
    
    async def get_user_info(self, access_token: str) -> SocialUserInfo:
        """Access token으로 사용자 정보 조회"""
        session = await self._get_session()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        # old-docs/login/kakao_lib.php와 동일: POST 요청, 빈 body
        async with session.post(self.config.user_info_url, headers=headers, data={}) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"카카오 사용자 정보 요청 실패: {result}")
            
            # 디버깅: 카카오 API 응답 로깅
            print(f"[DEBUG] 카카오 API 응답: {result}")
            
            # 카카오 응답 데이터 파싱
            kakao_account = result.get('kakao_account', {})
            profile = kakao_account.get('profile', {})
            
            # 디버깅: 이메일 정보 확인
            email = kakao_account.get('email')
            print(f"[DEBUG] 카카오 이메일: {email}")
            print(f"[DEBUG] kakao_account: {kakao_account}")
            
            return SocialUserInfo(
                provider=AuthProvider.KAKAO,
                social_id=str(result.get('id')),  # old-docs처럼 카카오 ID 사용 (kko+id 패턴용)
                email=kakao_account.get('email'),
                name=profile.get('nickname'),
                nickname=profile.get('nickname'),
                profile_image=profile.get('profile_image_url'),
                raw_data=result
            )
    
    async def logout(self, access_token: str) -> Dict[str, Any]:
        """사용자 로그아웃"""
        session = await self._get_session()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        async with session.post(self.config.logout_url, headers=headers) as response:
            result = await response.json()
            return result


class NaverOAuthClient(SocialOAuthClient):
    """네이버 OAuth 클라이언트"""
    
    def __init__(self, config: NaverOAuthConfig):
        super().__init__()
        self.config = config
    
    async def get_access_token(self, code: str, state: str) -> Dict[str, Any]:
        """인증 코드로 액세스 토큰 획득"""
        session = await self._get_session()
        
        # old-docs/login/naver_lib.php와 동일: GET 요청 + redirect_uri 포함
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'redirect_uri': self.config.redirect_uri,
            'code': code,
            'state': state
        }
        
        async with session.get(self.config.token_url, params=params) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"네이버 토큰 요청 실패: {result}")
            
            return result
    
    async def get_user_info(self, access_token: str) -> SocialUserInfo:
        """Access token으로 사용자 정보 조회"""
        session = await self._get_session()
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        async with session.get(self.config.user_info_url, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"네이버 사용자 정보 요청 실패: {result}")
            
            # 네이버 응답 데이터 파싱
            response_data = result.get('response', {})
            
            return SocialUserInfo(
                provider=AuthProvider.NAVER,
                social_id=response_data.get('email'),  # 기존 PHP 시스템과 동일 (이메일 사용)
                email=response_data.get('email'),
                name=response_data.get('name'),
                nickname=response_data.get('nickname'),
                profile_image=response_data.get('profile_image'),
                raw_data=result
            ) 