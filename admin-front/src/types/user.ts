// ARS tm60_users 사용자 정보 (백엔드 ArsUserInfo와 일치)
export interface ArsUserInfo {
    idx: number;
    u_id: string;
    u_tel: string;
    u_passwd: string;
    u_kname: string;
    u_memcd: string;
    u_login: string;
    u_state: string;
    u_point: number;
    u_fdate: string | null;
    u_rdate: string | null;
    regdate: string | null;
    u_memo: string;
}

// 사용자 목록 아이템 (백엔드 UserListItemResponse와 일치)
export interface UserListItemResponse {
    user_id: string;
    email: string;
    nickname: string;
    phone: string;
    join_type: string; // COMMON | NAVER | KAKAO
    grade_code: string;
    mileage_point: number;
    created_at: string;
    ars_user_info: ArsUserInfo | null;
}

// 사용자 상세 응답 (백엔드 UserDetailResponse와 일치)
export interface UserDetailResponse {
    user: {
        user_id: string;
        email: string;
        nickname: string;
        phone: string;
        join_type: string;
        grade_code: string;
        birth_date: string | null;
        gender: string | null;
        profile_image_url: string | null;
        email_verified: boolean;
        phone_verified: boolean;
        is_active: boolean;
        last_login_at: string | null;
        created_at: string;
        updated_at: string | null;
        withdrawn_at: string | null;
    };
    ars_user_info: ArsUserInfo | null;
}

// 사용자 목록 조회 파라미터 (백엔드 UserListParams와 일치)
export interface UserListParams {
    page: number;
    limit: number;
    search_type: string; // all | user_id | nickname | email | phone
    search_name?: string | null;
    join_type?: string | null; // COMMON | NAVER | KAKAO
    grade?: string | null;
    start_dt?: string | null; // yyyy-mm-dd
    end_dt?: string | null; // yyyy-mm-dd
}

// 사용자 정보 수정 요청 (백엔드 UserUpdateRequest와 일치)
export interface UserUpdateRequest {
    user_id: string;
    nickname?: string | null;
    email?: string | null;
    phone?: string | null;
    password?: string | null;
    grade?: string | null;
    birth_date?: string | null;
}

// 사용자 정보 수정 응답 (백엔드 UserUpdateResponse와 일치)
export interface UserUpdateResponse {
    user_id: string;
    updated: boolean;
}

// 사용자 포인트 조정 요청 (백엔드 UserPointAdjustRequest와 일치)
export interface UserPointAdjustRequest {
    user_id: string;
    amount: number; // 양수 값
    type: 'plus' | 'minus'; // 증가 | 감소
}

// 사용자 포인트 조정 응답 (백엔드 UserPointAdjustResponse와 일치)
export interface UserPointAdjustResponse {
    user_id: string;
    amount: number; // 적용된 금액 (차감은 음수)
    balance_after: number; // 조정 후 잔액
}

// 포인트 거래 내역 아이템 (백엔드 PointTransactionItem과 일치)
export interface PointTransactionItem {
    transaction_id: number;
    user_id: string;
    transaction_type: string; // CHARGE | USE | REFUND | ADJUST | EARN
    currency_type: string; // POINT | MILEAGE
    amount: number;
    balance_after: number;
    reference_type: string | null;
    reference_id: string | null;
    description: string | null;
    created_at: string;
}

// 알림톡 로그 아이템 (백엔드 NotificationLogItem과 일치)
export interface NotificationLogItem {
    log_id: number;
    recipient_type: string;
    recipient_id: string;
    channel: string;
    template_id: number | null;
    title: string | null;
    content: string;
    variables: Record<string, any> | null;
    send_status: string; // PENDING | SENT | FAILED | READ
    provider_response: Record<string, any> | null;
    sent_at: string | null;
    read_at: string | null;
    failed_reason: string | null;
    retry_count: number;
    created_at: string;
}

// API 응답 래퍼
export interface UserListResponse {
    data: UserListItemResponse[];
    meta: {
        pagination: {
            page: number;
            limit: number;
            total: number;
        };
    };
    message: string;
}
