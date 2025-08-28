"""
사용자 관련 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria
from src.repositories.user import UserRepository
from src.services.user import UserService
from src.services.auth import AuthService
from src.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    UserLogin, PasswordChange
)
from src.schemas.auth import LoginRequest, LoginData
from src.schemas.response import APIResponse, ok, fail

router = APIRouter(prefix="/users", tags=["users"])


# Dependency injection functions
def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    """사용자 리포지토리 의존성 주입"""
    return UserRepository(db)


def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserService:
    """사용자 서비스 의존성 주입"""
    return UserService(user_repo, auth_service)


@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
    responses={
        201: {"description": "성공"},
        400: {"description": "중복된 사용자 정보"}
    }
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 생성 - 중복 검증 및 비밀번호 해싱"""
    return await user_service.create_user(user_data)


@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="사용자 조회",
    responses={404: {"description": "사용자 없음"}}
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 ID로 조회"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return user


@router.get(
    "/email/{email}", 
    response_model=UserResponse,
    summary="이메일로 사용자 조회",
    responses={404: {"description": "사용자 없음"}}
)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """이메일로 사용자 조회"""
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return user


@router.put(
    "/{user_id}", 
    response_model=UserResponse,
    summary="사용자 정보 수정",
    responses={404: {"description": "사용자 없음"}}
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 정보 수정 - 중복 검증 포함"""
    return await user_service.update_user(user_id, user_data)


@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    responses={404: {"description": "사용자 없음"}}
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 삭제"""
    await user_service.delete_user(user_id)


@router.get(
    "/", 
    response_model=UserListResponse,
    summary="사용자 목록 조회",
    description="페이지네이션과 상태 필터 지원"
)
async def get_user_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    user_status: Optional[str] = Query(None, description="사용자 상태 필터"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 목록 조회 - 페이징 및 상태별 필터링"""
    return await user_service.get_user_list(page, size, user_status)


@router.post(
    "/authenticate", 
    response_model=UserResponse,
    summary="사용자 인증",
    responses={
        401: {"description": "인증 실패"},
        423: {"description": "계정 잠금"}
    }
)
async def authenticate_user(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 인증 - ID/이메일 및 비밀번호 검증"""
    user = await user_service.authenticate_user(login_data.user_id, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자 정보입니다."
        )
    return user


@router.post(
    "/login",
    response_model=APIResponse[LoginData],
    summary="사용자 로그인",
    description="사용자 ID와 비밀번호로 로그인하고 JWT 토큰을 HttpOnly 쿠키에 설정",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "인증 실패"},
        403: {"description": "계정 비활성화"},
        423: {"description": "계정 잠금"}
    }
)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_maria),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 로그인"""
    try:
        # 로그인 처리
        access_token, user_response = await user_service.login(
            user_id_or_email=request.user_id,
            password=request.password
        )
        
        # HttpOnly 쿠키에 JWT 토큰 설정
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # HTTPS에서만 전송
            samesite="lax",  # CSRF 보호
            max_age=30 * 60  # 30분
        )
        
        # 응답 데이터 생성
        login_data = LoginData(
            user_id=user_response.user_id,
            email=user_response.email,
            nickname=user_response.nickname
        )
        
        return ok(data=login_data, message="로그인 성공")
        
    except HTTPException as e:
        print(f"HTTPException in login: {e.detail}, status: {e.status_code}")
        return fail(message=e.detail, code=str(e.status_code))
    except Exception as e:
        print(f"Unexpected error in login: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return fail(message="로그인 처리 중 오류가 발생했습니다", code="INTERNAL_SERVER_ERROR")


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="사용자 로그아웃",
    description="현재 로그인된 사용자를 로그아웃하고 JWT 토큰 쿠키를 삭제",
    responses={200: {"description": "로그아웃 성공"}}
)
async def logout(response: Response):
    """사용자 로그아웃"""
    try:
        # HttpOnly 쿠키에서 JWT 토큰 삭제
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return ok(data=None, message="로그아웃 성공")
        
    except Exception as e:
        print(f"Unexpected error in logout: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return fail(message="로그아웃 처리 중 오류가 발생했습니다", code="INTERNAL_SERVER_ERROR")