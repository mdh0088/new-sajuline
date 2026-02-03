"""
데이터베이스 컬럼 한글 매핑.

영문 컬럼명을 사용자 친화적인 한글명으로 변환.

Stories: 2-4
FRs: FR-011, FR-013

TODO (Future Enhancement):
- DB 메타데이터 기반 자동 매핑 생성 (INFORMATION_SCHEMA.COLUMNS)
- 동적 컬럼 매핑 추가 메커니즘
- 사용자 정의 매핑 오버라이드 기능
"""

# 컬럼 영문 → 한글 매핑
# 현재 128개 컬럼 하드코딩 (사용자/상담사/결제/매출/통계 도메인)
COLUMN_MAPPINGS: dict[str, str] = {
    # 공통 컬럼
    "id": "ID",
    "created_at": "생성일시",
    "updated_at": "수정일시",
    "deleted_at": "삭제일시",
    "created_by": "생성자",
    "updated_by": "수정자",
    "status": "상태",
    "type": "유형",
    "name": "이름",
    "email": "이메일",
    "phone": "전화번호",
    "address": "주소",
    "description": "설명",
    "memo": "메모",
    "count": "건수",
    "total": "합계",
    "average": "평균",
    "sum": "총합",
    # 사용자 관련
    "user_id": "사용자 ID",
    "username": "사용자명",
    "user_name": "사용자명",
    "nickname": "닉네임",
    "user_grade": "사용자 등급",
    "gender": "성별",
    "birth_date": "생년월일",
    "birth": "생년월일",
    "join_date": "가입일",
    "last_login": "마지막 로그인",
    "is_active": "활성 여부",
    "is_verified": "인증 여부",
    # 상담사 관련
    "counselor_id": "상담사 ID",
    "counselor_name": "상담사명",
    "counselor_type": "상담사 유형",
    "rating": "평점",
    "review_count": "리뷰 수",
    "consultation_count": "상담 건수",
    # 결제 관련
    "payment_id": "결제 ID",
    "transaction_id": "거래 ID",
    "amount": "금액",
    "total_amount": "총 금액",
    "payment_amount": "결제 금액",
    "discount_amount": "할인 금액",
    "refund_amount": "환불 금액",
    "fee": "수수료",
    "charge": "청구 금액",
    "deposit": "예치금",
    "tax": "세금",
    "commission": "수수료",
    "price": "가격",
    "payment_method": "결제 수단",
    "payment_gateway": "결제 게이트웨이",
    "payment_status": "결제 상태",
    "payment_date": "결제일",
    "refund_date": "환불일",
    # 포인트 관련
    "point": "포인트",
    "point_amount": "포인트 금액",
    "point_balance": "포인트 잔액",
    "earned_points": "적립 포인트",
    "used_points": "사용 포인트",
    "point_history_type": "포인트 히스토리 유형",
    # 매출 관련
    "revenue": "매출",
    "total_revenue": "총 매출",
    "total_sales": "총 매출",
    "sales": "매출",
    "sales_amount": "매출 금액",
    "daily_sales": "일 매출",
    "monthly_sales": "월 매출",
    "yearly_sales": "연 매출",
    # 상담 관련
    "consultation_id": "상담 ID",
    "consultation_type": "상담 유형",
    "consultation_date": "상담일",
    "consultation_status": "상담 상태",
    "duration": "상담 시간",
    "session_duration": "세션 시간",
    "chat_count": "채팅 건수",
    "message_count": "메시지 수",
    "counselor_specialty": "상담사 전문분야",
    # 리뷰 관련
    "review_id": "리뷰 ID",
    "review_content": "리뷰 내용",
    "review_rating": "리뷰 평점",
    "review_rating_average": "평균 평점",
    "review_date": "리뷰 작성일",
    # 통계 관련
    "total_count": "총 건수",
    "active_count": "활성 건수",
    "inactive_count": "비활성 건수",
    "new_count": "신규 건수",
    "daily_count": "일별 건수",
    "monthly_count": "월별 건수",
    "growth_rate": "증가율",
    "conversion_rate": "전환율",
    "retention_rate": "재방문율",
    # 날짜 관련
    "date": "날짜",
    "start_date": "시작일",
    "end_date": "종료일",
    "year": "연도",
    "month": "월",
    "day": "일",
    "week": "주",
    "quarter": "분기",
    # 기타
    "category": "카테고리",
    "tag": "태그",
    "priority": "우선순위",
    "order_number": "주문번호",
    "rank": "순위",
    "percentage": "비율",
}


def get_column_display_name(column_name: str) -> str:
    """컬럼 한글 표시명 조회

    Args:
        column_name: 영문 컬럼명

    Returns:
        str: 한글 표시명 (매핑이 없으면 원본 반환)
    """
    return COLUMN_MAPPINGS.get(column_name.lower(), column_name)


def get_multiple_column_display_names(column_names: list[str]) -> dict[str, str]:
    """여러 컬럼의 한글 표시명 조회

    Args:
        column_names: 영문 컬럼명 리스트

    Returns:
        dict[str, str]: 원본 컬럼명 → 한글 표시명 매핑
    """
    return {col: get_column_display_name(col) for col in column_names}
