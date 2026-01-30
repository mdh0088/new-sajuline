"""
운세 비즈니스 로직 서비스

Story 2.4 Task 6: Fortune 서비스 구현 (AC: 1, 3, 5)
- get_daily_fortune() 메인 메서드
- 캐시 확인 → LLM 호출 → 폴백 순서
- source 필드 설정 ("llm" | "fallback" | "cache")
"""
from datetime import date, timedelta
from typing import Optional, Tuple

from src.common.utils.saju_calculator import (
    get_ilju,
    calculate_sipsung,
    calculate_luck_score,
    get_oheng,
    get_yin_yang,
    get_year_pillar,
    get_month_branch,
    get_month_energy,
    get_month_name,
    get_year_energy,
)
from src.core.langchain_chain import DailyFortuneChain
from src.models.fortune_history_model import FortuneType
from src.repositories.saju_repository import SajuRepository
from src.services.fortune_cache_service import FortuneCacheService
from src.schemas.fortune_schema import FortuneResponse, DayPillar
from src.common.logging import logger, get_logger_with_request_id


class FortuneService:
    """
    운세 비즈니스 로직 서비스

    캐시 → LLM → 폴백 순서로 운세를 조회/생성합니다.
    LLM 실패 시 DB 기본 해석으로 폴백하여 서비스 가용성을 보장합니다.
    """

    def __init__(
        self,
        saju_repo: SajuRepository,
        cache_service: FortuneCacheService,
        chain: DailyFortuneChain
    ):
        self.saju_repo = saju_repo
        self.cache_service = cache_service
        self.chain = chain

    @logger.catch(reraise=True)
    async def get_daily_fortune(
        self,
        user_id: str,
        birth_stem: str,  # 사용자 일간 (천간)
        birth_branch: str,  # 사용자 일지 (지지)
        target_date: Optional[date] = None
    ) -> FortuneResponse:
        """
        일일 운세 조회 (캐시 → LLM → 폴백)

        Args:
            user_id: 사용자 ID
            birth_stem: 사용자 일간 (갑, 을, 병 ...)
            birth_branch: 사용자 일지 (자, 축, 인 ...)
            target_date: 운세 날짜 (기본: 오늘)

        Returns:
            FortuneResponse: 운세 응답
        """
        log = get_logger_with_request_id()
        target_date = target_date or date.today()

        log.info(
            "Getting daily fortune",
            user_id=user_id,
            birth_stem=birth_stem,
            target_date=str(target_date)
        )

        # 1. 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.DAILY, target_date
        )
        if cached:
            log.info("Fortune cache hit", status=status, user_id=user_id)
            return cached

        # 2. 일진 계산
        day_gan, day_ji = get_ilju(target_date)

        # 3. 십성 계산
        sipsung = calculate_sipsung(day_gan, birth_stem)

        # 4. 사주 데이터 조회
        sipsung_data = await self.saju_repo.get_sipsung_interpretation(
            birth_stem, sipsung
        )
        jiji_data = await self.saju_repo.get_jiji_relation(
            birth_branch, day_ji
        )

        # 5. 폴백 데이터 준비
        sipsung_interp = self._get_sipsung_fallback(
            sipsung_data, birth_stem, sipsung
        )
        jiji_interp = self._get_jiji_fallback(jiji_data, birth_branch, day_ji)
        jiji_relation_type = jiji_data.relation_type if jiji_data else "무관"

        # 6. luck_score 계산 (LLM 독립)
        luck_score = calculate_luck_score(sipsung, jiji_relation_type, "총운")

        # 7. 키워드 추출
        keywords = self._extract_keywords(sipsung_data, jiji_data)

        try:
            # 8. LLM 호출
            llm_output = await self.chain.generate_fortune(
                ilgan=birth_stem,
                ilgan_oheng=get_oheng(birth_stem),
                ilgan_yin_yang=get_yin_yang(birth_stem),
                day_gan=day_gan,
                day_ji=day_ji,
                sipsung=sipsung,
                sipsung_interpretation=sipsung_interp,
                jiji_relation=f"{birth_branch} ↔ {day_ji} = {jiji_relation_type}",
                jiji_interpretation=jiji_interp,
                today=target_date.isoformat(),
            )

            fortune = self._build_response(
                target_date=target_date,
                day_gan=day_gan,
                day_ji=day_ji,
                llm_output=llm_output,
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords,
                source="llm"
            )

            log.info("Fortune generated via LLM", user_id=user_id)

        except Exception as e:
            # 9. 폴백: DB 데이터로 기본 응답
            log.warning(
                "LLM fallback triggered",
                error=str(e),
                user_id=user_id
            )
            fortune = self._build_fallback_response(
                target_date=target_date,
                day_gan=day_gan,
                day_ji=day_ji,
                sipsung_interp=sipsung_interp,
                jiji_interp=jiji_interp,
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords
            )

        # 10. 캐시 저장
        await self.cache_service.set_fortune_cache(
            user_id, FortuneType.DAILY, target_date, fortune
        )

        return fortune

    def _get_sipsung_fallback(
        self,
        data: Optional[object],
        ilgan: str,
        sipsung: str
    ) -> str:
        """십성 해석 폴백"""
        if data and hasattr(data, 'daily_advice') and data.daily_advice:
            return data.daily_advice
        return f"{ilgan} 일간이 {sipsung}을 만났습니다. 평온한 하루 되세요."

    def _get_jiji_fallback(
        self,
        data: Optional[object],
        jiji1: str,
        jiji2: str
    ) -> str:
        """지지 관계 해석 폴백"""
        if data and hasattr(data, 'daily_impact') and data.daily_impact:
            return data.daily_impact
        return f"{jiji1}과 {jiji2}의 만남입니다. 안정적인 에너지가 흐릅니다."

    def _extract_keywords(
        self,
        sipsung_data: Optional[object],
        jiji_data: Optional[object]
    ) -> list[str]:
        """키워드 추출"""
        keywords = []
        if sipsung_data and hasattr(sipsung_data, 'keywords') and sipsung_data.keywords:
            keywords.extend(sipsung_data.keywords[:3])  # 최대 3개
        if jiji_data and hasattr(jiji_data, 'keywords') and jiji_data.keywords:
            keywords.extend(jiji_data.keywords[:2])  # 최대 2개
        return keywords[:5]  # 최종 5개 제한

    def _build_response(
        self,
        target_date: date,
        day_gan: str,
        day_ji: str,
        llm_output: object,
        luck_score: int,
        sipsung: str,
        keywords: list[str],
        source: str
    ) -> FortuneResponse:
        """LLM 응답으로 FortuneResponse 생성"""
        return FortuneResponse(
            target_date=target_date,
            fortune_type="daily",
            day_pillar=DayPillar(stem=day_gan, branch=day_ji),
            overall=llm_output.overall,
            love=llm_output.love,
            career=llm_output.career,
            health=llm_output.health,
            wealth=llm_output.wealth,
            lucky_color=llm_output.lucky_color,
            lucky_number=llm_output.lucky_number,
            source=source,
            luck_score=luck_score,
            sipsung=sipsung,
            keywords=keywords if keywords else None,
        )

    def _build_fallback_response(
        self,
        target_date: date,
        day_gan: str,
        day_ji: str,
        sipsung_interp: str,
        jiji_interp: str,
        luck_score: int,
        sipsung: str,
        keywords: list[str],
        fortune_type: str = "daily"
    ) -> FortuneResponse:
        """폴백 응답 생성"""
        return FortuneResponse(
            target_date=target_date,
            fortune_type=fortune_type,
            day_pillar=DayPillar(stem=day_gan, branch=day_ji),
            overall=f"{sipsung_interp} {jiji_interp}",
            love="애정 운세는 잠시 후 다시 확인해주세요.",
            career="직장 운세는 잠시 후 다시 확인해주세요.",
            health="건강 운세는 잠시 후 다시 확인해주세요.",
            wealth="재물 운세는 잠시 후 다시 확인해주세요.",
            lucky_color=None,
            lucky_number=None,
            source="fallback",
            luck_score=luck_score,
            sipsung=sipsung,
            keywords=keywords if keywords else None,
        )

    # =========================================================================
    # 주간 운세 (Story 2.6)
    # =========================================================================

    def _get_week_start(self, target_date: date) -> date:
        """주의 시작일(월요일) 계산"""
        return target_date - timedelta(days=target_date.weekday())

    def _get_week_end(self, target_date: date) -> date:
        """주의 종료일(일요일) 계산"""
        return target_date + timedelta(days=6 - target_date.weekday())

    def _build_weekly_pillar_summary(
        self,
        week_start: date,
        birth_stem: str
    ) -> Tuple[str, str, str]:
        """
        주간 일진 흐름 요약 및 주요 십성 계산

        Returns:
            Tuple[str, str, str]: (주간 일진 요약, 주요 십성, 주요 지지 관계)
        """
        summary_lines = []
        sipsung_counts: dict[str, int] = {}

        for i in range(7):
            day = week_start + timedelta(days=i)
            day_gan, day_ji = get_ilju(day)
            sipsung = calculate_sipsung(day_gan, birth_stem)

            # 요일 이름
            day_names = ["월", "화", "수", "목", "금", "토", "일"]
            day_name = day_names[i]

            summary_lines.append(f"- {day_name}요일({day.day}일): {day_gan}{day_ji} ({sipsung})")
            sipsung_counts[sipsung] = sipsung_counts.get(sipsung, 0) + 1

        # 주요 십성 (가장 많이 나온 것)
        main_sipsung = max(sipsung_counts, key=sipsung_counts.get)

        return "\n".join(summary_lines), main_sipsung, "합"

    @logger.catch(reraise=True)
    async def get_weekly_fortune(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> FortuneResponse:
        """
        주간 운세 조회 (캐시 → LLM → 폴백)

        Args:
            user_id: 사용자 ID
            birth_stem: 사용자 일간 (천간)
            birth_branch: 사용자 일지 (지지)
            target_date: 운세 기준 날짜 (기본: 오늘)

        Returns:
            FortuneResponse: 주간 운세 응답
        """
        log = get_logger_with_request_id()
        target_date = target_date or date.today()
        week_start = self._get_week_start(target_date)
        week_end = self._get_week_end(target_date)

        log.info(
            "Getting weekly fortune",
            user_id=user_id,
            birth_stem=birth_stem,
            week_start=str(week_start),
            week_end=str(week_end)
        )

        # 1. 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.WEEKLY, week_start
        )
        if cached:
            log.info("Weekly fortune cache hit", status=status, user_id=user_id)
            return cached

        # 2. 주간 일진 계산 및 요약
        weekly_summary, main_sipsung, jiji_relation_type = self._build_weekly_pillar_summary(
            week_start, birth_stem
        )

        # 3. 대표 일진 (주 시작일 기준)
        day_gan, day_ji = get_ilju(week_start)

        # 4. 사주 데이터 조회
        sipsung_data = await self.saju_repo.get_sipsung_interpretation(
            birth_stem, main_sipsung
        )
        jiji_data = await self.saju_repo.get_jiji_relation(
            birth_branch, day_ji
        )

        # 5. 폴백 데이터 준비
        sipsung_interp = self._get_sipsung_fallback(
            sipsung_data, birth_stem, main_sipsung
        )
        jiji_interp = self._get_jiji_fallback(jiji_data, birth_branch, day_ji)

        # 6. luck_score 계산
        luck_score = calculate_luck_score(main_sipsung, jiji_relation_type, "총운")

        # 7. 키워드 추출
        keywords = self._extract_keywords(sipsung_data, jiji_data)

        try:
            # 8. LLM 호출
            llm_output = await self.chain.generate_weekly_fortune(
                ilgan=birth_stem,
                ilgan_oheng=get_oheng(birth_stem),
                ilgan_yin_yang=get_yin_yang(birth_stem),
                week_start=week_start.isoformat(),
                week_end=week_end.isoformat(),
                weekly_pillar_summary=weekly_summary,
                main_sipsung=main_sipsung,
                sipsung_interpretation=sipsung_interp,
                jiji_relation=f"{birth_branch} ↔ {day_ji} = {jiji_relation_type}",
                jiji_interpretation=jiji_interp,
                today=target_date.isoformat(),
            )

            fortune = FortuneResponse(
                target_date=week_start,
                fortune_type="weekly",
                day_pillar=DayPillar(stem=day_gan, branch=day_ji),
                overall=llm_output.overall,
                love=llm_output.love,
                career=llm_output.career,
                health=llm_output.health,
                wealth=llm_output.wealth,
                lucky_color=llm_output.lucky_color,
                lucky_number=llm_output.lucky_number,
                source="llm",
                luck_score=luck_score,
                sipsung=main_sipsung,
                keywords=keywords if keywords else None,
            )

            log.info("Weekly fortune generated via LLM", user_id=user_id)

        except Exception as e:
            log.warning(
                "LLM weekly fallback triggered",
                error=str(e),
                user_id=user_id
            )
            fortune = self._build_fallback_response(
                target_date=week_start,
                day_gan=day_gan,
                day_ji=day_ji,
                sipsung_interp=sipsung_interp,
                jiji_interp=jiji_interp,
                luck_score=luck_score,
                sipsung=main_sipsung,
                keywords=keywords,
                fortune_type="weekly"
            )

        # 9. 캐시 저장
        await self.cache_service.set_fortune_cache(
            user_id, FortuneType.WEEKLY, week_start, fortune
        )

        return fortune

    async def get_weekly_fortune_with_status(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> Tuple[FortuneResponse, str]:
        """
        주간 운세 조회 + 캐시 상태 반환

        Returns:
            Tuple[FortuneResponse, str]: (운세, 캐시 상태: "HIT" | "MISS")
        """
        target_date = target_date or date.today()
        week_start = self._get_week_start(target_date)

        # 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.WEEKLY, week_start
        )

        if cached:
            cache_status = "HIT" if status == "HIT" else "HIT"
            return cached, cache_status

        # 캐시 미스 - 생성
        fortune = await self.get_weekly_fortune(
            user_id, birth_stem, birth_branch, target_date
        )
        return fortune, "MISS"

    # =========================================================================
    # 월간 운세 (Story 2.6)
    # =========================================================================

    @logger.catch(reraise=True)
    async def get_monthly_fortune(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> FortuneResponse:
        """
        월간 운세 조회 (캐시 → LLM → 폴백)

        Args:
            user_id: 사용자 ID
            birth_stem: 사용자 일간 (천간)
            birth_branch: 사용자 일지 (지지)
            target_date: 운세 기준 날짜 (기본: 오늘)

        Returns:
            FortuneResponse: 월간 운세 응답
        """
        log = get_logger_with_request_id()
        target_date = target_date or date.today()
        # 월간 캐시 키용 날짜 (해당 월 1일)
        month_key_date = target_date.replace(day=1)

        log.info(
            "Getting monthly fortune",
            user_id=user_id,
            birth_stem=birth_stem,
            target_month=f"{target_date.year}-{target_date.month:02d}"
        )

        # 1. 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.MONTHLY, month_key_date
        )
        if cached:
            log.info("Monthly fortune cache hit", status=status, user_id=user_id)
            return cached

        # 2. 대표 일진 (1일 기준)
        day_gan, day_ji = get_ilju(month_key_date)

        # 3. 십성 계산
        sipsung = calculate_sipsung(day_gan, birth_stem)

        # 4. 월지 및 월 정보
        month_branch = get_month_branch(target_date)
        month_energy = get_month_energy(target_date)
        month_name = get_month_name(target_date.month)

        # 5. 사주 데이터 조회
        sipsung_data = await self.saju_repo.get_sipsung_interpretation(
            birth_stem, sipsung
        )
        jiji_data = await self.saju_repo.get_jiji_relation(
            birth_branch, month_branch
        )

        # 6. 폴백 데이터 준비
        sipsung_interp = self._get_sipsung_fallback(
            sipsung_data, birth_stem, sipsung
        )
        jiji_interp = self._get_jiji_fallback(jiji_data, birth_branch, month_branch)
        jiji_relation_type = jiji_data.relation_type if jiji_data else "무관"

        # 7. luck_score 계산
        luck_score = calculate_luck_score(sipsung, jiji_relation_type, "총운")

        # 8. 키워드 추출
        keywords = self._extract_keywords(sipsung_data, jiji_data)

        try:
            # 9. LLM 호출
            llm_output = await self.chain.generate_monthly_fortune(
                ilgan=birth_stem,
                ilgan_oheng=get_oheng(birth_stem),
                ilgan_yin_yang=get_yin_yang(birth_stem),
                target_month=target_date.year,
                month_num=target_date.month,
                month_name=month_name,
                month_branch=month_branch,
                month_energy=month_energy,
                main_sipsung=sipsung,
                sipsung_interpretation=sipsung_interp,
                jiji_relation=f"{birth_branch} ↔ {month_branch} = {jiji_relation_type}",
                jiji_interpretation=jiji_interp,
                today=target_date.isoformat(),
            )

            fortune = FortuneResponse(
                target_date=month_key_date,
                fortune_type="monthly",
                day_pillar=DayPillar(stem=day_gan, branch=day_ji),
                overall=llm_output.overall,
                love=llm_output.love,
                career=llm_output.career,
                health=llm_output.health,
                wealth=llm_output.wealth,
                lucky_color=llm_output.lucky_color,
                lucky_number=llm_output.lucky_number,
                source="llm",
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords if keywords else None,
            )

            log.info("Monthly fortune generated via LLM", user_id=user_id)

        except Exception as e:
            log.warning(
                "LLM monthly fallback triggered",
                error=str(e),
                user_id=user_id
            )
            fortune = self._build_fallback_response(
                target_date=month_key_date,
                day_gan=day_gan,
                day_ji=day_ji,
                sipsung_interp=sipsung_interp,
                jiji_interp=jiji_interp,
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords,
                fortune_type="monthly"
            )

        # 10. 캐시 저장
        await self.cache_service.set_fortune_cache(
            user_id, FortuneType.MONTHLY, month_key_date, fortune
        )

        return fortune

    async def get_monthly_fortune_with_status(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> Tuple[FortuneResponse, str]:
        """
        월간 운세 조회 + 캐시 상태 반환

        Returns:
            Tuple[FortuneResponse, str]: (운세, 캐시 상태: "HIT" | "MISS")
        """
        target_date = target_date or date.today()
        month_key_date = target_date.replace(day=1)

        # 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.MONTHLY, month_key_date
        )

        if cached:
            cache_status = "HIT" if status == "HIT" else "HIT"
            return cached, cache_status

        # 캐시 미스 - 생성
        fortune = await self.get_monthly_fortune(
            user_id, birth_stem, birth_branch, target_date
        )
        return fortune, "MISS"

    # =========================================================================
    # 연간 운세 (Story 2.6)
    # =========================================================================

    @logger.catch(reraise=True)
    async def get_yearly_fortune(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> FortuneResponse:
        """
        연간 운세 조회 (캐시 → LLM → 폴백)

        Args:
            user_id: 사용자 ID
            birth_stem: 사용자 일간 (천간)
            birth_branch: 사용자 일지 (지지)
            target_date: 운세 기준 날짜 (기본: 오늘)

        Returns:
            FortuneResponse: 연간 운세 응답
        """
        log = get_logger_with_request_id()
        target_date = target_date or date.today()
        # 연간 캐시 키용 날짜 (해당 연도 1월 1일)
        year_key_date = date(target_date.year, 1, 1)

        log.info(
            "Getting yearly fortune",
            user_id=user_id,
            birth_stem=birth_stem,
            target_year=target_date.year
        )

        # 1. 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.YEARLY, year_key_date
        )
        if cached:
            log.info("Yearly fortune cache hit", status=status, user_id=user_id)
            return cached

        # 2. 연주 계산
        year_gan, year_ji = get_year_pillar(target_date)
        year_energy = get_year_energy(target_date)

        # 3. 십성 계산 (일간 vs 연간)
        sipsung = calculate_sipsung(year_gan, birth_stem)

        # 4. 대표 일진 (1월 1일 기준)
        day_gan, day_ji = get_ilju(year_key_date)

        # 5. 사주 데이터 조회
        sipsung_data = await self.saju_repo.get_sipsung_interpretation(
            birth_stem, sipsung
        )
        jiji_data = await self.saju_repo.get_jiji_relation(
            birth_branch, year_ji
        )

        # 6. 폴백 데이터 준비
        sipsung_interp = self._get_sipsung_fallback(
            sipsung_data, birth_stem, sipsung
        )
        jiji_interp = self._get_jiji_fallback(jiji_data, birth_branch, year_ji)
        jiji_relation_type = jiji_data.relation_type if jiji_data else "무관"

        # 7. luck_score 계산
        luck_score = calculate_luck_score(sipsung, jiji_relation_type, "총운")

        # 8. 키워드 추출
        keywords = self._extract_keywords(sipsung_data, jiji_data)

        try:
            # 9. LLM 호출
            llm_output = await self.chain.generate_yearly_fortune(
                ilgan=birth_stem,
                ilgan_oheng=get_oheng(birth_stem),
                ilgan_yin_yang=get_yin_yang(birth_stem),
                target_year=target_date.year,
                year_gan=year_gan,
                year_ji=year_ji,
                year_energy=year_energy,
                main_sipsung=sipsung,
                sipsung_interpretation=sipsung_interp,
                jiji_relation=f"{birth_branch} ↔ {year_ji} = {jiji_relation_type}",
                jiji_interpretation=jiji_interp,
                today=target_date.isoformat(),
            )

            fortune = FortuneResponse(
                target_date=year_key_date,
                fortune_type="yearly",
                day_pillar=DayPillar(stem=year_gan, branch=year_ji),
                overall=llm_output.overall,
                love=llm_output.love,
                career=llm_output.career,
                health=llm_output.health,
                wealth=llm_output.wealth,
                lucky_color=llm_output.lucky_color,
                lucky_number=llm_output.lucky_number,
                source="llm",
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords if keywords else None,
            )

            log.info("Yearly fortune generated via LLM", user_id=user_id)

        except Exception as e:
            log.warning(
                "LLM yearly fallback triggered",
                error=str(e),
                user_id=user_id
            )
            fortune = self._build_fallback_response(
                target_date=year_key_date,
                day_gan=year_gan,
                day_ji=year_ji,
                sipsung_interp=sipsung_interp,
                jiji_interp=jiji_interp,
                luck_score=luck_score,
                sipsung=sipsung,
                keywords=keywords,
                fortune_type="yearly"
            )

        # 10. 캐시 저장
        await self.cache_service.set_fortune_cache(
            user_id, FortuneType.YEARLY, year_key_date, fortune
        )

        return fortune

    async def get_yearly_fortune_with_status(
        self,
        user_id: str,
        birth_stem: str,
        birth_branch: str,
        target_date: Optional[date] = None
    ) -> Tuple[FortuneResponse, str]:
        """
        연간 운세 조회 + 캐시 상태 반환

        Returns:
            Tuple[FortuneResponse, str]: (운세, 캐시 상태: "HIT" | "MISS")
        """
        target_date = target_date or date.today()
        year_key_date = date(target_date.year, 1, 1)

        # 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.YEARLY, year_key_date
        )

        if cached:
            cache_status = "HIT" if status == "HIT" else "HIT"
            return cached, cache_status

        # 캐시 미스 - 생성
        fortune = await self.get_yearly_fortune(
            user_id, birth_stem, birth_branch, target_date
        )
        return fortune, "MISS"
