"""
데이터베이스 베이스 모델 및 믹스인

모든 모델이 상속받는 기본 클래스와 공통 필드 정의
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    모든 모델의 기본 클래스
    
    SQLAlchemy 2.0 스타일의 DeclarativeBase 사용
    """
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True


class TimestampMixin:
    """
    생성/수정 시간 자동 관리 믹스인
    
    모든 모델에 created_at, updated_at 필드 추가
    """
    
    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True
    
    @declared_attr
    def created_at(cls):
        """생성 시간 (자동 설정)"""
        return Column(
            DateTime,
            nullable=False,
            server_default=func.now(),
            comment="생성 시간"
        )
    
    @declared_attr
    def updated_at(cls):
        """수정 시간 (자동 갱신)"""
        return Column(
            DateTime,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            comment="수정 시간"
        )

