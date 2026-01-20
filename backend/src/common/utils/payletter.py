"""
Payletter 유틸리티: 페이로드 생성/금액 계산/해시 검증 등
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
import hashlib

KST = timezone(timedelta(hours=9))


def generate_order_no(now: datetime | None = None) -> str:
    """고유한 주문번호 생성 (밀리초 포함)"""
    now = now or datetime.now(KST)
    return now.strftime("ORD-%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"


def calc_amounts(price: int, discount_rate: int) -> Tuple[int, int, int]:
    tax_amount = price // 10
    discount_amount = (price * discount_rate) // 100 if discount_rate and discount_rate > 0 else 0
    amount = price - discount_amount
    return amount, tax_amount, discount_amount


def build_payletter_request_body(
    *,
    client_id: str,
    user_id: str,
    user_name: str,
    user_email: str,
    product_name: str,
    order_no: str,
    amount: int,
    tax_amount: int,
    custom_parameter: str,
    return_url: str,
    callback_url: str,
    cancel_url: str,
    pgcode: str,
) -> Dict[str, object]:
    now = datetime.now(KST)
    expire_date = (now + timedelta(days=1)).strftime("%Y%m%d")
    expire_time = now.strftime("%H%M")

    return {
        "pgcode": pgcode,
        "client_id": client_id,
        "service_name": "사주라인",
        "user_id": user_id,
        "user_name": user_name,
        "order_no": order_no,
        "amount": amount,
        "taxfree_amount": 0,
        "tax_amount": tax_amount,
        "product_name": product_name,
        "email_flag": "Y",
        "email_addr": user_email,
        "autopay_flag": "N",
        "receipt_flag": "Y",
        "custom_parameter": custom_parameter,
        "return_url": return_url,
        "callback_url": callback_url,
        "cancel_url": cancel_url,
        "inapp_flag": "N",
        "expire_date": expire_date,
        "expire_time": expire_time,
        "company_name_flag": "Y",
    }


def verify_payhash_if_present(*, user_id: str | None, amount: int | None, tid: str | None, api_key: str, payhash: str | None) -> bool:
    """문서 기준 payhash가 존재하면 검증: sha256(user_id + amount + tid + API_KEY)
    일부 결제수단에서는 payhash가 전달되지 않음 → 전달된 경우에만 검증
    """
    if not payhash:
        return True
    if not (user_id and amount and tid):
        return False
    raw = f"{user_id}{amount}{tid}{api_key}".encode("utf-8")
    expected = hashlib.sha256(raw).hexdigest()
    return expected == payhash


# 엔드포인트 조합 유틸은 제거 (설정값을 그대로 사용)


