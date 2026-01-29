"""
사주 지식베이스 Repository 클래스

Story 2.4 Task 2: 사주 데이터 조회 (AC: 1, 5)
- 천간/지지/십성 해석 데이터 조회
- 조회 실패 시 None 반환 (폴백 지원)
"""
from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.saju_cheongan_model import SajuCheongan
from src.models.saju_jiji_model import SajuJiji
from src.models.saju_sipsung_model import SajuSipsungInterpretation
from src.models.saju_jiji_relation_model import SajuJijiRelation
from src.common.logging import logger, get_logger_with_request_id


class SajuRepository:
    """
    사주 지식베이스 리포지토리

    천간, 지지, 십성 해석, 지지 관계 데이터를 조회합니다.
    LLM RAG 체인에서 컨텍스트로 사용됩니다.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @logger.catch(reraise=True)
    async def get_sipsung_interpretation(
        self,
        ilgan: str,
        sipsung: str
    ) -> Optional[SajuSipsungInterpretation]:
        """
        일간+십성 조합의 해석 조회

        Args:
            ilgan: 일간 (갑, 을, 병, ...)
            sipsung: 십성 (비견, 겁재, 식신, ...)

        Returns:
            SajuSipsungInterpretation 또는 None
        """
        log = get_logger_with_request_id()
        log.debug("Fetching sipsung interpretation", ilgan=ilgan, sipsung=sipsung)

        stmt = select(SajuSipsungInterpretation).where(
            SajuSipsungInterpretation.ilgan == ilgan,
            SajuSipsungInterpretation.sipsung == sipsung
        )
        result = await self.session.execute(stmt)
        interpretation = result.scalar_one_or_none()

        log.debug(
            "Sipsung interpretation lookup completed",
            ilgan=ilgan,
            sipsung=sipsung,
            found=interpretation is not None
        )
        return interpretation

    @logger.catch(reraise=True)
    async def get_jiji_relation(
        self,
        jiji1: str,
        jiji2: str
    ) -> Optional[SajuJijiRelation]:
        """
        두 지지 간의 관계 조회 (합/충/형/파/해)

        양방향 조회를 지원합니다 (자축합 = 축자합).

        Args:
            jiji1: 첫 번째 지지
            jiji2: 두 번째 지지

        Returns:
            SajuJijiRelation 또는 None (관계 없음)
        """
        log = get_logger_with_request_id()
        log.debug("Fetching jiji relation", jiji1=jiji1, jiji2=jiji2)

        # 정방향 조회
        stmt = select(SajuJijiRelation).where(
            SajuJijiRelation.jiji1 == jiji1,
            SajuJijiRelation.jiji2 == jiji2
        )
        result = await self.session.execute(stmt)
        relation = result.scalar_one_or_none()

        # 역방향 조회 (자축합 = 축자합)
        if not relation:
            stmt = select(SajuJijiRelation).where(
                SajuJijiRelation.jiji1 == jiji2,
                SajuJijiRelation.jiji2 == jiji1
            )
            result = await self.session.execute(stmt)
            relation = result.scalar_one_or_none()

        log.debug(
            "Jiji relation lookup completed",
            jiji1=jiji1,
            jiji2=jiji2,
            found=relation is not None,
            relation_type=relation.relation_type if relation else None
        )
        return relation

    @logger.catch(reraise=True)
    async def get_cheongan_by_name(self, name: str) -> Optional[SajuCheongan]:
        """
        천간 이름으로 조회

        Args:
            name: 천간 이름 (갑, 을, 병, ...)

        Returns:
            SajuCheongan 또는 None
        """
        stmt = select(SajuCheongan).where(SajuCheongan.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @logger.catch(reraise=True)
    async def get_jiji_by_name(self, name: str) -> Optional[SajuJiji]:
        """
        지지 이름으로 조회

        Args:
            name: 지지 이름 (자, 축, 인, ...)

        Returns:
            SajuJiji 또는 None
        """
        stmt = select(SajuJiji).where(SajuJiji.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @logger.catch(reraise=True)
    async def get_all_cheongan(self) -> List[SajuCheongan]:
        """
        모든 천간 조회 (10개)

        Returns:
            List[SajuCheongan]: 천간 목록 (갑~계)
        """
        stmt = select(SajuCheongan).order_by(SajuCheongan.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @logger.catch(reraise=True)
    async def get_all_jiji(self) -> List[SajuJiji]:
        """
        모든 지지 조회 (12개)

        Returns:
            List[SajuJiji]: 지지 목록 (자~해)
        """
        stmt = select(SajuJiji).order_by(SajuJiji.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
