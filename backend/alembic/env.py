"""
Alembic 환경 설정 파일

SQLAlchemy 마이그레이션 환경을 구성하고
비동기 데이터베이스 연결을 지원합니다.
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# backend 모듈을 import할 수 있도록 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# 설정 및 모델 import
from src.config.settings import settings
from src.models.user_model import Base  # Base 메타데이터
# 모든 모델을 import (중요!)
from src.models.user_model import User
# 사주 지식베이스 모델 (Story 2.1)
from src.models.saju_cheongan_model import SajuCheongan
from src.models.saju_jiji_model import SajuJiji
from src.models.saju_sipsung_model import SajuSipsungInterpretation
from src.models.saju_jiji_relation_model import SajuJijiRelation
from src.models.fortune_history_model import FortuneHistory

# Alembic Config 객체
config = context.config

# 설정 파일에서 DATABASE_URL 가져오기 (동기 버전)
# mariadb_url은 aiomysql을 사용하므로 Alembic용 동기 URL로 변환
sync_url = settings.mariadb_url.replace("+aiomysql", "+pymysql")
config.set_main_option("sqlalchemy.url", sync_url)

# Python 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터 설정 (모든 모델이 포함됨)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    오프라인 모드에서 마이그레이션 실행
    
    데이터베이스에 연결하지 않고 SQL 스크립트만 생성
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """실제 마이그레이션 실행"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 모드에서 마이그레이션 실행"""

    # 비동기 엔진 설정 수정
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.mariadb_url  # 비동기 URL 사용

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    온라인 모드에서 마이그레이션 실행
    
    실제 데이터베이스에 연결하여 마이그레이션 수행
    """
    asyncio.run(run_async_migrations())


# Alembic 실행 모드 결정
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()