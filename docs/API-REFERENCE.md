# 사주라인 API 레퍼런스

## 개요

사주라인 프로젝트의 API 엔드포인트를 정리한 문서입니다.

---

## Backend API (사용자 서비스)

**Base URL**: `https://api.sajuline.com` (Production)
**Local URL**: `http://localhost:8000`

### 인증 (Auth)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/auth/login` | 이메일 로그인 |
| POST | `/api/v1/auth/logout` | 로그아웃 |
| POST | `/api/v1/auth/register` | 회원가입 |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 |
| GET | `/api/v1/auth/kakao` | 카카오 OAuth |
| GET | `/api/v1/auth/naver` | 네이버 OAuth |

### 사용자 (User)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/users/me` | 내 정보 조회 |
| PUT | `/api/v1/users/me` | 내 정보 수정 |
| DELETE | `/api/v1/users/me` | 회원 탈퇴 |
| GET | `/api/v1/users/saju-info` | 사주 정보 조회 |
| PUT | `/api/v1/users/saju-info` | 사주 정보 수정 |

### 상담사 (Counselor)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/counselors` | 상담사 목록 |
| GET | `/api/v1/counselors/{id}` | 상담사 상세 |
| GET | `/api/v1/counselors/{id}/schedule` | 상담사 스케줄 |
| POST | `/api/v1/counselors/{id}/reserve` | 상담 예약 |

### AI 운세 (Fortune)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/fortune/daily` | 오늘의 운세 |
| GET | `/api/v1/fortune/weekly` | 주간 운세 |
| GET | `/api/v1/fortune/monthly` | 월간 운세 |
| POST | `/api/v1/fortune/analysis` | AI 사주 분석 |

### 채팅 (Chat)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/chat/rooms` | 채팅방 목록 |
| GET | `/api/v1/chat/rooms/{id}` | 채팅방 상세 |
| GET | `/api/v1/chat/rooms/{id}/messages` | 메시지 조회 |
| POST | `/api/v1/chat/rooms` | 채팅방 생성 |

### 결제 (Payment)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/payments` | 결제 내역 |
| POST | `/api/v1/payments/request` | 결제 요청 |
| POST | `/api/v1/payments/webhook` | 결제 웹훅 |
| GET | `/api/v1/payments/{id}` | 결제 상세 |

### 포인트 (Point)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/points/balance` | 포인트 잔액 |
| GET | `/api/v1/points/history` | 포인트 내역 |
| POST | `/api/v1/points/use` | 포인트 사용 |

### 리뷰 (Review)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/reviews` | 리뷰 목록 |
| POST | `/api/v1/reviews` | 리뷰 작성 |
| PUT | `/api/v1/reviews/{id}` | 리뷰 수정 |
| DELETE | `/api/v1/reviews/{id}` | 리뷰 삭제 |

### 공지사항 (Notice)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/notices` | 공지 목록 |
| GET | `/api/v1/notices/{id}` | 공지 상세 |

### 문의 (Inquiry)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/inquiries` | 문의 목록 |
| POST | `/api/v1/inquiries` | 문의 작성 |
| GET | `/api/v1/inquiries/{id}` | 문의 상세 |

### 배너 (Banner)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/banners` | 배너 목록 |

### 알림 (Notification)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/notifications` | 알림 목록 |
| PUT | `/api/v1/notifications/{id}/read` | 알림 읽음 처리 |

### 파일 업로드
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/upload/image` | 이미지 업로드 |
| POST | `/api/v1/upload/file` | 파일 업로드 |

### 시스템
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 헬스체크 |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

---

## Admin-Backend API (관리자 서비스)

**Base URL**: `https://admin-api.sajuline.com` (Production)
**Local URL**: `http://localhost:8001`

### 인증 (Auth)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/auth/login` | 관리자 로그인 |
| POST | `/api/v1/auth/logout` | 로그아웃 |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 |

### 대시보드 (Dashboard)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/dashboard/summary` | 요약 통계 |
| GET | `/api/v1/dashboard/charts` | 차트 데이터 |
| GET | `/api/v1/dashboard/recent` | 최근 활동 |

### 회원 관리 (User)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/users` | 회원 목록 |
| GET | `/api/v1/users/{id}` | 회원 상세 |
| PUT | `/api/v1/users/{id}` | 회원 수정 |
| DELETE | `/api/v1/users/{id}` | 회원 삭제 |
| PUT | `/api/v1/users/{id}/status` | 상태 변경 |

### 상담사 관리 (Counselor)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/counselors` | 상담사 목록 |
| GET | `/api/v1/counselors/{id}` | 상담사 상세 |
| POST | `/api/v1/counselors` | 상담사 등록 |
| PUT | `/api/v1/counselors/{id}` | 상담사 수정 |
| DELETE | `/api/v1/counselors/{id}` | 상담사 삭제 |

### 상담사 신청 (Counselor Application)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/counselor-applications` | 신청 목록 |
| GET | `/api/v1/counselor-applications/{id}` | 신청 상세 |
| PUT | `/api/v1/counselor-applications/{id}/approve` | 승인 |
| PUT | `/api/v1/counselor-applications/{id}/reject` | 거절 |

### 결제 관리 (Payment)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/payments` | 결제 목록 |
| GET | `/api/v1/payments/{id}` | 결제 상세 |
| POST | `/api/v1/payments/{id}/refund` | 환불 처리 |

### 마일리지 관리 (Mileage)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/mileage` | 마일리지 목록 |
| POST | `/api/v1/mileage/adjust` | 마일리지 조정 |

### 포인트 상품 (Point Product)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/point-products` | 상품 목록 |
| POST | `/api/v1/point-products` | 상품 등록 |
| PUT | `/api/v1/point-products/{id}` | 상품 수정 |
| DELETE | `/api/v1/point-products/{id}` | 상품 삭제 |

### 프로모션 (Promotion)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/promotions` | 프로모션 목록 |
| POST | `/api/v1/promotions` | 프로모션 등록 |
| PUT | `/api/v1/promotions/{id}` | 프로모션 수정 |
| DELETE | `/api/v1/promotions/{id}` | 프로모션 삭제 |

### 등급 관리 (Grade)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/grades` | 등급 목록 |
| POST | `/api/v1/grades` | 등급 등록 |
| PUT | `/api/v1/grades/{id}` | 등급 수정 |

### 공지사항 관리 (Notice)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/notices` | 공지 목록 |
| POST | `/api/v1/notices` | 공지 등록 |
| PUT | `/api/v1/notices/{id}` | 공지 수정 |
| DELETE | `/api/v1/notices/{id}` | 공지 삭제 |

### 배너 관리 (Banner)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/banners` | 배너 목록 |
| POST | `/api/v1/banners` | 배너 등록 |
| PUT | `/api/v1/banners/{id}` | 배너 수정 |
| DELETE | `/api/v1/banners/{id}` | 배너 삭제 |

### 기획전 (Exhibition)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/exhibitions` | 기획전 목록 |
| POST | `/api/v1/exhibitions` | 기획전 등록 |
| PUT | `/api/v1/exhibitions/{id}` | 기획전 수정 |
| DELETE | `/api/v1/exhibitions/{id}` | 기획전 삭제 |

### 문의 관리 (Inquiry)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/inquiries` | 문의 목록 |
| GET | `/api/v1/inquiries/{id}` | 문의 상세 |
| POST | `/api/v1/inquiries/{id}/reply` | 답변 작성 |

### 상담 후기 관리 (Consultation Review)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/consultation-reviews` | 후기 목록 |
| PUT | `/api/v1/consultation-reviews/{id}/approve` | 승인 |
| DELETE | `/api/v1/consultation-reviews/{id}` | 삭제 |

### 관리자 계정 (Admin)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/admins` | 관리자 목록 |
| POST | `/api/v1/admins` | 관리자 등록 |
| PUT | `/api/v1/admins/{id}` | 관리자 수정 |
| DELETE | `/api/v1/admins/{id}` | 관리자 삭제 |

### 시스템
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 헬스체크 |
| GET | `/docs` | Swagger UI |

---

## WebSocket API

### 채팅 이벤트
| Event | Direction | 설명 |
|-------|-----------|------|
| `connect` | Client → Server | 연결 |
| `disconnect` | Client → Server | 연결 해제 |
| `join_room` | Client → Server | 채팅방 입장 |
| `leave_room` | Client → Server | 채팅방 퇴장 |
| `send_message` | Client → Server | 메시지 전송 |
| `new_message` | Server → Client | 새 메시지 수신 |
| `typing` | Bidirectional | 타이핑 상태 |
| `read_receipt` | Server → Client | 읽음 확인 |

---

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "message": "요청이 성공적으로 처리되었습니다."
}
```

### 페이지네이션 응답
```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "details": [ ... ]
  }
}
```

---

## 인증

### JWT 토큰
- **Access Token**: 15분 유효, Authorization 헤더
- **Refresh Token**: 7일 유효, HttpOnly 쿠키

### 헤더 형식
```
Authorization: Bearer {access_token}
```

### Rate Limiting
- **일반 API**: 60 requests/minute
- **인증 API**: 10 requests/minute
- **업로드 API**: 10 requests/minute

---

## 에러 코드

| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `VALIDATION_ERROR` | 422 | 입력값 오류 |
| `RATE_LIMIT` | 429 | 요청 제한 초과 |
| `INTERNAL_ERROR` | 500 | 서버 오류 |
