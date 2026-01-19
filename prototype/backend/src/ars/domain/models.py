"""
ARS(MSSQL) 도메인 모델

외부 MSSQL(ARS) 스키마 매핑 모델 정의
"""

from sqlalchemy import Column, Integer, Unicode, DateTime, UniqueConstraint, text

from src.common.database.base import Base


class TM60User(Base):
    """ARS 유저 테이블 매핑 (dbo.tm60_users)

    - NVARCHAR 매핑을 위해 Unicode 사용
    - created_at 서버 기본값은 MSSQL GETDATE() 사용
    - 이메일 유니크 인덱스 이름: UX_tm60_users_email
    """

    __tablename__ = "tm60_users"
    __table_args__ = (
        {"schema": "dbo"},
    )

    # SQLAlchemy 2.0에서 Mapped[] 타입 없이 어노테이션 허용
    __allow_unmapped__ = True

    user_id = Column("idx", Integer, primary_key=True, autoincrement=True, comment="PK(idx)")
    # 실제 스키마 컬럼 매핑 (01_schema_tables.sql 기준)
    u_id = Column(Unicode(50), nullable=False, server_default=text("''"), comment="사용자아이디")
    u_tel = Column(Unicode(18), nullable=False, server_default=text("''"), comment="전화번호")
    u_passwd = Column(Unicode(4), nullable=False, server_default=text("''"), comment="비밀번호(4)")
    u_kname = Column(Unicode(12), nullable=False, server_default=text("''"), comment="이름")
    u_memcd = Column(Unicode(1), nullable=False, server_default=text("'1'"), comment="회원코드")
    u_login = Column(Unicode(1), nullable=False, server_default=text("'1'"), comment="로그인여부")
    u_state = Column(Unicode(1), nullable=False, server_default=text("'0'"), comment="상태")
    u_point = Column(Integer, nullable=False, server_default=text("(0)"), comment="포인트")
    u_fdate = Column(DateTime, nullable=True, comment="첫로그인일")
    u_rdate = Column(DateTime, nullable=True, comment="최근로그인일")
    regdate = Column(DateTime, nullable=True, comment="등록일")
    u_memo = Column(Unicode(255), nullable=False, server_default=text("''"), comment="메모")


