"""
ARS 도메인 엔티티 정의

도메인 계층은 인프라(ORM 모델 등)에 의존하지 않도록, 별도의 엔티티를 정의합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ARSUser:
    user_id: int
    u_id: str
    u_tel: str
    u_kname: str
    u_passwd: str
    regdate: datetime | None = None


