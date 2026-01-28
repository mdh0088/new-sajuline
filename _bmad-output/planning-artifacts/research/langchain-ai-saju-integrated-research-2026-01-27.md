---
stepsCompleted: [1, 2, 3]
inputDocuments: ['brainstorming-session-2026-01-27.md']
workflowType: 'research'
lastStep: 3
research_type: 'Technical + Domain + Market (Integrated)'
research_topic: 'LangChain 활용 AI 사주 서비스 구현'
research_goals: '기술 아키텍처, 사주 도메인 지식, 시장 동향 통합 분석'
user_name: 'DongDong'
date: '2026-01-27'
web_research_enabled: true
source_verification: true
---

# LangChain 활용 AI 사주 서비스 통합 리서치

**Date:** 2026-01-27
**Author:** DongDong
**Research Type:** Technical + Domain + Market (Integrated)

---

## Executive Summary

본 리서치는 LangChain을 활용한 일일 AI 사주 서비스 구현을 위해 **기술 아키텍처**, **사주 도메인**, **시장 동향** 세 영역을 통합 분석했습니다.

### 핵심 발견사항

| 영역 | 핵심 인사이트 | 신뢰도 |
|------|--------------|--------|
| **기술** | RAG + 한국어 Reranker 조합이 환각 방지에 최적 | High |
| **도메인** | 사주 지식베이스 구조화가 서비스 품질의 핵심 | High |
| **시장** | 한국 점술 시장 1.4조원, AI 운세 검색량 129% 급증 | High |

### 전략적 권고사항

1. **MVP 우선순위**: 사주 지식DB → 만세력 API 연동 → LangChain RAG 체인
2. **비용 최적화**: GPT-4o mini + 선택지 UI로 토큰 소비 예측 가능화
3. **차별화 전략**: 한국어 특화 Reranker(ko-reranker) 적용으로 정확도 향상
4. **규제 대응**: 생년월일은 일반 개인정보 → 표준 동의 절차로 충분

---

## Table of Contents

1. [기술 리서치 (Technical Research)](#1-기술-리서치-technical-research)
2. [도메인 리서치 (Domain Research)](#2-도메인-리서치-domain-research)
3. [마켓 리서치 (Market Research)](#3-마켓-리서치-market-research)
4. [통합 분석 및 권고사항](#4-통합-분석-및-권고사항)
5. [참고문헌 및 출처](#5-참고문헌-및-출처)

---

## 1. 기술 리서치 (Technical Research)

### 1.1 LangChain RAG 아키텍처

#### RAG 시스템 핵심 구조 [High Confidence]

LangChain 기반 RAG 시스템은 두 가지 핵심 컴포넌트로 구성됩니다:

| 단계 | 설명 | 도구 |
|------|------|------|
| **Indexing** | 데이터 소스에서 데이터를 수집하여 인덱싱 | Document Loaders, Text Splitters, Vector Store |
| **Retrieval & Generation** | 사용자 쿼리에 대해 관련 데이터를 검색하고 모델에 전달 | Retrievers, Prompt Templates, LLM |

**Source**: [LangChain RAG Documentation](https://docs.langchain.com/oss/python/langchain/rag)

#### 2026년 RAG 구현 접근법

1. **Agentic RAG**: 에이전트가 검색 도구를 실행하는 방식 - 유연성 높음
2. **Two-step RAG Chain**: 쿼리당 단일 LLM 호출 - 지연시간 최소화

**사주 서비스 권장**: 선택지 기반 인터랙션 특성상 **Two-step RAG Chain**이 적합

**Source**: [DEV Community - RAG in 2026 Blueprint](https://dev.to/suraj_khaitan_f893c243958/-rag-in-2026-a-practical-blueprint-for-retrieval-augmented-generation-16pp)

#### Production-Grade RAG 파이프라인 단계

```
1. Document Ingestion → 메타데이터 추출
2. Text Splitting → 청킹 전략 (size, overlap)
3. Embedding Generation → 임베딩 모델 선택
4. Vector Store Storage → 메타데이터와 함께 저장
5. Query Embedding → 검색 (top-K, filters)
6. Prompt Construction → 컨텍스트 + 사용자 쿼리 조합
7. LLM Response → 응답 생성 및 소스 귀속
```

**Source**: [Medium - Production-Grade RAG Pipeline](https://medium.com/@namrata.gaddameedi414/production-grade-rag-pipeline-in-langchain-bb6d40b9b124)

---

### 1.2 벡터 데이터베이스 옵션

#### 2025-2026년 벡터DB 비교 [High Confidence]

| 특성 | Chroma | Pinecone | FAISS |
|------|--------|----------|-------|
| **배포 방식** | 오픈소스, 셀프호스팅 | 클라우드 전용, 완전 관리형 | 오픈소스, 로컬 |
| **확장성** | 수천~수백만 벡터 | 수십억 벡터 | 수백만 벡터 |
| **지연시간 (10M 벡터)** | ~89ms | ~47ms (p99) | 매우 빠름 |
| **비용** | 무료 | 유료 (사용량 기반) | 무료 |
| **추천 용도** | 프로토타입, 소규모 | 프로덕션, 대규모 | 프로토타입, 연구 |

**사주 서비스 권장**:
- **MVP 단계**: Chroma 또는 FAISS (빠른 개발, 무료)
- **프로덕션**: Pinecone (확장성, 안정성)

**Source**: [LiquidMetal AI - Vector Database Comparison 2025](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)

#### ChromaDB 2025 업데이트

ChromaDB의 2025년 Rust 재작성으로 원래 Python 구현 대비 **4배 빠른 쓰기/쿼리** 성능 달성. 1000만 벡터 이하 프로토타입에서는 성능 차이가 미미함.

**Source**: [DataCamp - Best Vector Databases 2026](https://www.datacamp.com/blog/the-top-5-vector-databases)

---

### 1.3 한국어 임베딩 모델

#### 한국어 RAG용 임베딩 모델 벤치마크 [High Confidence]

| 모델 | 특징 | 추천 용도 |
|------|------|----------|
| **KoSimCSE-roberta-multitask** | AVG Score 최고, KLUE-BERT 기반 | 한국어 RAG 메인 |
| **ko-sroberta-multitask** | 균형잡힌 성능 | 범용 |
| **multilingual-e5-large-instruct** | 다국어 지원 | 글로벌 확장 시 |
| **paraphrase-multilingual-mpnet-base-v2** | 다국어, 가벼움 | 리소스 제한 환경 |

**Source**: [GitHub - Korean Embedding Model Benchmark](https://github.com/ssisOneTeam/Korean-Embedding-Model-Performance-Benchmark-for-Retriever)

#### 한국어 Reranker (Cross-Encoder)

**ko-reranker**는 BAAI/bge-reranker-larger를 한국어 데이터로 파인튜닝한 모델입니다.

**2단계 검색 전략**:
1. **1단계 (Bi-encoder)**: 벡터 검색으로 후보 문서 빠르게 검색
2. **2단계 (Cross-encoder)**: Reranker로 정확한 관련성 재측정

**효과**: 한국어 파인튜닝 Reranker 적용 시 성능 향상 확인

**Source**: [AWS 기술 블로그 - 한국어 Reranker를 활용한 RAG 성능 올리기](https://aws.amazon.com/ko/blogs/tech/korean-reranker-rag/)

---

### 1.4 AI 환각 방지 기술

#### RAG의 환각 방지 메커니즘 [High Confidence]

> "RAG를 '환각 방지 기술'이라고 부르는 것은 그 중요성을 과소평가하는 것입니다. RAG는 신뢰할 수 있는, 동적으로 근거가 있는 AI 시스템을 구축하기 위한 기본 아키텍처 패턴으로 진화했습니다."

**핵심 전략**:

1. **실시간 지식 검색**: 응답 생성 전 외부 데이터베이스에서 관련 정보 검색
2. **근거 기반 응답**: 검색된 문서에 기반한 응답으로 추측 최소화
3. **프롬프트 엔지니어링**: "다음 문서에만 기반하여 답변하세요" 지시문 활용

**Source**: [Zero Gravity Marketing - Science Behind RAG](https://zerogravitymarketing.com/blog/the-science-behind-rag)

#### 다층 환각 방지 접근법

2024년 Stanford 연구에 따르면, **RAG + RLHF + Guardrails** 조합 시 기준 모델 대비 **96% 환각 감소** 달성.

**Production-Grade 환각 방지 요소**:
- Ensemble Retrievers (BM25 + Vector Search)
- Cross-encoder Reranking
- Guardrails for Safety
- Session Memory Management
- Structured Output Parsing

**Source**: [arXiv - Mitigating Hallucination in LLMs Survey](https://arxiv.org/abs/2510.24476)

#### RE-RAG 신뢰도 점수 시스템

RE-RAG는 검색된 각 문서에 **신뢰도 점수**를 부여하여 검색 품질이 낮을 때 모델 내부 지식으로 폴백할지 결정.

**사주 서비스 적용**: 사주 지식DB 검색 결과의 신뢰도에 따라 응답 전략 분기 가능

---

### 1.5 프롬프트 엔지니어링 패턴

#### LangChain 프롬프트 템플릿 유형 [High Confidence]

| 템플릿 유형 | 용도 | 사주 서비스 적용 |
|------------|------|-----------------|
| **String-based** | 단순 완성 모델 | 기본 운세 텍스트 생성 |
| **ChatPromptTemplate** | 다중 메시지 대화 | 대화형 사주 상담 |
| **Few-shot Templates** | 인컨텍스트 학습 | 사주 해석 예시 제공 |

**Source**: [LangChain Prompt Templates Tutorial](https://langchain-tutorials.com/lessons/langchain-essentials/lesson-6)

#### Structured Output 활용

```python
# 사주 해석 결과를 JSON 구조로 출력
from langchain.output_parsers import PydanticOutputParser

class SajuInterpretation(BaseModel):
    daily_fortune: str
    lucky_color: str
    lucky_number: int
    advice: str
    confidence_score: float
```

**Best Practices**:
- 원하는 출력 형식 명시 (리스트, JSON, 불릿포인트)
- 복잡한 프롬프트는 Few-shot 예시 추가
- 보안: Jinja2 대신 f-string 포맷팅 권장

**Source**: [Know How Stack - Best LangChain Prompt Templates 2025](https://knowhowstack.com/best-langchain-prompt-templates/)

---

### 1.6 만세력 API 분석

#### 한국 만세력 API 옵션 [High Confidence]

| API | 제공자 | 기능 | 비용 | 트래픽 |
|-----|--------|------|------|--------|
| **음양력 정보 API** | 한국천문연구원 (KASI) | 음양력 변환, 간지(세차/일진), 율리우스적일 | 무료 | 개발 10,000건/운영 확장 가능 |
| **특일 정보 API** | KASI | 공휴일, 기념일 | 무료 | 동일 |
| **절기 정보** | 공공데이터포털 | 24절기, 절입 시간 | 무료 | 동일 |

**Source**: [한국천문연구원 Open API](https://astro.kasi.re.kr/information/pageView/31), [공공데이터포털](https://www.data.go.kr/data/15012679/openapi.do)

#### API 데이터 항목

- 연/월/일 (음력/양력)
- 윤년/윤달 구분
- 요일
- **간지(세차)**: 연간지
- **간지(일진)**: 일간지
- **간지(월)**: 월간지
- 율리우스적일
- 월일수(음력)

**추가 개발 필요 사항**:
- 시간 간지(시주) 계산 로직 자체 구현 필요
- 24절기 기반 월주 보정 로직
- 야자시/조자시 처리

**Source**: [사주 만세력 JAVA 백엔드 개발 블로그](https://rgbitcode.com/blog/senspond/6)

---

### 1.7 OpenAI API 비용 분석

#### GPT-4o 가격 (2025-2026) [High Confidence]

| 모델 | 입력 (1M 토큰) | 출력 (1M 토큰) | 원화 환산 (입력) |
|------|---------------|---------------|-----------------|
| **GPT-4o** | $2.50 | $10.00 | ≈₩3,625 |
| **GPT-4o mini** | $0.15 | $0.60 | ≈₩218 |
| **GPT-4 Turbo** | $10.00 | $30.00 | ≈₩14,500 |

**사주 서비스 비용 예측 (GPT-4o mini 기준)**:

| 시나리오 | 토큰 사용량 | 예상 비용/건 |
|----------|------------|-------------|
| 일운 기본 해석 | 입력 500 + 출력 300 | ≈₩0.25 |
| 선택지 추가 질문 | 입력 800 + 출력 500 | ≈₩0.42 |
| 심층 상담 (5턴) | 입력 3000 + 출력 2000 | ≈₩1.65 |

**Source**: [OpenAI API Pricing](https://openai.com/api/pricing/)

---

## 2. 도메인 리서치 (Domain Research)

### 2.1 사주명리학 기초 구조

#### 사주팔자 핵심 개념 [High Confidence]

**사주(四柱)**: 연주(年柱), 월주(月柱), 일주(日柱), 시주(時柱)의 네 기둥

**팔자(八字)**: 각 기둥의 천간(天干)과 지지(地支), 총 8글자

```
        연주    월주    일주    시주
천간     甲      丙      戊      庚
지지     子      寅      辰      午
```

**Source**: [위키백과 - 사주팔자](https://ko.wikipedia.org/wiki/%EC%82%AC%EC%A3%BC%ED%8C%94%EC%9E%90)

#### 천간(天干) - 10개

| 양(+) | 음(-) | 오행 |
|-------|-------|------|
| 갑(甲) | 을(乙) | 목(木) |
| 병(丙) | 정(丁) | 화(火) |
| 무(戊) | 기(己) | 토(土) |
| 경(庚) | 신(辛) | 금(金) |
| 임(壬) | 계(癸) | 수(水) |

#### 지지(地支) - 12개

| 양(+) | 음(-) | 연관 |
|-------|-------|------|
| 자(子), 인(寅), 진(辰), 오(午), 신(申), 술(戌) | 축(丑), 묘(卯), 사(巳), 미(未), 유(酉), 해(亥) | 12띠, 12달, 12시 |

**Source**: [사주스터디 - 천간지지 관계](https://www.sajustudy.com/54)

#### 십성(十星) 체계

일간(日干, 나)을 기준으로 다른 글자들과의 관계:

| 십성 | 관계 | 의미 |
|------|------|------|
| 비견(比肩) | 같은 오행, 같은 음양 | 형제, 경쟁자 |
| 겁재(劫財) | 같은 오행, 다른 음양 | 협력자, 라이벌 |
| 식신(食神) | 내가 생하는 오행, 같은 음양 | 재능, 표현 |
| 상관(傷官) | 내가 생하는 오행, 다른 음양 | 창의, 반항 |
| 편재(偏財) | 내가 극하는 오행, 같은 음양 | 투자, 아버지 |
| 정재(正財) | 내가 극하는 오행, 다른 음양 | 급여, 아내 |
| 편관(偏官) | 나를 극하는 오행, 같은 음양 | 권력, 스트레스 |
| 정관(正官) | 나를 극하는 오행, 다른 음양 | 직장, 남편 |
| 편인(偏印) | 나를 생하는 오행, 같은 음양 | 학문, 편모 |
| 정인(正印) | 나를 생하는 오행, 다른 음양 | 어머니, 문서 |

**Source**: [위키백과 - 십성](https://ko.wikipedia.org/wiki/%EC%8B%AD%EC%84%B1_(%EC%82%AC%EC%A3%BC%ED%8C%94%EC%9E%90))

#### DB 설계 권장 구조

```sql
-- 핵심 테이블
천간(id, 한자, 음양, 오행, 색상, 방향, 장기)
지지(id, 한자, 음양, 오행, 계절, 방위, 월, 띠, 색상)
육십갑자(id, 천간_id, 지지_id)
지장간(지지_id, 여기, 중기, 정기)
십성(id, 명칭, 유형)
십성관계(일간_id, 대상천간_id, 십성_id)

-- 확장 테이블
대운(사주_id, 순서, 천간, 지지, 시작나이)
세운(연도, 천간, 지지)
일운(날짜, 천간, 지지, 절기)
```

**Source**: [Google Patents - 사주풀이 서비스 시스템](https://patents.google.com/patent/KR102502645B1/ko)

---

### 2.2 AI 운세 서비스 산업 현황

#### 주요 경쟁 서비스 분석 [High Confidence]

| 서비스 | 운영사 | 누적 이용자 | 주요 특징 | 매출 |
|--------|--------|------------|----------|------|
| **점신** | 테크랩스 | 1,900만+ | 빅데이터 AI, 관상 분석, 인맥보고서 | 830억원/년 |
| **포스텔러** | 운칠기삼 | 860만+ | 전문가 콘텐츠, 해외 진출 | 100억원+/년 |
| **운세박사 GPT** | 로켓AI | 300만+ | GPT 스토어 1위, CES 2025 참가 | - |
| **사주GPT** | - | - | 무료, 웹 기반 | - |

**Source**: [한국일보 - 포스텔러 인터뷰](https://www.hankookilbo.com/News/Read/A2023051514260005915), [점신 공식](https://www.jeomsin.co.kr/)

#### 점신 기술 특징

- AI + 사주 알고리즘 결합
- 오늘의 운세, 감정 흐름, 대인 관계 즉시 해석
- AI 관상 분석 → 손금 분석 확대 예정
- 사주·오행 흐름과 대운·세운 시각화 만세력

**Source**: [전자신문 - AI 운세 플랫폼](https://www.etnews.com/20221130000250)

#### 포스텔러/운칠기삼 기술 접근법

- **FAS(Fortune Analysis System)**: 사주 값 수치화 자체 개발
- **명리학 AI 학습**: 다양한 가설 적용, 이용자 반응 데이터 반영
- **12명 전문가 파트너십**: 점성술, 타로, 동양철학 분야

**Source**: [ZDNet - 포스텔러 인터뷰](https://zdnet.co.kr/view/?no=20250203104315)

---

### 2.3 규제 및 법적 고려사항

#### 개인정보 보호법 적용 [High Confidence]

**생년월일의 법적 지위**: 일반 개인정보 (민감정보 아님)

| 정보 유형 | 예시 | 운세 앱 해당 |
|----------|------|-------------|
| **일반 개인정보** | 이름, 생년월일, 전화번호 | ✅ 해당 |
| **민감정보** | 건강, 사상·신념, 성생활 | ❌ 미해당 |
| **고유식별정보** | 주민번호, 여권번호 | ❌ 미해당 |

**Source**: [찾기쉬운 생활법령정보](https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1257&ccfNo=2&cciNo=3&cnpClsNo=2)

#### 운세 앱 운영 시 준수사항

1. **수집 동의**: 목적 명확히 고지, 동의 획득
2. **14세 미만**: 법정대리인 동의 필수
3. **안전성 확보**: 암호화, 접근 통제 조치
4. **제3자 제공**: 별도 동의 필요

#### 포인트 서비스 규제

| 발행 잔액 | 규제 |
|----------|------|
| **30억 이하** | 금융위 등록 불필요 |
| **30억 초과** | 선불전자지급수단 발행 및 관리업 등록 필수 |

**Source**: [NEPLA - 포인트 서비스 유의점](https://www.nepla.ai/wiki/%EA%B8%B0%EC%97%85%EA%B3%BC-%EC%86%8C%EB%B9%84%EC%9E%90/%EC%86%8C%EB%B9%84%EC%9E%90-%EC%A0%84%EC%9E%90%EC%83%81%EA%B1%B0%EB%9E%98/%ED%8F%AC%EC%9D%B8%ED%8A%B8-%EC%84%9C%EB%B9%84%EC%8A%A4%EB%A5%BC-%EC%8B%9C%EC%9E%91%ED%95%A0-%EB%95%8C-%EC%9C%A0%EC%9D%98%ED%95%A0-%EC%A0%90-x6w9wd2z18gk)

---

## 3. 마켓 리서치 (Market Research)

### 3.1 AI 운세 시장 규모

#### 한국 점술 시장 [High Confidence]

| 지표 | 수치 | 출처 |
|------|------|------|
| **시장 규모** | 1조 4,000억원 | 혁신의숲 |
| **1인당 소비** | 약 8만원 (10~39세) | 혁신의숲 |
| **앱 시장 성장** | 5년간 3배 이상 | 업계 집계 |

**Source**: [매거진한경 - 비대면 점술 시장](https://magazine.hankyung.com/business/article/202405226315b)

#### 주요 플레이어 실적

| 서비스 | 2024년 실적 | 성장률 |
|--------|------------|--------|
| 점신 (테크랩스) | 매출 830억, 영업이익 100억 | 매출 +58%, 영업이익 +85% |
| 포스텔러 (운칠기삼) | 매출 100억+ 달성, 흑자전환 | 투자 85억 유치 |

**Source**: [아시아경제 - AI에 신년운세 묻는 MZ](https://www.asiae.co.kr/article/2026010711243850054)

#### AI 운세 검색량 급증

- **'GPT 사주'** 네이버 검색량: 전월 대비 **129.48% 증가**
- **GPT 스토어** 라이프스타일 부문: 운세 서비스 상위권 다수 진입

**Source**: [디지털포용뉴스 - MZ세대 챗GPT 사주](https://www.dginclusion.com/news/articleView.html?idxno=840)

---

### 3.2 MZ세대 이용 패턴

#### 이용자 통계 [High Confidence]

| 지표 | 수치 |
|------|------|
| 비대면 점술 플랫폼 MZ세대 비중 | **80%** |
| Z세대 운세로 자기이해 추구 비율 | **68.4%** |
| 재미로 점·운세 이용 (Z세대) | **68.4%** (전 세대 최고) |
| 월평균 운세 상담 건수/거래액 증가율 | **30%** YoY |

**Source**: [대학내일20대연구소 - Z세대 점·운세 이용 실태 (2022)](https://www.asiae.co.kr/article/2024122714492037903)

#### MZ세대 운세 이용 동기

1. **자기 이해 도구**: 미신이 아닌 자기 파악 방법으로 인식
2. **스트레스 해소**: 미래 불확실성에 대한 심리적 안정 추구
3. **엔터테인먼트**: 재미있는 콘텐츠로 소비
4. **디지털 친숙성**: 채팅/화상 기반 비대면 선호

**심각한 스트레스 경험 응답자**: 2022년 36% → 2024년 **46.3%** (+10.3%p)

**Source**: [빠띠 - MZ세대가 무속에 진심이 된 이유](https://campaigns.do/articles/19615)

#### AI 운세의 차별화 요소

- **접근 편의성**: 시간/장소 제약 없음
- **비용 효율**: 무료~저가 서비스 다수
- **부담 없음**: AI에겐 솔직한 질문 가능
- **초개인화**: '나의 인생' 분석에 대한 매력

---

### 3.3 과금 모델 벤치마크

#### 한국 생성형 AI 구독 현황 [High Confidence]

| 지표 | 2024년 1월 | 2024년 12월 | 성장 |
|------|-----------|------------|------|
| 주요 7개 AI 서비스 결제 건수 | 5.2만 건 | **166.6만 건** | **32배** |
| 건당 평균 결제액 (개인) | - | **₩34,700** | - |
| 건당 평균 결제액 (법인) | - | **₩107,400** | - |

**비교**: 넷플릭스(₩7,000), 쿠팡(₩7,890), 멜론(₩7,590)의 **5~7배**

**Source**: [한국경제 - 생성형 AI 구독 30배 급증](https://www.hankyung.com/article/2026011875001)

#### 운세 서비스 과금 모델 유형

| 모델 | 설명 | 사례 |
|------|------|------|
| **건당 포인트** | 콘텐츠별 포인트 차감 | 점신, 포스텔러 |
| **구독제** | 월정액 무제한 이용 | - |
| **프리미엄** | 기본 무료 + 심화 유료 | 대부분 서비스 |
| **광고 기반** | 무료 + 광고 수익 | 일부 무료 앱 |

**사주 서비스 권장 모델**:
- **MVP**: 건당 포인트 (비용 예측 가능, 업셀링 용이)
- **성장기**: 등급별 쿼터 (무료 → 베이직 → 프리미엄)

---

### 3.4 성장 동향 및 전망

#### 글로벌 확장 사례

- **운세박사 GPT**: CES 2025에서 **3,000여 명** 체험
- **포스텔러**: 미국, 일본, 인도, 필리핀, 싱가포르 **5개국** 진출

**Source**: [아시아경제 - AI에 신년운세 묻는 MZ](https://www.asiae.co.kr/article/2026010711243850054)

#### 기술 트렌드

1. **대화형 AI 심화**: 후속 질문, 심층 탐구 기능 강화
2. **멀티모달 확장**: 관상(얼굴), 손금 이미지 분석
3. **개인화 고도화**: 실시간 맥락(날씨, 뉴스) 반영
4. **소셜 기능**: 궁합, 인맥보고서 등 바이럴 요소

---

## 4. 통합 분석 및 권고사항

### 4.1 기술 아키텍처 권고

#### 권장 기술 스택

```yaml
LLM:
  primary: GPT-4o mini  # 비용 효율
  fallback: GPT-4o      # 복잡한 해석

Embedding:
  model: BM-K/KoSimCSE-roberta-multitask
  dimension: 768

Vector DB:
  mvp: ChromaDB  # 빠른 개발
  production: Pinecone  # 확장성

Reranker:
  model: Dongjin-kr/ko-reranker
  strategy: Two-stage (Bi-encoder → Cross-encoder)

Framework:
  langchain: 0.3+
  langsmith: 모니터링/평가
```

#### RAG 파이프라인 설계

```
[사용자 입력: 생년월일시]
        ↓
[만세력 API: 사주팔자 계산]
        ↓
[사주 지식DB 검색: 천간/지지/십성 해석]
        ↓
[한국어 Reranker: 관련성 재순위]
        ↓
[프롬프트 구성: 컨텍스트 + 질문 + 출력 형식]
        ↓
[LLM 응답: 일운 해석]
        ↓
[Structured Output: JSON 파싱]
```

---

### 4.2 비즈니스 모델 권고

#### MVP 과금 구조

| 기능 | 무료 | 베이직 (₩3,900/월) | 프리미엄 (₩9,900/월) |
|------|------|-------------------|---------------------|
| 일운 조회 | 1회/일 | 무제한 | 무제한 |
| 선택지 질문 | 2회/일 | 10회/일 | 무제한 |
| 심층 상담 | ❌ | 3회/월 | 무제한 |
| 궁합 분석 | 건당 ₩1,000 | 5회/월 | 무제한 |

#### API 비용 최적화 전략

1. **선택지 기반 UI**: 토큰 소비 예측 가능
2. **캐싱**: 동일 일운 요청 캐시 (1일 단위)
3. **프롬프트 최적화**: 시스템 프롬프트 토큰 최소화
4. **모델 계층화**: 단순 → mini, 복잡 → 4o

---

### 4.3 구현 우선순위 (MVP)

| 순서 | 작업 | 예상 기간 | 의존성 |
|------|------|----------|--------|
| 1 | 사주 지식베이스 구축 (천간/지지/십성) | 1주 | - |
| 2 | 만세력 API 연동 (KASI) | 3일 | - |
| 3 | 한국어 임베딩 + ChromaDB 설정 | 3일 | 1 |
| 4 | LangChain RAG 체인 구현 | 1주 | 1, 2, 3 |
| 5 | 선택지 UI 개발 | 1주 | 4 |
| 6 | 포인트 시스템 연동 | 3일 | 5 |
| 7 | 한국어 Reranker 적용 | 3일 | 4 |

**총 예상 기간**: 4-5주

---

### 4.4 리스크 및 대응 전략

| 리스크 | 영향도 | 대응 전략 |
|--------|--------|----------|
| **AI 환각** | High | RAG + 신뢰도 점수 + 폴백 메시지 |
| **API 비용 폭주** | High | 선택지 UI + 등급별 쿼터 + 캐싱 |
| **개인정보 이슈** | Medium | 명확한 동의 절차 + 암호화 저장 |
| **사주 해석 정확도** | Medium | 전문가 검수 + 사용자 피드백 반영 |
| **경쟁 심화** | Medium | 친근한 코칭 톤 + 대화형 차별화 |

---

## 5. 참고문헌 및 출처

### 기술 문서

1. [LangChain RAG Documentation](https://docs.langchain.com/oss/python/langchain/rag)
2. [DEV Community - RAG in 2026 Blueprint](https://dev.to/suraj_khaitan_f893c243958/-rag-in-2026-a-practical-blueprint-for-retrieval-augmented-generation-16pp)
3. [AWS 기술 블로그 - 한국어 Reranker RAG](https://aws.amazon.com/ko/blogs/tech/korean-reranker-rag/)
4. [GitHub - Korean Embedding Model Benchmark](https://github.com/ssisOneTeam/Korean-Embedding-Model-Performance-Benchmark-for-Retriever)
5. [LiquidMetal AI - Vector Database Comparison 2025](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)
6. [OpenAI API Pricing](https://openai.com/api/pricing/)
7. [LangChain Prompt Templates Tutorial](https://langchain-tutorials.com/lessons/langchain-essentials/lesson-6)
8. [arXiv - Mitigating Hallucination in LLMs](https://arxiv.org/abs/2510.24476)

### 도메인 자료

9. [위키백과 - 사주팔자](https://ko.wikipedia.org/wiki/%EC%82%AC%EC%A3%BC%ED%8C%94%EC%9E%90)
10. [위키백과 - 십성](https://ko.wikipedia.org/wiki/%EC%8B%AD%EC%84%B1_(%EC%82%AC%EC%A3%BC%ED%8C%94%EC%9E%90))
11. [사주스터디 - 천간지지 관계](https://www.sajustudy.com/54)
12. [한국천문연구원 Open API](https://astro.kasi.re.kr/information/pageView/31)
13. [공공데이터포털 - 음양력 정보](https://www.data.go.kr/data/15012679/openapi.do)

### 시장 분석

14. [매거진한경 - 비대면 점술 시장](https://magazine.hankyung.com/business/article/202405226315b)
15. [아시아경제 - AI에 신년운세 묻는 MZ](https://www.asiae.co.kr/article/2026010711243850054)
16. [디지털포용뉴스 - MZ세대 챗GPT 사주](https://www.dginclusion.com/news/articleView.html?idxno=840)
17. [ZDNet - 포스텔러 인터뷰](https://zdnet.co.kr/view/?no=20250203104315)
18. [한국경제 - 생성형 AI 구독 30배 급증](https://www.hankyung.com/article/2026011875001)
19. [빠띠 - MZ세대가 무속에 진심이 된 이유](https://campaigns.do/articles/19615)

### 규제 및 법률

20. [찾기쉬운 생활법령정보 - 고유식별정보](https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1257&ccfNo=2&cciNo=3&cnpClsNo=2)
21. [NEPLA - 포인트 서비스 유의점](https://www.nepla.ai/wiki/%EA%B8%B0%EC%97%85%EA%B3%BC-%EC%86%8C%EB%B9%84%EC%9E%90/%EC%86%8C%EB%B9%84%EC%9E%90-%EC%A0%84%EC%9E%90%EC%83%81%EA%B1%B0%EB%9E%98/%ED%8F%AC%EC%9D%B8%ED%8A%B8-%EC%84%9C%EB%B9%84%EC%8A%A4%EB%A5%BC-%EC%8B%9C%EC%9E%91%ED%95%A0-%EB%95%8C-%EC%9C%A0%EC%9D%98%ED%95%A0-%EC%A0%90-x6w9wd2z18gk)

---

_Research completed: 2026-01-27_
_Facilitator: AI Research Assistant_
_Participant: DongDong_
