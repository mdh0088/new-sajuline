"""
모든 도메인 모델 수집

Alembic 마이그레이션이 모든 모델을 인식할 수 있도록
각 도메인의 모델을 import합니다.
"""

# User Domain
from src.user.domain.models import (
    User, Admin, SystemConfig, Notice, FAQ
)

# Counselor Domain
from src.counselor.domain.models import Counselor, CounselorSpecialty

# ARS Domain (MSSQL)
from src.ars.domain.models import TM60User as ARS_TM60User




# 모든 모델 목록 (Alembic에서 사용)
__all__ = [
    # User Domain
    "User",
    "Admin", 
    "SystemConfig",
    "Notice",
    "FAQ",
    # Counselor Domain
    "Counselor",
    "CounselorSpecialty",
    # ARS Domain
    "ARS_TM60User",
] 