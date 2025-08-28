# 데이터베이스 마이그레이션 매핑 문서

## 개요
이 문서는 기존 MariaDB 스키마에서 새로운 개선된 스키마로의 마이그레이션 매핑 관계를 정의합니다.

## 테이블 매핑 요약

### 사용자 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_USER | t_user | 기본 정보 + 인증 정보 통합 |
| TBL_USER.MILEAGE | t_user_point_balance | 포인트/마일리지 잔액 분리 |
| - | t_user_preference | 신규 추가 |
| TBL_USER_EX | - | 탈퇴 사용자는 user_status로 관리 |

### 상담사 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_CS (승인됨) | t_counselor | 승인된 상담사만 |
| TBL_CS (미승인) | t_counselor_application | 신청 정보 |
| TBL_CS.IMG1~5 | t_counselor_application_image | 이미지 정규화 |
| TBL_CS.분야_YN | t_counselor_specialty | 전문분야 정규화 |
| TBL_CS.WORK_TIME | t_counselor_schedule | 근무시간 구조화 |

### 상담 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| ars.tm60_chatlog | t_consultation_session | 상담 세션 |
| - | t_chat_message | 채팅 메시지 분리 |
| TBL_KAKAO_ALARM_WAIT_LIST | t_consultation_queue | 대기열 관리 |

### 후기/신고 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_CS_REVIEW | t_consultation_review | 상담 후기 |
| TBL_CS_REVIEW_LIKE | t_review_like | 좋아요 |
| TBL_CS_REPORT | t_report | 신고 (테이블명 수정) |
| TBL_CS_REVIEW_DUMY | t_review_dummy | 더미 후기 |

### 결제/포인트 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_USER_TRADE | t_payment | 결제 내역 |
| TBL_PRODUCT | t_point_product | 포인트 상품 |
| TBL_USER_POINT_HIST | t_point_transaction | 포인트 거래 |
| TBL_MILEAGE_SAVE | t_point_transaction | 마일리지도 통합 |
| TBL_MILEAGE_USAGE | t_point_transaction | 통합 관리 |
| TBL_MILEAGE_BALANCE | t_user_point_balance | 사용자 잔액에 통합 |
| - | t_external_point_sync | 외부 동기화 로그 신규 |

### 관리자/시스템 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_MANAGER | t_admin | 관리자 |
| - | t_system_config | 시스템 설정 신규 |
| TBL_GRADE | t_grade | 등급 정의 |
| TBL_GRADE_BATCH_CONFIG | t_grade_batch_config | 배치 설정 |
| TBL_MEMBERSHIP_BATCH_CONFIG | - | 중복 제거 |
| TBL_MILEAGE_CONFIG | t_mileage_config | 마일리지 설정 |

### 알림 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_KAKAO_ALARM_TEMPLATE | t_notification_template | 알림 템플릿 확장 |
| TBL_KAKAO_ALARM_HISTORY | t_notification_log | 알림 로그 확장 |

### 콘텐츠 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_CS_NOTICE | t_notice | 공지사항 통합 |
| TBL_ADMIN_FAQ | t_faq | FAQ 통합 |
| TBL_CS_FAQ | t_inquiry | 1:1 문의로 변경 |
| TBL_CS_ADMIN_FAQ | t_inquiry | 1:1 문의로 통합 |
| TBL_BANNER | t_banner | 배너 |
| TBL_POPUP | t_banner | 배너로 통합 (type 구분) |
| TBL_EVENT | t_event | 이벤트 |

### 로그 도메인
| 기존 테이블 | 신규 테이블 | 비고 |
|-------------|-------------|------|
| TBL_LOG_USER_LOGIN | t_user_activity_log | 활동 로그 통합 |
| TBL_LOG_SEARCH | t_search_log | 검색 로그 |
| TBL_EVENT_LOG | t_event_participation_log | 이벤트 참여 로그 |
| TBL_GRADE_HISTORY | t_grade_change_log | 등급 변경 로그 |
| TBL_BATCH | t_batch_execution_log | 배치 실행 로그 |

### 제거 테이블
- TBL_EXHIBITION - 사용하지 않음
- TBL_EXHIBITION_REPLY - 사용하지 않음
- TBL_LOG_DAILY - 사용하지 않음
- TBL_MILEAGE_PRODUCT - TBL_PRODUCT와 중복
- TBL_USER_EX - user_status로 관리

## 상세 컬럼 매핑

### 1. TBL_USER → t_user + t_user_point_balance
```
기존 테이블: TBL_USER
신규 테이블: t_user, t_user_point_balance

[t_user]
IDX                  → user_id (AUTO_INCREMENT)
USER_ID              → login_id
EMAIL                → email
PASSWORD             → password_hash
NICK_NAME            → nickname
PHONE                → phone
JOIN_TYPE            → join_type (ENUM → VARCHAR)
-                    → social_provider (JOIN_TYPE에서 추출)
-                    → social_id (JOIN_TYPE이 소셜인 경우 USER_ID)
USER_STATUS          → user_status (1/2/3 → ACTIVE/DORMANT/WITHDRAWN)
GRADE                → grade_code
-                    → profile_image_url (신규)
-                    → birth_date (신규)
-                    → gender (신규)
-                    → marketing_agreed (신규)
-                    → password_changed_at (신규)
-                    → failed_login_count (신규)
-                    → locked_until (신규)
REGIST_DATE          → created_at
UPDATE_DATE          → updated_at
LAST_LOGIN           → last_login_at
-                    → withdrawn_at (신규)

[t_user_point_balance]
IDX                  → user_id (FK)
MILEAGE              → mileage_balance
-                    → point_balance (외부 시스템에서 동기화)
-                    → total_earned_point (신규)
-                    → total_used_point (신규)
-                    → total_earned_mileage (신규)
-                    → total_used_mileage (신규)
```

### 2. TBL_CS → t_counselor + t_counselor_application
```
기존 테이블: TBL_CS
신규 테이블: t_counselor, t_counselor_application, t_counselor_application_image, 
           t_counselor_specialty, t_counselor_schedule

[승인된 상담사 → t_counselor]
IDX                  → counselor_id
CODE                 → counselor_code
EMAIL                → login_id (로그인용)
EMAIL                → email
PASSWORD             → password_hash
NAME                 → name
NICK_NAME            → nickname
PHONE                → phone
IMG                  → profile_image_url
SHORT_INFO           → introduction_short
GREETING             → greeting_message
CAREER               → career_info
STATUS               → counselor_status (1/2/3 → WAITING/CONSULTING/ABSENT)
GRADE                → grade
-                    → rating_avg (신규)
-                    → rating_count (신규)
-                    → consultation_count (신규)
AFTER_AMOUNT         → point_per_minute
NEW_YN               → is_new (CHAR → TINYINT)
CS_DATE              → approved_at
UPDATE_DATE          → updated_at
LAST_LOGIN           → last_login_at
OUT_DATE             → withdrawn_at

[미승인 상담사 → t_counselor_application]
IDX                  → application_id
NAME                 → name
NICK_NAME            → nickname
EMAIL                → email
PHONE                → phone
ADDRESS              → address
TYPE                 → specialty_types (JSON 배열)
CS_KEYWORD           → keywords
IMG                  → selected_image_url (선택된 이미지)
APPROVAL_YN          → application_status (PENDING/REVIEWING/APPROVED/REJECTED)
RECRUIT_DATE         → created_at

[상담사 이미지 → t_counselor_application_image]
IMG1                 → image_url (image_order=1)
IMG2                 → image_url (image_order=2)
IMG3                 → image_url (image_order=3)
IMG4                 → image_url (image_order=4)
IMG5                 → image_url (image_order=5)

[전문분야 → t_counselor_specialty]
TARO_YN='Y'          → specialty_code='TARO'
LUCK_YN='Y'          → specialty_code='SAJU'
FORTUNE_YN='Y'       → specialty_code='FORTUNE'
EASY_YN='Y'          → specialty_code='EASY'

[근무시간 → t_counselor_schedule]
WORK_TIME (TEXT)     → 구조화된 스케줄 레코드
```

### 3. 외부 MSSQL 연동
```
외부 테이블: ars.tm60_chatlog
신규 테이블: t_consultation_session + t_external_point_sync

[상담 세션]
idx                  → (외부 참조 ID로 저장)
u_id                 → user_id (매핑 필요)
m_code               → counselor_code (매핑 필요)
chatstart            → started_at
chatend              → ended_at
chattm               → duration_seconds
usepoint             → point_used
-                    → session_code (생성)
-                    → session_status

[포인트 동기화]
u_id                 → external_user_id
usepoint             → point_amount
-                    → sync_status
-                    → external_response
```

### 4. TBL_USER_TRADE → t_payment
```
기존 테이블: TBL_USER_TRADE
신규 테이블: t_payment

IDX                  → payment_id
ORDER_NO             → order_no
USER_ID              → user_id (문자열 → FK 매핑)
PRODUCT_NAME         → (product_id로 매핑)
AMOUNT               → amount (VARCHAR → DECIMAL)
USER_POINT           → point_amount + bonus_point
PGCODE               → payment_method
TID                  → pg_tid
CID                  → (pg_response JSON에 포함)
PAY_TYPE             → payment_status (SUCCESS → SUCCESS 등)
REGIST_DATE          → created_at
UPDATE_DATE          → updated_at
CANCEL_DATE          → cancelled_at
CANCEL_AMOUNT        → refund_amount
기타 PG 데이터       → pg_response (JSON)
```

### 5. 포인트/마일리지 통합
```
기존: TBL_USER_POINT_HIST, TBL_MILEAGE_SAVE, TBL_MILEAGE_USAGE
신규: t_point_transaction

[TBL_USER_POINT_HIST → t_point_transaction]
USER_IDX             → user_id
POINT_ACTION         → transaction_type (지급→CHARGE, 차감→USE)
ACTIVE_POINT         → amount
USER_POINT           → balance_after
REASON               → description
-                    → currency_type='POINT'
REGIST_DATE          → created_at

[TBL_MILEAGE_SAVE → t_point_transaction]
USER_ID              → user_id
AMOUNT               → amount (양수)
-                    → transaction_type='EARN'
-                    → currency_type='MILEAGE'
SOURCE_TYPE          → reference_type
SOURCE_ID            → reference_id
REASON               → description
SAVE_RATE            → earn_rate
EXPIRE_DATE          → expires_at

[TBL_MILEAGE_USAGE → t_point_transaction]
USER_ID              → user_id
USE_AMOUNT           → amount (음수)
-                    → transaction_type='USE'
-                    → currency_type='MILEAGE'
SOURCE_TYPE          → reference_type
SOURCE_ID            → reference_id
REASON               → description
```

### 6. 알림 통합
```
기존: TBL_KAKAO_ALARM_TEMPLATE, TBL_KAKAO_ALARM_HISTORY
신규: t_notification_template, t_notification_log

[TBL_KAKAO_ALARM_TEMPLATE → t_notification_template]
IDX                  → template_id
CODE                 → template_code
NAME                 → template_name
CONTENT              → content_template
PC_LINK              → button_info.pc_link (JSON)
MO_LINK              → button_info.mo_link (JSON)
-                    → channel='KAKAO'

[TBL_KAKAO_ALARM_HISTORY → t_notification_log]
IDX                  → log_id
USER_TYPE            → recipient_type
USER_IDX             → recipient_id
CODE                 → (template_id 매핑)
SEND_CONT            → content
RESULT_CODE          → send_status (0→SUCCESS, 기타→FAILED)
-                    → channel='KAKAO'
NO                   → provider_response.transaction_no (JSON)
REGIST_DATE          → created_at
```

### 7. 문의/FAQ 통합
```
기존: TBL_ADMIN_FAQ, TBL_CS_FAQ, TBL_CS_ADMIN_FAQ
신규: t_inquiry, t_faq

[실제 FAQ → t_faq]
- 반복적인 질문과 답변은 t_faq로 이동

[1:1 문의 → t_inquiry]
USER_IDX             → inquirer_id
USER_TYPE            → inquirer_type
USER_TITLE           → title
USER_CONT            → content
ADMIN_CONT           → admin_reply
ATTACH_FILE          → attachments (JSON)
USER_REGIST_DATE     → created_at
ADMIN_REGIST_DATE    → answered_at
```

### 8. 로그 테이블 통합
```
[TBL_LOG_USER_LOGIN → t_user_activity_log]
USER_IDX             → user_id
IP                   → ip_address
TYPE                 → activity_type='LOGIN'
OS                   → user_agent
YEAR/MONDTH/DAY      → created_at (통합)
REGIST_DATE          → created_at

[TBL_LOG_SEARCH → t_search_log]
USER_IDX             → user_id
USER_TYPE            → user_type
KEYWORD              → keyword
REGIST_DATE          → created_at
```

## 데이터 변환 규칙

### 1. ENUM → VARCHAR 변환
```
USER_STATUS:
- '1' → 'ACTIVE'
- '2' → 'DORMANT'
- '3' → 'WITHDRAWN'

JOIN_TYPE:
- 'common' → 'COMMON'
- 'kakao' → 'KAKAO'
- 'naver' → 'NAVER'

CS STATUS:
- '1' → 'WAITING'
- '2' → 'CONSULTING'
- '3' → 'ABSENT'
```

### 2. Y/N → TINYINT(1) 변환
```
'Y' → 1
'N' → 0
NULL → 0
```

### 3. 날짜 분리 → DATETIME 통합
```
YEAR + MONDTH + DAY + REGIST_DATE(시간) → created_at
```

### 4. 금액 타입 통일
```
모든 금액: DECIMAL(12,2)
포인트/마일리지: INT
```

## 주의사항

1. **외래키 관계**: 마이그레이션 시 참조 무결성 확인 필요
2. **중복 데이터**: TBL_USER.MILEAGE와 TBL_MILEAGE_BALANCE 중 최신값 사용
3. **외부 시스템**: MSSQL 데이터는 동기화 로그 테이블로 관리
4. **더미 데이터**: t_review_dummy는 실제 후기와 분리 관리
5. **비밀번호**: 평문인 경우 bcrypt 해시 적용 필요
6. **NULL 처리**: 필수 필드의 NULL값은 기본값으로 대체