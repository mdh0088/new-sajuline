# AI 관리자 어시스턴트 - GA4 연동 가이드

> **문서 버전**: 1.0.0
> **최종 수정**: 2026-01-29
> **상태**: 설계 단계 (Phase 4)

---

## 1. 개요

### 1.1 GA4 연동 목적
Google Analytics 4 Data API를 통해 웹사이트 유입 데이터와 내부 매출/상담 데이터를 연계 분석하여 **마케팅 ROI 측정** 및 **전환 퍼널 분석**을 지원합니다.

### 1.2 핵심 분석 시나리오

| 시나리오 | 예시 질문 | 데이터 소스 |
|----------|----------|------------|
| 유입-매출 연계 | "카카오 유입 유저 중 결제한 사람 몇 명?" | MariaDB + GA4 |
| 채널별 전환율 | "이번 달 채널별 전환율 알려줘" | GA4 + MariaDB |
| 마케팅 ROI | "네이버 광고 ROAS 계산해줘" | GA4 + MariaDB |
| 퍼널 분석 | "방문→가입→결제 퍼널 드롭오프율?" | GA4 + MariaDB |
| 유입 트렌드 | "이번 주 일별 유입 추이" | GA4 |

---

## 2. GA4 Data API 개요

### 2.1 API 선택 이유

| API 옵션 | 설명 | 선택 |
|----------|------|------|
| **GA4 Data API** | REST API, 무료 할당량 | ✅ 선택 |
| BigQuery Export | 대용량 분석, 추가 비용 | 폴백 옵션 |
| Reporting API (UA) | 레거시, 지원 종료 | ❌ 미사용 |

### 2.2 무료 할당량

| 항목 | 할당량 |
|------|--------|
| 일일 요청 수 | 10,000 requests/day |
| 분당 요청 수 | 600 requests/minute |
| 동시 요청 수 | 10 concurrent requests |

### 2.3 사용 가능한 차원 (Dimensions)

| 차원 | 설명 | 활용 예시 |
|------|------|----------|
| `date` | 날짜 (YYYYMMDD) | 일별 추이 |
| `sessionSource` | 유입 소스 (google, naver, kakao) | 채널 분석 |
| `sessionMedium` | 유입 매체 (organic, cpc, referral) | 광고 분석 |
| `sessionCampaignName` | 캠페인명 | 캠페인 성과 |
| `deviceCategory` | 디바이스 (desktop, mobile) | 기기별 분석 |
| `country` | 국가 | 지역 분석 |
| `pagePath` | 페이지 경로 | 페이지별 분석 |

### 2.4 사용 가능한 지표 (Metrics)

| 지표 | 설명 | 활용 예시 |
|------|------|----------|
| `sessions` | 세션 수 | 방문 트래픽 |
| `activeUsers` | 활성 사용자 | 순 방문자 |
| `screenPageViews` | 페이지뷰 | 페이지 인기도 |
| `conversions` | 전환 수 | 전환 이벤트 |
| `userEngagementDuration` | 참여 시간 | 사용자 참여도 |
| `bounceRate` | 이탈률 | 콘텐츠 품질 |

---

## 3. 아키텍처

### 3.1 GA4 Agent 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                        📈 GA4 Agent                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │ Intent Parser   │ →  │ Query Builder   │ →  │ API Executor   │  │
│  │ (자연어 분석)   │    │ (GA4 Request)   │    │ (Data API)     │  │
│  └─────────────────┘    └─────────────────┘    └────────────────┘  │
│           │                     │                     │             │
│           ▼                     ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Response Formatter                        │   │
│  │  • 데이터 정규화                                             │   │
│  │  • 날짜 형식 변환 (YYYYMMDD → DATE)                         │   │
│  │  • 사용자 ID 매핑 준비                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 흐름

```
┌───────────┐    ┌───────────┐    ┌───────────┐
│   GA4     │    │ MariaDB   │    │  결과     │
│ Data API  │    │ (결제)    │    │  통합     │
└─────┬─────┘    └─────┬─────┘    └─────┬─────┘
      │                │                │
      ▼                ▼                ▼
┌─────────────────────────────────────────────────┐
│               Cross-DB Joiner                   │
│                                                 │
│   GA4 유입 데이터      MariaDB 결제 데이터      │
│   ┌──────────────┐    ┌──────────────┐         │
│   │ date         │    │ created_at   │         │
│   │ source       │ ── │ utm_source   │ (매핑)  │
│   │ medium       │    │ utm_medium   │         │
│   │ sessions     │    │ payment_count│         │
│   └──────────────┘    └──────────────┘         │
│                                                 │
│   결과: 채널별 전환율 = 결제건수 / 세션수       │
└─────────────────────────────────────────────────┘
```

---

## 4. 구현 가이드

### 4.1 환경 설정

```bash
# .env 추가 설정
# GA4 설정
GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=./credentials/ga4-service-account.json

# 또는 환경변수로 직접 설정
GOOGLE_APPLICATION_CREDENTIALS=./credentials/ga4-service-account.json
```

### 4.2 의존성

```toml
# pyproject.toml
dependencies = [
    # ... 기존 의존성 ...
    "google-analytics-data>=0.18.0",
]
```

### 4.3 GA4 Agent 구현 예시

```python
# src/ai/agents/ga4_agent.py
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

class GA4Agent:
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient()

    async def query(
        self,
        dimensions: list[str],
        metrics: list[str],
        date_range: tuple[str, str],
    ) -> pd.DataFrame:
        """GA4 Data API 조회"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(
                start_date=date_range[0],
                end_date=date_range[1]
            )],
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
        )

        response = self.client.run_report(request)
        return self._to_dataframe(response)

    def _to_dataframe(self, response) -> pd.DataFrame:
        """GA4 응답을 DataFrame으로 변환"""
        rows = []
        for row in response.rows:
            row_data = {}
            for i, dim in enumerate(response.dimension_headers):
                row_data[dim.name] = row.dimension_values[i].value
            for i, met in enumerate(response.metric_headers):
                row_data[met.name] = float(row.metric_values[i].value)
            rows.append(row_data)
        return pd.DataFrame(rows)
```

### 4.4 유입-매출 연계 분석 예시

```python
async def analyze_channel_conversion(
    ga4_agent: GA4Agent,
    mariadb_agent: MariaDBAgent,
    date_range: tuple[str, str]
) -> pd.DataFrame:
    """채널별 전환율 분석"""

    # 1. GA4에서 채널별 세션 조회
    ga4_data = await ga4_agent.query(
        dimensions=["sessionSource", "sessionMedium"],
        metrics=["sessions", "activeUsers"],
        date_range=date_range
    )

    # 2. MariaDB에서 채널별 결제 조회
    payment_query = f"""
        SELECT
            utm_source,
            utm_medium,
            COUNT(*) as payment_count,
            SUM(amount) as total_amount
        FROM t_payment
        WHERE status = 'SUCCESS'
          AND created_at BETWEEN '{date_range[0]}' AND '{date_range[1]}'
        GROUP BY utm_source, utm_medium
    """
    payment_data = await mariadb_agent.query(payment_query)

    # 3. 크로스 조인
    merged = pd.merge(
        ga4_data,
        payment_data,
        left_on=["sessionSource", "sessionMedium"],
        right_on=["utm_source", "utm_medium"],
        how="left"
    )

    # 4. 전환율 계산
    merged["conversion_rate"] = merged["payment_count"] / merged["sessions"]
    merged["arpu"] = merged["total_amount"] / merged["activeUsers"]

    return merged
```

---

## 5. 데이터 매핑

### 5.1 유입 소스 매핑

| GA4 sessionSource | 설명 | t_payment.utm_source |
|-------------------|------|---------------------|
| `google` | 구글 검색/광고 | `google` |
| `naver` | 네이버 검색/광고 | `naver` |
| `kakao` | 카카오 채널 | `kakao` |
| `direct` | 직접 방문 | `direct` |
| `(not set)` | 미분류 | `null` |

### 5.2 날짜 형식 변환

```python
def convert_ga4_date(ga4_date: str) -> datetime.date:
    """GA4 날짜 형식 변환 (YYYYMMDD → date)"""
    return datetime.strptime(ga4_date, "%Y%m%d").date()
```

### 5.3 사용자 ID 매핑 (선택적)

```python
# GA4 user_pseudo_id와 MariaDB user_id 매핑
# (별도 매핑 테이블 필요)
CREATE TABLE t_user_ga4_mapping (
    user_id BIGINT,
    ga4_client_id VARCHAR(50),
    created_at DATETIME
);
```

---

## 6. 캐싱 전략

### 6.1 캐싱 정책

| 데이터 유형 | TTL | 이유 |
|------------|-----|------|
| 일별 집계 (과거) | 24시간 | 변경되지 않음 |
| 당일 데이터 | 15분 | 실시간성 필요 |
| 채널 목록 | 1시간 | 거의 변경 없음 |

### 6.2 캐싱 구현

```python
from functools import lru_cache
import redis

redis_client = redis.Redis()

def cache_ga4_result(ttl: int = 900):  # 15분
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"ga4:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 캐시 확인
            cached = redis_client.get(cache_key)
            if cached:
                return pd.read_json(cached)

            # 실제 조회
            result = await func(*args, **kwargs)

            # 캐시 저장
            redis_client.setex(cache_key, ttl, result.to_json())

            return result
        return wrapper
    return decorator
```

---

## 7. 할당량 관리

### 7.1 사용량 모니터링

```python
class GA4QuotaManager:
    DAILY_LIMIT = 10000
    MINUTE_LIMIT = 600

    def __init__(self):
        self.daily_count = 0
        self.minute_count = 0

    def can_request(self) -> bool:
        if self.daily_count >= self.DAILY_LIMIT * 0.9:
            logger.warning("GA4 일일 할당량 90% 도달")
            return False
        return True

    def record_request(self):
        self.daily_count += 1
        self.minute_count += 1
```

### 7.2 할당량 초과 시 폴백

```python
async def query_with_fallback(query_params):
    if not quota_manager.can_request():
        # BigQuery Export 또는 캐시된 데이터 사용
        return await query_from_cache_or_bigquery(query_params)

    return await ga4_agent.query(**query_params)
```

---

## 8. 예상 질문 및 SQL 패턴

### 8.1 자주 묻는 질문 템플릿

| 질문 | GA4 조회 | MariaDB 조회 | 조인 로직 |
|------|----------|--------------|----------|
| "이번 달 채널별 전환율" | sessions by source/medium | payments by utm_source/medium | source=utm_source |
| "네이버 광고 ROAS" | sessions, source=naver, medium=cpc | sum(amount), utm_source=naver | 날짜 + 채널 |
| "모바일 vs 데스크탑 전환율" | sessions by deviceCategory | payments by device_type | device 매핑 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-29 | 초기 GA4 연동 가이드 작성 |
