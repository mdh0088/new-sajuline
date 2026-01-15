# 사주라인 데이터 모델

## 개요

사주라인 프로젝트의 데이터베이스 모델을 정리한 문서입니다.

---

## 데이터베이스 구성

| 데이터베이스 | 용도 | 접근 |
|-------------|------|------|
| MariaDB 10.6 | 주 데이터 저장소 | 읽기/쓰기 |
| MSSQL 2005 | 레거시 ARS 시스템 | 읽기 전용 |
| Redis 7.0 | 세션/캐시 | 읽기/쓰기 |

---

## Backend 모델 (사용자 서비스)

### 사용자 (User)
```
users
├── id (PK, UUID)
├── email (UNIQUE)
├── password_hash
├── name
├── phone
├── birth_date
├── birth_time
├── gender (ENUM: male, female)
├── lunar_calendar (BOOLEAN)
├── profile_image
├── provider (ENUM: email, kakao, naver)
├── provider_id
├── is_active (BOOLEAN)
├── is_verified (BOOLEAN)
├── last_login_at
├── created_at
└── updated_at
```

### 상담사 (Counselor)
```
counselors
├── id (PK, UUID)
├── user_id (FK → users)
├── display_name
├── introduction
├── specialty (JSON)
├── profile_image
├── is_online (BOOLEAN)
├── rating (DECIMAL)
├── review_count (INT)
├── consultation_count (INT)
├── price_per_minute (INT)
├── status (ENUM: active, inactive, suspended)
├── created_at
└── updated_at
```

### 상담 예약 (Reservation)
```
reservations
├── id (PK, UUID)
├── user_id (FK → users)
├── counselor_id (FK → counselors)
├── scheduled_at (DATETIME)
├── duration_minutes (INT)
├── status (ENUM: pending, confirmed, completed, cancelled)
├── total_points (INT)
├── created_at
└── updated_at
```

### 채팅방 (ChatRoom)
```
chat_rooms
├── id (PK, UUID)
├── user_id (FK → users)
├── counselor_id (FK → counselors)
├── reservation_id (FK → reservations, nullable)
├── status (ENUM: active, closed)
├── started_at
├── ended_at
├── created_at
└── updated_at
```

### 채팅 메시지 (ChatMessage)
```
chat_messages
├── id (PK, UUID)
├── room_id (FK → chat_rooms)
├── sender_id (FK → users)
├── sender_type (ENUM: user, counselor, system)
├── content (TEXT, encrypted)
├── message_type (ENUM: text, image, file, system)
├── is_read (BOOLEAN)
├── created_at
└── updated_at
```

### 결제 (Payment)
```
payments
├── id (PK, UUID)
├── user_id (FK → users)
├── order_id (UNIQUE)
├── amount (INT)
├── points (INT)
├── payment_method (ENUM: card, bank, kakao, naver)
├── status (ENUM: pending, completed, failed, refunded)
├── pg_transaction_id
├── paid_at
├── created_at
└── updated_at
```

### 포인트 거래 (PointTransaction)
```
point_transactions
├── id (PK, UUID)
├── user_id (FK → users)
├── type (ENUM: charge, use, refund, bonus, admin)
├── amount (INT)
├── balance_after (INT)
├── description
├── reference_type (ENUM: payment, consultation, review, admin)
├── reference_id
├── created_at
└── updated_at
```

### 리뷰 (Review)
```
reviews
├── id (PK, UUID)
├── user_id (FK → users)
├── counselor_id (FK → counselors)
├── reservation_id (FK → reservations)
├── rating (INT, 1-5)
├── content (TEXT)
├── is_visible (BOOLEAN)
├── created_at
└── updated_at
```

### 공지사항 (Notice)
```
notices
├── id (PK, UUID)
├── title
├── content (TEXT)
├── category (ENUM: general, event, update, maintenance)
├── is_pinned (BOOLEAN)
├── is_active (BOOLEAN)
├── view_count (INT)
├── created_at
└── updated_at
```

### 문의 (Inquiry)
```
inquiries
├── id (PK, UUID)
├── user_id (FK → users)
├── category (ENUM: general, payment, counselor, technical)
├── title
├── content (TEXT)
├── status (ENUM: pending, answered, closed)
├── created_at
└── updated_at
```

### 문의 답변 (InquiryReply)
```
inquiry_replies
├── id (PK, UUID)
├── inquiry_id (FK → inquiries)
├── admin_id (FK → admins)
├── content (TEXT)
├── created_at
└── updated_at
```

### 배너 (Banner)
```
banners
├── id (PK, UUID)
├── title
├── image_url
├── link_url
├── position (ENUM: main, sub, popup)
├── sort_order (INT)
├── is_active (BOOLEAN)
├── start_date
├── end_date
├── created_at
└── updated_at
```

### 알림 (Notification)
```
notifications
├── id (PK, UUID)
├── user_id (FK → users)
├── type (ENUM: consultation, payment, system, promotion)
├── title
├── content
├── is_read (BOOLEAN)
├── data (JSON)
├── created_at
└── updated_at
```

### 운세 기록 (FortuneHistory)
```
fortune_histories
├── id (PK, UUID)
├── user_id (FK → users)
├── type (ENUM: daily, weekly, monthly, custom)
├── content (TEXT)
├── ai_model
├── created_at
└── updated_at
```

### 사주 프로필 (SajuProfile)
```
saju_profiles
├── id (PK, UUID)
├── user_id (FK → users, UNIQUE)
├── birth_year
├── birth_month
├── birth_day
├── birth_hour
├── is_lunar (BOOLEAN)
├── gender (ENUM: male, female)
├── saju_data (JSON)
├── created_at
└── updated_at
```

---

## Admin-Backend 모델 (관리자 서비스)

### 관리자 (Admin)
```
admins
├── id (PK, UUID)
├── email (UNIQUE)
├── password_hash
├── name
├── role (ENUM: super, admin, manager)
├── permissions (JSON)
├── is_active (BOOLEAN)
├── last_login_at
├── created_at
└── updated_at
```

### 상담사 신청 (CounselorApplication)
```
counselor_applications
├── id (PK, UUID)
├── user_id (FK → users)
├── name
├── phone
├── email
├── introduction (TEXT)
├── experience (TEXT)
├── certification_files (JSON)
├── status (ENUM: pending, approved, rejected)
├── reviewed_by (FK → admins)
├── reviewed_at
├── rejection_reason
├── created_at
└── updated_at
```

### 포인트 상품 (PointProduct)
```
point_products
├── id (PK, UUID)
├── name
├── description
├── points (INT)
├── price (INT)
├── bonus_points (INT)
├── sort_order (INT)
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

### 프로모션 (Promotion)
```
promotions
├── id (PK, UUID)
├── name
├── description
├── discount_type (ENUM: percent, fixed)
├── discount_value (INT)
├── min_amount (INT)
├── max_discount (INT)
├── coupon_code
├── usage_limit (INT)
├── used_count (INT)
├── start_date
├── end_date
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

### 회원 등급 (Grade)
```
grades
├── id (PK, UUID)
├── name
├── min_points (INT)
├── discount_rate (DECIMAL)
├── benefits (JSON)
├── color
├── icon
├── sort_order (INT)
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

### 등급 변경 로그 (GradeChangeLog)
```
grade_change_logs
├── id (PK, UUID)
├── user_id (FK → users)
├── previous_grade_id (FK → grades)
├── new_grade_id (FK → grades)
├── reason
├── changed_by (FK → admins, nullable)
├── created_at
└── updated_at
```

### 기획전 (Exhibition)
```
exhibitions
├── id (PK, UUID)
├── title
├── description (TEXT)
├── banner_image
├── counselor_ids (JSON)
├── discount_rate (DECIMAL)
├── start_date
├── end_date
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

### 마일리지 상품 (MileageProduct)
```
mileage_products
├── id (PK, UUID)
├── name
├── description
├── mileage_cost (INT)
├── stock (INT)
├── image_url
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

### 상담 후기 (ConsultationReview)
```
consultation_reviews
├── id (PK, UUID)
├── user_id (FK → users)
├── counselor_id (FK → counselors)
├── reservation_id (FK → reservations)
├── rating (INT, 1-5)
├── content (TEXT)
├── status (ENUM: pending, approved, rejected)
├── reviewed_by (FK → admins)
├── reviewed_at
├── created_at
└── updated_at
```

### 알림 템플릿 (NotificationTemplate)
```
notification_templates
├── id (PK, UUID)
├── type
├── title_template
├── content_template
├── variables (JSON)
├── is_active (BOOLEAN)
├── created_at
└── updated_at
```

---

## ARS 연동 모델 (MSSQL 2005, 읽기 전용)

### TM60 회원 (tm60_member)
```
tm60_member (읽기 전용)
├── member_id (PK)
├── name
├── phone
├── birth_date
├── gender
├── register_date
└── status
```

### TM60 사용자 (tm60_users)
```
tm60_users (읽기 전용)
├── user_id (PK)
├── username
├── email
├── phone
├── created_at
└── status
```

---

## Redis 데이터 구조

### 세션 저장
```
session:{session_id} → JSON {user_id, created_at, expires_at}
TTL: 7 days
```

### 캐시
```
cache:user:{user_id} → JSON {user_data}
TTL: 5 minutes

cache:counselor:{counselor_id} → JSON {counselor_data}
TTL: 1 minute

cache:fortune:{user_id}:{date} → JSON {fortune_data}
TTL: 24 hours
```

### 실시간 상태
```
online:counselors → SET {counselor_ids}
TTL: none (managed by application)

typing:{room_id} → SET {user_ids}
TTL: 5 seconds
```

### Rate Limiting
```
ratelimit:{ip}:{endpoint} → INT (count)
TTL: 1 minute
```

---

## 인덱스 전략

### 주요 인덱스
```sql
-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_provider ON users(provider, provider_id);
CREATE INDEX idx_users_created_at ON users(created_at);

-- counselors
CREATE INDEX idx_counselors_status ON counselors(status, is_online);
CREATE INDEX idx_counselors_rating ON counselors(rating DESC);

-- payments
CREATE INDEX idx_payments_user_status ON payments(user_id, status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- chat_messages
CREATE INDEX idx_messages_room ON chat_messages(room_id, created_at);

-- point_transactions
CREATE INDEX idx_points_user ON point_transactions(user_id, created_at DESC);
```

---

## ERD (Entity Relationship Diagram)

```
┌─────────┐     ┌──────────────┐     ┌────────────┐
│  users  │────<│ reservations │>────│ counselors │
└────┬────┘     └──────────────┘     └─────┬──────┘
     │                                      │
     │          ┌──────────────┐            │
     └─────────<│  chat_rooms  │>───────────┘
                └──────┬───────┘
                       │
                ┌──────┴───────┐
                │chat_messages │
                └──────────────┘

┌─────────┐     ┌──────────────┐
│  users  │────<│   payments   │
└────┬────┘     └──────────────┘
     │
     │          ┌──────────────────┐
     └─────────<│point_transactions│
                └──────────────────┘

┌─────────┐     ┌──────────────┐     ┌────────────┐
│  users  │────<│   reviews    │>────│ counselors │
└─────────┘     └──────────────┘     └────────────┘
```
