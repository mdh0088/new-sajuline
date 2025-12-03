# 관리자 시스템 AWS Serverless 배포 가이드

Admin Frontend (S3) + Admin Backend (Lambda) 배포 가이드 - **NAT Gateway 없이 월 $9.50**

## 목차
1. [아키텍처 및 비용 개요](#1-아키텍처-및-비용-개요)
2. [NAT Instance 설정 (비용 절감)](#2-nat-instance-설정-비용-절감)
3. [Admin Backend - Lambda 배포](#3-admin-backend---lambda-배포)
4. [Admin Frontend - S3 배포](#4-admin-frontend---s3-배포)
5. [배포 자동화](#5-배포-자동화)
6. [모니터링 및 관리](#6-모니터링-및-관리)
7. [트러블슈팅](#7-트러블슈팅)

---

## 1. 아키텍처 및 비용 개요

### 1.1 전체 아키텍처

```
┌──────────────────────────────────────────────────────────────────┐
│                     Internet / Users                              │
└───────────────────────┬──────────────────────────────────────────┘
                        │
    ┌───────────────────┴───────────────────┐
    │                                       │
    ▼                                       ▼
┌──────────────────┐              ┌──────────────────────┐
│  CloudFront CDN  │              │ Lambda Function URL  │
│  (선택사항)       │              │ (직접 HTTP 엔드포인트)│
└────────┬─────────┘              └──────────┬───────────┘
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌──────────────────────┐
│   S3 Bucket      │              │   Lambda Function    │
│ (Admin Frontend) │              │  (Admin Backend)     │
│ - Vue 3 SPA      │              │  - FastAPI + Mangum  │
└──────────────────┘              └──────────┬───────────┘
                                             │
                    ┌────────────────────────┴────────────────────┐
                    │             VPC                              │
                    │  ┌────────────────┐    ┌──────────────────┐ │
                    │  │ Public Subnet  │    │  Private Subnet  │ │
                    │  │                │    │                  │ │
                    │  │ ┌────────────┐ │    │ ┌──────────────┐ │ │
                    │  │ │  Bastion   │◄┼────┼─│   Lambda     │ │ │
                    │  │ │ (NAT역할) │ │    │ │              │ │ │
                    │  │ └─────┬──────┘ │    │ └──────┬───────┘ │ │
                    │  └───────┼────────┘    │        │         │ │
                    │          │             │        │         │ │
                    │          │             │ ┌──────▼───────┐ │ │
                    │          │             │ │   MariaDB    │ │ │
                    │          │             │ │ 10.0.134.96  │ │ │
                    │          │             │ └──────────────┘ │ │
                    │          │             └──────────────────┘ │
                    └──────────┼──────────────────────────────────┘
                               │ (Internet Gateway)
                               ▼
                          Internet
```

### 1.2 비용 비교

#### 기존 방식 (NAT Gateway 사용)
```
Lambda 실행:        $8.00/월
API Gateway:        $3.50/월
NAT Gateway:        $32.00/월  ← 가장 큰 비용!
S3 + CloudFront:    $1.50/월
────────────────────────────
총계:               $45.00/월
```

#### 최적화 방식 (Bastion NAT + Function URL)
```
Lambda 실행:        $8.00/월
Function URL:       $0.00/월   ✅ API Gateway 제거
Bastion (NAT):      $0.00/월   ✅ 기존 서버 활용
S3 + CloudFront:    $1.50/월
────────────────────────────
총계:               $9.50/월
절감액:             $35.50/월 (-79% 절감!)
```

### 1.3 핵심 최적화 포인트

1. **NAT Gateway → Bastion NAT Instance**: $32/월 절감
   - 기존 Bastion을 NAT 역할로 재활용
   - iptables 기반 NAT 구성

2. **API Gateway → Lambda Function URL**: $3.50/월 절감
   - 직접 HTTPS 엔드포인트 제공
   - CORS 자동 처리

3. **Private DB 보안 유지**
   - MariaDB는 Private Subnet 유지
   - VPC 통합으로 안전한 접근

---

## 2. NAT Instance 설정 (비용 절감)

### 2.1 현재 환경 확인

#### AWS Console
1. **EC2 Console** → **Instances** 이동
2. Bastion 인스턴스 확인
   - Name: `bastion` 또는 `sajuline-bastion`
   - Instance Type: t2.micro, t3.small 등
   - Subnet: **Public Subnet**인지 확인 (필수)
   - Private IP: 예) 10.0.x.x
   - Public IP: 있어야 함

#### CLI로 확인
```bash
# Bastion 인스턴스 정보 조회
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*bastion*" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].[InstanceId,InstanceType,SubnetId,PrivateIpAddress,PublicIpAddress,State.Name]' \
  --output table

# 출력 예시:
# i-0abc123def456     t3.small    subnet-abc123    10.0.1.50    54.180.x.x    running

# 환경변수 저장 (다음 단계에서 사용)
export BASTION_INSTANCE_ID="i-0abc123def456"  # 실제 ID로 변경
export BASTION_PRIVATE_IP="10.0.1.50"         # 실제 IP로 변경
```

### 2.2 Bastion에 NAT 기능 추가

#### Step 1: Bastion 서버 접속

```bash
# SSH 접속 (키 파일 경로는 실제 경로로 변경)
ssh -i ~/.ssh/sajuline-key.pem ec2-user@<BASTION_PUBLIC_IP>
```

#### Step 2: NAT 기능 활성화

```bash
# 1. IP Forwarding 활성화 (커널 파라미터)
sudo sysctl -w net.ipv4.ip_forward=1

# 2. IP Forwarding 영구 설정 (재부팅 후에도 유지)
sudo bash -c 'echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf'

# 3. 확인
sysctl net.ipv4.ip_forward
# 출력: net.ipv4.ip_forward = 1

# 4. 네트워크 인터페이스 확인
ip addr show
# eth0, ens5, enX0 등의 인터페이스 확인 (보통 eth0)
export NET_INTERFACE="eth0"  # 실제 인터페이스명으로 변경

# 5. iptables NAT 마스커레이딩 설정
sudo iptables -t nat -A POSTROUTING -o $NET_INTERFACE -j MASQUERADE

# 6. iptables 규칙 확인
sudo iptables -t nat -L -n -v
# MASQUERADE 규칙이 POSTROUTING 체인에 있어야 함

# 7. iptables 규칙 영구 저장
# Amazon Linux 2 / CentOS
sudo yum install -y iptables-services
sudo service iptables save

# Ubuntu (있는 경우)
# sudo apt-get install -y iptables-persistent
# sudo netfilter-persistent save

# 8. 재부팅 시 자동 적용 (rc.local)
sudo bash -c "cat > /etc/rc.d/rc.local << 'EOF'
#!/bin/bash
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
exit 0
EOF"

sudo chmod +x /etc/rc.d/rc.local

# 9. SSH 접속 종료
exit
```

#### Step 3: Source/Destination Check 비활성화

**AWS Console 방식** (권장):
1. **EC2 Console** → **Instances**
2. Bastion 인스턴스 **선택**
3. **Actions** → **Networking** → **Change source/destination check**
4. **Stop** 선택 (체크박스 **해제**)
5. **Save** 클릭

**CLI 방식**:
```bash
# Source/Destination Check 비활성화
aws ec2 modify-instance-attribute \
  --instance-id $BASTION_INSTANCE_ID \
  --no-source-dest-check

# 확인
aws ec2 describe-instance-attribute \
  --instance-id $BASTION_INSTANCE_ID \
  --attribute sourceDestCheck
# 출력: "Value": false (비활성화 확인)
```

### 2.3 Route Table 변경

#### AWS Console 방식 (권장)

1. **VPC Console** → **Route Tables** 이동

2. **Private Subnet의 Route Table 찾기**
   - Filter: Subnet associations에서 Private Subnet 확인
   - 예) `rt-private-sajuline`

3. **Routes 탭** 선택

4. **Edit routes** 클릭

5. **기존 NAT Gateway 라우트 삭제** (있는 경우)
   - Destination: `0.0.0.0/0`
   - Target: `nat-xxxxx`
   - **Delete** 클릭

6. **Add route** 클릭
   - Destination: `0.0.0.0/0`
   - Target: **Instance** → Bastion 인스턴스 선택 (ID: `i-xxxxx`)
   - **Save changes** 클릭

7. **확인**
   - Routes 탭에서 `0.0.0.0/0` → `i-xxxxx` (Bastion) 확인

#### CLI 방식

```bash
# 1. Private Subnet ID 확인 (Lambda가 배치될 Subnet)
aws ec2 describe-subnets \
  --filters "Name=tag:Name,Values=*private*" \
  --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock,Tags[?Key==`Name`].Value|[0]]' \
  --output table

export PRIVATE_SUBNET_ID="subnet-xxxxx"  # 실제 Subnet ID

# 2. Private Subnet의 Route Table ID 찾기
export ROUTE_TABLE_ID=$(aws ec2 describe-route-tables \
  --filters "Name=association.subnet-id,Values=$PRIVATE_SUBNET_ID" \
  --query 'RouteTables[0].RouteTableId' \
  --output text)

echo "Route Table ID: $ROUTE_TABLE_ID"

# 3. 기존 라우트 확인
aws ec2 describe-route-tables \
  --route-table-ids $ROUTE_TABLE_ID \
  --query 'RouteTables[0].Routes'

# 4. 기존 NAT Gateway 라우트 삭제 (있는 경우)
aws ec2 delete-route \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0

# 5. Bastion (NAT Instance) 라우트 추가
aws ec2 create-route \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --instance-id $BASTION_INSTANCE_ID

# 6. 변경 확인
aws ec2 describe-route-tables \
  --route-table-ids $ROUTE_TABLE_ID \
  --query 'RouteTables[0].Routes' \
  --output table
```

### 2.4 NAT Instance 테스트

#### Private Subnet에서 테스트 (EC2가 있는 경우)

```bash
# Private Subnet의 EC2에 접속 (Bastion을 경유)
ssh -J ec2-user@<BASTION_PUBLIC_IP> ec2-user@<PRIVATE_EC2_PRIVATE_IP>

# 인터넷 연결 테스트
curl -I https://www.google.com
# HTTP/2 200 응답 확인

ping -c 3 8.8.8.8
# 패킷 정상 수신 확인
```

#### Bastion에서 트래픽 모니터링

```bash
# Bastion SSH 접속
ssh -i ~/.ssh/sajuline-key.pem ec2-user@<BASTION_PUBLIC_IP>

# NAT 트래픽 실시간 모니터링
sudo tcpdump -i eth0 -n | grep -E "443|80"
# Private Subnet에서 오는 트래픽 확인 가능

# iptables NAT 통계 확인
sudo iptables -t nat -L -n -v
# pkts (패킷 수)와 bytes 확인
```

### 2.5 기존 NAT Gateway 삭제 (비용 절감)

⚠️ **주의**: Lambda 배포 및 테스트 완료 후 삭제하세요!

#### AWS Console 방식 (권장)

1. **VPC Console** → **NAT Gateways** 이동

2. 사용 중인 NAT Gateway **선택**

3. **Actions** → **Delete NAT gateway** 클릭

4. 확인 메시지에 `delete` 입력

5. **Delete** 클릭

6. **상태 확인** (5-10분 소요)
   - State: `Deleted`

7. **Elastic IP 해제**
   - **VPC Console** → **Elastic IPs**
   - NAT Gateway가 사용하던 EIP 선택 (Associated: 비어있음)
   - **Actions** → **Release Elastic IP addresses**
   - **Release** 클릭

#### CLI 방식

```bash
# 1. NAT Gateway ID 확인
NAT_GW_ID=$(aws ec2 describe-nat-gateways \
  --filter "Name=state,Values=available" \
  --query 'NatGateways[0].NatGatewayId' \
  --output text)

echo "NAT Gateway ID: $NAT_GW_ID"

# NAT Gateway의 EIP 기록 (나중에 해제)
NAT_EIP_ALLOCATION=$(aws ec2 describe-nat-gateways \
  --nat-gateway-ids $NAT_GW_ID \
  --query 'NatGateways[0].NatGatewayAddresses[0].AllocationId' \
  --output text)

echo "NAT EIP Allocation ID: $NAT_EIP_ALLOCATION"

# 2. NAT Gateway 삭제
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_ID

# 3. 삭제 대기 (5-10분)
aws ec2 describe-nat-gateways \
  --nat-gateway-ids $NAT_GW_ID \
  --query 'NatGateways[0].State' \
  --output text

# State가 "deleted"가 될 때까지 대기

# 4. Elastic IP 해제
aws ec2 release-address --allocation-id $NAT_EIP_ALLOCATION

# 5. 확인
aws ec2 describe-addresses --allocation-ids $NAT_EIP_ALLOCATION
# Error: InvalidAllocationID.NotFound (정상)
```

**💰 비용 절감 즉시 효과**: NAT Gateway 삭제 시점부터 **월 $32 절감**

---

## 3. Admin Backend - Lambda 배포

### 3.1 사전 준비

#### VPC 리소스 확인

**AWS Console**:
1. **VPC Console** → **Subnets**
   - Private Subnet ID 2개 이상 확인 (다른 AZ)
   - 예) `subnet-abc123` (ap-northeast-2a), `subnet-def456` (ap-northeast-2c)

2. **EC2 Console** → **Security Groups**
   - DB 접근 가능한 Security Group 확인
   - Inbound: Port 33060 (MariaDB) 허용

**CLI**:
```bash
# Private Subnet ID 확인 (최소 2개, 다른 AZ)
aws ec2 describe-subnets \
  --filters "Name=tag:Name,Values=*private*" \
  --query 'Subnets[].[SubnetId,AvailabilityZone,Tags[?Key==`Name`].Value|[0]]' \
  --output table

export VPC_SUBNET_IDS="subnet-abc123,subnet-def456"

# Security Group ID 확인
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=*database*,*rds*" \
  --query 'SecurityGroups[].[GroupId,GroupName,Description]' \
  --output table

export VPC_SECURITY_GROUP_IDS="sg-xxxxx"
```

### 3.2 IAM Role 생성

#### AWS Console 방식 (권장)

1. **IAM Console** → **Roles** → **Create role**

2. **Trusted entity type**: AWS service 선택

3. **Use case**: Lambda 선택 → **Next**

4. **Permissions policies** 추가:
   - `AWSLambdaBasicExecutionRole` (필수)
   - `AWSLambdaVPCAccessExecutionRole` (필수, VPC 접근)

5. **Role name**: `sajuline-admin-lambda-role`

6. **Create role** 클릭

7. **생성된 Role 선택** → **Add permissions** → **Create inline policy**

8. **JSON 탭** 선택, 다음 입력:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::static.sajuline.com/*",
        "arn:aws:s3:::static.sajuline.com"
      ]
    }
  ]
}
```

9. **Review policy** → **Name**: `S3AccessPolicy` → **Create policy**

10. **Role ARN 복사** (나중에 사용)
    - 예) `arn:aws:iam::123456789012:role/sajuline-admin-lambda-role`

#### CLI 방식

```bash
# 1. Trust Policy 파일 생성
cat > lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 2. IAM Role 생성
aws iam create-role \
  --role-name sajuline-admin-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

# 3. 관리형 정책 연결
aws iam attach-role-policy \
  --role-name sajuline-admin-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name sajuline-admin-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

# 4. S3 접근 인라인 정책 생성
cat > s3-access-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::static.sajuline.com/*",
        "arn:aws:s3:::static.sajuline.com"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name sajuline-admin-lambda-role \
  --policy-name S3AccessPolicy \
  --policy-document file://s3-access-policy.json

# 5. Role ARN 확인 및 저장
export LAMBDA_ROLE_ARN=$(aws iam get-role \
  --role-name sajuline-admin-lambda-role \
  --query 'Role.Arn' \
  --output text)

echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"
```

### 3.3 Lambda 코드 준비

```bash
cd admin-backend

# 1. Mangum 의존성 추가
cat >> pyproject.toml << 'EOF'

[project.optional-dependencies]
lambda = [
    "mangum==0.17.0",
]
EOF

uv sync --extra lambda
```

#### Lambda Handler 파일 생성

```bash
cat > lambda_handler.py << 'EOF'
"""
AWS Lambda Handler for Admin Backend API
"""
import os
from mangum import Mangum
from src.main import app

# Lambda 환경 플래그
os.environ["IS_LAMBDA"] = "true"

# Mangum: ASGI (FastAPI) → AWS Lambda 어댑터
handler = Mangum(app, lifespan="off")
EOF
```

#### 환경변수 파일 생성

```bash
cat > .env.lambda << 'EOF'
# Application
APP_NAME=Sajuline Admin API
APP_VERSION=0.1.0
APP_ENV=production
DEBUG=false
PORT=8001

# Security (⚠️ 프로덕션용 강력한 값으로 변경!)
SECRET_KEY=CHANGE_THIS_TO_STRONG_SECRET_KEY_PROD
ADMIN_SECRET_KEY=CHANGE_THIS_TO_ADMIN_SECRET_PROD
JWT_SECRET_KEY=CHANGE_THIS_TO_JWT_SECRET_PROD
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (Frontend URL 추가)
CORS_ORIGINS=https://admin.sajuline.com,https://d1234567890.cloudfront.net

# MariaDB (VPC Private Subnet)
DATABASE_URL=mysql+aiomysql://sajuro1:tkwnfh01!@10.0.134.96:33060/sajuro_dev?charset=utf8mb4
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30

# MSSQL (외부 읽기 전용)
MSSQL_SERVER=175.117.146.168
MSSQL_PORT=2866
MSSQL_DATABASE=ars
MSSQL_USERNAME=peopleline
MSSQL_PASSWORD=peopleline##
MSSQL_DRIVER=pymssql
MSSQL_TIMEOUT=30

# AWS S3
AWS_ACCESS_KEY_ID=AKIAQEIP3DTTO5WQ2MHF
AWS_SECRET_ACCESS_KEY=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
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=static.sajuline.com
S3_DIRECTORY=admin-upload

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/tmp/admin.log

# Sentry (선택)
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Admin Settings
ADMIN_ROLES=super_admin,admin,manager,viewer
SUPER_ADMIN_EMAIL=admin@sajuline.com
ENABLE_2FA=true
OTP_ISSUER=Sajuline Admin
ENABLE_AUDIT_LOG=true
AUDIT_LOG_RETENTION_DAYS=90
SESSION_TIMEOUT_MINUTES=60
SESSION_EXTEND_ON_ACTIVITY=true

# API Docs
DOCS_URL=/docs
REDOC_URL=/redoc
OPENAPI_URL=/openapi.json

# External Services
MAIN_BACKEND_URL=https://test.sajuline.com
MAIN_FRONTEND_URL=https://test.sajuline.com

# Other
TIMEZONE=Asia/Seoul
MAX_UPLOAD_SIZE=10485760
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,gif,pdf,xlsx,xls,csv
PAGINATION_DEFAULT_LIMIT=20
PAGINATION_MAX_LIMIT=100
BACKUP_ENABLED=false
ENABLE_ANALYTICS=true
EMAIL_NOTIFICATION_ENABLED=false
EMAIL_FROM=noreply@sajuline.com

# Payment (테스트)
PAYMENT_GATEWAY_URL=https://testpgapi.payletter.com/v1.0/payments/request
PAYMENT_GATEWAY_KEY=MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=
PAYMENT_CLIENT_ID=pay_test
EOF
```

### 3.4 Lambda 배포 패키지 생성

#### Lambda Layer (의존성 패키징)

```bash
# 1. Layer 디렉토리 생성
mkdir -p lambda-layer/python

# 2. 의존성 설치 (Lambda 환경 타겟)
uv pip install \
  --target lambda-layer/python \
  --platform manylinux2014_x86_64 \
  --python-version 3.11 \
  --only-binary=:all: \
  fastapi[all]==0.110.0 \
  sqlalchemy[asyncio]==2.0.28 \
  aiomysql==0.2.0 \
  pymysql==1.1.0 \
  pymssql==2.3.0 \
  pydantic==2.6.4 \
  pydantic-settings==2.2.1 \
  python-jose[cryptography]==3.3.0 \
  passlib[bcrypt]==1.7.4 \
  boto3==1.34.162 \
  httpx==0.27.0 \
  loguru==0.7.2 \
  sentry-sdk[fastapi]==1.45.0

# 3. Layer ZIP 생성
cd lambda-layer
zip -r9 ../lambda-layer.zip .
cd ..

# 4. 패키지 크기 확인
ls -lh lambda-layer.zip
# 50MB 이하 확인
```

#### Lambda Layer 업로드

**AWS Console**:
1. **Lambda Console** → **Layers** → **Create layer**
2. **Name**: `sajuline-admin-dependencies`
3. **Upload a .zip file**: `lambda-layer.zip` 업로드
4. **Compatible runtimes**: `Python 3.11` 선택
5. **Compatible architectures**: `x86_64` 선택
6. **Create** 클릭
7. **Layer ARN 복사** (예: `arn:aws:lambda:ap-northeast-2:123456789012:layer:sajuline-admin-dependencies:1`)

**CLI**:
```bash
# Layer 생성
aws lambda publish-layer-version \
  --layer-name sajuline-admin-dependencies \
  --description "Admin Backend Python Dependencies" \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python3.11 \
  --compatible-architectures x86_64

# Layer ARN 저장
export LAMBDA_LAYER_ARN=$(aws lambda list-layer-versions \
  --layer-name sajuline-admin-dependencies \
  --query 'LayerVersions[0].LayerVersionArn' \
  --output text)

echo "Layer ARN: $LAMBDA_LAYER_ARN"
```

#### 애플리케이션 코드 패키징

```bash
# 1. 배포 디렉토리 생성
mkdir -p lambda-package

# 2. 소스 코드 복사
cp -r src lambda-package/
cp lambda_handler.py lambda-package/

# 3. Mangum만 포함 (나머지는 Layer에서 제공)
uv pip install mangum==0.17.0 --target lambda-package/

# 4. 불필요한 파일 제거 (크기 최적화)
cd lambda-package
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# 5. ZIP 생성
zip -r9 ../lambda-deployment.zip .
cd ..

# 6. 패키지 크기 확인
ls -lh lambda-deployment.zip
# 10-20MB 정도 (Layer 제외)
```

### 3.5 Lambda 함수 생성

#### 환경변수 준비

```bash
# .env.lambda 파일을 JSON 형태로 변환
python3 << 'PYTHON_SCRIPT'
import json

env_vars = {}
with open('.env.lambda', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key] = value

with open('lambda-env.json', 'w') as f:
    json.dump({"Variables": env_vars}, f, indent=2)

print("lambda-env.json 생성 완료")
PYTHON_SCRIPT
```

#### AWS Console 방식 (권장)

1. **Lambda Console** → **Functions** → **Create function**

2. **Author from scratch** 선택

3. **기본 정보**:
   - Function name: `sajuline-admin-backend`
   - Runtime: `Python 3.11`
   - Architecture: `x86_64`

4. **Permissions**:
   - Execution role: **Use an existing role**
   - Existing role: `sajuline-admin-lambda-role` 선택

5. **Create function** 클릭

6. **Code 탭**:
   - **Upload from** → **.zip file** 선택
   - `lambda-deployment.zip` 업로드
   - **Save** 클릭

7. **Configuration 탭**:
   - **General configuration** → **Edit**
     - Memory: `512 MB`
     - Timeout: `30 seconds`
     - **Save**

   - **Environment variables** → **Edit**
     - `lambda-env.json` 내용 복사하여 추가
     - 또는 하나씩 수동 입력
     - **Save**

   - **VPC** → **Edit**
     - VPC: sajuline VPC 선택
     - Subnets: Private Subnet 2개 이상 선택 (다른 AZ)
     - Security groups: DB 접근 가능한 SG 선택
     - **Save**

8. **Layers** → **Add a layer**:
   - **Custom layers** 선택
   - Layer: `sajuline-admin-dependencies` 선택
   - Version: 최신 버전 선택
   - **Add** 클릭

#### CLI 방식

```bash
# Lambda 함수 생성
aws lambda create-function \
  --function-name sajuline-admin-backend \
  --runtime python3.11 \
  --role $LAMBDA_ROLE_ARN \
  --handler lambda_handler.handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 30 \
  --memory-size 512 \
  --architecture x86_64 \
  --vpc-config SubnetIds=$VPC_SUBNET_IDS,SecurityGroupIds=$VPC_SECURITY_GROUP_IDS \
  --environment file://lambda-env.json \
  --description "Sajuline Admin Backend API"

# Lambda Layer 연결
aws lambda update-function-configuration \
  --function-name sajuline-admin-backend \
  --layers $LAMBDA_LAYER_ARN

# 업데이트 완료 대기
aws lambda wait function-updated \
  --function-name sajuline-admin-backend
```

### 3.6 Lambda Function URL 생성

#### AWS Console 방식 (권장)

1. **Lambda Console** → **Functions** → `sajuline-admin-backend` 선택

2. **Configuration 탭** → **Function URL** → **Create function URL**

3. **설정**:
   - Auth type: **NONE** (공개 API, 인증은 JWT로 처리)
   - CORS:
     - **Configure CORS** 체크
     - Allow origins: `*` 또는 `https://admin.sajuline.com`
     - Allow methods: `*`
     - Allow headers: `*`
     - Max age: `86400`

4. **Save** 클릭

5. **Function URL 복사**:
   - 예) `https://abc123def456.lambda-url.ap-northeast-2.on.aws/`
   - 이 URL이 Admin Frontend의 API Base URL

#### CLI 방식

```bash
# Function URL 생성
aws lambda create-function-url-config \
  --function-name sajuline-admin-backend \
  --auth-type NONE \
  --cors '{
    "AllowOrigins": ["*"],
    "AllowMethods": ["*"],
    "AllowHeaders": ["*"],
    "MaxAge": 86400
  }'

# Function URL 확인
export LAMBDA_FUNCTION_URL=$(aws lambda get-function-url-config \
  --function-name sajuline-admin-backend \
  --query 'FunctionUrl' \
  --output text)

echo "Lambda Function URL: $LAMBDA_FUNCTION_URL"
```

### 3.7 Lambda 테스트

#### AWS Console 테스트

1. **Lambda Console** → **Functions** → `sajuline-admin-backend`

2. **Test 탭** → **Create new test event**

3. **Event JSON**:
```json
{
  "rawPath": "/health",
  "requestContext": {
    "http": {
      "method": "GET"
    }
  }
}
```

4. **Test** 클릭

5. **결과 확인**:
   - Status: Success
   - Response body: `{"status": "healthy", ...}`

#### CLI 테스트

```bash
# Health Check
curl $LAMBDA_FUNCTION_URL/health

# 출력 예시:
# {"status":"healthy","message":"API 서버가 정상적으로 동작 중입니다.","version":"0.1.0"}

# API 문서 확인
curl $LAMBDA_FUNCTION_URL/docs
# HTML 문서 반환 (Swagger UI)
```

---

## 4. Admin Frontend - S3 배포

### 4.1 S3 Bucket 생성

#### AWS Console 방식 (권장)

1. **S3 Console** → **Buckets** → **Create bucket**

2. **Bucket name**: `admin.sajuline.com`
   - 고유한 이름이어야 함

3. **AWS Region**: `ap-northeast-2` (Asia Pacific Seoul)

4. **Block Public Access settings**:
   - **모든 체크 해제** (Public Access 허용)
   - 경고 확인 체크

5. **Bucket Versioning**: Disable (선택사항)

6. **Create bucket** 클릭

7. **생성된 Bucket 선택** → **Properties 탭**

8. **Static website hosting** → **Edit**:
   - Static website hosting: **Enable**
   - Hosting type: **Host a static website**
   - Index document: `index.html`
   - Error document: `index.html` (SPA 라우팅용)
   - **Save changes**

9. **Permissions 탭** → **Bucket policy** → **Edit**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::admin.sajuline.com/*"
    }
  ]
}
```
   - **Save changes**

10. **Website endpoint 확인**:
    - Properties 탭 → Static website hosting
    - 예) `http://admin.sajuline.com.s3-website.ap-northeast-2.amazonaws.com`

#### CLI 방식

```bash
export BUCKET_NAME="admin.sajuline.com"

# 1. Bucket 생성
aws s3 mb s3://$BUCKET_NAME --region ap-northeast-2

# 2. Static Website Hosting 활성화
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document index.html

# 3. Public Access Block 비활성화
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# 4. Bucket Policy 설정
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file://bucket-policy.json

# 5. Website URL 확인
echo "S3 Website URL: http://$BUCKET_NAME.s3-website.ap-northeast-2.amazonaws.com"
```

### 4.2 Frontend 빌드 및 배포

```bash
cd admin-front

# 1. 환경변수 설정 (.env.prod)
cat > .env.prod << EOF
VITE_API_BASE_URL=$LAMBDA_FUNCTION_URL
VITE_APP_TITLE=Sajuline Admin
VITE_APP_ENV=production
EOF

# 2. 의존성 설치
npm ci

# 3. Production 빌드
npm run build:prod

# 4. 빌드 결과 확인
ls -lh dist/
# index.html, assets/ 등 확인

# 5. S3에 업로드
aws s3 sync dist/ s3://$BUCKET_NAME/ \
  --delete \
  --cache-control "public,max-age=31536000,immutable" \
  --exclude "index.html" \
  --exclude "*.map"

# 6. index.html은 캐시 없이 업로드
aws s3 cp dist/index.html s3://$BUCKET_NAME/index.html \
  --cache-control "no-cache,no-store,must-revalidate" \
  --content-type "text/html"

# 7. 배포 확인
echo "Admin Frontend URL: http://$BUCKET_NAME.s3-website.ap-northeast-2.amazonaws.com"
```

### 4.3 CloudFront 배포 (선택사항, 성능 향상)

#### 왜 CloudFront를 사용하나요?
- **HTTPS 지원** (S3 Static Hosting은 HTTP만)
- **커스텀 도메인** (admin.sajuline.com)
- **글로벌 CDN** (전 세계 엣지 로케이션에서 캐싱)
- **성능 향상** (지연시간 감소)

#### AWS Console 방식 (권장)

1. **CloudFront Console** → **Distributions** → **Create distribution**

2. **Origin**:
   - Origin domain: S3 Bucket Website Endpoint 선택
     - ⚠️ 주의: Bucket 자체가 아니라 **Website endpoint** 선택
     - 예) `admin.sajuline.com.s3-website.ap-northeast-2.amazonaws.com`
   - Protocol: **HTTP only**
   - Name: `S3-admin-sajuline` (자동)

3. **Default cache behavior**:
   - Viewer protocol policy: **Redirect HTTP to HTTPS**
   - Allowed HTTP methods: **GET, HEAD, OPTIONS**
   - Cache key and origin requests: **CachingOptimized**
   - Compress objects automatically: **Yes**

4. **Settings**:
   - Price class: **Use only North America, Europe, Asia, Middle East, and Africa**
   - Alternate domain name (CNAME): `admin.sajuline.com` 입력
   - Custom SSL certificate: **Request certificate** (ACM)
   - Default root object: `index.html`

5. **Custom error responses** → **Create custom error response**:
   - HTTP error code: `404`
   - Customize error response: **Yes**
   - Response page path: `/index.html`
   - HTTP response code: `200`
   - **Create**

6. **Create distribution** 클릭

7. **Distribution 배포 대기** (5-10분)
   - Status: `Enabled`, Last modified: 최근 시간

8. **Distribution domain name 확인**:
   - 예) `d1234567890.cloudfront.net`

#### Route 53 연결 (커스텀 도메인)

1. **Route 53 Console** → **Hosted zones** → `sajuline.com` 선택

2. **Create record**:
   - Record name: `admin`
   - Record type: `A`
   - Alias: **Yes**
   - Route traffic to: **CloudFront distribution**
   - Distribution: 위에서 생성한 Distribution 선택
   - **Create records**

3. **접속 확인**:
   - `https://admin.sajuline.com`

---

## 5. 배포 자동화

### 5.1 GitHub Actions - Lambda 배포

`.github/workflows/deploy-admin-backend.yml`:

```yaml
name: Deploy Admin Backend to Lambda

on:
  push:
    branches: [main]
    paths:
      - 'admin-backend/**'
      - '.github/workflows/deploy-admin-backend.yml'
  workflow_dispatch:

env:
  AWS_REGION: ap-northeast-2
  LAMBDA_FUNCTION_NAME: sajuline-admin-backend

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Build Lambda Package
        working-directory: admin-backend
        run: |
          mkdir -p lambda-package
          cp -r src lambda-package/
          cp lambda_handler.py lambda-package/
          uv pip install mangum==0.17.0 --target lambda-package/
          cd lambda-package
          find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
          find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
          zip -r9 ../lambda-deployment.zip .

      - name: Deploy to Lambda
        working-directory: admin-backend
        run: |
          aws lambda update-function-code \
            --function-name ${{ env.LAMBDA_FUNCTION_NAME }} \
            --zip-file fileb://lambda-deployment.zip

      - name: Wait for Update
        run: |
          aws lambda wait function-updated \
            --function-name ${{ env.LAMBDA_FUNCTION_NAME }}

      - name: Health Check
        run: |
          FUNCTION_URL=$(aws lambda get-function-url-config \
            --function-name ${{ env.LAMBDA_FUNCTION_NAME }} \
            --query 'FunctionUrl' \
            --output text)

          echo "Testing: ${FUNCTION_URL}health"
          curl -f "${FUNCTION_URL}health" || echo "Health check warning"
```

### 5.2 GitHub Actions - S3 배포

`.github/workflows/deploy-admin-frontend.yml`:

```yaml
name: Deploy Admin Frontend to S3

on:
  push:
    branches: [main]
    paths:
      - 'admin-front/**'
      - '.github/workflows/deploy-admin-frontend.yml'
  workflow_dispatch:

env:
  AWS_REGION: ap-northeast-2
  S3_BUCKET: admin.sajuline.com
  CLOUDFRONT_DISTRIBUTION_ID: E1234567890ABC  # 실제 ID로 변경

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: admin-front/package-lock.json

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Get Lambda Function URL
        id: lambda-url
        run: |
          FUNCTION_URL=$(aws lambda get-function-url-config \
            --function-name sajuline-admin-backend \
            --query 'FunctionUrl' \
            --output text)
          echo "url=$FUNCTION_URL" >> $GITHUB_OUTPUT

      - name: Install Dependencies
        working-directory: admin-front
        run: npm ci

      - name: Build
        working-directory: admin-front
        run: npm run build:prod
        env:
          VITE_API_BASE_URL: ${{ steps.lambda-url.outputs.url }}

      - name: Deploy to S3
        working-directory: admin-front
        run: |
          aws s3 sync dist/ s3://${{ env.S3_BUCKET }}/ \
            --delete \
            --cache-control "public,max-age=31536000,immutable" \
            --exclude "index.html" \
            --exclude "*.map"

          aws s3 cp dist/index.html s3://${{ env.S3_BUCKET }}/index.html \
            --cache-control "no-cache,no-store,must-revalidate" \
            --content-type "text/html"

      - name: Invalidate CloudFront Cache
        if: env.CLOUDFRONT_DISTRIBUTION_ID != ''
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ env.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

### 5.3 GitHub Secrets 설정

**GitHub Repository** → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

추가할 Secrets:
- `AWS_ACCESS_KEY_ID`: IAM User Access Key
- `AWS_SECRET_ACCESS_KEY`: IAM User Secret Key

---

## 6. 모니터링 및 관리

### 6.1 CloudWatch 로그

#### AWS Console
1. **CloudWatch Console** → **Logs** → **Log groups**
2. `/aws/lambda/sajuline-admin-backend` 선택
3. 최근 로그 스트림 확인

#### CLI
```bash
# 실시간 로그 확인
aws logs tail /aws/lambda/sajuline-admin-backend --follow

# 에러만 필터링
aws logs filter-log-events \
  --log-group-name /aws/lambda/sajuline-admin-backend \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# 최근 1시간 로그
aws logs tail /aws/lambda/sajuline-admin-backend \
  --since 1h \
  --follow
```

### 6.2 Lambda 메트릭

#### AWS Console
1. **Lambda Console** → **Functions** → `sajuline-admin-backend`
2. **Monitor 탭** → **Metrics** 확인:
   - Invocations (호출 횟수)
   - Duration (실행 시간)
   - Errors (에러 발생)
   - Throttles (제한)

#### CLI
```bash
# 최근 1시간 호출 횟수
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=sajuline-admin-backend \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### 6.3 Bastion NAT 모니터링

```bash
# Bastion SSH 접속
ssh -i ~/.ssh/sajuline-key.pem ec2-user@<BASTION_PUBLIC_IP>

# NAT 트래픽 통계
sudo iptables -t nat -L -n -v

# 실시간 트래픽 모니터링
sudo tcpdump -i eth0 -n | grep -E "443|80"

# 네트워크 연결 상태
netstat -an | grep ESTABLISHED | wc -l
```

### 6.4 CloudWatch Alarm 설정

```bash
# Lambda 에러율 알람
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-admin-high-errors \
  --alarm-description "Lambda error rate > 5%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=sajuline-admin-backend

# Bastion CPU 알람
aws cloudwatch put-metric-alarm \
  --alarm-name bastion-high-cpu \
  --alarm-description "Bastion CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=$BASTION_INSTANCE_ID
```

---

## 7. 트러블슈팅

### 7.1 Lambda VPC 연결 실패

**증상**: Lambda에서 MariaDB 연결 시 타임아웃

**확인 사항**:
1. **Security Group Inbound 규칙**
   - DB Security Group에서 Lambda Security Group 허용 확인
   - Port: 33060 (MariaDB)

```bash
# Lambda Security Group 확인
aws lambda get-function-configuration \
  --function-name sajuline-admin-backend \
  --query 'VpcConfig.SecurityGroupIds' \
  --output text

# DB Security Group Inbound 확인
aws ec2 describe-security-groups \
  --group-ids sg-database-xxxxx \
  --query 'SecurityGroups[0].IpPermissions'
```

2. **Route Table 확인**
   - Private Subnet → Bastion (NAT) 라우팅 확인

```bash
# Route Table 확인
aws ec2 describe-route-tables \
  --route-table-ids $ROUTE_TABLE_ID \
  --query 'RouteTables[0].Routes' \
  --output table

# 0.0.0.0/0 → i-xxxxx (Bastion) 확인
```

**해결방법**:
```bash
# Security Group 규칙 추가
aws ec2 authorize-security-group-ingress \
  --group-id sg-database-xxxxx \
  --protocol tcp \
  --port 33060 \
  --source-group sg-lambda-xxxxx
```

### 7.2 Lambda Cold Start 지연

**증상**: 첫 요청이 5-10초 소요

**원인**: VPC ENI 생성 + Lambda 초기화

**해결방법**:
1. **Provisioned Concurrency** (비용 추가 발생)
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name sajuline-admin-backend \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST
```

2. **메모리 증가** (CPU 성능 향상)
```bash
aws lambda update-function-configuration \
  --function-name sajuline-admin-backend \
  --memory-size 1024
```

### 7.3 Bastion NAT 트래픽 병목

**증상**: Lambda 응답 느림, Bastion CPU 높음

**확인**:
```bash
# Bastion CPU 사용률
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$BASTION_INSTANCE_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**해결방법**:
1. **Instance Type 업그레이드**
```bash
# t3.small → t3.medium
aws ec2 modify-instance-attribute \
  --instance-id $BASTION_INSTANCE_ID \
  --instance-type t3.medium
```

2. **Multi-AZ Bastion** (고가용성)
   - 다른 AZ에 Bastion 추가 배치
   - Route Table에서 Active-Standby 구성

### 7.4 S3 CORS 오류

**증상**: Frontend에서 API 호출 시 CORS 에러

**확인**:
```bash
# Lambda Function URL CORS 설정 확인
aws lambda get-function-url-config \
  --function-name sajuline-admin-backend \
  --query 'Cors'
```

**해결방법**:
```bash
# CORS 재설정
aws lambda update-function-url-config \
  --function-name sajuline-admin-backend \
  --cors '{
    "AllowOrigins": ["https://admin.sajuline.com", "https://d1234567890.cloudfront.net"],
    "AllowMethods": ["*"],
    "AllowHeaders": ["*"],
    "MaxAge": 86400
  }'
```

### 7.5 Lambda 패키지 크기 초과

**증상**: Deployment package size exceeds 50MB

**해결방법 1**: Layer 최적화
```bash
# 불필요한 패키지 제거
# numpy, pandas 등 대용량 패키지 제외
```

**해결방법 2**: Docker 이미지 사용 (최대 10GB)
```bash
# Dockerfile 생성
cat > Dockerfile << 'EOF'
FROM public.ecr.aws/lambda/python:3.11

COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

RUN pip install --no-cache-dir \
    fastapi[all]==0.110.0 \
    mangum==0.17.0 \
    sqlalchemy[asyncio]==2.0.28 \
    aiomysql==0.2.0

CMD ["lambda_handler.handler"]
EOF

# ECR에 푸시 및 Lambda 업데이트
# (상세 내용은 AWS ECR 문서 참고)
```

---

## 부록

### A. 체크리스트

**NAT Instance 설정**:
- [ ] Bastion Public Subnet 확인
- [ ] IP Forwarding 활성화
- [ ] iptables NAT 설정
- [ ] Source/Destination Check 비활성화
- [ ] Route Table 변경 (0.0.0.0/0 → Bastion)
- [ ] Private Subnet에서 인터넷 연결 테스트
- [ ] NAT Gateway 삭제

**Lambda 배포**:
- [ ] IAM Role 생성
- [ ] VPC Subnet/SG 확인
- [ ] Lambda Layer 생성
- [ ] Lambda 함수 생성
- [ ] Lambda Function URL 생성
- [ ] Health Check 성공

**S3 배포**:
- [ ] S3 Bucket 생성
- [ ] Static Hosting 활성화
- [ ] Bucket Policy 설정
- [ ] Frontend 빌드 및 업로드
- [ ] CloudFront 배포 (선택)
- [ ] 접속 테스트

### B. 최종 접속 URL

```
Admin Frontend:
- S3: http://admin.sajuline.com.s3-website.ap-northeast-2.amazonaws.com
- CloudFront: https://admin.sajuline.com (커스텀 도메인)

Admin Backend:
- Lambda Function URL: https://xxxxx.lambda-url.ap-northeast-2.on.aws
- API 문서: https://xxxxx.lambda-url.ap-northeast-2.on.aws/docs
```

### C. 예상 비용 (월간)

```
Lambda 실행:        $8.00   (100만 요청, 평균 500ms)
Lambda Storage:     $0.00   (1GB 이하 무료)
Function URL:       $0.00   (추가 비용 없음)
S3 Storage:         $0.25   (10GB)
S3 Requests:        $0.05   (10만 요청)
CloudFront:         $1.20   (10GB 전송)
Bastion (NAT):      $0.00   (기존 서버 활용)
────────────────────────────
총계:               $9.50/월

기존 대비 절감:     $35.50/월 (-79%)
```

### D. 유용한 명령어 모음

```bash
# Lambda 로그 실시간 확인
aws logs tail /aws/lambda/sajuline-admin-backend --follow

# Lambda 함수 재배포
aws lambda update-function-code \
  --function-name sajuline-admin-backend \
  --zip-file fileb://lambda-deployment.zip

# S3 동기화
aws s3 sync admin-front/dist/ s3://admin.sajuline.com/ --delete

# CloudFront 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

# Bastion NAT 트래픽 확인
ssh ec2-user@<BASTION_IP> "sudo iptables -t nat -L -n -v"

# Lambda 환경변수 업데이트
aws lambda update-function-configuration \
  --function-name sajuline-admin-backend \
  --environment file://lambda-env.json
```

### E. 참고 링크

- [AWS Lambda 공식 문서](https://docs.aws.amazon.com/lambda/)
- [Mangum (ASGI Adapter)](https://mangum.io/)
- [Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [NAT Instance 설정 가이드](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_NAT_Instance.html)

---

**배포 완료!**

**비용 최적화 달성**: NAT Gateway 제거로 **월 $32 절감** (-79%)

**접속 확인**:
- Admin Frontend: https://admin.sajuline.com
- Admin Backend API: Lambda Function URL
- API 문서: Lambda Function URL + /docs
