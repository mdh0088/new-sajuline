/**
 * 결제 관리 타입 정의
 * 백엔드 API: /api/v1/payment_api.py
 */

/**
 * 결제 목록 조회 파라미터
 */
export interface PaymentListParams {
    page: number;
    limit: number;
    search_type?: string; // all|user_id|nickname|email|phone
    search_name?: string;
    amount?: number;
    payment_method?: string;
    payment_status?: string; // SUCCESS|HOLD|FAIL
    start_dt?: string; // yyyy-mm-dd
    end_dt?: string; // yyyy-mm-dd
}

/**
 * 결제 아이템 (리스트용)
 */
export interface PaymentItem {
    payment_id: number;
    order_no: string;
    user_id: string;
    amount: number;
    payment_method: string;
    payment_status: string;
    paid_at: string | null;
    created_at: string;
}

/**
 * 결제와 유저 정보를 포함한 아이템
 */
export interface PaymentWithUserItem {
    payment: Record<string, any>;
    user: Record<string, any>;
}

/**
 * 결제 목록 응답
 */
export interface PaymentListResponse {
    items: PaymentWithUserItem[];
    page: number;
    limit: number;
    total: number;
}

/**
 * 결제 상세 응답
 */
export interface PaymentDetailResponse {
    payment: Record<string, any>;
    user: Record<string, any>;
}
