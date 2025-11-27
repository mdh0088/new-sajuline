# AWS Lambda 배포 가이드

FastAPI 백엔드를 AWS Lambda로 배포하기 위한 가이드입니다.

## 목차
1. [Lambda vs EC2 비교](#1-lambda-vs-ec2-비교)
2. [Cold Start 이해](#2-cold-start-이해)
3. [Cold Start 해결 방법](#3-cold-start-해결-방법)
4. [동시성 계산](#4-동시성-계산)
5. [VPC Lambda 아키텍처](#5-vpc-lambda-아키텍처)
6. [구현 가이드](#6-구현-가이드)
7. [권장 사항](#7-권장-사항)

---

## 1. Lambda vs EC2 비교

### 개요

| 항목 | EC2 | Lambda |
|------|-----|--------|
| **서버 관리** | 직접 관리 필요 | 서버리스 (AWS 관리) |
| **과금 방식** | 24시간 고정 비용 | 요청당 과금 |
| **확장성** | 수동/Auto Scaling | 자동 확장 |
| **Cold Start** | 없음 | 있음 (5-15초) |
| **WebSocket** | 지원 | 미지원 (별도 구성 필요) |
| **최대 실행 시간** | 무제한 | 15분 |

### 비용 비교 (50-100명 규모)

| 항목 | EC2 (t3.small) | Lambda |
|------|----------------|--------|
| 월 기본 비용 | ~$15-20 | $0 |
| 요청 비용 | 없음 | 100만 요청당 $0.20 |
| 예상 총 비용 | ~$20-30/월 | ~$5-15/월 |

---

## 2. Cold Start 이해

### Cold Start란?

Lambda 함수가 **처음 실행되거나 오랫동안 사용되지 않았을 때** 발생하는 초기화 지연 시간입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Lambda 실행 과정                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Cold Start 발생 시]                                        │
│                                                              │
│   요청 ──► 컨테이너 생성 ──► 코드 로드 ──► 초기화 ──► 실행   │
│            (1-2초)         (1-2초)      (1-5초)    (실제처리) │
│            └──────────── Cold Start ──────────┘              │
│                         (총 3-15초)                          │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Warm Start - 이미 실행 중일 때]                            │
│                                                              │
│   요청 ──► 바로 실행                                         │
│           (수십 ms)                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Cold Start 발생 조건

1. 첫 번째 요청
2. 약 5-15분간 요청이 없었을 때
3. 동시 요청이 급증할 때 (새 인스턴스 생성)

### VPC Lambda의 추가 지연

```
일반 Lambda:  컨테이너 생성 + 코드 로드           = 1-3초
VPC Lambda:   컨테이너 생성 + 코드 로드 + ENI 연결 = 5-15초
                                         └── 네트워크 인터페이스
                                             (DB 연결용)
```

---

## 3. Cold Start 해결 방법

### 방법 1: Lambda Warm-up (무료)

5분마다 Lambda를 호출하여 "Warm" 상태를 유지합니다.

```
┌─────────────────────────────────────────┐
│  CloudWatch Events (5분마다)            │
│         │                               │
│         ▼                               │
│  Lambda 함수 호출 (빈 요청)              │
│         │                               │
│         ▼                               │
│  Lambda가 "Warm" 상태 유지              │
└─────────────────────────────────────────┘
```

**구현:**
```python
@app.get("/warmup")
async def warmup():
    return {"status": "warm"}
```

**CloudWatch Events 규칙:**
```
rate(5 minutes) → Lambda 호출 → /warmup 엔드포인트
```

**장점:** 거의 무료 (월 수십 원)
**단점:** 동시 요청 급증 시 새 인스턴스는 여전히 Cold Start 발생

### 방법 2: Provisioned Concurrency (유료)

항상 N개의 Lambda를 "Warm" 상태로 유지합니다.

| 설정 | Cold Start | 추가 비용 |
|------|------------|----------|
| 없음 | 5-15초 | $0 |
| 3개 유지 | 없음 | ~$20-30/월 |
| 5개 유지 | 없음 | ~$30-50/월 |

### 방법 3: 코드 최적화

```python
# ❌ 나쁜 예 - 모든 것을 한번에 import
from langchain import *
from openai import *
from sqlalchemy import *

# ✅ 좋은 예 - 필요한 것만 import, 나머지는 lazy load
from fastapi import FastAPI

def get_openai_client():
    from openai import OpenAI
    return OpenAI()
```

| 최적화 | 효과 |
|--------|------|
| 패키지 크기 줄이기 | 1-3초 단축 |
| 불필요한 import 제거 | 0.5-2초 단축 |
| DB 연결 재사용 | 1-2초 단축 |

---

## 4. 동시성 계산

### 핵심 개념: 동시 접속자 ≠ 동시 요청

```
┌─────────────────────────────────────────────────────────────┐
│  100명 동시 접속 중                                          │
│                                                              │
│  사용자 행동:                                                │
│  - 페이지 읽는 시간: 5-30초                                  │
│  - API 호출: 순간적 (0.1-0.5초)                              │
│                                                              │
│  실제 동시 API 요청: 5-10개 정도                             │
└─────────────────────────────────────────────────────────────┘
```

### 계산 공식

```
필요한 Lambda 인스턴스 = 동시 접속자 × (API 응답 시간 / 요청 간격)
```

**예시:**
```
동시 접속자: 100명
평균 요청 간격: 10초에 1번
API 응답 시간: 200ms (0.2초)

필요한 Lambda 인스턴스 = 100 × (0.2 / 10) = 2개
```

### 시나리오별 예상치

| 시나리오 | 동시 접속 | 필요 인스턴스 |
|----------|----------|--------------|
| 일반 사용 | 50명 | 2-5개 |
| 활발한 사용 | 100명 | 5-15개 |
| 피크 타임 | 100명 | 10-20개 |
| AI 분석 (3초 소요) | 100명 | 30-50개 |

### 50-100명 서비스의 경우

```
┌──────────────────────────────────────────┐
│  오후 2시 - 50명 접속 중                  │
│                                          │
│  14:00:00.000  유저A API 호출 → Lambda #1 │
│  14:00:00.050  유저B API 호출 → Lambda #1 │ ← A 끝나서 재사용
│  14:00:00.100  유저C API 호출 → Lambda #1 │
│  14:00:00.150  유저D API 호출 → Lambda #1 │
│                                          │
│  → 1-2개 인스턴스로 충분히 처리           │
└──────────────────────────────────────────┘
```

---

## 5. VPC Lambda 아키텍처

### 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                           AWS VPC                                    │
│  ┌─────────────────────┐    ┌─────────────────────────────────────┐ │
│  │   Public Subnet     │    │         Private Subnet               │ │
│  │                     │    │                                       │ │
│  │  ┌───────────────┐  │    │  ┌─────────────┐  ┌───────────────┐ │ │
│  │  │ NAT Gateway   │  │    │  │   Lambda    │  │  RDS/MariaDB  │ │ │
│  │  │               │◄─┼────┼──│  (FastAPI)  │──│  (Private)    │ │ │
│  │  └───────────────┘  │    │  └─────────────┘  └───────────────┘ │ │
│  │         ▲           │    │         │                            │ │
│  │         │           │    │         │         ┌───────────────┐ │ │
│  │  ┌──────┴────────┐  │    │         └────────►│    Redis      │ │ │
│  │  │ API Gateway   │  │    │                   │  (ElastiCache)│ │ │
│  │  │ (HTTP API)    │  │    │                   └───────────────┘ │ │
│  │  └───────────────┘  │    │                                       │ │
│  └─────────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
    ┌────┴────┐
    │  Users  │
    └─────────┘
```

### 필요한 AWS 리소스

| 리소스 | 용도 | 필수 여부 |
|--------|------|----------|
| API Gateway (HTTP API) | 외부 요청 수신 | 필수 |
| Lambda | FastAPI 실행 | 필수 |
| VPC | 네트워크 격리 | 필수 |
| NAT Gateway | 외부 API 호출 (OpenAI 등) | 필수 |
| RDS/MariaDB | 데이터베이스 | 필수 |
| ElastiCache (Redis) | 캐시/세션 | 선택 |
| RDS Proxy | DB 연결 풀링 | 권장 |

### Security Group 설정

```
Lambda Security Group:
  - Outbound: All traffic (0.0.0.0/0)

RDS Security Group:
  - Inbound: MySQL/Aurora (3306) from Lambda SG
```

---

## 6. 구현 가이드

### 6.1 Mangum 설치

```bash
cd backend
pip install mangum
```

### 6.2 Lambda 핸들러 생성

```python
# src/lambda_handler.py
from mangum import Mangum
from src.main import app

# lifespan="off" - Lambda에서는 startup/shutdown 이벤트 비활성화
handler = Mangum(app, lifespan="off")
```

### 6.3 배포 옵션

#### 옵션 A: AWS SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  SajulineApi:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src.lambda_handler.handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 512
      VpcConfig:
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
      Events:
        Api:
          Type: HttpApi
```

#### 옵션 B: Serverless Framework

```yaml
# serverless.yml
service: sajuline-api

provider:
  name: aws
  runtime: python3.11
  region: ap-northeast-2
  vpc:
    securityGroupIds:
      - sg-xxxxxxxx
    subnetIds:
      - subnet-xxxxxxxx
      - subnet-xxxxxxxx

functions:
  api:
    handler: src.lambda_handler.handler
    timeout: 30
    memorySize: 512
    events:
      - httpApi: '*'
```

#### 옵션 C: Docker 컨테이너 Lambda (권장)

의존성이 많은 경우 Docker 이미지로 배포:

```dockerfile
# Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["src.lambda_handler.handler"]
```

### 6.4 Warm-up 설정

**CloudWatch Events 규칙 생성:**

```bash
aws events put-rule \
  --name "lambda-warmup" \
  --schedule-expression "rate(5 minutes)"

aws events put-targets \
  --rule "lambda-warmup" \
  --targets "Id"="1","Arn"="arn:aws:lambda:ap-northeast-2:xxx:function:sajuline-api"
```

---

## 7. 권장 사항

### 50-100명 규모 서비스

| 항목 | 권장 설정 |
|------|----------|
| Warm-up | 2-3개 유지 (5분마다 ping) |
| 또는 Provisioned | 3개 |
| Memory | 512MB - 1GB |
| Timeout | 30초 |
| 예상 비용 | 월 $10-30 |

### Lambda vs EC2 선택 기준

| 상황 | 권장 |
|------|------|
| 트래픽 불규칙/적음 | Lambda |
| 트래픽 일정/많음 | EC2/ECS |
| 서버 관리 인력 없음 | Lambda |
| 빠른 응답 필수 | EC2 또는 Lambda + Provisioned |
| 비용 최소화 우선 | Lambda |
| WebSocket 필요 | EC2/ECS |

### 현재 프로젝트 (사주라인) 권장

```
현재 상태: EC2 아키텍처 구축됨 (DEPLOYMENT_GUIDE.md 참조)

권장:
  - 초기 (트래픽 적음): Lambda 전환 고려 (비용 절감)
  - 성장 후 (트래픽 증가): EC2 유지 또는 ECS 전환

Lambda 전환 시:
  - WebSocket 사용 안 함 ✓
  - VPC 내 DB 통신 필요 ✓ (VPC Lambda로 해결)
  - Warm-up 2-3개 설정
  - AI 분석 API는 응답 시간 고려 (3초 이상 소요)
```

---

## 참고 자료

- [AWS Lambda 공식 문서](https://docs.aws.amazon.com/lambda/)
- [Mangum - ASGI Adapter for AWS Lambda](https://mangum.io/)
- [AWS SAM 공식 문서](https://docs.aws.amazon.com/serverless-application-model/)
- [Serverless Framework](https://www.serverless.com/framework/docs)
