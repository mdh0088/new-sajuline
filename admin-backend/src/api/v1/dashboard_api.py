"""
대시보드 API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard/test")
async def test_dashboard():
    """대시보드 테스트 엔드포인트"""
    return {"message": "Dashboard API is working"}