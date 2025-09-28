"""
관리자 관리 API (권한 체크 예시 포함)
"""
from fastapi import APIRouter, Depends

from src.common.response import ok
from src.services.security import get_current_user
from src.schemas.auth_schema import TokenPayload
from src.common.utils.auth_utils import verify_admin_role


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/test")
async def test_admin(current_user: TokenPayload = Depends(get_current_user)):
    verify_admin_role(current_user)
    return ok({"message": "Admin management API is working"})