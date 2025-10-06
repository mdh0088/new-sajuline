"""
관리자 백엔드 사용자 서비스
"""
from __future__ import annotations

from typing import List, Tuple
from datetime import datetime

from src.repositories.user_repository import UserRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.schemas.user_schema import (
    UserListParams,
    UserListItem,
    UserListItemResponse,
    ArsUserInfo,
    UserDetailResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserPointAdjustRequest,
    UserPointAdjustResponse,
)
from src.exceptions.custom_exceptions import NotFoundError
from src.services.auth_service import AuthService
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.schemas.point_transaction_schema import PointTransactionItem


class UserService:
    def __init__(self, user_repo: UserRepository, tm60_repo: Tm60UsersRepository, auth: AuthService | None = None, pt_repo: PointTransactionRepository | None = None):
        self.user_repo = user_repo
        self.tm60_repo = tm60_repo
        self.auth = auth or AuthService()
        self.pt_repo = pt_repo

    async def get_user_list(
        self,
        params: UserListParams
    ) -> tuple[list[UserListItemResponse], int, int, int]:
        """유저 목록 조회 및 각 유저의 ars_user_info 매칭 정보 포함"""

        # 페이지/리밋 보정
        if params.page < 1:
            params.page = 1
        if params.limit < 1 or params.limit > 100:
            params.limit = 10

        # 날짜 파싱 (yyyy-mm-dd)
        start_dt = None
        end_dt = None
        try:
            if params.start_dt:
                start_dt = datetime.strptime(params.start_dt, "%Y-%m-%d")
            if params.end_dt:
                end_dt = datetime.strptime(params.end_dt, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception:
            start_dt = start_dt or None
            end_dt = end_dt or None

        # 메인 목록 조회
        users, total = await self.user_repo.get_list(
            page=params.page,
            limit=params.limit,
            search_type=params.search_type,
            search_name=params.search_name or None,
            join_type=params.join_type or None,
            grade=params.grade or None,
            start_dt=start_dt,
            end_dt=end_dt,
        )

        if not users:
            return [], params.page, params.limit, 0

        # tm60_users 묶어 조회 (user_id = u_id)
        user_ids: List[str] = [u.user_id for u in users]
        tm_map = await self.tm60_repo.find_by_user_ids(user_ids)

        items: list[UserListItemResponse] = []
        for u in users:
            # 첫 번째 매칭된 ARS 레코드만 사용
            tm_records = tm_map.get(u.user_id, [])
            ars_info = None
            if tm_records:
                r = tm_records[0]
                ars_info = ArsUserInfo(
                    idx=r.idx,
                    u_id=r.u_id,
                    u_tel=r.u_tel,
                    u_passwd=r.u_passwd,
                    u_kname=r.u_kname,
                    u_memcd=r.u_memcd,
                    u_login=r.u_login,
                    u_state=r.u_state,
                    u_point=r.u_point,
                    u_fdate=r.u_fdate,
                    u_rdate=r.u_rdate,
                    regdate=r.regdate,
                    u_memo=r.u_memo,
                )

            items.append(UserListItemResponse(
                user_id=u.user_id,
                email=u.email,
                nickname=u.nickname,
                phone=u.phone,
                join_type=u.join_type,
                grade_code=u.grade_code,
                mileage_point=getattr(u, 'mileage_point', 0),
                created_at=u.created_at,
                ars_user_info=ars_info
            ))

        return items, params.page, params.limit, total

    async def get_user_detail(self, user_id: str) -> UserDetailResponse:
        """회원 상세 조회: t_user 모든 필드 + ars_user_info"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        tm_list_rows = await self.tm60_repo.find_all_by_user_id(user.user_id)

        # 첫 번째 매칭된 ARS 레코드만 사용
        ars_info = None
        if tm_list_rows:
            r = tm_list_rows[0]
            ars_info = ArsUserInfo(
                idx=r.idx,
                u_id=r.u_id,
                u_tel=r.u_tel,
                u_passwd=r.u_passwd,
                u_kname=r.u_kname,
                u_memcd=r.u_memcd,
                u_login=r.u_login,
                u_state=r.u_state,
                u_point=r.u_point,
                u_fdate=r.u_fdate,
                u_rdate=r.u_rdate,
                regdate=r.regdate,
                u_memo=r.u_memo,
            )

        # t_user 모든 필드 dict 변환 (from_attributes)
        user_dict = {
            "user_id": user.user_id,
            "email": user.email,
            "password_hash": user.password_hash,
            "nickname": user.nickname,
            "phone": user.phone,
            "join_type": user.join_type,
            "social_provider": getattr(user, "social_provider", None),
            "social_id": getattr(user, "social_id", None),
            "user_status": getattr(user, "user_status", None),
            "grade_code": user.grade_code,
            "profile_image_url": getattr(user, "profile_image_url", None),
            "birth_date": getattr(user, "birth_date", None),
            "gender": getattr(user, "gender", None),
            "is_marketing_agreed": getattr(user, "is_marketing_agreed", None),
            "password_changed_at": getattr(user, "password_changed_at", None),
            "failed_login_count": getattr(user, "failed_login_count", 0),
            "locked_until": getattr(user, "locked_until", None),
            "created_at": user.created_at,
            "updated_at": getattr(user, "updated_at", None),
            "last_login_at": getattr(user, "last_login_at", None),
            "withdrawn_at": getattr(user, "withdrawn_at", None),
        }

        return UserDetailResponse(user=user_dict, ars_user_info=ars_info)

    async def update_user(self, payload: UserUpdateRequest) -> UserUpdateResponse:
        user = await self.user_repo.get_by_id(payload.user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        password_hash = None
        if payload.password:
            password_hash = self.auth.hash_password(payload.password)

        updated = await self.user_repo.partial_update(
            payload.user_id,
            nickname=payload.nickname,
            email=payload.email,
            phone=payload.phone,
            password_hash=password_hash,
            grade_code=payload.grade,
            birth_date=payload.birth_date,
        )
        return UserUpdateResponse(user_id=payload.user_id, updated=bool(updated))

    async def adjust_user_points(self, payload: UserPointAdjustRequest) -> UserPointAdjustResponse:
        # 사용자 존재 확인
        user = await self.user_repo.get_by_id(payload.user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        # delta 계산
        delta = payload.amount if payload.type == "plus" else -payload.amount

        # MSSQL 포인트 증감
        new_balance = await self.tm60_repo.adjust_points(user.user_id, delta)
        if new_balance == -1:
            raise NotFoundError("TM60 사용자 정보를 찾을 수 없습니다")
        if new_balance == -2:
            raise NotFoundError("포인트가 부족합니다")

        # 트랜잭션 로그 기록
        if self.pt_repo is not None:
            description = "관리자 포인트 지급" if delta > 0 else "관리자 포인트 차감"
            await self.pt_repo.create_transaction(
                user_id=user.user_id,
                transaction_type="ADMIN",
                currency_type="POINT",
                amount=delta,
                balance_after=new_balance,
                reference_type="ADMIN",
                reference_id=None,
                description=description,
            )

        return UserPointAdjustResponse(user_id=user.user_id, amount=delta, balance_after=new_balance)

    async def get_mileage_use_logs(self, user_id: str) -> list[PointTransactionItem]:
        if self.pt_repo is None:
            return []
        rows = await self.pt_repo.find_mileage_use_logs(user_id)
        return [PointTransactionItem.model_validate(r, from_attributes=True) for r in rows]

    async def get_mileage_earn_logs(self, user_id: str) -> list[PointTransactionItem]:
        if self.pt_repo is None:
            return []
        rows = await self.pt_repo.find_mileage_earn_logs(user_id)
        return [PointTransactionItem.model_validate(r, from_attributes=True) for r in rows]


