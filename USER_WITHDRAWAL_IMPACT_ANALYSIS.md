# 회원 탈퇴 시 t_user 테이블 삭제 영향도 분석

> 작성일: 2024-12-04
> 수정일: 2025-12-04
> 대상 프로젝트: `backend/`, `admin-backend/`
>
> **변경 이력**
> - 2025-12-04: 옵션 4 (Tombstone User 패턴) 추가, 권장 조치사항 업데이트
> - 2025-12-04: 노출 제어 컬럼 분석 추가 (섹션 8-1), `is_visible` 필터링 현황 문서화

---

## 1. 개요

회원 탈퇴 시 `t_user` 테이블의 row를 삭제할 경우, `user_id`를 참조하는 다른 테이블들과의 JOIN 쿼리에서 오류가 발생하거나 데이터 정합성 문제가 발생할 수 있습니다.

본 문서는 영향받는 테이블과 서비스를 분석하고 해결 방안을 제시합니다.

---

## 2. 영향받는 테이블 총괄표

| # | 테이블명 | FK 설정 | JOIN 사용 | 프로젝트 | 위험도 |
|---|---------|:-------:|:---------:|----------|:------:|
| 1 | `t_payment` | ✅ | ✅ | admin-backend | 🔴 Critical |
| 2 | `t_consultation_review` | ❌ | ✅ | admin-backend | 🔴 Critical |
| 3 | `t_inquiry` | ❌ | ✅ | admin-backend | 🔴 Critical |
| 4 | `t_point_transaction` | ❌ | ❌ | both | 🟡 Medium |
| 5 | `t_user_bookmark` | ❌ | ❌ | backend | 🟡 Medium |
| 6 | `t_event_participation_log` | ❌ | ❌ | backend | 🟢 Low |
| 7 | `t_user_activity_log` | ❌ | ❌ | backend | 🟢 Low |
| 8 | `t_notification_log` | ❌ | ❌ | backend | 🟢 Low |
| 9 | `t_user_out` | ❌ | ❌ | backend | 🟢 Low |

---

## 3. Critical 위험도 테이블 상세

### 3.1 t_payment (결제 내역)

**모델 위치**: `admin-backend/src/models/payment_model.py:36-40`

```python
user_id: Mapped[str] = mapped_column(
    String(100),
    ForeignKey("t_user.user_id"),  # FK 제약조건 설정됨
    nullable=False,
    comment="사용자 ID",
)
```

**영향받는 리포지토리**: `admin-backend/src/repositories/payment_repository.py`

| 메서드 | 라인 | 설명 |
|--------|------|------|
| `get_list_with_user()` | :44 | 결제 목록 + 사용자 JOIN |
| `get_detail_with_user()` | :108 | 결제 상세 + 사용자 JOIN |

**JOIN 쿼리 예시**:
```python
stmt = select(Payment, User).join(User, Payment.user_id == User.user_id)
```

**발생 문제**:
- FK 제약조건으로 `t_user` 삭제 시 **참조 무결성 오류** 발생
- 관리자 결제 목록/상세 조회 시 **JOIN 실패**

---

### 3.2 t_consultation_review (상담 후기)

**모델 위치**: `admin-backend/src/models/consultation_review_model.py:25`

```python
user_id: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    comment="작성자 ID"
)
# FK 없음, 단순 컬럼
```

**영향받는 리포지토리**: `admin-backend/src/repositories/consultation_review_repository.py`

| 메서드 | 라인 | 설명 |
|--------|------|------|
| `get_list_with_users()` | :44 | 후기 목록 + User/Counselor JOIN |
| `get_by_id_with_users()` | :120 | 후기 상세 + User/Counselor JOIN |

**JOIN 쿼리 예시**:
```python
.join(User, ConsultationReview.user_id == User.user_id)
.join(Counselor, ConsultationReview.counselor_id == Counselor.counselor_id)
```

**발생 문제**:
- 탈퇴 사용자의 후기가 **목록에서 누락**됨
- 관리자 후기 관리 페이지에서 **데이터 불일치**

---

### 3.3 t_inquiry (1:1 문의)

**모델 위치**: `backend/src/models/inquiry_model.py:40-44`

```python
inquirer_id: Mapped[Optional[str]] = mapped_column(
    String(100),
    nullable=True,
    comment="문의자 ID"
)
# FK 없음
```

**영향받는 리포지토리**: `admin-backend/src/repositories/inquiry_repository.py`

| 메서드 | 라인 | 설명 |
|--------|------|------|
| `get_user_list_with_user()` | :191 | 사용자→관리자 문의 목록 |
| `get_user_detail_with_user()` | :213 | 문의 상세 |
| `get_user_to_cs_list()` | :271 | 사용자→상담사 문의 목록 |
| `get_user_to_cs_detail()` | :296 | 상담사 문의 상세 |

**JOIN 쿼리 예시**:
```python
stmt = select(Inquiry, User).join(User, Inquiry.inquirer_id == User.user_id)
```

**발생 문제**:
- 탈퇴 사용자의 문의 내역이 **조회 불가**
- 관리자 1:1 문의 관리에서 **해당 문의 누락**

---

## 4. Medium 위험도 테이블 상세

### 4.1 t_point_transaction (포인트 거래 내역)

**모델 위치**: `backend/src/models/point_transaction_model.py:55-59`

```python
user_id: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    comment="사용자 ID"
)
# FK 없음
```

**발생 문제**:
- user_id 참조 끊김으로 **내역 조회 시 사용자 정보 매핑 불가**
- 고아 데이터 잔존

---

### 4.2 t_user_bookmark (즐겨찾기)

**모델 위치**: `backend/src/models/user_bookmark_model.py:26-30`

```python
user_id: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    comment="유저 id"
)
# FK 없음
```

**발생 문제**:
- 탈퇴 사용자의 즐겨찾기 데이터가 **고아 데이터로 잔존**

---

## 5. Low 위험도 테이블 (로그성 데이터)

| 테이블 | 모델 위치 | 설명 | 권장 처리 |
|--------|----------|------|----------|
| `t_user_activity_log` | `backend/src/models/user_activity_log_model.py:28` | 사용자 활동 로그 | 함께 삭제 또는 보존 |
| `t_event_participation_log` | `backend/src/models/event_participation_model.py:31` | 이벤트 참여 로그 | 함께 삭제 또는 보존 |
| `t_notification_log` | `backend/src/models/notification_log_model.py:35` | 알림 발송 로그 | 함께 삭제 또는 보존 |
| `t_user_out` | `backend/src/models/user_model.py:204` | 탈퇴 기록 | 보존 (탈퇴 이력 관리용) |

---

## 6. 영향받는 API/서비스 총괄표

| 프로젝트 | 파일 | 메서드 | 기능 | 오류 유형 |
|----------|------|--------|------|----------|
| admin-backend | `payment_repository.py` | `get_list_with_user()` | 결제 목록 | JOIN 실패/FK 오류 |
| admin-backend | `payment_repository.py` | `get_detail_with_user()` | 결제 상세 | JOIN 실패/FK 오류 |
| admin-backend | `consultation_review_repository.py` | `get_list_with_users()` | 후기 목록 | JOIN 결과 누락 |
| admin-backend | `consultation_review_repository.py` | `get_by_id_with_users()` | 후기 상세 | JOIN 결과 없음 |
| admin-backend | `inquiry_repository.py` | `get_user_list_with_user()` | 문의 목록 | JOIN 결과 누락 |
| admin-backend | `inquiry_repository.py` | `get_user_detail_with_user()` | 문의 상세 | JOIN 결과 없음 |
| admin-backend | `inquiry_repository.py` | `get_user_to_cs_list()` | 상담사 문의 목록 | JOIN 결과 누락 |
| admin-backend | `inquiry_repository.py` | `get_user_to_cs_detail()` | 상담사 문의 상세 | JOIN 결과 없음 |

---

## 7. 현재 구현 상태

현재 `backend/src/services/user_service.py`의 `withdraw_user()` 메서드는 **Soft Delete** 방식으로 구현되어 있습니다:

```python
# user_service.py:751-768
# 1. t_user_out에 탈퇴 정보 기록
user_out = await self.user_repo.create_user_out(
    user_id=user.user_id,
    nickname=user.nickname,
    phone=user.phone,
    email=user.email
)

# 2. t_user 상태를 WITHDRAWN으로 변경 (삭제하지 않음!)
update_success = await self.user_repo.update_user_status_to_withdrawn(user_id)
```

**현재 상태**: `t_user` row가 삭제되지 않고 상태만 변경되므로 **JOIN 오류 없음**

---

## 8. 해결 방안

### 옵션 1: Soft Delete 유지 (현재 방식, 권장)

`t_user.user_status = 'WITHDRAWN'`으로 상태만 변경하고 row 유지.

| 장점 | 단점 |
|------|------|
| JOIN 문제 없음 | 개인정보 보존 (규정 검토 필요) |
| 데이터 정합성 유지 | 저장 공간 사용 |
| 구현 변경 불필요 | - |

**개인정보 최소화 방안**:
```python
# 탈퇴 시 민감 정보 마스킹
user.email = f"withdrawn_{user_id}@deleted.local"
user.phone = "00000000000"
user.nickname = f"탈퇴회원_{user_id[:4]}"
user.user_status = UserStatus.WITHDRAWN
```

---

### 옵션 2: Hard Delete + 연관 데이터 처리

`t_user` 삭제 전 모든 연관 테이블 처리.

**처리 순서**:
```python
async def hard_delete_user(user_id: str):
    # 1. FK 제약조건 테이블 먼저 처리
    # t_payment: FK 제거 또는 user_id NULL로 변경
    await payment_repo.nullify_user_id(user_id)

    # 2. JOIN 사용 테이블 처리 (삭제 또는 익명화)
    await consultation_review_repo.anonymize_user(user_id)
    await inquiry_repo.anonymize_user(user_id)

    # 3. 단순 참조 테이블 처리
    await point_transaction_repo.delete_by_user(user_id)
    await user_bookmark_repo.delete_by_user(user_id)

    # 4. 로그 테이블 처리 (선택)
    await activity_log_repo.delete_by_user(user_id)
    await event_participation_repo.delete_by_user(user_id)
    await notification_log_repo.delete_by_user(user_id)

    # 5. 최종 사용자 삭제
    await user_repo.hard_delete(user_id)
```

| 장점 | 단점 |
|------|------|
| 완전한 데이터 삭제 | 대량의 코드 수정 필요 |
| GDPR 등 규정 준수 용이 | 트랜잭션 복잡도 증가 |
| - | 연관 데이터 손실 |

---

### 옵션 3: LEFT JOIN으로 변경

`admin-backend`의 INNER JOIN을 LEFT JOIN으로 변경.

**변경 전**:
```python
.join(User, Payment.user_id == User.user_id)
```

**변경 후**:
```python
.outerjoin(User, Payment.user_id == User.user_id)
```

| 장점 | 단점 |
|------|------|
| t_user 삭제해도 쿼리 실패 없음 | 사용자 정보가 NULL로 표시 |
| 기존 데이터 유지 | UI에서 NULL 처리 필요 |
| - | FK 제약조건 제거 필요 (t_payment) |

---

### 옵션 4: Tombstone User 패턴 (권장)

탈퇴 전용 사용자(`WITHDRAWN`)를 생성하고, 탈퇴 시 모든 참조를 해당 사용자로 이관 후 원본 삭제.

#### 개념도

```
[탈퇴 전]
t_payment.user_id = "user123"      → t_user.user_id = "user123" (홍길동)
t_inquiry.inquirer_id = "user123"  → t_user.user_id = "user123" (홍길동)

[탈퇴 후]
t_payment.user_id = "WITHDRAWN"    → t_user.user_id = "WITHDRAWN" (탈퇴회원)
t_inquiry.inquirer_id = "WITHDRAWN"→ t_user.user_id = "WITHDRAWN" (탈퇴회원)
t_user.user_id = "user123"         → 삭제됨 ✅
```

#### Tombstone 사용자 생성 (1회성 설정)

```sql
-- 시스템 초기화 시 1회 실행
INSERT INTO t_user (
    user_id,
    nickname,
    email,
    phone,
    user_status,
    created_at
) VALUES (
    'WITHDRAWN',
    '탈퇴회원',
    'withdrawn@system.local',
    '00000000000',
    'SYSTEM',
    NOW()
);
```

#### 구현 코드 예시

```python
# backend/src/services/user_service.py

TOMBSTONE_USER_ID = "WITHDRAWN"

async def withdraw_user_with_tombstone(self, user_id: str) -> UserOutResponse:
    """Tombstone User 패턴을 사용한 회원 탈퇴 처리"""

    async with self.db.begin():
        # 1. 사용자 존재 확인
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # 2. t_user_out에 탈퇴 이력 기록 (원본 정보 보존)
        user_out = await self.user_repo.create_user_out(
            user_id=user.user_id,
            nickname=user.nickname,
            phone=user.phone,
            email=user.email
        )

        # 3. FK 제약조건 테이블 먼저 이관 (t_payment)
        await self.payment_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)

        # 4. JOIN 사용 테이블 이관
        await self.consultation_review_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)
        await self.inquiry_repo.migrate_inquirer_id(user_id, TOMBSTONE_USER_ID)

        # 5. 단순 참조 테이블 이관
        await self.point_transaction_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)
        await self.user_bookmark_repo.delete_by_user_id(user_id)  # 북마크는 삭제

        # 6. 로그성 테이블 처리 (선택: 이관 또는 삭제)
        await self.activity_log_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)
        await self.event_participation_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)
        await self.notification_log_repo.migrate_user_id(user_id, TOMBSTONE_USER_ID)

        # 7. 외부 시스템 처리 (ARS)
        await self.tm60_users_service.delete_user_by_phone(user.phone)

        # 8. 원본 사용자 Hard Delete
        await self.user_repo.hard_delete(user_id)

        return UserOutResponse.model_validate(user_out)
```

#### Repository 메서드 예시

```python
# backend/src/repositories/payment_repository.py

async def migrate_user_id(self, old_user_id: str, new_user_id: str) -> int:
    """user_id를 새로운 값으로 일괄 변경"""
    stmt = (
        update(Payment)
        .where(Payment.user_id == old_user_id)
        .values(user_id=new_user_id)
    )
    result = await self.db.execute(stmt)
    return result.rowcount
```

#### 장단점 비교표

| 구분 | Tombstone User | Soft Delete | Hard Delete | LEFT JOIN |
|------|:--------------:|:-----------:|:-----------:|:---------:|
| **개인정보 완전 삭제** | ✅ | ❌ | ✅ | ❌ |
| **JOIN 정상 작동** | ✅ | ✅ | ❌ | ✅ |
| **관리자 화면 표시** | "탈퇴회원" | "탈퇴회원" | 오류/누락 | NULL |
| **개별 이력 추적** | ⚠️ t_user_out 활용 | ✅ | ❌ | ❌ |
| **GDPR 준수** | ✅ | ⚠️ 마스킹 필요 | ✅ | ⚠️ |
| **구현 복잡도** | 중간 | 낮음 | 높음 | 중간 |
| **저장 공간** | ✅ 절약 | ❌ 누적 | ✅ 절약 | ❌ 누적 |

#### 고려사항

1. **트랜잭션 관리**: 모든 이관 작업은 단일 트랜잭션으로 처리하여 원자성 보장
2. **대량 데이터 처리**: 활동이 많은 사용자는 수백~수천 건 업데이트 필요 → 배치 처리 고려
3. **FK 제약조건 순서**: `t_payment`는 FK가 있으므로 반드시 먼저 이관
4. **이력 추적**: `t_user_out` 테이블에 원본 user_id 보존으로 필요 시 역추적 가능

---

## 8-1. 노출 제어 컬럼 분석

### 테이블별 노출 제어 현황

| 테이블 | 노출 제어 컬럼 | 사이트 공개 노출 | 기존 필터링 | 탈퇴 시 조치 |
|--------|---------------|:---------------:|:-----------:|-------------|
| `t_consultation_review` | `is_visible` ✅ | ✅ 공개 (후기 목록) | ✅ 정상 작동 | `is_visible = False` |
| `t_inquiry` | ❌ 없음 | ❌ 비공개 (본인/관리자) | - | 불필요 |
| `t_payment` | ❌ 없음 | ❌ 비공개 (본인) | - | 불필요 |
| `t_point_transaction` | ❌ 없음 | ❌ 비공개 (본인) | - | 불필요 |
| `t_user_bookmark` | ❌ 없음 | ❌ 비공개 (본인) | - | 삭제 |
| `t_event_participation_log` | ❌ 없음 | ❌ 시스템 로그 | - | 이관/삭제 |
| `t_user_activity_log` | ❌ 없음 | ❌ 시스템 로그 | - | 이관/삭제 |
| `t_notification_log` | ❌ 없음 | ❌ 시스템 로그 | - | 이관/삭제 |

### t_consultation_review 노출 제어 상세

**모델 정의** (`backend/src/models/consultation_review_model.py:75-80`):
```python
is_visible: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=True,
    comment="공개 여부"
)
```

**기존 서비스 쿼리 필터링 현황** (`backend/src/services/consultation_review_service.py`):

| 메서드 | 라인 | 필터 조건 | 상태 |
|--------|------|-----------|:----:|
| `get_user_reviews()` | :129 | `is_visible = True` (default) | ✅ |
| `get_counselor_reviews()` | :188 | `is_visible = True` (default) | ✅ |
| `get_user_review_summary()` | :390 | `is_visible = True` | ✅ |
| `get_my_reviews_detailed()` | :433 | `is_visible = True` | ✅ |
| `get_all_public_reviews()` | :673 | `is_visible = True` | ✅ |
| `get_counselor_reviews_count()` | :229 | `is_visible = True` | ✅ |

### 결론: 쿼리 수정 불필요

```
탈퇴 시 is_visible = False 설정
              ↓
기존 쿼리: WHERE is_visible = True (이미 적용됨)
              ↓
자동으로 노출 제외 ✅
```

**기존 쿼리 변경**: ❌ 불필요
**탈퇴 프로세스에 추가할 코드**:

```python
# consultation_review_repository.py에 추가
async def set_invisible_by_user_id(self, user_id: str) -> int:
    """탈퇴 사용자의 모든 후기 비공개 처리"""
    stmt = (
        update(ConsultationReview)
        .where(ConsultationReview.user_id == user_id)
        .values(is_visible=False, updated_at=datetime.utcnow())
    )
    result = await self.db.execute(stmt)
    return result.rowcount
```

```python
# user_service.py - withdraw_user_with_tombstone() 내 추가
await consultation_review_repo.set_invisible_by_user_id(user_id)
```

---

## 9. 권장 조치사항

### 옵션별 권장 시나리오

| 요구사항 | 권장 옵션 |
|----------|-----------|
| 현재 상태 유지, 최소 변경 | **옵션 1: Soft Delete** |
| GDPR/개인정보 완전 삭제 필수 | **옵션 4: Tombstone User** ⭐ |
| 탈퇴자별 개별 이력 분석 필요 | **옵션 1: Soft Delete** |
| JOIN 유지 + 개인정보 삭제 | **옵션 4: Tombstone User** ⭐ |

### ⭐ Tombstone User 패턴 도입 시 작업 목록

#### Phase 1: 사전 준비
1. [ ] Tombstone 사용자 레코드 생성 (DB 마이그레이션)
2. [ ] `t_user_out` 테이블에 원본 `user_id` 컬럼 확인

#### Phase 2: Repository 구현
3. [ ] `payment_repository.py`: `migrate_user_id()` 메서드 추가
4. [ ] `consultation_review_repository.py`: `migrate_user_id()` 메서드 추가
5. [ ] `consultation_review_repository.py`: `set_invisible_by_user_id()` 메서드 추가 ⭐ **노출 제어**
6. [ ] `inquiry_repository.py`: `migrate_inquirer_id()` 메서드 추가
7. [ ] `point_transaction_repository.py`: `migrate_user_id()` 메서드 추가
8. [ ] `user_bookmark_repository.py`: `delete_by_user_id()` 메서드 확인
9. [ ] 로그 테이블용 Repository 메서드 추가 (선택)

#### Phase 3: Service 구현
10. [ ] `user_service.py`: `withdraw_user_with_tombstone()` 메서드 구현
11. [ ] `user_repository.py`: `hard_delete()` 메서드 추가
12. [ ] 트랜잭션 롤백 처리 로직 구현

#### Phase 4: 테스트 및 검증
13. [ ] 단위 테스트 작성
14. [ ] 통합 테스트 (전체 탈퇴 플로우)
15. [ ] 관리자 페이지 JOIN 쿼리 정상 작동 확인
16. [ ] 탈퇴 후 후기 목록 노출 제외 확인

### 현재 방식 유지 시 (Soft Delete)

1. **현재 Soft Delete 방식 유지**
2. 탈퇴 사용자 개인정보 마스킹 처리 추가 검토
3. 관리자 페이지에서 탈퇴 사용자 표시 방식 정의

### Hard Delete 전환 시 필요 작업 (비권장)

1. `admin-backend/src/models/payment_model.py`: FK 제약조건 제거
2. `admin-backend/src/repositories/` 내 모든 JOIN 쿼리 LEFT JOIN 변환
3. 연관 데이터 삭제/익명화 로직 구현
4. 트랜잭션 관리 및 롤백 처리

---

## 10. 참고 파일 목록

### 모델 파일
- `backend/src/models/user_model.py`
- `backend/src/models/payment_model.py`
- `backend/src/models/consultation_review_model.py`
- `backend/src/models/inquiry_model.py`
- `backend/src/models/point_transaction_model.py`
- `backend/src/models/user_bookmark_model.py`
- `backend/src/models/user_activity_log_model.py`
- `backend/src/models/event_participation_model.py`
- `backend/src/models/notification_log_model.py`
- `admin-backend/src/models/payment_model.py`
- `admin-backend/src/models/consultation_review_model.py`

### 리포지토리 파일
- `admin-backend/src/repositories/payment_repository.py`
- `admin-backend/src/repositories/consultation_review_repository.py`
- `admin-backend/src/repositories/inquiry_repository.py`

### 서비스 파일
- `backend/src/services/user_service.py` (withdraw_user 메서드)
