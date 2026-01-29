"""
API v1 라우터들
"""
from src.api.v1.fortune_api import router as fortune_router

__all__ = [
    "fortune_router",
]