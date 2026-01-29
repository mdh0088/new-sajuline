# Story 2.4: LangChain RAG 체인 구축

Status: done

## Story

As a **시스템**,
I want **사주 지식베이스를 검색하고 GPT-4o-mini로 운세를 생성하는 RAG 체인**,
So that **개인화된 고품질 AI 운세를 생성할 수 있다 (FR15)**.

## Acceptance Criteria

1. **AC1**: Given 사용자의 사주 정보와 오늘 날짜가 있을 때, When RAG 체인이 실행되면, Then 사주 지식베이스에서 관련 천간/지지/십성 정보가 검색된다 And GPT-4o-mini에 컨텍스트와 함께 프롬프트가 전송된다 And 운세 결과가 3초 이내에 생성된다 (NFR-P2)

2. **AC2**: Given OpenAI API를 mock으로 테스트할 때, When RAG 체인이 실행되면, Then mock 응답으로 정상 동작이 검증된다

3. **AC3**: Given OpenAI API 호출 시, When 타임아웃(10초)이 발생하면, Then 1회 자동 재시도한다 And 재시도 실패 시 캐시된 일반 운세 또는 에러 메시지를 반환한다 (NFR-R3)

4. **AC4**: Given 운세 생성 요청 시, When RAG 체인이 실행되면, Then 응답에 `overall` (총운), `love` (애정운), `career` (직장운), `health` (건강운), `wealth` (재물운) 섹션이 포함된다 And 각 섹션은 50~150자 이내로 생성된다

5. **AC5**: Given DB에서 십성/지지 데이터 조회 실패 시, When RAG 체인이 실행되면, Then 기본 해석으로 폴백하여 서비스가 중단되지 않는다

6. **AC6**: Given LangChain RAG 체인, When 단위 테스트가 실행되면, Then 커버리지 85% 이상 달성

## Tasks / Subtasks

- [x] **Task 1: LangChain 패키지 업그레이드** (선행 조건)
  - [x] `backend/pyproject.toml` 수정: `langchain>=1.2.7`, `langchain-openai>=1.1.7`, `langchain-core>=1.0.0`
  - [x] `uv lock && uv sync` 실행
  - [x] 기존 import 호환성 확인

- [x] **Task 2: 사주 리포지토리 구현** (AC: 1, 5)
  - [x] `backend/src/repositories/saju_repository.py` 생성
  - [x] `SajuRepository` 클래스 구현
  - [x] `get_sipsung_interpretation(ilgan, sipsung)` 메서드
  - [x] `get_jiji_relation(jiji1, jiji2)` 메서드
  - [x] `get_all_cheongan()`, `get_all_jiji()` 메서드
  - [x] 조회 실패 시 None 반환 (폴백 지원)

- [x] **Task 3: 프롬프트 템플릿 정의** (AC: 4)
  - [x] `backend/src/core/prompts.py` 생성
  - [x] `FORTUNE_SYSTEM_PROMPT` 상수 (명리학 전문가 페르소나)
  - [x] `FORTUNE_USER_PROMPT_TEMPLATE` 상수 (구조화된 프롬프트)
  - [x] 운세 섹션별 지침 포함 (총운/애정/직장/건강/재물)

- [x] **Task 4: LangChain 체인 빌더 구현** (AC: 1, 2, 3)
  - [x] `backend/src/core/langchain_chain.py` 생성
  - [x] `DailyFortuneChain` 클래스 구현
  - [x] `ChatOpenAI(model="gpt-4o-mini", temperature=0.7, timeout=10)`
  - [x] `PromptTemplate` + `RunnableSequence` 구성
  - [x] JSON 응답 파싱 로직 (Pydantic 검증)
  - [x] 재시도 로직 (1회, exponential backoff)

- [x] **Task 5: Fortune 스키마 확장** (AC: 4)
  - [x] `backend/src/schemas/fortune_schema.py` 확장
  - [x] `DailyFortuneRequest` 스키마 (birth_datetime, category 검증)
  - [x] `FortuneResponse` 스키마에 `luck_score`, `keywords`, `sipsung` 필드 추가
  - [x] `LLMFortuneOutput` 스키마 (LLM 응답 파싱용)

- [x] **Task 6: Fortune 서비스 구현** (AC: 1, 3, 5)
  - [x] `backend/src/services/fortune_service.py` 생성
  - [x] `FortuneService` 클래스 구현
  - [x] `get_daily_fortune()` 메인 메서드:
    - 캐시 확인 (FortuneCacheService 연동)
    - 사주 데이터 조회 (SajuRepository)
    - 일진/십성 계산 (saju_calculator)
    - RAG 체인 실행 (DailyFortuneChain)
    - 캐시 저장
  - [x] 폴백 로직 (LLM 실패 시 DB 기본 해석)
  - [x] source 필드 설정 ("llm" | "fallback")

- [x] **Task 7: DI 의존성 추가** (AC: 1)
  - [x] `backend/src/core/dependencies.py` 수정
  - [x] `get_saju_repository()` 함수
  - [x] `get_daily_fortune_chain()` 함수 (stateless)
  - [x] `get_fortune_service()` 함수 (복합 의존성)
  - [x] `SajuRepositoryDep`, `FortuneServiceDep`, `DailyFortuneChainDep` Annotated 타입

- [x] **Task 8: 단위 테스트 작성** (AC: 2, 6)
  - [x] `backend/tests/unit/core/test_langchain_chain.py` 생성
  - [x] `backend/tests/unit/services/test_fortune_service.py` 생성
  - [x] `backend/tests/unit/repositories/test_saju_repository.py` 생성
  - [x] LLM Mock 테스트 (정상 응답, 타임아웃, 에러)
  - [x] 폴백 로직 테스트
  - [x] 커버리지 100% 달성 ✅

## Dev Notes

### 필수 준수 사항 (Architecture Compliance)

**파일 위치:**
```
backend/src/
├── core/
│   ├── langchain_chain.py   # 신규: LangChain 체인 빌더
│   ├── prompts.py           # 신규: 프롬프트 템플릿
│   └── dependencies.py      # 수정: DI 추가
├── services/
│   └── fortune_service.py   # 신규: 운세 비즈니스 로직
├── repositories/
│   └── saju_repository.py   # 신규: 사주 데이터 조회
└── schemas/
    └── fortune_schema.py    # 수정: 스키마 확장
```

### 이전 스토리 학습 포인트 (반드시 활용)

**Story 2-1에서 생성된 모델:**
- `SajuCheongan`: 천간 10행 (`name`, `hanja`, `oheng`, `yin_yang`)
- `SajuJiji`: 지지 12행 (`name`, `hanja`, `oheng`, `yin_yang`, `animal`)
- `SajuSipsungInterpretation`: 십성 해석 100행 (`ilgan`, `sipsung`, `keywords`, `positive_meaning`, `negative_meaning`, `daily_advice`)
- `SajuJijiRelation`: 지지 관계 (합/충/형/파/해), `daily_impact`
- `FortuneHistory`: 운세 이력 (UUID PK)

**Story 2-2에서 생성된 유틸리티:**
```python
# backend/src/common/utils/saju_calculator.py
from src.common.utils.saju_calculator import (
    get_ilju,           # (date) -> tuple[str, str] 일주 계산
    calculate_sipsung,  # (day_stem, birth_stem) -> str 십성 계산
    calculate_luck_score,  # (sipsung, jiji_relation, category) -> int
    get_oheng,          # (stem) -> str 오행 반환
    get_yin_yang,       # (stem) -> str 음양 반환
)
```

**Story 2-3에서 생성된 캐시 서비스:**
```python
# backend/src/services/fortune_cache_service.py
from src.services.fortune_cache_service import FortuneCacheService
from src.core.dependencies import FortuneCacheServiceDep

# 사용법:
cache_service: FortuneCacheServiceDep
fortune, status = await cache_service.get_cached_fortune(user_id, FortuneType.DAILY, target_date)
if status == "MISS":
    # LLM 호출 후 캐시 저장
    await cache_service.set_fortune_cache(user_id, FortuneType.DAILY, target_date, fortune_data)
```

**Story 2-3에서 생성된 FortuneResponse 스키마:**
```python
# backend/src/schemas/fortune_schema.py
class FortuneResponse(BaseModel):
    target_date: date
    fortune_type: str
    day_pillar: DayPillar  # {"stem": "갑", "branch": "진"}
    overall: str
    love: str
    career: str
    health: str
    wealth: str
    lucky_color: Optional[str]
    lucky_number: Optional[int]
    source: str  # "llm" | "fallback" | "cache"
```

### LangChain 체인 설계

> **⚠️ 중요: LangChain 1.x 공식 문서 참조 필수**
> LangChain 1.x는 최신 버전으로, API가 이전 버전과 다를 수 있습니다.
> 구현 전 반드시 [LangChain 공식 문서](https://python.langchain.com/docs/)를 웹 검색하여 최신 API를 확인하세요.
> - ChatOpenAI 사용법: `langchain-openai ChatOpenAI 1.x documentation`
> - Output Parser: `langchain JsonOutputParser 1.x`
> - Prompt Template: `langchain ChatPromptTemplate 1.x`

**체인 구조 (LangChain v1.2.7):**
```python
# backend/src/core/langchain_chain.py
# ⚠️ 구현 시 반드시 LangChain 1.x 공식 문서를 웹 검색하여 최신 API 확인

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.core.prompts import FORTUNE_SYSTEM_PROMPT, FORTUNE_USER_PROMPT_TEMPLATE
from src.schemas.fortune_schema import LLMFortuneOutput
from src.config.settings import settings

class DailyFortuneChain:
    """LangChain RAG 체인 빌더 (LangChain 1.x)"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,  # "gpt-4o-mini"
            temperature=0.7,
            timeout=10,
            max_retries=1,
            api_key=settings.openai_api_key,
        )
        self.parser = JsonOutputParser(pydantic_object=LLMFortuneOutput)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", FORTUNE_SYSTEM_PROMPT),
            ("human", FORTUNE_USER_PROMPT_TEMPLATE),
        ])
        self.chain = self.prompt | self.llm | self.parser

    async def generate_fortune(
        self,
        ilgan: str,
        ilgan_oheng: str,
        ilgan_yin_yang: str,
        day_gan: str,
        day_ji: str,
        sipsung: str,
        sipsung_interpretation: str,
        jiji_relation: str,
        jiji_interpretation: str,
        today: str,
    ) -> LLMFortuneOutput:
        """운세 생성"""
        result = await self.chain.ainvoke({
            "ilgan": ilgan,
            "ilgan_oheng": ilgan_oheng,
            "ilgan_yin_yang": ilgan_yin_yang,
            "day_gan": day_gan,
            "day_ji": day_ji,
            "sipsung": sipsung,
            "sipsung_interpretation": sipsung_interpretation,
            "jiji_relation": jiji_relation,
            "jiji_interpretation": jiji_interpretation,
            "today": today,
        })
        return LLMFortuneOutput.model_validate(result)
```

### 프롬프트 템플릿

**시스템 프롬프트:**
```python
# backend/src/core/prompts.py

FORTUNE_SYSTEM_PROMPT = """당신은 30년 경력의 명리학 전문가입니다.
주어진 사주 데이터를 바탕으로 오늘의 운세를 해석해주세요.

규칙:
- 각 섹션(총운, 애정운, 직장운, 건강운, 재물운)은 50~150자로 작성
- 구체적인 조언 포함
- 긍정적이되 현실적인 톤
- 미신적 표현 지양 (예: "큰 재앙", "대박")
- JSON 형식으로 응답

응답 형식:
{{
  "overall": "총운 내용",
  "love": "애정운 내용",
  "career": "직장운 내용",
  "health": "건강운 내용",
  "wealth": "재물운 내용",
  "lucky_color": "색상 또는 null",
  "lucky_number": 숫자 또는 null
}}
"""

FORTUNE_USER_PROMPT_TEMPLATE = """
오늘 날짜: {today}
사용자 일간: {ilgan} ({ilgan_oheng} {ilgan_yin_yang})
오늘 일진: {day_gan}{day_ji}

[십성 관계]
일간({ilgan}) → 일진 천간({day_gan}) = {sipsung}
해석: {sipsung_interpretation}

[지지 관계]
{jiji_relation}
해석: {jiji_interpretation}

위 정보를 바탕으로 오늘의 운세를 JSON 형식으로 작성해주세요.
"""
```

### 사주 리포지토리 설계

```python
# backend/src/repositories/saju_repository.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.saju_cheongan_model import SajuCheongan
from src.models.saju_jiji_model import SajuJiji
from src.models.saju_sipsung_model import SajuSipsungInterpretation
from src.models.saju_jiji_relation_model import SajuJijiRelation


class SajuRepository:
    """사주 지식베이스 리포지토리"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_sipsung_interpretation(
        self,
        ilgan: str,
        sipsung: str
    ) -> Optional[SajuSipsungInterpretation]:
        """일간+십성 조합의 해석 조회"""
        stmt = select(SajuSipsungInterpretation).where(
            SajuSipsungInterpretation.ilgan == ilgan,
            SajuSipsungInterpretation.sipsung == sipsung
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jiji_relation(
        self,
        jiji1: str,
        jiji2: str
    ) -> Optional[SajuJijiRelation]:
        """두 지지 간의 관계 조회 (합/충/형 등)"""
        stmt = select(SajuJijiRelation).where(
            SajuJijiRelation.jiji1 == jiji1,
            SajuJijiRelation.jiji2 == jiji2
        )
        result = await self.session.execute(stmt)
        relation = result.scalar_one_or_none()

        # 역방향도 확인 (자축합 = 축자합)
        if not relation:
            stmt = select(SajuJijiRelation).where(
                SajuJijiRelation.jiji1 == jiji2,
                SajuJijiRelation.jiji2 == jiji1
            )
            result = await self.session.execute(stmt)
            relation = result.scalar_one_or_none()

        return relation

    async def get_cheongan_by_name(self, name: str) -> Optional[SajuCheongan]:
        """천간 이름으로 조회"""
        stmt = select(SajuCheongan).where(SajuCheongan.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jiji_by_name(self, name: str) -> Optional[SajuJiji]:
        """지지 이름으로 조회"""
        stmt = select(SajuJiji).where(SajuJiji.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

### Fortune 서비스 설계

```python
# backend/src/services/fortune_service.py

from datetime import date
from typing import Optional

from src.common.utils.saju_calculator import (
    get_ilju, calculate_sipsung, calculate_luck_score,
    get_oheng, get_yin_yang
)
from src.core.langchain_chain import DailyFortuneChain
from src.models.fortune_history_model import FortuneType
from src.repositories.saju_repository import SajuRepository
from src.services.fortune_cache_service import FortuneCacheService
from src.schemas.fortune_schema import FortuneResponse, DayPillar
from src.common.logging import get_logger_with_request_id


class FortuneService:
    """운세 비즈니스 로직 서비스"""

    def __init__(
        self,
        saju_repo: SajuRepository,
        cache_service: FortuneCacheService,
        chain: DailyFortuneChain
    ):
        self.saju_repo = saju_repo
        self.cache_service = cache_service
        self.chain = chain

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

        # 1. 캐시 확인
        cached, status = await self.cache_service.get_cached_fortune(
            user_id, FortuneType.DAILY, target_date
        )
        if cached:
            log.info("Cache hit", status=status)
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

        try:
            # 7. LLM 호출
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
                target_date, day_gan, day_ji, llm_output,
                luck_score, sipsung, source="llm"
            )

        except Exception as e:
            # 8. 폴백: DB 데이터로 기본 응답
            log.warning("LLM fallback triggered", error=str(e))
            fortune = self._build_fallback_response(
                target_date, day_gan, day_ji,
                sipsung_interp, jiji_interp,
                luck_score, sipsung
            )

        # 9. 캐시 저장
        await self.cache_service.set_fortune_cache(
            user_id, FortuneType.DAILY, target_date, fortune
        )

        return fortune

    def _get_sipsung_fallback(
        self,
        data: Optional[any],
        ilgan: str,
        sipsung: str
    ) -> str:
        """십성 해석 폴백"""
        if data and data.daily_advice:
            return data.daily_advice
        return f"{ilgan} 일간이 {sipsung}을 만났습니다. 평온한 하루 되세요."

    def _get_jiji_fallback(
        self,
        data: Optional[any],
        jiji1: str,
        jiji2: str
    ) -> str:
        """지지 관계 해석 폴백"""
        if data and data.daily_impact:
            return data.daily_impact
        return f"{jiji1}과 {jiji2}의 만남입니다. 안정적인 에너지가 흐릅니다."

    def _build_response(
        self,
        target_date: date,
        day_gan: str,
        day_ji: str,
        llm_output: any,
        luck_score: int,
        sipsung: str,
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
        )

    def _build_fallback_response(
        self,
        target_date: date,
        day_gan: str,
        day_ji: str,
        sipsung_interp: str,
        jiji_interp: str,
        luck_score: int,
        sipsung: str
    ) -> FortuneResponse:
        """폴백 응답 생성"""
        return FortuneResponse(
            target_date=target_date,
            fortune_type="daily",
            day_pillar=DayPillar(stem=day_gan, branch=day_ji),
            overall=f"{sipsung_interp} {jiji_interp}",
            love="애정 운세는 잠시 후 다시 확인해주세요.",
            career="직장 운세는 잠시 후 다시 확인해주세요.",
            health="건강 운세는 잠시 후 다시 확인해주세요.",
            wealth="재물 운세는 잠시 후 다시 확인해주세요.",
            lucky_color=None,
            lucky_number=None,
            source="fallback",
        )
```

### 주의사항: 안티패턴 방지

> **⚠️ LangChain 1.x 구현 시 필수 확인 사항**
> - 구현 전 반드시 공식 문서를 웹 검색하여 최신 API 확인
> - 검색 예시: "langchain 1.x ChatOpenAI async usage", "langchain-openai 1.1 documentation"

**❌ 절대 하지 말 것:**
```python
# 잘못: 동기 OpenAI 클라이언트 사용
import openai
openai.ChatCompletion.create(...)  # ❌

# 잘못: LangChain 레거시 패턴 사용 (0.1.x 이하)
from langchain.chat_models import ChatOpenAI  # ❌

# 잘못: 타임아웃 없이 LLM 호출
ChatOpenAI(model="gpt-4o-mini")  # timeout 없음 ❌

# 잘못: 폴백 없이 LLM만 의존
llm_result = await chain.ainvoke(...)  # try-except 없음 ❌

# 잘못: 캐시 서비스 재구현
redis.setex(...)  # FortuneCacheService 사용해야 함 ❌

# 잘못: saju_calculator 함수 재구현
def calculate_ilju(...):  # 이미 존재함 ❌

# 잘못: 공식 문서 확인 없이 구현
# LangChain 1.x API는 자주 변경됨 - 반드시 웹 검색으로 확인 ❌
```

**✅ 올바른 패턴:**
```python
# LangChain 1.x import (공식 문서 확인 필수)
from langchain_openai import ChatOpenAI  # ✅
from langchain_core.prompts import ChatPromptTemplate  # ✅
from langchain_core.output_parsers import JsonOutputParser  # ✅

# 타임아웃 + 재시도 설정
ChatOpenAI(model="gpt-4o-mini", timeout=10, max_retries=1)  # ✅

# 기존 유틸리티 활용
from src.common.utils.saju_calculator import get_ilju, calculate_sipsung  # ✅

# 기존 캐시 서비스 활용
from src.services.fortune_cache_service import FortuneCacheService  # ✅
```

### DI 의존성 패턴 (기존 코드 준수)

```python
# backend/src/core/dependencies.py 추가

from src.repositories.saju_repository import SajuRepository
from src.services.fortune_service import FortuneService
from src.core.langchain_chain import DailyFortuneChain


def get_saju_repository(db: AsyncSession = Depends(get_db_maria)) -> SajuRepository:
    """사주 리포지토리 의존성 주입"""
    return SajuRepository(db)


def get_daily_fortune_chain() -> DailyFortuneChain:
    """LangChain 체인 의존성 주입 (stateless)"""
    return DailyFortuneChain()


def get_fortune_service(
    saju_repo: SajuRepository = Depends(get_saju_repository),
    cache_service: FortuneCacheService = Depends(get_fortune_cache_service),
    chain: DailyFortuneChain = Depends(get_daily_fortune_chain)
) -> FortuneService:
    """운세 서비스 의존성 주입 (3개 의존성)"""
    return FortuneService(saju_repo, cache_service, chain)


# Annotated Types
SajuRepositoryDep = Annotated[SajuRepository, Depends(get_saju_repository)]
FortuneServiceDep = Annotated[FortuneService, Depends(get_fortune_service)]
```

### 테스트 전략

**단위 테스트:**
```python
# tests/unit/core/test_langchain_chain.py

import pytest
from unittest.mock import AsyncMock, patch

class TestDailyFortuneChain:

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI 응답"""
        return {
            "overall": "오늘은 창의적인 에너지가 넘칩니다.",
            "love": "로맨틱한 만남이 기대됩니다.",
            "career": "업무에서 좋은 성과가 있습니다.",
            "health": "규칙적인 운동을 권장합니다.",
            "wealth": "재물운이 상승합니다.",
            "lucky_color": "초록색",
            "lucky_number": 7
        }

    @pytest.mark.asyncio
    async def test_generate_fortune_success(self, mock_openai_response):
        """정상 운세 생성"""
        with patch.object(DailyFortuneChain, 'chain') as mock_chain:
            mock_chain.ainvoke = AsyncMock(return_value=mock_openai_response)
            chain = DailyFortuneChain()
            result = await chain.generate_fortune(...)
            assert result.overall is not None

    @pytest.mark.asyncio
    async def test_generate_fortune_timeout(self):
        """타임아웃 시 예외 발생"""
        with patch.object(DailyFortuneChain, 'chain') as mock_chain:
            mock_chain.ainvoke = AsyncMock(side_effect=TimeoutError())
            chain = DailyFortuneChain()
            with pytest.raises(TimeoutError):
                await chain.generate_fortune(...)
```

### 성능 요구사항

| 항목 | 목표 | 근거 |
|------|------|------|
| LLM 응답 | < 3초 | NFR-P2 |
| 캐시 히트 | < 100ms | Story 2-3 |
| 폴백 응답 | < 500ms | DB 조회만 |
| LLM 타임아웃 | 10초 | Architecture |
| 재시도 | 1회 | Architecture |

### Project Structure Notes

**신규 생성:**
```
backend/
├── src/core/
│   ├── langchain_chain.py    # LangChain 체인 빌더
│   └── prompts.py            # 프롬프트 템플릿
├── src/services/
│   └── fortune_service.py    # 운세 비즈니스 로직
├── src/repositories/
│   └── saju_repository.py    # 사주 데이터 조회
└── tests/unit/
    ├── core/test_langchain_chain.py
    ├── services/test_fortune_service.py
    └── repositories/test_saju_repository.py
```

**수정:**
```
backend/
├── pyproject.toml            # LangChain 버전 업그레이드
├── src/core/dependencies.py  # DI 추가
└── src/schemas/fortune_schema.py  # 스키마 확장
```

### References

- [Tech Spec] `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md#Task 11-13`
- [Architecture] `docs/architecture/core-architectural-decisions.md#OpenAI 연동 전략`
- [Previous Story 2.1] `_bmad-output/implementation-artifacts/2-1-saju-knowledge-base-data-model.md`
- [Previous Story 2.2] `_bmad-output/implementation-artifacts/2-2-saju-calculation-utility.md`
- [Previous Story 2.3] `_bmad-output/implementation-artifacts/2-3-fortune-cache-system.md`
- [Repository Pattern] `backend/src/repositories/user_repository.py`
- [Service Pattern] `backend/src/services/auth_service.py`
- [DI Pattern] `backend/src/core/dependencies.py`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- LangChain 1.2.7 + langchain-openai 1.1.7 버전 사용
- Pydantic 버전 2.7.4+ 호환성 확인
- 전체 39개 테스트 통과, 100% 커버리지 달성

### Completion Notes List

- Task 1-8 모두 완료
- LangChain 1.x 공식 패턴 준수 (ChatPromptTemplate, PydanticOutputParser, RunnableSequence)
- 캐시 → LLM → 폴백 3단계 플로우 구현 완료
- DI 의존성 패턴 일관성 유지 (Annotated 타입 사용)
- AC1~AC6 모든 수용 기준 충족

### File List

**신규 생성:**
- `backend/src/repositories/saju_repository.py` - 사주 지식베이스 리포지토리
- `backend/src/core/prompts.py` - 운세 프롬프트 템플릿
- `backend/src/core/langchain_chain.py` - LangChain RAG 체인 빌더
- `backend/src/services/fortune_service.py` - 운세 비즈니스 로직 서비스
- `backend/tests/unit/repositories/test_saju_repository.py` - 사주 리포지토리 테스트
- `backend/tests/unit/core/test_langchain_chain.py` - LangChain 체인 테스트
- `backend/tests/unit/services/test_fortune_service.py` - 운세 서비스 테스트

**수정:**
- `backend/pyproject.toml` - LangChain 1.2.7, Pydantic 2.7.4+ 버전 업그레이드
- `backend/src/core/dependencies.py` - DI 함수 및 Annotated 타입 추가
- `backend/src/schemas/fortune_schema.py` - LLMFortuneOutput, DailyFortuneRequest 스키마 추가

