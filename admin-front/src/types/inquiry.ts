/**
 * 문의사항 타입 정의
 */

// ===========================================
// 상담사 문의 (CS_TO_ADMIN)
// ===========================================

export interface InquiryListParams {
    page: number;
    limit: number;
    search_type: string; // all|user_title|user_content|reply_content
    search_name?: string;
    counselor_id?: string;
    start_dt?: string;
    end_dt?: string;
}

export interface CounselorInquiryItem {
    inquiry: {
        inquiry_id: number;
        inquirer_type: string;
        inquirer_id: string;
        category: string;
        title: string | null;
        content: string;
        reply_content: string | null;
        answered_at: string | null;
        created_at: string;
    };
    counselor: {
        counselor_id: string;
        name: string;
        nickname: string;
        phone: string;
    };
}

export interface InquiryReplyUpdateRequest {
    inquiry_id: number;
    reply_content: string;
}

export interface InquiryUpdateRequest {
    inquiry_id: number;
    title?: string;
    content?: string;
    reply_content?: string;
}

export interface InquiryDeleteResponse {
    inquiry_id: number;
    deleted: boolean;
}

// ===========================================
// 1:1 고객센터 문의 (USER_TO_ADMIN)
// ===========================================

export interface UserInquiryListParams {
    page: number;
    limit: number;
    search_type: string; // all|title|content
    search_name?: string;
    user_id?: string;
    start_dt?: string;
    end_dt?: string;
}

export interface UserInquiryItem {
    inquiry: {
        inquiry_id: number;
        inquirer_type: string;
        inquirer_id: string;
        category: string;
        title: string | null;
        content: string;
        reply_content: string | null;
        answered_at: string | null;
        created_at: string;
    };
    user: {
        user_id: string;
        name: string;
        nickname: string;
        email: string;
        phone: string;
    };
}

// ===========================================
// 1:1 상담사 문의 (USER_TO_CS)
// ===========================================

export interface UserToCsListParams {
    page: number;
    limit: number;
    search_type: string; // all|user_title|user_content|reply_content
    search_name?: string;
    user_id?: string;
    counselor_id?: string;
    start_dt?: string;
    end_dt?: string;
}

export interface UserToCsInquiryItem {
    inquiry: {
        inquiry_id: number;
        inquirer_type: string;
        inquirer_id: string;
        category: string;
        counselor_id: string | null;
        title: string | null;
        content: string;
        reply_content: string | null;
        answered_at: string | null;
        created_at: string;
    };
    user: {
        user_id: string;
        name: string;
        nickname: string;
        email: string;
        phone: string;
    };
    counselor: {
        counselor_id: string;
        name: string;
        nickname: string;
        phone: string;
    } | null;
}
