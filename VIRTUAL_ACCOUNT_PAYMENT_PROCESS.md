# 가상계좌(무통장입금) 결제 프로세스 가이드

## 목차
1. [개요](#개요)
2. [가상계좌 vs 일반결제 차이점](#가상계좌-vs-일반결제-차이점)
3. [전체 프로세스 흐름](#전체-프로세스-흐름)
4. [API 상세 명세](#api-상세-명세)
5. [현재 구현 현황 분석](#현재-구현-현황-분석)
6. [필요한 개선사항](#필요한-개선사항)

---

## 개요

가상계좌(무통장입금)는 **즉시 승인이 아닌 입금 대기** 형태의 결제 방식입니다.
- 사용자에게 가상계좌가 발급되고, 해당 계좌로 입금하면 결제가 완료됩니다.
- Payletter에서 **반드시 callback_url 연동 필수**로 명시하고 있습니다.

> **중요**: 토스, 체크페이, 가상계좌는 반드시 callback_url을 연동하셔야 합니다. - Payletter 공식문서

---

## 가상계좌 vs 일반결제 차이점

| 구분 | 일반결제 (카드/카카오페이) | 가상계좌 |
|------|---------------------------|----------|
| **결제 완료 시점** | 즉시 완료 | 입금 완료 후 |
| **Callback 호출 시점** | 결제창에서 승인 직후 | 실제 입금 완료 후 |
| **Return URL 의미** | 결제 완료 안내 | 가상계좌 발급 안내 (입금 대기) |
| **payhash 검증** | 제공됨 | **제공되지 않음** |
| **취소 가능 여부** | 가능 | **취소 불가** |

---

## 전체 프로세스 흐름

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        가상계좌 결제 프로세스 흐름도                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [PHASE 1: 가상계좌 발급]                                                       │
│                                                                                 │
│  Frontend              Backend                    Payletter                     │
│      │                    │                           │                         │
│  1. 가상계좌 선택         │                           │                         │
│      │── POST /payment/request ──>│                   │                         │
│      │   (pgcode: virtualaccount) │                   │                         │
│      │                    │── POST /v1.0/payments/request ──>│                  │
│      │                    │   (pgcode: virtualaccount,       │                  │
│      │                    │    expire_date, expire_time)     │                  │
│      │                    │<── {token, online_url, mobile_url} ─│               │
│      │<── 결제 URL 반환 ──│                           │                         │
│      │                    │                           │                         │
│  2. 결제창 이동           │                           │                         │
│      │──────────────────────────────────────────────>│                          │
│      │                    │                           │                         │
│  3. 가상계좌 발급 완료    │                           │                         │
│      │<── Return URL (POST) ─────────────────────────│                          │
│      │   account_no: "123-456-789"                   │                          │
│      │   bank_name: "국민은행"                        │                          │
│      │   expire_date: "20251220"                     │                          │
│      │   expire_time: "2359"                         │                          │
│      │                    │                           │                         │
│  4. 가상계좌 정보 표시    │                           │                         │
│      │   "입금 대기 중"   │                           │                         │
│      │                    │                           │                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [PHASE 2: 입금 완료 처리] (수 시간 ~ 수 일 후)                                  │
│                                                                                 │
│  사용자 은행              Payletter                  Backend                    │
│      │                        │                          │                      │
│  5. 가상계좌로 입금           │                          │                      │
│      │── 입금 ───────────────>│                          │                      │
│      │                        │                          │                      │
│  6. 입금 확인                 │                          │                      │
│      │                        │── POST /payment/point_callback ──>│             │
│      │                        │   (Server-to-Server)     │                      │
│      │                        │   tid, amount, order_no  │                      │
│      │                        │                          │                      │
│      │                        │                   7. 포인트 충전                │
│      │                        │                      마일리지 적립              │
│      │                        │                      알림톡 발송                │
│      │                        │                          │                      │
│      │                        │<── {"code":0, "message":"success"} ─│           │
│      │                        │                          │                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## API 상세 명세

### 1. 결제 요청 (가상계좌 발급)

**Endpoint**: `POST /v1.0/payments/request`

**Request Parameters (가상계좌 관련)**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pgcode` | string | 필수 | **"virtualaccount"** |
| `expire_date` | string | 선택 | 가상계좌 만료일 (YYYYMMDD) |
| `expire_time` | string | 선택 | 가상계좌 만료시각 (HHMM) |

**현재 코드** (backend/src/common/utils/payletter.py:41-43):
```python
now = datetime.now(KST)
expire_date = (now + timedelta(days=1)).strftime("%Y%m%d")
expire_time = now.strftime("%H%M")
```

---

### 2. Return URL 응답 (가상계좌 발급 완료)

가상계좌 발급 완료 시 Return URL로 POST 전송되는 파라미터:

**공통 파라미터**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | string | 결과 코드 (성공: "0") |
| `message` | string | 결과 메시지 |
| `user_id` | string | 가맹점 결제자 아이디 |
| `order_no` | string | 가맹점 주문번호 |
| `tid` | string | 결제고유번호 |
| `amount` | number | 결제요청 금액 |
| `custom_parameter` | string | 결제요청시 전송한 값 |

**가상계좌 전용 파라미터**:

| Parameter | Type | Description | 예시 |
|-----------|------|-------------|------|
| `account_no` | string | 가상계좌 번호 | "123-456-78901234" |
| `account_name` | string | 가상계좌 입금자명 | "홍길동" |
| `account_holder` | string | 가상계좌 예금주명 | "(주)사주라인" |
| `bank_code` | string | 가상계좌 은행 코드 | "004" |
| `bank_name` | string | 가상계좌 은행명 | "국민은행" |
| `issue_tid` | string | 가상계좌 채번 승인번호 | "VA20251215..." |
| `expire_date` | string | 입금만료일 | "20251220" |
| `expire_time` | string | 만료시각 | "2359" |

> **주의**: 가상계좌는 `payhash`가 전달되지 않습니다.

---

### 3. Callback URL 응답 (입금 완료)

**호출 시점**: 사용자가 가상계좌로 **실제 입금 완료 후** 호출됨

**전송 방식**: Server-to-Server (JSON)

**주요 파라미터**:

```json
{
    "user_id": "test_user_id",
    "user_name": "테스터",
    "amount": 11000,
    "tax_amount": 1000,
    "tid": "va_test-202512151234567",
    "cid": "20251215120000123456",
    "order_no": "ORD-20251215120000",
    "transaction_date": "2025-12-15 15:30:00",
    "pgcode": "virtualaccount",
    "custom_parameter": "{\"point_amount\":10000,\"product_id\":1}"
}
```

**응답 형식**:

```json
// 성공
{"code": 0, "message": "success"}

// 실패 (5분마다 최대 20번 재전송)
{"code": 9999, "message": "실패 사유"}
```

---

## 현재 구현 현황 분석

### 데이터베이스 및 모델 현황

| 계층 | 가상계좌 필드 | 상태 |
|------|--------------|------|
| **DB (t_payment)** | account_no, account_name, account_holder, bank_code, bank_name, expire_date, expire_time, issue_tid | ✅ 존재 |
| **Model (payment_model.py)** | Line 182-230에 모든 필드 정의 | ✅ 존재 |
| **PaymentResponse 스키마** | Line 87-95에 모든 필드 정의 | ✅ 존재 |
| **PaymentUpdate 스키마** | 가상계좌 필드 없음 | ❌ **누락** |

### Backend (payment_api.py)

#### /payment/request (Line 125-302)
- **pgcode 전달**: Frontend에서 받은 `payment_method`를 Payletter에 `pgcode`로 전달 ✅
- **expire_date/time 설정**: 현재 시간 + 1일로 설정됨 ✅

#### /payment/point_return (Line 498-779)

**현재 가상계좌 처리 로직** (Line 612-663):
```python
if payment_method == "virtualaccount":
    # 가상계좌는 입금 대기 상태로 처리
    log.info("Virtual account payment pending", order_no=order_no)

    # postMessage로 'payment_pending' 전송
    html_content = """..."""
    return HTMLResponse(content=html_content)
```

**문제점**:
1. ❌ 가상계좌 정보(account_no, bank_name, expire_date 등)를 **저장하지 않음**
2. ❌ 가상계좌 정보를 **사용자에게 표시하지 않음**
3. ❌ `PaymentUpdate` 스키마에 가상계좌 필드가 **없어서 저장 불가**

#### /payment/point_callback (Line 305-487)
- **포인트 충전**: `tm60_users_service.update_user_points()` ✅
- **마일리지 적립**: `point_transaction_service.earn_mileage_from_payment()` ✅
- **알림톡 발송**: `notification_service.user_charge_confirm_alert()` ✅

> Callback 처리 로직은 일반결제와 동일하게 동작하여 **정상 작동**

---

### Frontend (point/index.vue)

**결제 수단 정의** (Line 224-230):
```typescript
{
  icon: '🏦',
  image: '/images/bank.png',
  name: '가상계좌',
  description: '무통장입금',
  code: 'virtualaccount'
}
```

**결제 결과 처리** (Line 361-369):
```typescript
else if (event.data?.type === 'payment_pending') {
  showPaymentModal.value = false
  const message = event.data.message || '가상계좌가 발급되었습니다. 입금해주세요.'
  notifyInfo(message)
  setTimeout(() => {
    window.location.reload()
  }, 1500)
}
```

**문제점**:
1. ❌ 가상계좌 정보(계좌번호, 은행명, 만료일)를 **표시하지 않음**
2. ❌ 가상계좌 정보 확인 페이지가 **없음**

---

## 필요한 개선사항

### 1. PaymentUpdate 스키마 수정 (backend/src/schemas/payment_schema.py)

**현재 PaymentUpdate 스키마에 가상계좌 필드가 누락되어 있어 저장 불가**

```python
class PaymentUpdate(BaseModel):
    """결제 수정 요청 스키마"""
    # ... 기존 필드들 ...

    # 가상계좌 필드 추가 필요
    account_no: Optional[str] = Field(None, description="가상계좌 번호")
    account_name: Optional[str] = Field(None, description="가상계좌 입금자명")
    account_holder: Optional[str] = Field(None, description="가상계좌 예금주")
    bank_code: Optional[str] = Field(None, description="은행 코드")
    bank_name: Optional[str] = Field(None, description="은행명")
    expire_date: Optional[str] = Field(None, description="만료일 (YYYYMMDD)")
    expire_time: Optional[str] = Field(None, description="만료시각 (HHMM)")
    issue_tid: Optional[str] = Field(None, description="채번 승인번호")
```

### 2. payment_api.py - /point_return 수정

```python
if payment_method == "virtualaccount":
    # 1. 가상계좌 정보 저장
    update_data = PaymentUpdate(
        payment_status="PENDING",  # 입금 대기
        account_no=body.account_no,
        account_name=body.account_name,
        account_holder=body.account_holder,
        bank_code=body.bank_code,
        bank_name=body.bank_name,
        expire_date=body.expire_date,
        expire_time=body.expire_time,
        issue_tid=body.issue_tid,
    )
    await payment_service.update_payment(existing_payment.payment_id, update_data)

    # 2. 가상계좌 정보를 postMessage로 전달
    va_info = json.dumps({
        "account_no": body.account_no,
        "bank_name": body.bank_name,
        "expire_date": body.expire_date,
        "expire_time": body.expire_time,
        "amount": existing_payment.amount
    })
    # JavaScript에서 vaInfo 사용
```

### 3. Frontend 수정사항

#### 가상계좌 정보 표시 모달/페이지 추가
```vue
<div v-if="showVirtualAccountInfo" class="va-info-modal">
  <h3>가상계좌 발급 완료</h3>
  <div class="va-details">
    <p><strong>은행:</strong> {{ vaInfo.bank_name }}</p>
    <p><strong>계좌번호:</strong> {{ vaInfo.account_no }}</p>
    <p><strong>입금금액:</strong> {{ vaInfo.amount.toLocaleString() }}원</p>
    <p><strong>입금기한:</strong> {{ formatExpireDate(vaInfo.expire_date, vaInfo.expire_time) }}</p>
  </div>
  <p class="warning">입금 기한 내에 정확한 금액을 입금해주세요.</p>
</div>
```

### 4. 가상계좌 입금 대기 알림톡 발송 (선택사항)

가상계좌 발급 시 사용자에게 입금 안내 알림톡 발송:
- 은행명, 계좌번호, 입금금액, 입금기한 포함

---

## 참고 문서

- Payletter 기술문서: https://www.payletter.com/ko/m/technical/index#payment-integration
- 내부 에러 로그: `/251215error/temp.txt`

---

## 작성일

2025-12-16
