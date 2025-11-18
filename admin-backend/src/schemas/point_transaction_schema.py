"""
포인트/마일리지 거래 내역 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PointTransactionItem(BaseModel):
    transaction_id: int
    user_id: str
    transaction_type: str
    currency_type: str
    amount: int
    balance_after: int
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PointTransactionListResponse(BaseModel):
    items: List[PointTransactionItem]



































