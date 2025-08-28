"""
사용자 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.models.user import User, UserStatus
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from src.repositories.user import UserRepository
from src.services.auth import AuthService


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
        # 중복 검증
        if await self.user_repo.exists_by_user_id(user_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자 ID입니다."
            )
        
        if await self.user_repo.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 이메일입니다."
            )
        
        if await self.user_repo.exists_by_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 전화번호입니다."
            )
        
        # 비밀번호 해싱 (소셜 로그인이 아닌 경우)
        password_hash = None
        if user_data.password and user_data.join_type.value == "COMMON":
            password_hash = self.auth_service.hash_password(user_data.password)
        
        # 사용자 생성
        user = await self.user_repo.create(user_data, password_hash)
        
        return UserResponse.model_validate(user)
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """사용자 조회"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        return UserResponse.model_validate(user)
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """이메일로 사용자 조회"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        return UserResponse.model_validate(user)
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        사용자 정보 수정 비즈니스 로직
        - 존재 여부 확인
        - 중복 검증 (닉네임, 전화번호 변경시)
        - 정보 수정
        """
        # 사용자 존재 여부 확인
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 전화번호 변경시 중복 검증
        if user_data.phone and user_data.phone != existing_user.phone:
            if await self.user_repo.exists_by_phone(user_data.phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 전화번호입니다."
                )
        
        # 사용자 정보 수정
        updated_user = await self.user_repo.update(user_id, user_data)
        
        return UserResponse.model_validate(updated_user) if updated_user else None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제 비즈니스 로직
        - 존재 여부 확인
        - 삭제 처리
        """
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
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
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        skip = (page - 1) * size
        
        # 상태 검증
        if user_status and user_status not in [status.value for status in UserStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 사용자 상태입니다."
            )
        
        users = await self.user_repo.get_list(skip, size, user_status)
        total = await self.user_repo.get_count(user_status)
        
        user_responses = [UserResponse.model_validate(user) for user in users]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            size=size
        )
    
    async def authenticate_user(self, user_id_or_email: str, password: str) -> Optional[UserResponse]:
        """
        사용자 인증 비즈니스 로직
        - 사용자 ID 또는 이메일로 조회
        - 비밀번호 검증
        - 계정 잠금 확인
        """
        # 사용자 조회 (ID 또는 이메일)
        user = None
        if "@" in user_id_or_email:
            user = await self.user_repo.get_by_email(user_id_or_email)
        else:
            user = await self.user_repo.get_by_id(user_id_or_email)
        
        if not user:
            return None
        
        # 계정 잠금 확인
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"계정이 {user.locked_until}까지 잠겨있습니다."
            )
        
        # 비밀번호 검증
        if not user.password_hash or not self.auth_service.verify_password(password, user.password_hash):
            return None
        
        return UserResponse.model_validate(user)
    
    async def login(self, user_id_or_email: str, password: str) -> Tuple[str, UserResponse]:
        """
        사용자 로그인 비즈니스 로직
        - 사용자 인증
        - JWT 토큰 생성
        - 로그인 실패 횟수 관리
        - 마지막 로그인 시간 업데이트
        """
        # 사용자 인증
        user_response = await self.authenticate_user(user_id_or_email, password)
        
        if not user_response:
            # 실패 횟수 증가 (실제 사용자가 있는 경우)
            user = None
            if "@" in user_id_or_email:
                user = await self.user_repo.get_by_email(user_id_or_email)
            else:
                user = await self.user_repo.get_by_id(user_id_or_email)
            
            if user:
                await self.user_repo.increment_failed_login(user.user_id)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다"
            )
        
        # 계정 상태 확인
        user = await self.user_repo.get_by_id(user_response.user_id)
        if user.user_status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="계정이 비활성화되었습니다"
            )
        
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
        
        return access_token, user_response