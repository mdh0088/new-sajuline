# Payletter 결제 API 통합 가이드

## 1. Payletter API 개요

### 1.1 기본 정보
- **제공업체**: Payletter (페이레터)
- **API 문서**: https://www.payletter.com/ko/m/technical/index
- **가이드 문서**: https://pg.payletter.com/APIDocument/index.html

### 1.2 API 엔드포인트
| 환경 | URL |
|------|-----|
| 테스트 | https://testpgapi.payletter.com/v1.0/ |
| 프로덕션 | https://pgapi.payletter.com/v1.0/ |

### 1.3 테스트 계정 정보
- **가맹점 ID**: pay_test
- **API Key (PAYMENT)**: MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=
- **API Key (SEARCH)**: MUI3MjM0RUExQTgyRDA1ODZGRDUyOEM4OTY2QTVCN0Y=

## 2. 주요 API 플로우

### 2.1 결제 프로세스 흐름
```
[사용자] → [Frontend] → [Backend] → [Payletter API] → [결제 페이지]
                ↓                           ↓
         [결제 완료]  ← [Callback URL] ← [결제 결과]
```

### 2.2 단계별 처리
1. **결제 요청**: Backend에서 Payletter API 호출
2. **토큰 수신**: 결제 페이지 접근용 토큰 및 URL 반환
3. **결제 진행**: 사용자가 결제 페이지에서 결제
4. **콜백 처리**: 결제 완료 후 callback_url로 결과 전송
5. **검증 및 저장**: 결제 결과 검증 후 DB 저장

## 3. PHP 샘플 코드 분석

### 3.1 결제 요청 (Payment.php)
```php
// 주요 파라미터
{
    "pgcode": "mobile",              // PG 타입 (mobile, card, bank 등)
    "user_id": "tests",              // 가맹점 회원 ID
    "user_name": "테스터",           // 회원명
    "service_name": "페이레터",      // 서비스명
    "client_id": "pay_test",         // 가맹점 ID
    "order_no": "1234567890",        // 주문번호 (unique)
    "amount": 1000,                  // 결제금액
    "product_name": "테스트상품",     // 상품명
    "email_flag": "Y",               // 이메일 발송 여부
    "email_addr": "test@test.com",  // 이메일 주소
    "autopay_flag": "N",             // 자동결제 여부
    "receipt_flag": "Y",             // 영수증 발급 여부
    "custom_parameter": "",          // 커스텀 파라미터
    "return_url": "",                // 결제 완료 후 리턴 URL
    "callback_url": "",              // 서버간 콜백 URL
    "cancel_url": ""                 // 결제 취소시 리턴 URL
}
```

### 3.2 콜백 처리 (CallBack.php)
```php
// 콜백으로 전달되는 주요 데이터
{
    "user_id": "",                   // 회원 ID
    "user_name": "",                 // 회원명
    "order_no": "",                  // 주문번호
    "tid": "",                       // 거래고유번호
    "cid": "",                       // 승인번호
    "amount": 0,                     // 결제금액
    "pay_info": "",                  // 결제 부가정보
    "pgcode": "",                    // PG 코드
    "transaction_date": "",          // 거래일시
    "payhash": "",                   // 검증용 해시값
    "install_month": 0,              // 할부개월
    "card_info": ""                  // 카드정보 (마스킹)
}
```

## 4. FastAPI 통합 설계

### 4.1 레이어 구조
```
API Layer (Router)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Database)
    ↓
External Client (Payletter API)
```

### 4.2 디렉토리 구조
```
backend/src/
├── api/v1/
│   └── payment_api.py          # API 엔드포인트
├── services/
│   ├── payment_service.py      # 기존 결제 서비스
│   └── payletter_client.py     # Payletter API 클라이언트
├── schemas/
│   └── payment_schema.py       # 요청/응답 스키마
├── models/
│   └── payment_model.py        # 결제 모델
└── repositories/
    └── payment_repository.py   # 데이터베이스 처리
```

## 5. 구현 상세 설계

### 5.1 환경 설정 (settings.py)
```python
# Payletter 설정 추가
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # Payletter 결제 설정
    payletter_api_url: str = Field(..., env="PAYLETTER_API_URL")
    payletter_client_id: str = Field(..., env="PAYLETTER_CLIENT_ID")
    payletter_api_key_payment: str = Field(..., env="PAYLETTER_API_KEY_PAYMENT")
    payletter_api_key_search: str = Field(..., env="PAYLETTER_API_KEY_SEARCH")
    payletter_callback_url: str = Field(..., env="PAYLETTER_CALLBACK_URL")
    payletter_return_url: str = Field(..., env="PAYLETTER_RETURN_URL")
    payletter_cancel_url: str = Field(..., env="PAYLETTER_CANCEL_URL")
```

### 5.2 Payletter 클라이언트 (payletter_client.py)
```python
import httpx
import hashlib
from typing import Dict, Optional
from pydantic import BaseModel

class PayletterClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.payletter_api_url
        self.client_id = settings.payletter_client_id
        self.api_key_payment = settings.payletter_api_key_payment
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"PLKEY {self.api_key_payment}"
        }

    async def request_payment(self, payment_data: Dict) -> Dict:
        """결제 요청"""
        url = f"{self.base_url}/payments/request"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payment_data, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            raise PayletterAPIError(response.json())

    async def verify_callback(self, callback_data: Dict) -> bool:
        """콜백 해시 검증"""
        # SHA256(user_id + amount + tid + API Key)
        hash_string = f"{callback_data['user_id']}{callback_data['amount']}{callback_data['tid']}{self.api_key_payment}"
        calculated_hash = hashlib.sha256(hash_string.encode()).hexdigest().upper()
        return calculated_hash == callback_data.get('payhash')

    async def check_payment_status(self, order_no: str) -> Dict:
        """결제 상태 조회"""
        url = f"{self.base_url}/payments/status"
        data = {"order_no": order_no}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=self.headers)
            return response.json()

    async def cancel_payment(self, tid: str, cancel_data: Dict) -> Dict:
        """결제 취소"""
        url = f"{self.base_url}/payments/cancel"
        data = {
            "tid": tid,
            **cancel_data
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=self.headers)
            return response.json()
```

### 5.3 스키마 정의 (payment_schema.py)
```python
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

# Payletter 결제 요청
class PayletterPaymentRequest(BaseModel):
    pgcode: str = "card"  # mobile, card, bank 등
    user_id: str
    user_name: str
    order_no: str
    amount: Decimal
    product_name: str
    email_flag: str = "Y"
    email_addr: Optional[str] = None
    autopay_flag: str = "N"
    receipt_flag: str = "Y"
    custom_parameter: Optional[str] = None

# Payletter 콜백 데이터
class PayletterCallback(BaseModel):
    user_id: str
    user_name: str
    order_no: str
    tid: str
    cid: Optional[str] = None
    amount: Decimal
    pay_info: Optional[str] = None
    pgcode: str
    transaction_date: str
    payhash: str
    install_month: Optional[int] = None
    card_info: Optional[str] = None

# 결제 요청 응답
class PaymentRequestResponse(BaseModel):
    token: str
    online_url: str
    mobile_url: str
    order_no: str
```

### 5.4 서비스 레이어 수정 (payment_service.py)
```python
class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        payletter_client: PayletterClient
    ):
        self.payment_repo = payment_repo
        self.payletter_client = payletter_client

    async def initiate_payment(
        self,
        user_id: str,
        product_id: int,
        amount: Decimal
    ) -> PaymentRequestResponse:
        """Payletter 결제 요청 시작"""
        # 1. 주문번호 생성
        order_no = self.generate_order_no()

        # 2. DB에 결제 정보 초기 저장 (PENDING 상태)
        payment_data = PaymentCreate(
            order_no=order_no,
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            payment_status="PENDING"
        )
        payment = await self.payment_repo.create(payment_data)

        # 3. Payletter API 호출
        payletter_request = PayletterPaymentRequest(
            user_id=user_id,
            user_name=await self.get_user_name(user_id),
            order_no=order_no,
            amount=amount,
            product_name=await self.get_product_name(product_id),
            custom_parameter=str(payment.payment_id)
        )

        result = await self.payletter_client.request_payment(
            payletter_request.dict()
        )

        # 4. 토큰 저장
        await self.payment_repo.update_token(payment.payment_id, result['token'])

        return PaymentRequestResponse(**result, order_no=order_no)

    async def process_callback(
        self,
        callback_data: PayletterCallback
    ) -> Dict:
        """Payletter 콜백 처리"""
        # 1. 해시 검증
        if not await self.payletter_client.verify_callback(callback_data.dict()):
            return {"code": 9001, "message": "Hash verification failed"}

        # 2. 결제 정보 업데이트
        payment = await self.payment_repo.get_by_order_no(callback_data.order_no)
        if not payment:
            return {"code": 9002, "message": "Order not found"}

        # 3. 결제 상태 업데이트
        await self.payment_repo.update_payment_result(
            payment_id=payment.payment_id,
            tid=callback_data.tid,
            cid=callback_data.cid,
            payment_status="SUCCESS",
            pay_info=callback_data.pay_info,
            card_info=callback_data.card_info
        )

        # 4. 포인트 충전 처리 (결제 성공시)
        await self.process_point_charge(payment.user_id, payment.point_amount)

        # 5. 성공 응답
        return {"code": 0, "message": "success"}
```

### 5.5 API 엔드포인트 (payment_api.py)
```python
from fastapi import APIRouter, Depends, HTTPException
from src.services.payment_service import PaymentService
from src.schemas.payment_schema import (
    PaymentRequestResponse,
    PayletterCallback
)

router = APIRouter(prefix="/api/v1/payment", tags=["payment"])

@router.post("/request", response_model=PaymentRequestResponse)
async def request_payment(
    user_id: str,
    product_id: int,
    amount: Decimal,
    payment_service: PaymentService = Depends()
):
    """결제 요청 - Payletter 결제 페이지 URL 반환"""
    try:
        result = await payment_service.initiate_payment(
            user_id=user_id,
            product_id=product_id,
            amount=amount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/callback")
async def payment_callback(
    callback_data: PayletterCallback,
    payment_service: PaymentService = Depends()
):
    """Payletter 결제 콜백 처리"""
    result = await payment_service.process_callback(callback_data)
    return result

@router.get("/status/{order_no}")
async def check_payment_status(
    order_no: str,
    payment_service: PaymentService = Depends()
):
    """결제 상태 조회"""
    return await payment_service.get_payment_status(order_no)

@router.post("/cancel/{order_no}")
async def cancel_payment(
    order_no: str,
    cancel_reason: str,
    payment_service: PaymentService = Depends()
):
    """결제 취소"""
    return await payment_service.cancel_payment(order_no, cancel_reason)
```

## 6. 보안 고려사항

### 6.1 인증 및 보안
- **API Key 관리**: 환경변수로 관리, 코드에 하드코딩 금지
- **해시 검증**: 모든 콜백에서 SHA256 해시 검증 필수
- **HTTPS 사용**: 모든 API 통신은 HTTPS로만 진행

### 6.2 데이터 검증
- **중복 결제 방지**: order_no 유니크 체크
- **금액 검증**: 요청 금액과 콜백 금액 일치 확인
- **상태 검증**: 결제 상태 변경시 이전 상태 확인

### 6.3 에러 처리
- **API 에러 코드 처리**
  - 401: 인증 오류
  - 403: 권한 오류
  - 405: 메소드 오류
  - 406: 비즈니스 로직 오류
  - 500: 시스템 오류

### 6.4 콜백 재시도 처리
- 콜백 처리 실패시 (code ≠ 0) Payletter에서 5분마다 최대 20회 재시도
- 멱등성 보장 필요 (동일 결제 중복 처리 방지)

## 7. 데이터베이스 스키마 업데이트

### 7.1 Payment 테이블 추가 필드
```sql
-- 기존 Payment 테이블에 추가할 필드들
ALTER TABLE payments ADD COLUMN pg_token VARCHAR(255);
ALTER TABLE payments ADD COLUMN card_info VARCHAR(100);
ALTER TABLE payments ADD COLUMN billkey VARCHAR(255);
ALTER TABLE payments ADD COLUMN install_month INT DEFAULT 0;
ALTER TABLE payments ADD COLUMN transaction_date DATETIME;
ALTER TABLE payments ADD COLUMN pay_hash VARCHAR(255);
ALTER TABLE payments ADD COLUMN custom_parameter TEXT;
```

## 8. 테스트 시나리오

### 8.1 단위 테스트
- Payletter API 클라이언트 테스트 (Mock 응답)
- 해시 검증 로직 테스트
- 결제 서비스 비즈니스 로직 테스트

### 8.2 통합 테스트
- 결제 요청 → 콜백 처리 전체 플로우
- 에러 상황 처리 (네트워크 오류, 검증 실패 등)
- 결제 취소 및 부분 취소

### 8.3 E2E 테스트
- 실제 테스트 환경에서 전체 결제 프로세스
- 다양한 결제 수단 테스트 (카드, 휴대폰, 계좌이체)
- 실패 시나리오 및 복구 테스트

## 9. 환경별 설정

### 9.1 개발 환경
```env
PAYLETTER_API_URL=https://testpgapi.payletter.com/v1.0
PAYLETTER_CLIENT_ID=pay_test
PAYLETTER_API_KEY_PAYMENT=MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=
PAYLETTER_CALLBACK_URL=https://dev.sajuline.com/api/v1/payment/callback
```

### 9.2 프로덕션 환경
```env
PAYLETTER_API_URL=https://pgapi.payletter.com/v1.0
PAYLETTER_CLIENT_ID=[실제 가맹점 ID]
PAYLETTER_API_KEY_PAYMENT=[실제 API KEY]
PAYLETTER_CALLBACK_URL=https://sajuline.com/api/v1/payment/callback
```

## 10. 구현 체크리스트

- [ ] 환경 설정 파일 업데이트
- [ ] Payletter API 클라이언트 구현
- [ ] 결제 요청/응답 스키마 정의
- [ ] 결제 서비스 로직 구현
- [ ] API 엔드포인트 구현
- [ ] 콜백 처리 및 해시 검증
- [ ] 데이터베이스 마이그레이션
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 에러 처리 및 로깅
- [ ] 문서화

## 11. 참고 자료

- [Payletter API 문서](https://pg.payletter.com/APIDocument/index.html)
- [Payletter 기술 지원](https://www.payletter.com/ko/m/technical/index)
- PHP 샘플 코드: `/payment_sample/Payment.php`, `/payment_sample/CallBack.php`