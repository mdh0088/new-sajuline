"""
관리자/상담사 인증 API (로그인/로그아웃)
"""
from fastapi import APIRouter, Depends, Response, Request

from src.common.response import ok, APIResponse
from src.schemas.auth_schema import LoginRequest, LoginResponse, TokenPayload
from src.services.admin_service import AdminService
from src.services.counselor_service import CounselorService
from src.services.auth_service import AuthService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.core.database import get_db as get_db_maria, get_db_mssql
from src.repositories.admin_repository import AdminRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.services.ars.tm60_member_service import Tm60MemberService


def get_auth_service() -> AuthService:
    return AuthService()


def get_admin_service(
    admin_repo: AdminRepository = Depends(lambda db=Depends(get_db_maria): AdminRepository(db)),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminService:
    return AdminService(admin_repo, auth_service)


def get_counselor_service(
    counselor_repo: CounselorRepository = Depends(lambda db=Depends(get_db_maria): CounselorRepository(db)),
    auth_service: AuthService = Depends(get_auth_service),
    tm60_service: Tm60MemberService = Depends(lambda mssql=Depends(get_db_mssql): Tm60MemberService(Tm60MemberRepository(mssql))),
) -> CounselorService:
    return CounselorService(counselor_repo, auth_service, tm60_service)
from src.common.utils.auth_utils import verify_admin_role, verify_counselor_role


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    # Access Token (쿠키: 30분)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 60,
    )
    # Refresh Token (쿠키: 7일)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/admin/login", response_model=APIResponse[LoginResponse], summary="관리자 로그인")
async def admin_login(
    login_request: LoginRequest,
    response: Response,
    admin_service: AdminService = Depends(get_admin_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, summary = await admin_service.login(login_request.user_id, login_request.password)
    refresh_token = auth_service.create_refresh_token(user_id=summary["user_id"], email=summary["email"], role="admin")

    _set_auth_cookies(response, access_token, refresh_token)

    return ok(
        data=LoginResponse(
            user_id=summary["user_id"],
            email=summary["email"],
            nickname=summary["nickname"],
            access_token_expires_in=30 * 60,
            refresh_token_expires_in=7 * 24 * 60 * 60,
        ),
        message="관리자 로그인 성공",
    )


@router.post("/admin/logout", summary="관리자 로그아웃")
async def admin_logout(response: Response):
    _clear_auth_cookies(response)
    return ok(data=None, message="관리자 로그아웃 성공")


@router.post("/counselor/login", response_model=APIResponse[LoginResponse], summary="상담사 로그인(관리자)")
async def counselor_login(
    login_request: LoginRequest,
    response: Response,
    counselor_service: CounselorService = Depends(get_counselor_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, summary = await counselor_service.login(login_request.user_id, login_request.password)
    refresh_token = auth_service.create_refresh_token(user_id=summary["user_id"], email=summary["email"], role="counselor")

    _set_auth_cookies(response, access_token, refresh_token)

    return ok(
        data=LoginResponse(
            user_id=summary["user_id"],
            email=summary["email"],
            nickname=summary["nickname"],
            access_token_expires_in=30 * 60,
            refresh_token_expires_in=7 * 24 * 60 * 60,
        ),
        message="상담사 로그인 성공",
    )


@router.post("/counselor/logout", summary="상담사 로그아웃(관리자)")
async def counselor_logout(response: Response):
    _clear_auth_cookies(response)
    return ok(data=None, message="상담사 로그아웃 성공")
