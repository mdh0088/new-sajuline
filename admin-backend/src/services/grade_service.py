"""
등급 서비스 (관리자 백엔드)
"""
from __future__ import annotations

from typing import List, Optional, Dict, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import UploadFile

from src.repositories.grade_repository import GradeRepository
from src.repositories.grade_change_log_repository import GradeChangeLogRepository
from src.schemas.grade_schema import (
    GradeItem,
    GradeListResponse,
    GradeDetailResponse,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradeDeleteResponse,
    UsersByGradeResponse,
    UsersByGradeItem,
    MonthlyGradeUpdateResponse,
    GradeUpdateResultItem,
    GradeChangeLogItem,
    GradeChangeLogListResponse,
)
from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.common.storage.s3 import upload_public_image
from src.repositories.user_repository import UserRepository
from src.common.logging import get_logger_with_request_id

KST = ZoneInfo("Asia/Seoul")


class GradeService:
    def __init__(
        self,
        grade_repo: GradeRepository,
        user_repo: UserRepository | None = None,
        grade_change_log_repo: GradeChangeLogRepository | None = None
    ):
        self.grade_repo = grade_repo
        self.user_repo = user_repo
        self.grade_change_log_repo = grade_change_log_repo

    async def get_all(self) -> GradeListResponse:
        rows = await self.grade_repo.get_all_desc_by_level()
        items: List[GradeItem] = [GradeItem.model_validate(r, from_attributes=True) for r in rows]
        return GradeListResponse(grades=items, total=len(items))

    async def get_detail(self, grade_code: str) -> GradeDetailResponse:
        row = await self.grade_repo.get_by_code(grade_code)
        if row is None:
            raise NotFoundError("등급을 찾을 수 없습니다")
        return GradeDetailResponse(grade=GradeItem.model_validate(row, from_attributes=True))

    async def create_with_image(
        self,
        *,
        payload: GradeCreateRequest,
        image: Optional[UploadFile] = None,
    ) -> GradeDetailResponse:
        filename: Optional[str] = None
        if image is not None:
            content = await image.read()
            if content:
                filename = upload_public_image(subdirectory="grade", content=content, original_name=image.filename or "image.png")
        fields = payload.model_dump(exclude_none=True)
        if filename:
            fields["grade_image_url"] = filename
        row = await self.grade_repo.create(**fields)
        return GradeDetailResponse(grade=GradeItem.model_validate(row, from_attributes=True))

    async def update_with_image(
        self,
        *,
        payload: GradeUpdateRequest,
        image: Optional[UploadFile] = None,
    ) -> GradeDetailResponse:
        current = await self.grade_repo.get_by_code(payload.grade_code)
        if current is None:
            raise NotFoundError("등급을 찾을 수 없습니다")

        updates = payload.model_dump(exclude_none=True)
        updates.pop("grade_code", None)

        if image is not None:
            content = await image.read()
            if content:
                filename = upload_public_image(subdirectory="grade", content=content, original_name=image.filename or "image.png")
                updates["grade_image_url"] = filename

        updated = await self.grade_repo.partial_update(current.grade_code, **updates)
        if not updated:
            # 변경사항 없거나 실패 시 최신값 반환
            refreshed = await self.grade_repo.get_by_code(current.grade_code)
            if refreshed is None:
                raise NotFoundError("등급을 찾을 수 없습니다")
            return GradeDetailResponse(grade=GradeItem.model_validate(refreshed, from_attributes=True))

        refreshed = await self.grade_repo.get_by_code(current.grade_code)
        return GradeDetailResponse(grade=GradeItem.model_validate(refreshed, from_attributes=True))

    async def delete(self, grade_code: str) -> GradeDeleteResponse:
        # 존재 확인 후 삭제
        current = await self.grade_repo.get_by_code(grade_code)
        if current is None:
            # 없는 경우에도 일관 응답 (deleted=False)
            return GradeDeleteResponse(grade_code=grade_code, deleted=False)
        deleted = await self.grade_repo.delete(grade_code)
        return GradeDeleteResponse(grade_code=grade_code, deleted=bool(deleted))

    async def get_users_by_grade(self, grade_code: str) -> UsersByGradeResponse:
        if self.user_repo is None:
            # 방어: 의존성 누락 시 빈 응답
            return UsersByGradeResponse(users=[], total=0)
        rows = await self.user_repo.get_all_by_grade(grade_code)
        items = [UsersByGradeItem.model_validate(r, from_attributes=True) for r in rows]
        return UsersByGradeResponse(users=items, total=len(items))

    # =====================================================
    # 월별 등급 업데이트 배치 메서드
    # =====================================================

    def _get_previous_month(self, now: datetime) -> Tuple[int, int]:
        """현재 시점 기준 전월 연도/월 반환"""
        if now.month == 1:
            return now.year - 1, 12
        return now.year, now.month - 1

    def _determine_grade(
        self,
        purchase_amount: int,
        grades: List,
        default_grade_code: str
    ) -> str:
        """
        결제 금액에 따른 등급 결정

        등급은 min_purchase_amount 내림차순으로 정렬되어 있음.
        purchase_amount >= min_purchase_amount 인 첫 번째 등급이 해당 사용자의 등급.

        예시:
        - GOLD: min_purchase_amount=500000
        - BRONZE: min_purchase_amount=100000
        - WHITE: min_purchase_amount=0

        결제 금액이 200000이면 BRONZE (200000 >= 100000)
        결제 금액이 600000이면 GOLD (600000 >= 500000)
        """
        for grade in grades:
            if purchase_amount >= grade.min_purchase_amount:
                return grade.grade_code
        return default_grade_code

    async def execute_monthly_grade_update(
        self,
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
        dry_run: bool = False
    ) -> MonthlyGradeUpdateResponse:
        """
        월별 사용자 등급 업데이트 실행

        1. 대상 유저: t_user 테이블의 ACTIVE 상태 유저
        2. 전월 결제 금액: t_payment에서 payment_status='SUCCESS'인 amount 합산
        3. 등급 결정: t_grade의 min_purchase_amount 기준으로 등급 결정
        4. 로그 기록: t_grade_change_log에 변경 내역 기록
        5. 등급 적용: t_user의 grade_code 필드 업데이트

        Args:
            target_year: 대상 연도 (미입력시 현재 기준 전월)
            target_month: 대상 월 (미입력시 현재 기준 전월)
            dry_run: True이면 실제 업데이트 없이 결과만 반환

        Returns:
            MonthlyGradeUpdateResponse: 처리 결과
        """
        log = get_logger_with_request_id()
        now = datetime.now(KST)

        # 1. 대상 연월 결정
        if target_year is None or target_month is None:
            target_year, target_month = self._get_previous_month(now)

        log.info(
            "Starting monthly grade update",
            target_year=target_year,
            target_month=target_month,
            dry_run=dry_run
        )

        # 의존성 검증
        if self.grade_change_log_repo is None:
            raise ValidationError("등급 변경 로그 레포지토리가 초기화되지 않았습니다.")

        # 2. ACTIVE 사용자 목록 조회
        active_users = await self.grade_change_log_repo.get_active_users()
        total_active_users = len(active_users)
        log.info(f"Found {total_active_users} active users")

        # 3. 전월 결제 금액 합산 조회
        payment_totals = await self.grade_change_log_repo.get_previous_month_payment_totals(
            target_year, target_month
        )
        payment_map: Dict[str, int] = {user_id: amount for user_id, amount in payment_totals}
        log.info(f"Found payment records for {len(payment_map)} users")

        # 4. 등급 목록 조회 (min_purchase_amount DESC)
        grades = await self.grade_change_log_repo.get_all_grades_ordered_by_amount()
        if not grades:
            raise ValidationError("활성화된 등급이 없습니다.")

        # 기본 등급 (가장 낮은 등급)
        lowest_grade = await self.grade_change_log_repo.get_lowest_grade()
        default_grade_code = lowest_grade.grade_code if lowest_grade else grades[-1].grade_code
        log.info(f"Default grade: {default_grade_code}")

        # 5. 각 사용자별 등급 계산
        results: List[GradeUpdateResultItem] = []
        grade_updates: List[Tuple[str, str]] = []  # (user_id, new_grade_code)
        change_logs: List[dict] = []

        total_upgraded = 0
        total_downgraded = 0
        total_unchanged = 0

        # 등급 레벨 매핑 (비교용)
        grade_level_map = {g.grade_code: g.grade_level for g in grades}

        for user in active_users:
            user_id = user.user_id
            current_grade_code = user.grade_code
            purchase_amount = payment_map.get(user_id, 0)

            # 새 등급 결정
            new_grade_code = self._determine_grade(
                purchase_amount, grades, default_grade_code
            )

            # 등급 레벨 비교
            current_level = grade_level_map.get(current_grade_code, 0)
            new_level = grade_level_map.get(new_grade_code, 0)

            is_changed = current_grade_code != new_grade_code

            if is_changed:
                if new_level > current_level:
                    total_upgraded += 1
                else:
                    total_downgraded += 1

                # 변경된 사용자만 결과에 포함
                results.append(GradeUpdateResultItem(
                    user_id=user_id,
                    grade_before=current_grade_code,
                    grade_after=new_grade_code,
                    purchase_amount=purchase_amount,
                    is_changed=True
                ))

                grade_updates.append((user_id, new_grade_code))
                change_logs.append({
                    "user_id": user_id,
                    "grade_before": current_grade_code,
                    "grade_after": new_grade_code,
                    "purchase_amount": purchase_amount,
                    "change_reason": "AUTO_BATCH",
                    "admin_id": None
                })
            else:
                total_unchanged += 1

        log.info(
            f"Grade calculation completed: upgraded={total_upgraded}, "
            f"downgraded={total_downgraded}, unchanged={total_unchanged}"
        )

        # 6. dry_run이 아닌 경우 실제 업데이트 수행
        if not dry_run and grade_updates:
            # 등급 변경 로그 저장
            await self.grade_change_log_repo.bulk_create(change_logs)
            log.info(f"Created {len(change_logs)} grade change logs")

            # 사용자 등급 업데이트
            updated_count = await self.grade_change_log_repo.bulk_update_user_grades(grade_updates)
            log.info(f"Updated {updated_count} user grades")

        return MonthlyGradeUpdateResponse(
            target_year=target_year,
            target_month=target_month,
            total_active_users=total_active_users,
            total_processed=total_active_users,
            total_upgraded=total_upgraded,
            total_downgraded=total_downgraded,
            total_unchanged=total_unchanged,
            dry_run=dry_run,
            executed_at=now,
            results=results
        )

    async def get_grade_change_logs(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> GradeChangeLogListResponse:
        """등급 변경 로그 조회 (기존 메서드 - 하위호환용)"""
        if self.grade_change_log_repo is None:
            return GradeChangeLogListResponse(logs=[], total=0, page=1, size=limit)

        if user_id:
            logs = await self.grade_change_log_repo.get_by_user_id(user_id, limit)
        else:
            # 전체 조회 (제한된 수)
            logs = await self.grade_change_log_repo.get_by_user_id("", limit)

        items = [GradeChangeLogItem.model_validate(log, from_attributes=True) for log in logs]
        return GradeChangeLogListResponse(logs=items, total=len(items), page=1, size=limit)

    async def get_grade_change_logs_with_pagination(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        user_id: Optional[str] = None,
        change_reason: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> GradeChangeLogListResponse:
        """등급 변경 로그 목록 조회 (페이지네이션, 월별 검색)

        Args:
            year: 대상 연도 (선택)
            month: 대상 월 (선택)
            user_id: 사용자 ID (선택)
            change_reason: 변경 사유 (선택)
            page: 페이지 번호 (기본값: 1)
            size: 페이지 당 개수 (기본값: 20)

        Returns:
            GradeChangeLogListResponse: 등급 변경 로그 목록
        """
        log = get_logger_with_request_id()
        log.info(
            "Getting grade change logs",
            year=year,
            month=month,
            user_id=user_id,
            change_reason=change_reason,
            page=page,
            size=size
        )

        if self.grade_change_log_repo is None:
            return GradeChangeLogListResponse(logs=[], total=0, page=page, size=size)

        # 페이지네이션 계산
        skip = (page - 1) * size

        # 로그 목록 조회
        logs = await self.grade_change_log_repo.get_logs_with_pagination(
            year=year,
            month=month,
            user_id=user_id,
            change_reason=change_reason,
            skip=skip,
            limit=size
        )

        # 총 개수 조회
        total = await self.grade_change_log_repo.count_logs(
            year=year,
            month=month,
            user_id=user_id,
            change_reason=change_reason
        )

        items = [GradeChangeLogItem.model_validate(log_item, from_attributes=True) for log_item in logs]

        log.info(
            "Grade change logs retrieved",
            count=len(items),
            total=total
        )

        return GradeChangeLogListResponse(
            logs=items,
            total=total,
            page=page,
            size=size
        )


