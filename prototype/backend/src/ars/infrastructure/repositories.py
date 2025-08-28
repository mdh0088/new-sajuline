"""
ARS 인프라스트럭처 - MSSQL 리포지토리
"""

from datetime import datetime

from sqlalchemy.orm import Session as SyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import anyio

from src.ars.domain.models import TM60User
from src.ars.domain.entities import ARSUser
from src.ars.domain.ports import ARSUserRepositoryPort as IARSUserRepositoryPort
from src.common.exceptions.custom import DatabaseError, ConflictException

class MSSQLARSUserRepository(IARSUserRepositoryPort):
    """MSSQL ARS User 리포지토리 구현 (동기 세션을 비동기 메서드에서 안전히 사용)"""

    def __init__(self, session: SyncSession):
        self.session = session

    async def create_tm60_user(
        self,
        u_id: str,
        u_tel: str,
        u_kname: str,
        u_passwd: str = "",
    ) -> ARSUser:
        def _work() -> TM60User:
            try:
                entity = TM60User(
                    u_id=u_id,
                    u_tel=u_tel or "",
                    u_passwd=(u_passwd or "")[:4],  # 요구: 빈 란 저장
                    u_kname=u_kname or u_id,
                    regdate=datetime.utcnow(),       # 요구: 등록일 현재값
                )
                self.session.add(entity)
                self.session.commit()
                self.session.refresh(entity)
                return entity
            except IntegrityError as e:
                self.session.rollback()
                raise ConflictException(f"TM60 사용자 생성 실패 - 제약 위반: {str(e)}")
            except SQLAlchemyError as e:
                self.session.rollback()
                raise DatabaseError(f"TM60 사용자 생성 실패: {str(e)}")

        # 블로킹 작업을 워커 스레드에서 실행 후 도메인 엔티티로 매핑
        sa_user = await anyio.to_thread.run_sync(_work)
        return ARSUser(
            user_id=sa_user.user_id,
            u_id=sa_user.u_id,
            u_tel=sa_user.u_tel,
            u_kname=sa_user.u_kname,
            u_passwd=sa_user.u_passwd,
            regdate=sa_user.regdate,
        )


